# """
# ed_recorder_autologin.py - chế độ "ghi hình": BẠN tự thao tác trên web như bình thường
# (đổi Intermediate 2/3, bấm từng lesson, từng step, bài test cuối unit...),
# script chỉ lặng lẽ lưu audio/video/ảnh/JSON/XML và nội dung trang vào thư mục theo nhãn bạn gõ.

# Cài đặt:  pip install playwright   rồi   playwright install chromium
# Chạy:     .\\get_data_flow.ps1 [--I2 | --I3]
#           (hoặc trực tiếp: python ed_recorder_autologin.py [--I2 | --I3])

# Tham số:
#     --I2   sau khi đăng nhập, tự chuyển tới Intermediate 2
#     --I3   sau khi đăng nhập, tự chuyển tới Intermediate 3

# Trong cửa sổ terminal:
#     gõ một nhãn + Enter   -> bắt đầu thư mục mới, vd:  I2-U02-L01-Be Careful
#     Enter (để trống)      -> chụp nội dung trang hiện tại (HTML + text của mọi iframe), dùng sau mỗi step/tab
#     q + Enter             -> thoát
# Mọi file tải về sau khi bạn gõ nhãn sẽ nằm trong thư mục của nhãn đó.
# """
import asyncio, hashlib, json, re
from pathlib import Path
from types import SimpleNamespace
from playwright.async_api import async_playwright

from ed_config import load_settings  # .env + tham số dòng lệnh (khóa học, bài cần lấy, tài khoản)

OUT = Path("out/record")
PROFILE = Path("browser_profile")

HELP = """
Cách chạy:  .\\get_data_flow.ps1 [--course I2|I3] [--targets "U02-L01..L03"] [--manual]
Cấu hình nằm trong .env (xem .env.example): tài khoản, khai báo khóa học, khóa mặc định, bài cần lấy.
Chế độ thủ công (ED_TARGETS để trống hoặc --manual), trong cửa sổ terminal:
    gõ một nhãn + Enter   -> bắt đầu thư mục mới, vd:  I2-U02-L01-Be Careful
    Enter (để trống)      -> chụp nội dung trang hiện tại (HTML + text của mọi iframe)
    q + Enter             -> thoát
"""

SKIP_HOSTS = ("mixpanel", "mxpnl", "google", "gstatic", "doubleclick", "facebook", "clarity")
AUDIO_VIDEO = (".mp3", ".mp4", ".m4a", ".wav", ".ogg", ".webm")
IMAGES = (".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp")
MIN_IMG = 5 * 1024  # bỏ qua icon nhỏ


def slug(s, n=60):
    s = re.sub(r"[^\w\s.-]", "", s, flags=re.U).strip(" .")
    return re.sub(r"\s+", "_", s)[:n].strip(" .") or "untitled"


class State:
    dir = None
    label = ""
    seen = set()
    log = []
    reqs = []
    snaps = 0
    seq = 0
    index = {}


S = State()


def flush():
    if S.dir is None:
        return
    (S.dir / "network_log.json").write_text(json.dumps(S.log, ensure_ascii=False, indent=1), "utf-8")
    (S.dir / "requests_meta.json").write_text(json.dumps(S.reqs, ensure_ascii=False, indent=1), "utf-8")
    S.index[S.dir.name] = {"label": S.label, "files": len(S.log)}
    (OUT / "index.json").write_text(json.dumps(S.index, ensure_ascii=False, indent=1), "utf-8")


async def check_and_dismiss_already_logged_in(page):
    """Kiểm tra và click ngay nút chiếm phiên nếu popup #confirmModal đang hiển thị."""
    msg = page.get_by_text("You are already logged in").first
    modal = page.locator("#confirmModal, .layout__confirmModal, .confirmPopup__main").first
    btn = page.locator("#btnOk, button:has-text('Login on This Device'), [name='Login on This Device']").first

    try:
        is_msg = await msg.is_visible()
        is_modal = await modal.is_visible()
        is_btn = await btn.is_visible()
        if is_msg or is_modal or is_btn:
            print("Tài khoản đang đăng nhập ở thiết bị khác -> chiếm phiên trên máy này.")
            await page.wait_for_timeout(400)
            try:
                await btn.click(timeout=2000, force=True)
            except Exception:
                await page.evaluate("() => { const b = document.getElementById('btnOk') || document.querySelector('.layout__confirmModal #btnOk'); if (b) b.click(); }")
            await page.wait_for_timeout(1000)
            return True
    except Exception:
        pass
    return False


async def handle_post_conflict(page):
    """Chờ Angular xử lý đồng bộ phiên sau khi chiếm phiên."""
    try:
        await page.wait_for_url(lambda u: "login" not in u.lower(), timeout=15000)
    except Exception:
        pass
    await asyncio.sleep(2)
    try:
        await page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    print("Đã chiếm phiên và đăng nhập tự động thành công.")


async def auto_login(page, cfg):
    user, pwd = cfg.username, cfg.password
    if not user or not pwd:
        print("Không có ED_USERNAME/ED_PASS, hãy đăng nhập tay.")
        return

    # 1. Kiểm tra NGAY TỪ ĐẦU nếu popup 'You are already logged in...' (#confirmModal) đang hiển thị sẵn
    if await check_and_dismiss_already_logged_in(page):
        await handle_post_conflict(page)
        return

    try:
        # :visible để bỏ qua các ô password ẩn chống autofill của trang
        pw_input = page.locator("input[type=password]:visible").first
        await pw_input.wait_for(state="visible", timeout=10000)
    except Exception:
        # Nếu không thấy form login, có thể popup chiếm phiên vừa xuất hiện
        if await check_and_dismiss_already_logged_in(page):
            await handle_post_conflict(page)
            return
        print("Không thấy form đăng nhập (có thể đã đăng nhập sẵn).")
        return

    user_input = page.locator(
        "input[type=text]:visible, input[type=email]:visible, input:not([type]):visible").first
    await user_input.fill(user)
    await pw_input.fill(pwd)

    # 2. Trước khi bấm nút Login, kiểm tra lại nếu popup vừa xuất hiện đè lên form
    if await check_and_dismiss_already_logged_in(page):
        await handle_post_conflict(page)
        return

    # 3. Bấm nút Login an toàn (dùng force hoặc JS click nếu bị chặn pointer)
    try:
        await page.get_by_role("button", name="Login", exact=True).click(timeout=4000, force=True)
    except Exception:
        if await check_and_dismiss_already_logged_in(page):
            await handle_post_conflict(page)
            return
        try:
            await page.locator("#submit1, input[type=submit][value='Login']").first.evaluate("e => e.click()")
        except Exception:
            pass

    # 4. Nếu sau khi bấm Login mới hiện popup "You are already logged in..."
    conflict = await handle_already_logged_in(page)
    if conflict:
        await handle_post_conflict(page)
    else:
        await page.wait_for_load_state("networkidle")
        print("Đã đăng nhập tự động.")


async def handle_already_logged_in(page, timeout_ms=30000):
    """Chờ popup 'You are already logged in...' rồi bấm 'Login on This Device'.
    Dừng sớm nếu đã rời trang login (không có popup)."""
    waited = 0
    while waited < timeout_ms:
        if await check_and_dismiss_already_logged_in(page):
            return True
        if "login" not in page.url.lower():
            return False
        await page.wait_for_timeout(300)
        waited += 300
    print("Không thấy popup 'already logged in' sau thời gian chờ (có thể đăng nhập sai hoặc mạng chậm).")
    return False


async def goto_course(page, cfg):
    # chờ đăng nhập xong (URL không còn chứa "login") rồi mới chuyển khoá
    try:
        await page.wait_for_url(lambda u: "login" not in u.lower(), timeout=15000)
    except Exception:
        print("Cảnh báo: vẫn chưa thoát khỏi trang login, kiểm tra lại đăng nhập.")
    url = cfg.course_url()
    await asyncio.sleep(1)
    await page.goto(url)
    try:
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    print(f"Đã chuyển đến khoá {cfg.course}: {url}")


async def main():
    cfg = load_settings()
    print(cfg.describe())
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        ctx = await pw.chromium.launch_persistent_context(
            str(PROFILE), headless=False, viewport={"width": 1500, "height": 900})

        async def attach(page):
            # tắt cache để media phát lại vẫn đi qua mạng và được ghi lại
            try:
                cdp = await ctx.new_cdp_session(page)
                await cdp.send("Network.enable")
                await cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
            except Exception:
                pass

        ctx.on("page", lambda p: asyncio.create_task(attach(p)))
        for p in ctx.pages:
            await attach(p)

        async def on_response(resp):
            if S.dir is None or resp.status not in (200, 206):
                return
            url = resp.url
            if url in S.seen or any(h in url for h in SKIP_HOSTS):
                return
            path = url.split("?")[0].lower()
            ct = (resp.headers.get("content-type") or "").lower()
            if path.endswith(AUDIO_VIDEO) or ct.startswith(("audio/", "video/")):
                kind = "media"
            elif path.endswith((".m3u8", ".mpd")):
                kind = "stream"
            elif path.endswith(IMAGES) or ct.startswith("image/"):
                kind = "image"
            elif "json" in ct or "xml" in ct or path.endswith((".json", ".xml", ".vtt", ".srt")):
                kind = "data"
            elif path.endswith(".js") and "static.engdis.com" in url and any(
                    k in path for k in ("/runtime/lessons/", "/runtime/content/", "/localization/content/")):
                kind = "data"  # cấu trúc bài + văn bản bài đọc (EN) + bản dịch (VI)
            else:
                return
            S.seen.add(url)
            entry = {"url": url, "kind": kind, "status": resp.status, "type": ct, "file": None}
            try:
                if kind == "stream":
                    pass  # chỉ ghi URL; tải bằng: yt-dlp "<url>"
                else:
                    # media hay bị trả từng đoạn (206) -> tải lại nguyên file qua cùng phiên đăng nhập
                    body = await (await ctx.request.get(url)).body() if kind == "media" else await resp.body()
                    if kind == "image" and len(body) < MIN_IMG:
                        return
                    # đặt tên theo 3 đoạn cuối của đường dẫn (giữ đuôi file) để biết file thuộc API nào
                    parts = [x for x in path.split("/") if x][-3:]
                    name = slug("_".join(parts), 90)
                    if kind == "data" and "." not in parts[-1] and "json" in ct:
                        name += ".json"
                    fname = f"{hashlib.md5(url.encode()).hexdigest()[:6]}_{name}"
                    (S.dir / fname).write_bytes(body)
                    entry.update(file=fname, bytes=len(body))
            except Exception as e:
                entry["error"] = str(e)
            S.log.append(entry)
            print(f"   + {kind:6} {Path(path).name[:60]}")

        ctx.on("response", lambda r: asyncio.create_task(on_response(r)))

        def mask_query(url):
            # che giá trị query dài (có thể là token); chỉ giữ tên tham số
            if "?" not in url:
                return url
            base, q = url.split("?", 1)
            q = re.sub(r"=([^&]{17,})", "=<masked>", q)
            return base + "?" + q

        async def on_request(req):
            # ghi lại MỌI request API/script (chỉ TÊN header, KHÔNG ghi giá trị) để biết web xác thực thế nào
            if S.dir is None or req.resource_type in ("image", "stylesheet", "font", "media"):
                return
            if any(h in req.url for h in SKIP_HOSTS):
                return
            try:
                names = sorted((await req.all_headers()).keys())
            except Exception:
                names = sorted(req.headers.keys())
            S.reqs.append({"method": req.method, "type": req.resource_type,
                           "url": mask_query(req.url), "header_names": names})

        ctx.on("request", lambda r: asyncio.create_task(on_request(r)))

        async def snapshot():
            if S.dir is None:
                print("   (chưa có nhãn - hãy gõ nhãn trước)")
                return
            S.snaps += 1
            n = 0
            for pi, pg in enumerate(ctx.pages):
                for fi, fr in enumerate(pg.frames):
                    try:
                        txt = await fr.inner_text("body")
                        html = await fr.content()
                    except Exception:
                        continue
                    if not txt.strip():
                        continue
                    base = S.dir / f"snap{S.snaps:02d}_p{pi}_f{fi}"
                    base.with_suffix(".txt").write_text(f"URL: {fr.url}\n\n{txt}", "utf-8")
                    base.with_suffix(".html").write_text(html, "utf-8")
                    n += 1
            flush()
            print(f"   📸 snap{S.snaps:02d}: {n} khung")

        def start_label(label):
            """Mở thư mục mới cho một nhãn (dùng chung cho chế độ thủ công và tự động)."""
            S.seq += 1
            S.label = label
            S.dir = OUT / f"{S.seq:03d}_{slug(label)}"
            S.dir.mkdir(parents=True, exist_ok=True)
            S.seen, S.log, S.reqs, S.snaps = set(), [], [], 0
            print(f"   → thư mục: {S.dir}")
            return S.dir

        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(cfg.home_url)
        await auto_login(page, cfg)
        if cfg.course:
            await goto_course(page, cfg)

        if cfg.mode == "auto":  # móc nối sang ed_operation.py (module thao tác bài học - viết ở bước sau)
            try:
                from ed_operation import run_auto
            except ImportError:
                print("Chế độ tự động cần ed_operation.py (chưa có) -> chuyển sang chế độ thủ công.")
            else:
                rec = SimpleNamespace(start_label=start_label, snapshot=snapshot, flush=flush, state=S)
                await run_auto(ctx, page, cfg, rec)
                flush()
                await ctx.close()
                return

        print(HELP)
        print("Cứ thao tác bình thường. Nhớ gõ nhãn trước khi mở mỗi bài.\n")

        while True:
            cmd = (await asyncio.to_thread(input, "> ")).strip()
            if cmd.lower() in ("q", "quit", "exit"):
                break
            if cmd == "":
                await snapshot()
                continue
            if S.dir is not None:
                await snapshot()  # tự chụp nốt trạng thái cuối của nhãn trước
            start_label(cmd)

        if S.dir is not None:
            await snapshot()
        flush()
        await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())

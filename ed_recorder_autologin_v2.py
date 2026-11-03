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
import argparse
import asyncio, hashlib, json, os, re
from pathlib import Path
from playwright.async_api import async_playwright

START_URL = "https://ed22.engdis.com/ptithcm#/home"
OUT = Path("out/record")
PROFILE = Path("browser_profile")

COURSES = {
    "I2": "https://ed22.engdis.com/ptithcm#/MyProgress/Course/45178/Unit/",
    "I3": "https://ed22.engdis.com/ptithcm#/MyProgress/Course/45441/Unit/",
}

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


def parse_args():
    ap = argparse.ArgumentParser(description="Ghi lại dữ liệu bài học ed22.engdis.com")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--I2", action="store_true", help="tự chuyển tới Intermediate 2")
    g.add_argument("--I3", action="store_true", help="tự chuyển tới Intermediate 3")
    a = ap.parse_args()
    return "I2" if a.I2 else "I3" if a.I3 else None


async def auto_login(page):
    user = os.environ.get("ED_USERNAME")
    pwd = os.environ.get("ED_PASS")
    print(f"[env] ED_USERNAME={user!r}, ED_PASS có {len(pwd) if pwd else 0} ký tự")
    if not user or not pwd:
        print("Không có ED_USERNAME/ED_PASS, hãy đăng nhập tay.")
        return
    try:
        # :visible để bỏ qua các ô password ẩn chống autofill của trang
        pw_input = page.locator("input[type=password]:visible").first
        await pw_input.wait_for(state="visible", timeout=10000)
    except Exception:
        print("Không thấy form đăng nhập (có thể đã đăng nhập sẵn).")
        return
    user_input = page.locator(
        "input[type=text]:visible, input[type=email]:visible, input:not([type]):visible").first
    await user_input.fill(user)
    await pw_input.fill(pwd)
    await page.get_by_role("button", name="Login", exact=True).click()

    # Nếu tài khoản đang treo ở máy khác, web hiện popup "You are already logged in..."
    # -> bấm "Login on This Device" (#btnOk) để đăng nhập lại trên máy này.
    # Vòng lặp dừng ngay khi popup xuất hiện hoặc khi đã rời trang login.
    confirm = page.locator("#btnOk:visible")
    for _ in range(20):  # tối đa ~6 giây
        if await confirm.count() > 0:
            print("Tài khoản đang đăng nhập ở thiết bị khác -> chiếm phiên trên máy này.")
            await confirm.first.click()
            break
        if "login" not in page.url:
            break
        await page.wait_for_timeout(300)

    await page.wait_for_load_state("networkidle")
    print("Đã đăng nhập tự động.")


async def goto_course(page, key):
    # chờ đăng nhập xong (URL không còn chứa "login") rồi mới chuyển khoá
    try:
        await page.wait_for_url(lambda u: "login" not in u, timeout=15000)
    except Exception:
        print("Cảnh báo: vẫn chưa thoát khỏi trang login, kiểm tra lại đăng nhập.")
    await page.goto(COURSES[key])
    await page.wait_for_load_state("networkidle")
    print(f"Đã chuyển đến khoá {key}: {COURSES[key]}")


async def main():
    course = parse_args()
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

        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(START_URL)
        await auto_login(page)
        if course:
            await goto_course(page, course)
        print(__doc__)
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
            S.seq += 1
            S.label = cmd
            S.dir = OUT / f"{S.seq:03d}_{slug(cmd)}"
            S.dir.mkdir(parents=True, exist_ok=True)
            S.seen, S.log, S.reqs, S.snaps = set(), [], [], 0
            print(f"   → thư mục: {S.dir}")

        if S.dir is not None:
            await snapshot()
        flush()
        await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())

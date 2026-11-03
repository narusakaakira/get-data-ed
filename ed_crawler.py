"""
ed_crawler.py - tải lại nội dung khoá học của CHÍNH tài khoản bạn để ôn tập offline.

Cài đặt:
    pip install playwright
    playwright install chromium

Dùng:
    python ed_crawler.py discover          # bước 1: lưu HTML + ảnh chụp trang Progress để chỉnh selector
    python ed_crawler.py run               # bước 2: cào toàn bộ
    python ed_crawler.py run --unit 2      # chỉ cào Unit thứ 2 (theo thứ tự hiển thị trên web)
    python ed_crawler.py run --unit 2 --lesson 3

Thứ tự/đánh số: script KHÔNG tự đoán số thứ tự. Nó đọc đúng thứ tự hiển thị của từng
unit trên trang Progress (mỗi unit có danh sách lesson riêng), đặt tên thư mục theo
"vị trí + tiêu đề" lấy từ web, và ghi mapping vào out/manifest.json.
"""
import argparse, asyncio, hashlib, json, random, re
from pathlib import Path
from playwright.async_api import async_playwright

# ====================== CẤU HÌNH (sửa theo DevTools -> Inspect) ======================
PROGRESS_URL = "https://ed22.engdis.com/ptithcm#/MyProgress/Course/45178/Unit/"
OUT = Path("out")
PROFILE = Path("browser_profile")      # lưu phiên đăng nhập, chỉ cần đăng nhập 1 lần

# CSS selector - đây chỉ là GỢI Ý, hãy chỉnh sau khi chạy `discover`
SEL_UNIT_ROW   = ".home__unitW"        # mỗi hàng Unit (Unit 1, Unit 2, ...)
SEL_UNIT_TITLE = ".home__detailsTitle"         # tiêu đề trong hàng unit (nếu rỗng sẽ dùng text của hàng)
SEL_LESSON_ROW = "tr.lesson-row"       # mỗi hàng Lesson sau khi mở rộng unit
SEL_STEP_BTN   = ".step-btn"           # nút step 1/2/3 trong hàng lesson

DELAY = (2.0, 4.0)                     # nghỉ ngẫu nhiên giữa các thao tác (giây) - đừng chỉnh quá nhanh
MAX_BYTES = 300 * 1024 * 1024
MEDIA_EXT = (".mp3", ".mp4", ".m4a", ".wav", ".ogg", ".webm", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".vtt", ".srt")
DATA_EXT = (".json", ".xml", ".txt", ".js")  # .js thường là dữ liệu bài kiểu `var data = {...}`
# =====================================================================================


def slug(s: str, n: int = 50) -> str:
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U).strip()
    return re.sub(r"\s+", "_", s)[:n] or "untitled"


async def nap():
    await asyncio.sleep(random.uniform(*DELAY))


class Capture:
    """Gom mọi response media/dữ liệu phát sinh khi đang mở 1 step."""

    def __init__(self):
        self.dir: Path | None = None
        self.seen: set[str] = set()
        self.log: list[dict] = []

    def start(self, d: Path):
        d.mkdir(parents=True, exist_ok=True)
        self.dir, self.seen, self.log = d, set(), []

    async def on_response(self, resp):
        if self.dir is None or resp.status != 200:
            return
        url = resp.url
        path = url.split("?")[0].lower()
        ctype = (resp.headers.get("content-type") or "").lower()
        is_media = path.endswith(MEDIA_EXT) or ctype.startswith(("audio/", "video/", "image/"))
        is_data = path.endswith(DATA_EXT) or "json" in ctype or "xml" in ctype
        is_playlist = path.endswith(".m3u8") or path.endswith(".mpd")
        if not (is_media or is_data or is_playlist) or url in self.seen:
            return
        self.seen.add(url)
        name = Path(path).name or "file"
        fname = f"{hashlib.md5(url.encode()).hexdigest()[:6]}_{slug(name, 60)}"
        try:
            body = await resp.body()
            if len(body) > MAX_BYTES:
                raise ValueError("too large")
            (self.dir / fname).write_bytes(body)
            self.log.append({"url": url, "file": fname, "type": ctype, "bytes": len(body)})
        except Exception as e:  # stream / bị huỷ -> chỉ ghi URL, tải sau bằng yt-dlp
            self.log.append({"url": url, "file": None, "error": str(e)})


async def expand_unit(page, ui):
    await page.goto(PROGRESS_URL)
    await page.wait_for_selector(SEL_UNIT_ROW)
    await nap()
    row = page.locator(SEL_UNIT_ROW).nth(ui)
    await row.click()
    await page.wait_for_selector(SEL_LESSON_ROW + ":visible")
    await asyncio.sleep(1)


async def main(args):
    OUT.mkdir(exist_ok=True)
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8")) if manifest_path.exists() else {}

    async with async_playwright() as pw:
        ctx = await pw.chromium.launch_persistent_context(str(PROFILE), headless=False, viewport={"width": 1500, "height": 900})
        cap = Capture()
        ctx.on("response", lambda r: asyncio.create_task(cap.on_response(r)))
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(PROGRESS_URL)
        input(">> Đăng nhập (nếu cần) tới khi thấy trang My Progress, rồi nhấn Enter ở đây...")

        if args.cmd == "discover":
            await page.wait_for_timeout(2000)
            (OUT / "progress.html").write_text(await page.content(), "utf-8")
            await page.screenshot(path=str(OUT / "progress.png"), full_page=True)
            print("Đã lưu out/progress.html và out/progress.png. Mở bằng DevTools để tìm selector, rồi sửa mục CẤU HÌNH.")
            await ctx.close()
            return

        await page.wait_for_selector(SEL_UNIT_ROW)
        n_units = await page.locator(SEL_UNIT_ROW).count()
        print(f"Tìm thấy {n_units} unit")

        for ui in range(n_units):
            if args.unit and ui + 1 != args.unit:
                continue
            await expand_unit(page, ui)
            urow = page.locator(SEL_UNIT_ROW).nth(ui)
            utitle = (await (urow.locator(SEL_UNIT_TITLE).first.inner_text() if SEL_UNIT_TITLE else urow.inner_text())).strip()
            udir = OUT / f"U{ui+1:02d}_{slug(utitle)}"
            n_lessons = await page.locator(SEL_LESSON_ROW + ":visible").count()
            print(f"Unit {ui+1}: {utitle} ({n_lessons} lesson)")

            for li in range(n_lessons):
                if args.lesson and li + 1 != args.lesson:
                    continue
                await expand_unit(page, ui)
                lrow = page.locator(SEL_LESSON_ROW + ":visible").nth(li)
                ltitle = " ".join((await lrow.inner_text()).split())[:60]
                n_steps = await lrow.locator(SEL_STEP_BTN).count()  # mỗi lesson có thể có số step khác nhau

                for si in range(n_steps):
                    key = f"{ui+1}-{li+1}-{si+1}"
                    if manifest.get(key, {}).get("done"):
                        continue
                    await expand_unit(page, ui)
                    lrow = page.locator(SEL_LESSON_ROW + ":visible").nth(li)
                    sdir = udir / f"L{li+1:02d}_{slug(ltitle)}" / f"S{si+1}"
                    cap.start(sdir)
                    before = set(ctx.pages)
                    await lrow.locator(SEL_STEP_BTN).nth(si).click()
                    await page.wait_for_timeout(1500)
                    target = next(iter(set(ctx.pages) - before), page)  # step có thể mở tab mới
                    try:
                        await target.wait_for_load_state("networkidle", timeout=20000)
                    except Exception:
                        pass
                    await asyncio.sleep(6)  # chờ media/dữ liệu bài tải xong

                    # lưu text + HTML của trang và mọi iframe (nội dung bài thường nằm trong iframe)
                    for fi, fr in enumerate(target.frames):
                        try:
                            (sdir / f"frame{fi}.html").write_text(await fr.content(), "utf-8")
                            (sdir / f"frame{fi}.txt").write_text(await fr.inner_text("body"), "utf-8")
                        except Exception:
                            pass
                    (sdir / "network_log.json").write_text(json.dumps(cap.log, ensure_ascii=False, indent=1), "utf-8")
                    manifest[key] = {"unit": utitle, "lesson": ltitle, "step": si + 1, "dir": str(sdir), "files": len(cap.log), "done": True}
                    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")
                    print(f"  ✓ {key}  {ltitle}  step {si+1}  ({len(cap.log)} file)")
                    if target is not page:
                        await target.close()
                    await nap()
        await ctx.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["discover", "run"])
    ap.add_argument("--unit", type=int)
    ap.add_argument("--lesson", type=int)
    asyncio.run(main(ap.parse_args()))

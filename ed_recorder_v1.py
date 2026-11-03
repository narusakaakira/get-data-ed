"""
ed_recorder.py - chế độ "ghi hình": BẠN tự thao tác trên web như bình thường
(đổi Intermediate 2/3, bấm từng lesson, từng step, bài test cuối unit...),
script chỉ lặng lẽ lưu audio/video/ảnh/JSON/XML và nội dung trang vào thư mục theo nhãn bạn gõ.

Cài đặt:  pip install playwright   rồi   playwright install chromium
Chạy:     python ed_recorder.py

Trong cửa sổ terminal:
    gõ một nhãn + Enter   -> bắt đầu thư mục mới, vd:  I2-U02-L01-Be Careful
    Enter (để trống)      -> chụp nội dung trang hiện tại (HTML + text của mọi iframe), dùng sau mỗi step/tab
    q + Enter             -> thoát
Mọi file tải về sau khi bạn gõ nhãn sẽ nằm trong thư mục của nhãn đó.
"""
import asyncio, hashlib, json, re
from pathlib import Path
from playwright.async_api import async_playwright

START_URL = "https://ed22.engdis.com/ptithcm#/home"
OUT = Path("out/record")
PROFILE = Path("browser_profile")

SKIP_HOSTS = ("mixpanel", "mxpnl", "google", "gstatic", "doubleclick", "facebook", "clarity")
AUDIO_VIDEO = (".mp3", ".mp4", ".m4a", ".wav", ".ogg", ".webm")
IMAGES = (".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp")
MIN_IMG = 5 * 1024  # bỏ qua icon nhỏ


def slug(s, n=60):
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U).strip()
    return re.sub(r"\s+", "_", s)[:n] or "untitled"


class State:
    dir = None
    label = ""
    seen = set()
    log = []
    snaps = 0
    seq = 0
    index = {}


S = State()


def flush():
    if S.dir is None:
        return
    (S.dir / "network_log.json").write_text(json.dumps(S.log, ensure_ascii=False, indent=1), "utf-8")
    S.index[S.dir.name] = {"label": S.label, "files": len(S.log)}
    (OUT / "index.json").write_text(json.dumps(S.index, ensure_ascii=False, indent=1), "utf-8")


async def main():
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
                    name = Path(path).name or "file"
                    fname = f"{hashlib.md5(url.encode()).hexdigest()[:6]}_{slug(name, 70)}"
                    (S.dir / fname).write_bytes(body)
                    entry.update(file=fname, bytes=len(body))
            except Exception as e:
                entry["error"] = str(e)
            S.log.append(entry)
            print(f"   + {kind:6} {Path(path).name[:60]}")

        ctx.on("response", lambda r: asyncio.create_task(on_response(r)))

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
        print(__doc__)
        print("Đăng nhập nếu cần, rồi cứ thao tác bình thường. Nhớ gõ nhãn trước khi mở mỗi bài.\n")

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
            S.seen, S.log, S.snaps = set(), [], 0
            print(f"   → thư mục: {S.dir}")

        if S.dir is not None:
            await snapshot()
        flush()
        await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())

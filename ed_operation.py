# """
# ed_operation.py - chế độ TỰ ĐỘNG của ed_recorder: mở từng lesson theo ED_TARGETS, bấm Next đến hết bài,
# mỗi lesson ghi vào một thư mục nhãn (I3-U02-L01-Tên bài) rồi chuyển sang bài kế.

# Được gọi từ ed_recorder_autologin.py:  await run_auto(ctx, page, cfg, rec)
#     cfg = ed_config.Settings, rec = (start_label, snapshot, flush, state) do recorder cung cấp.

# Tham số/biến liên quan:
#     --dry-run              chỉ liệt kê các bài sẽ lấy (kèm nhãn), không mở bài nào
#     --redo                 làm lại cả các bài đã có meta.json status=ok (mặc định bỏ qua)
#     ED_MAX_CLICKS=250      số lần bấm Next tối đa cho 1 bài
#     ED_LESSON_TIMEOUT=1500 giây tối đa cho 1 bài
#     ED_STOP_AT_TEST=0      =1: dừng bài ngay khi tới bước Test

# Mỗi thư mục bài có thêm: meta.json (trạng thái, lý do dừng...) và walk_trace.json (từng lần bấm Next).
# """
import asyncio
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from ed_config import make_label, wanted

OUT = Path("out/record")

SEL_UNIT = ".myProgress__unitW"
SEL_UNIT_HEADER = ".myProgress__unitHeader"            # bấm để xổ/đóng danh sách lesson; có class --locked khi khóa
SEL_UNIT_NAME = ".myProgress__unitNameLabel"
SEL_LESSONS_OPEN = ".myProgress__unitLessons"           # chỉ tồn tại khi unit đang mở
# hàng "Unit Test" và "Unit Reflections" cũng mang class myProgress__unitLesson -> phải loại ra
SEL_LESSON = ".myProgress__unitLesson:not(.myProgress__unitTest):not(.myProgress__unitReflection)"
SEL_LESSON_NAME = ".myProgress__unitLesson_name"
SEL_STEP_BTN = ".myProgress__unitLesson_stepIW"        # cả 3 ô step đều gọi gotoLesson -> bấm ô đầu là đủ
NEXT_SEL = "#learning__nextItem a, a.learning__nextItemLink"

CODE = re.compile(r"^(.*?)([pt])(\d+)$")
LESSON_JS = re.compile(r"/Runtime/Lessons/([A-Za-z0-9_]+)\.js", re.I)
GETITEM = re.compile(r"GetItem/\d+/([A-Za-z0-9_]+)/(\d+)/", re.I)

STATE_JS = r"""() => {
  const vis = e => !!(e && (e.offsetWidth || e.offsetHeight || e.getClientRects().length));
  const leaf = [...document.querySelectorAll('body *')].filter(e => e.children.length === 0 && vis(e));
  const find = re => { const e = leaf.find(e => re.test((e.textContent || '').trim()));
                       return e ? e.textContent.trim().replace(/\s+/g, ' ') : null; };
  const tm = document.querySelector('ed-la-tasksmenu');
  const flags = {};
  if (tm) for (const a of tm.attributes) if (a.name.startsWith('ng-reflect-')) flags[a.name.slice(11)] = a.value.slice(0, 100);
  const bar = document.querySelector('.learning__practiceToolsOW');
  const nx = document.querySelector('#learning__nextItem a, a.learning__nextItemLink');
  return {
    lesson: find(/^Lesson \d+\s*:/), step: find(/^Step \d+\s*:/),
    bar: bar ? bar.innerText.trim().replace(/\s+/g, ' ').slice(0, 80) : null,
    next_visible: nx ? vis(nx) : false, flags,
    body_head: document.body.innerText.trim().replace(/\s+/g, ' ').slice(0, 140)
  };
}"""


@dataclass
class Job:
    ui: int          # chỉ số unit (0-based) trên trang
    li: int          # chỉ số lesson (0-based) trong unit
    u: int           # số unit hiển thị (1-based)
    l: int           # số lesson hiển thị (1-based)
    unit_name: str
    lesson_name: str


# ---------- tiện ích thuần ----------
def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def slug(s, n=60):
    s = re.sub(r"[^\w\s.-]", "", s, flags=re.U).strip(" .")
    return re.sub(r"\s+", "_", s)[:n].strip(" .") or "untitled"


def codes_in(reqs):
    """Mã bài (vd i3ltag) suy ra từ danh sách request đã ghi (dict có khóa 'url')."""
    out = []
    for e in reqs:
        u = e["url"] if isinstance(e, dict) else e
        m = LESSON_JS.search(u)
        if m:
            out.append(m.group(1))
            continue
        m = GETITEM.search(u)
        if m:
            cm = CODE.match(m.group(1))
            out.append(cm.group(1) if cm else m.group(1))
    return out


def purge_code(S, code):
    """Xóa khỏi log + đĩa các file thuộc bài kế (đã bị ghi lẫn sau lần bấm Next cuối)."""
    code, keep, removed = code.lower(), [], 0
    for e in S.log:
        if code in e["url"].lower():
            if e.get("file"):
                try:
                    (S.dir / e["file"]).unlink()
                except OSError:
                    pass
            removed += 1
        else:
            keep.append(e)
    S.log[:] = keep
    return removed


def already_done(label):
    for d in OUT.glob(f"*_{slug(label)}"):
        m = d / "meta.json"
        if m.exists():
            try:
                if json.loads(m.read_text("utf-8")).get("status") == "ok":
                    return d
            except Exception:
                pass
    return None


def fingerprint(st):
    return (st.get("lesson"), st.get("step"), st.get("bar"), st.get("body_head"))


# ---------- thao tác trên trang ----------
async def read_state(page):
    best = None
    for fr in page.frames:
        try:
            st = await fr.evaluate(STATE_JS)
        except Exception:
            continue
        if st.get("next_visible") or st.get("flags"):
            return st
        best = best or st
    return best or {}


async def open_progress(page, cfg):
    await page.goto(cfg.course_url())
    await page.wait_for_selector(SEL_UNIT, timeout=30000)
    await asyncio.sleep(1)


async def expand_unit(page, ui):
    row = page.locator(SEL_UNIT).nth(ui)
    if await row.locator(SEL_LESSONS_OPEN).count() == 0:  # chỉ bấm khi đang đóng (tránh bấm làm nó đóng lại)
        await row.locator(SEL_UNIT_HEADER).first.click()
    await row.locator(SEL_LESSON).first.wait_for(state="visible", timeout=15000)
    return row


async def build_jobs(page, cfg):
    await open_progress(page, cfg)
    n_units = await page.locator(SEL_UNIT).count()
    jobs, skipped = [], []
    for ui in range(n_units):
        u = ui + 1
        if not any(t.u1 <= u <= t.u2 and (t.course is None or t.course.upper() == cfg.course.upper())
                   for t in cfg.targets):
            continue
        row = page.locator(SEL_UNIT).nth(ui)
        uname = clean(await row.locator(SEL_UNIT_NAME).first.inner_text())
        locked = await row.locator(SEL_UNIT_HEADER).first.evaluate(
            "e => e.classList.contains('myProgress__unitHeader--locked')")
        if locked:
            skipped.append(f"U{u:02d} {uname} (unit bị khóa)")
            continue
        row = await expand_unit(page, ui)
        lessons = row.locator(SEL_LESSON)
        for li in range(await lessons.count()):
            l = li + 1
            if not wanted(cfg.targets, cfg.course, u, l):
                continue
            lr = lessons.nth(li)
            lname = clean(await lr.locator(SEL_LESSON_NAME).first.inner_text())
            lock = await lr.evaluate("e => e.classList.contains('myProgress__unitLesson--locked')"
                                     " || e.classList.contains('myProgress__unitLesson--parentLocked')")
            if lock:
                skipped.append(f"U{u:02d}-L{l:02d} {lname} (bài bị khóa)")
                continue
            for t in cfg.targets:  # đối chiếu tên người dùng gõ với tên thật trên web
                if t.name and t.matches(cfg.course, u, l) and slug(t.name).lower() != slug(lname).lower():
                    print(f"  [cảnh báo] U{u:02d}-L{l:02d}: bạn ghi '{t.name}' nhưng web hiển thị '{lname}'")
            jobs.append(Job(ui, li, u, l, uname, lname))
    return jobs, skipped


async def wait_player(lp):
    for _ in range(80):
        try:
            st = await read_state(lp)
            if st.get("lesson") or st.get("next_visible"):
                return st
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return {}


async def walk(lp, rec, cfg):
    """Bấm Next liên tục. Trả về (kind, lý do dừng, trace, thông tin phụ); kind = 'ok' (hết bài) hoặc 'partial'."""
    S = rec.state
    max_clicks = int(os.environ.get("ED_MAX_CLICKS", "250"))
    tmax = float(os.environ.get("ED_LESSON_TIMEOUT", "1500"))
    stop_test = os.environ.get("ED_STOP_AT_TEST", "0") == "1"
    t0 = time.time()

    await wait_player(lp)
    await asyncio.sleep(max(cfg.delay, 4))  # chờ video/nội dung bước đầu tải
    st = await read_state(lp)
    init_lesson = st.get("lesson")
    cur_code = next(iter(codes_in(S.reqs)), None)
    await rec.snapshot()
    trace = [{"n": 0, "lesson": init_lesson, "step": st.get("step"), "bar": st.get("bar"), "flags": st.get("flags")}]
    last, no_change, mark = fingerprint(st), 0, len(S.reqs)
    kind = "partial"
    reason, info = f"đạt giới hạn ED_MAX_CLICKS={max_clicks}", {"purged": 0, "next_code": None, "changed_lesson": False}

    for n in range(1, max_clicks + 1):
        if time.time() - t0 > tmax:
            reason = "quá thời gian ED_LESSON_TIMEOUT"
            break
        if stop_test and st.get("flags", {}).get("is-step-test") == "true":
            reason = "dừng ở bước Test (ED_STOP_AT_TEST=1)"
            break
        nx = lp.locator(NEXT_SEL).first
        try:
            if await nx.count() == 0 or not await nx.is_visible():
                reason = "không thấy nút Next (cuối bài hoặc màn hình nộp bài/kết quả)"
                kind = "partial" if st.get("flags", {}).get("is-step-test") == "true" else "ok"
                break
            await nx.click(timeout=4000)
        except Exception as e:
            reason = f"không bấm được Next: {str(e)[:120]}"
            break
        await asyncio.sleep(cfg.delay)
        try:
            await lp.wait_for_load_state("networkidle", timeout=6000)
        except Exception:
            pass
        if "learningarea" not in lp.url.lower():
            reason, kind = "đã thoát khỏi trình phát", "ok"
            break
        try:
            st = await read_state(lp)
        except Exception as e:
            reason = f"mất trang sau khi bấm: {str(e)[:100]}"
            break
        prev_mark = mark
        new, mark = S.reqs[prev_mark:], len(S.reqs)
        codes = codes_in(new)
        cur_code = cur_code or next(iter(codes), None)
        fp = fingerprint(st)
        changed = fp != last
        no_change = 0 if changed else no_change + 1
        step_changed = st.get("step") != trace[-1]["step"]
        trace.append({"n": n, "lesson": st.get("lesson"), "step": st.get("step"), "bar": st.get("bar"),
                      "flags": st.get("flags"), "codes": sorted(set(codes)), "changed": changed})
        print(f"     #{n:03d} {st.get('step')} | {st.get('bar')} | +{len(new)} req{'' if changed else '  (không đổi)'}")

        other = next((c for c in codes if cur_code and c != cur_code), None)
        label_changed = bool(init_lesson and st.get("lesson") and st["lesson"] != init_lesson)
        code_changed = bool(other) and not st.get("lesson")  # chỉ tin mã bài khi không đọc được nhãn
        if label_changed or code_changed:
            reason = (f"đổi lesson: '{init_lesson}' -> '{st.get('lesson')}'" if label_changed
                      else f"đổi lesson (mã bài): {cur_code} -> {other}")
            kind = "ok"
            await asyncio.sleep(3)  # chờ các request đầu tiên của bài kế để biết mã mà dọn
            nxt = next((c for c in codes_in(S.reqs[prev_mark:]) if cur_code and c != cur_code), other)
            if nxt:
                info["next_code"] = nxt
                info["purged"] = purge_code(S, nxt)
            info["changed_lesson"] = True
            break
        if no_change >= 3:
            reason = "Next không làm gì 3 lần liền (có thể đang chờ trả lời / nộp bài)"
            break
        if step_changed:
            await rec.snapshot()  # chụp chữ + HTML mỗi khi sang bước mới
        last = fp
    if not info["changed_lesson"]:
        await rec.snapshot()
    return kind, reason, trace, info


# ---------- điều phối ----------
async def run_auto(ctx, page, cfg, rec):
    dialogs = []

    def on_dialog(d):
        dialogs.append(d.message[:200])
        asyncio.create_task(d.accept() if d.type == "beforeunload" else d.dismiss())  # beforeunload: phải accept mới rời trang

    ctx.on("page", lambda p: p.on("dialog", on_dialog))
    for p in ctx.pages:
        p.on("dialog", on_dialog)

    S = rec.state
    S.dir = None  # tạm dừng ghi trong lúc duyệt danh sách
    print(f"\n== Tự động: khóa {cfg.course}, bài cần lấy: {len(cfg.targets)} mục ==")
    jobs, skipped = await build_jobs(page, cfg)
    for s in skipped:
        print(f"  bỏ qua: {s}")
    print(f"Sẽ lấy {len(jobs)} bài:")
    for j in jobs:
        print(f"  {make_label(cfg.course, j.u, j.l, j.lesson_name)}")
    if "--dry-run" in sys.argv:
        print("\n(--dry-run: dừng tại đây, chưa mở bài nào)")
        return
    if not jobs:
        print("Không có bài nào khớp ED_TARGETS.")
        return

    redo = "--redo" in sys.argv
    report = []
    for k, job in enumerate(jobs, 1):
        label = make_label(cfg.course, job.u, job.l, job.lesson_name)
        print(f"\n[{k}/{len(jobs)}] {label}")
        done = None if redo else already_done(label)
        if done:
            print(f"   đã có ({done.name}), bỏ qua (dùng --redo để làm lại)")
            report.append({"label": label, "status": "skipped"})
            continue
        lp, status, reason, trace, info = None, "error", "", [], {}
        started = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            S.dir = None
            await open_progress(page, cfg)
            row = await expand_unit(page, job.ui)  # mở sẵn để lúc bấm chỉ còn một thao tác
            rec.start_label(label)  # bắt đầu ghi ngay trước khi bấm vào bài
            btn = row.locator(SEL_LESSON).nth(job.li).locator(SEL_STEP_BTN).first
            try:
                await btn.click(timeout=5000)
            except Exception:
                await btn.evaluate("e => e.click()")
            lp = None
            for _ in range(80):
                lp = next((p for p in ctx.pages if "learningarea" in p.url.lower()), None)
                if lp:
                    break
                await asyncio.sleep(0.5)
            if lp is None:
                raise TimeoutError("không thấy trình phát bài học sau khi bấm vào lesson")
            status, reason, trace, info = await walk(lp, rec, cfg)
        except Exception as e:
            reason = f"lỗi: {type(e).__name__}: {str(e)[:200]}"
            print(f"   ✗ {reason}")
        finally:
            await asyncio.sleep(3)  # cho các tác vụ tải media đang dở kịp ghi
            if S.dir is not None:
                (S.dir / "walk_trace.json").write_text(json.dumps(trace, ensure_ascii=False, indent=1), "utf-8")
                (S.dir / "meta.json").write_text(json.dumps({
                    "label": label, "course": cfg.course, "unit": job.u, "lesson": job.l,
                    "unit_name": job.unit_name, "lesson_name": job.lesson_name, "status": status,
                    "stop_reason": reason, "clicks": max(0, len(trace) - 1), "started": started,
                    "finished": time.strftime("%Y-%m-%d %H:%M:%S"), "dialogs": dialogs[-5:], **info},
                    ensure_ascii=False, indent=1), "utf-8")
                rec.flush()
            S.dir = None
            if lp is not None and lp is not page:
                try:
                    await lp.close()
                except Exception:
                    pass
        print(f"   → {status}: {reason}")
        report.append({"label": label, "status": status, "reason": reason})
        await asyncio.sleep(cfg.delay)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "auto_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), "utf-8")
    n_ok = sum(1 for r in report if r["status"] == "ok")
    print(f"\n== Xong: {n_ok} ok, {sum(1 for r in report if r['status'] == 'partial')} một phần, "
          f"{sum(1 for r in report if r['status'] == 'error')} lỗi, "
          f"{sum(1 for r in report if r['status'] == 'skipped')} bỏ qua. Báo cáo: {OUT / 'auto_report.json'}")

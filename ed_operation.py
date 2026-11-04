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

# Nút điều hướng bài học
NEXT_SEL = "#learning_nextItem a, #learning__nextItem a, a.learning_nextItemLink, .learning_nextItem a, a.tasksBInext:not(.learning_submitTestLink)"
START_TEST_SEL = "a.btnStartTest, .btnStartTest, #testIntro a, a.layout__roundBtn.btnStartTest, a.layout_roundBtn.btnStartTest"
SUBMIT_TEST_SEL = "#learning_submitTestItem a, #learning__submitTestItem a, a.learning_submitTestLink, .learning_submitTestItem a"

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
  const nx = document.querySelector('#learning_nextItem a, #learning__nextItem a, a.learning_nextItemLink, .learning_nextItem a');
  const st = document.querySelector('a.btnStartTest, .btnStartTest, #testIntro a');
  const sm = document.querySelector('#learning_submitTestItem a, #learning__submitTestItem a, a.learning_submitTestLink, .learning_submitTestItem a');
  const counter = find(/^\d+\s*\/\s*\d+$/) || find(/\b\d+\s*\/\s*\d+\b/);
  const qEl = document.querySelector('.prMCQ__questionText, .prMCQ__questionW, .learning__taskQuestion, .learning__question');
  const qText = qEl ? qEl.innerText.trim().replace(/\s+/g, ' ').slice(0, 120) : null;
  return {
    lesson: find(/^Lesson \d+\s*:/), step: find(/^Step \d+\s*:/),
    bar: bar ? bar.innerText.trim().replace(/\s+/g, ' ').slice(0, 80) : null,
    counter: counter,
    question_text: qText,
    next_visible: nx ? vis(nx) : false,
    start_test_visible: st ? vis(st) : false,
    submit_visible: sm ? vis(sm) : false,
    flags,
    body_head: document.body.innerText.trim().replace(/\s+/g, ' ').slice(0, 200)
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
    return (st.get("lesson"), st.get("step"), st.get("bar"), st.get("counter"), st.get("question_text"))


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


async def open_progress(page, cfg, max_retries=3):
    url = cfg.course_url()
    for attempt in range(1, max_retries + 1):
        try:
            # Điều hướng đến URL khóa học nếu chưa ở đó hoặc cần tải lại
            if "myprogress" not in page.url.lower():
                await page.goto(url)
            else:
                await page.goto(url)

            # Chờ danh sách Unit xuất hiện (timeout 12s cho mỗi lần thử)
            await page.locator(SEL_UNIT).first.wait_for(state="visible", timeout=12000)
            await asyncio.sleep(1)
            return
        except Exception:
            curr_url = page.url
            print(f"  [Thử lại {attempt}/{max_retries}] Chưa thấy danh sách Unit (URL hiện tại: {curr_url}). Đang thử kết nối lại...")
            # Nếu phát hiện bị văng về login (do thiết bị khác vừa chiếm lại)
            if "login" in curr_url.lower():
                print("  Phát hiện bị đưa về trang đăng nhập, tiến hành chiếm lại phiên...")
                from ed_recorder_autologin_v3 import auto_login
                await auto_login(page, cfg)
            await asyncio.sleep(2)
            try:
                await page.goto(url)
                await page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass

    # Lần cuối cùng: chờ tối đa 30s với URL gốc
    await page.goto(url)
    await page.locator(SEL_UNIT).first.wait_for(state="visible", timeout=30000)
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
            if st.get("lesson") or st.get("next_visible") or st.get("start_test_visible") or st.get("submit_visible"):
                return st
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return {}


async def find_visible(page, selector):
    """Tìm phần tử hiển thị đầu tiên khớp selector trên page hoặc bất kỳ frame con nào."""
    for ctx in [page] + list(page.frames):
        try:
            loc = ctx.locator(selector).first
            if await loc.count() > 0 and await loc.is_visible():
                return loc
        except Exception:
            continue
    return None


async def handle_submit_confirmation(lp, timeout=6.0):
    """Xử lý hộp thoại double check sau khi bấm Submit (DOM modal / popup xác nhận nộp bài)."""
    t_end = time.time() + timeout
    confirm_selectors = [
        # Nút xác nhận trong modal Angular / Bootstrap
        ".modal.show button:has-text('Submit')",
        ".modal.show button:has-text('Yes')",
        ".modal.show button:has-text('OK')",
        ".modal.show button:has-text('Confirm')",
        "ngb-modal-window button:has-text('Submit')",
        "ngb-modal-window button:has-text('Yes')",
        "ngb-modal-window button:has-text('OK')",
        "ngb-modal-window button:has-text('Confirm')",
        ".modal-dialog button:has-text('Submit')",
        ".modal-dialog button:has-text('Yes')",
        ".modal-dialog button:has-text('OK')",
        "#BSModal button:has-text('OK')",
        "#BSModal .btn-primary",
        "button#btnOk",
        ".modal-footer .btn-primary",
        ".modal-footer button:not(.btn-secondary):not(.btn-cancel)",
        # Thử tìm trực tiếp theo text nút hiển thị
        "button:has-text('Submit'):visible",
        "button:has-text('Yes'):visible",
        "button:has-text('OK'):visible",
        "a.btnOk:visible",
        "a:has-text('OK'):visible",
        "a:has-text('Yes'):visible",
    ]
    while time.time() < t_end:
        for ctx in [lp] + list(lp.frames):
            for sel in confirm_selectors:
                try:
                    btn = ctx.locator(sel).first
                    if await btn.count() > 0 and await btn.is_visible():
                        print(f"     ✓ Đã tìm thấy nút xác nhận hộp thoại nộp bài ({sel}), đang click...")
                        try:
                            await btn.click(timeout=2000)
                        except Exception:
                            await btn.evaluate("e => e.click()")
                        return True
                except Exception:
                    pass
        await asyncio.sleep(0.3)
    return False


async def walk(lp, rec, cfg):
    """Bấm Next / Start Test / Submit liên tục. Trả về (kind, lý do dừng, trace, thông tin phụ); kind = 'ok' hoặc 'partial'."""
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
        flags = st.get("flags", {})
        if stop_test and flags.get("is-step-test") == "true":
            reason = "dừng ở bước Test (ED_STOP_AT_TEST=1)"
            break

        # Kiểm tra nếu đã ở màn hình kết quả bài Test (đã nộp xong)
        is_test_results = (flags.get("is-test-results") == "true" or
                           any(k in (st.get("body_head") or "").lower() for k in ("test score", "your total score", "test results")))
        if is_test_results:
            reason, kind = "đã ở màn hình kết quả bài Test", "ok"
            break

        # Tìm các nút điều hướng khả dụng: Start Test > Submit Test > Next
        btn_start = await find_visible(lp, START_TEST_SEL)
        btn_submit = await find_visible(lp, SUBMIT_TEST_SEL)
        btn_next = await find_visible(lp, NEXT_SEL)

        action_name = "next"
        target_btn = None
        if btn_start:
            action_name = "start_test"
            target_btn = btn_start
        elif btn_submit:
            action_name = "submit"
            target_btn = btn_submit
        elif btn_next:
            action_name = "next"
            target_btn = btn_next
        else:
            # Thử kiểm tra xem có modal xác nhận nào đang mở không
            if await handle_submit_confirmation(lp, timeout=1.0):
                await asyncio.sleep(cfg.delay)
                continue
            # Đợi một chút rồi thử lại một lần nữa phòng trường hợp web đang render/lag
            await asyncio.sleep(1.5)
            btn_start = await find_visible(lp, START_TEST_SEL)
            btn_submit = await find_visible(lp, SUBMIT_TEST_SEL)
            btn_next = await find_visible(lp, NEXT_SEL)
            if btn_start:
                action_name, target_btn = "start_test", btn_start
            elif btn_submit:
                action_name, target_btn = "submit", btn_submit
            elif btn_next:
                action_name, target_btn = "next", btn_next
            else:
                reason = "không thấy nút điều hướng (Next / Start Test / Submit)"
                kind = "partial" if flags.get("is-step-test") == "true" and flags.get("is-test-results") != "true" else "ok"
                break

        try:
            if action_name == "start_test":
                print(f"     #{n:03d} [Start Test] Bắt đầu bài kiểm tra...")
                await target_btn.click(timeout=4000)
            elif action_name == "submit":
                print(f"     #{n:03d} [Submit] Bấm nút Submit nộp bài Test...")
                await rec.snapshot()  # chụp lại câu hỏi cuối trước khi submit
                await target_btn.click(timeout=4000)

                # Chờ và xử lý hộp thoại double check xác nhận nộp bài
                print("     Đang chờ hộp thoại double check xác nhận nộp bài...")
                confirmed = await handle_submit_confirmation(lp, timeout=6.0)
                if confirmed:
                    print("     ✓ Đã xác nhận nộp bài trên hộp thoại double check.")
                else:
                    print("     (Không thấy DOM modal xác nhận hoặc đã được xử lý qua browser dialog).")

                # Chờ web ghi nhận kết quả và gửi dữ liệu mạng
                await asyncio.sleep(max(cfg.delay, 3))
                try:
                    await lp.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                await rec.snapshot()  # chụp màn hình kết quả sau khi nộp bài
                reason, kind = "đã hoàn thành bài Test và nộp bài thành công", "ok"
                break
            else:
                await target_btn.click(timeout=4000)
        except Exception as e:
            reason = f"không bấm được {action_name}: {str(e)[:120]}"
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
        has_new_reqs = len(new) > 0
        changed = (fp != last) or has_new_reqs
        no_change = 0 if (changed or action_name == "start_test") else no_change + 1
        step_changed = st.get("step") != trace[-1].get("step")
        in_test_step = st.get("flags", {}).get("is-step-test") == "true"
        trace.append({"n": n, "action": action_name, "lesson": st.get("lesson"), "step": st.get("step"), "bar": st.get("bar"),
                      "counter": st.get("counter"), "flags": st.get("flags"), "codes": sorted(set(codes)), "changed": changed})
        disp_info = st.get('counter') or st.get('bar') or ''
        print(f"     #{n:03d} [{action_name}] {st.get('step')} | {disp_info} | +{len(new)} req{'' if changed else '  (không đổi)'}")

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
        if step_changed or action_name == "start_test" or in_test_step:
            await rec.snapshot()  # chụp chữ + HTML mỗi khi sang bước mới hoặc mỗi câu trong bài test
        last = fp

    if not info["changed_lesson"] and kind != "ok":
        await rec.snapshot()
    return kind, reason, trace, info


# ---------- điều phối ----------
async def run_auto(ctx, page, cfg, rec):
    dialogs = []

    def on_dialog(d):
        dialogs.append(f"{d.type}: {d.message[:200]}")
        print(f"   [Dialog {d.type}] {d.message[:100]} -> tự động chấp nhận (accept)")
        asyncio.create_task(d.accept())

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

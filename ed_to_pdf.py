"""
ed_to_pdf.py - biến thư mục đã ghi bằng ed_recorder.py thành PDF (và .txt) để ôn tập.

Cài đặt:  pip install reportlab pillow
Chạy:
    python ed_to_pdf.py out/record/001_I3-U01-L01-Nick_and_Emily
    python ed_to_pdf.py out/record --all            # mọi thư mục con -> out/pdf/

Cách hiểu dữ liệu (mỗi thư mục = một nhãn bạn đã gõ):
  network_log.json  = danh sách file đã bắt được: URL gốc + tên file đã lưu (chìa khóa để ghép mọi thứ)
  GetItem/<id>/<mã>/<loại>/...  = 1 câu/bài tập. Mã dạng <mã-bài>p01 (Practice) hoặc <mã-bài>t01 (Test)
        -> file JSON: {"i": {"ii": đề bài, "q": [{"qt": câu hỏi, "al": [{"a": [{"txt":..., "c":"1"=đúng}]}]}]}}
  .../Content/..., .../Localization/Content/vie/...  = văn bản bài đọc (EN) và bản dịch (VI), nếu đã ghi
  ảnh trong GraphicsAng / Media = hình minh họa; .mp3/.mp4 = âm thanh/video (không nhúng được vào PDF,
        chỉ liệt kê tên file để bạn mở cạnh PDF)
Bài Test không có đáp án trong dữ liệu (web chấm ở server), nên PDF chỉ có câu hỏi.
"""
import argparse, html, json, re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer)

FONTS = [  # (thường, đậm) - cần font hỗ trợ tiếng Việt
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"),
    ("C:/Windows/Fonts/tahoma.ttf", "C:/Windows/Fonts/tahomabd.ttf"),
    ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]
GETITEM = re.compile(r"GetItem/(\d+)/([A-Za-z0-9_]+)/(\d+)/(\d+)/(\d+)")
CODE = re.compile(r"^(.*?)([pt])(\d+)$")
TAG = re.compile(r"<[^>]+>")
STR = re.compile(r'"((?:[^"\\\n]|\\.){25,})"|\'((?:[^\'\\\n]|\\.){25,})\'')


def setup_fonts():
    for reg, bold in FONTS:
        if Path(reg).exists() and Path(bold).exists():
            pdfmetrics.registerFont(TTFont("UF", reg))
            pdfmetrics.registerFont(TTFont("UF-B", bold))
            pdfmetrics.registerFontFamily("UF", normal="UF", bold="UF-B", italic="UF", boldItalic="UF-B")
            return
    raise SystemExit("Không tìm thấy font hỗ trợ tiếng Việt - sửa danh sách FONTS ở đầu file.")


def clean(s):
    return html.unescape(TAG.sub("", str(s))).replace("\xa0", " ").strip()


def esc(s):
    return html.escape(clean(s))


def strings_of(node, skip=(), path=""):
    """Gom mọi chuỗi chữ trong cấu trúc lạ (dự phòng khi chưa nhận diện được loại bài)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k not in skip:
                yield from strings_of(v, skip, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from strings_of(v, skip, f"{path}[{i}]")
    elif isinstance(node, str) and len(clean(node)) >= 2 and not clean(node).isdigit():
        yield path, clean(node)


def describe_item(data):
    """-> danh sách khối: ('instr',t) ('q',t) ('blank',t) ('opt',t,đúng|None) ('raw',t)"""
    root = data.get("i") if isinstance(data, dict) and isinstance(data.get("i"), dict) else data
    out = []
    if not isinstance(root, dict):
        return [("raw", json.dumps(data, ensure_ascii=False)[:1500])]
    if root.get("ii"):
        out.append(("instr", clean(root["ii"])))
    qs = root.get("q")
    if isinstance(qs, list) and qs:
        for qi, q in enumerate(qs, 1):
            if q.get("qt"):
                out.append(("q", f"{qi}. {clean(q['qt'])}"))
            als = q.get("al") or []
            for ai, al in enumerate(als, 1):
                if len(als) > 1:
                    out.append(("blank", f"Ô {ai}"))
                for o in al.get("a") or []:
                    txt = clean(o.get("txt", ""))
                    if txt:
                        out.append(("opt", txt, (str(o.get("c")) == "1") if "c" in o else None))
        skip = ("ii", "q", "ra", "type", "t", "id")
    else:
        skip = ("ii",)
        out.append(("raw", "[Loại bài chưa nhận diện - hiển thị toàn bộ chữ tìm thấy]"))
    for path, s in list(strings_of(root.get("d") if "d" in root else {k: v for k, v in root.items() if k not in skip}))[:60]:
        out.append(("raw", s))
    return out


def content_strings(text):
    seen, out = set(), []
    for m in STR.finditer(text):
        raw = m.group(1) or m.group(2)
        try:
            s = json.loads('"' + raw.replace('\\"', '"').replace('"', '\\"') + '"')
        except Exception:
            s = raw
        s = clean(s)
        if len(s) >= 25 and " " in s and s not in seen and not s.startswith(("http", "function", "var ")):
            seen.add(s)
            out.append(s)
    return out


def load_folder(folder):
    log = json.loads((folder / "network_log.json").read_text("utf-8"))
    items, images, media, texts = {}, [], [], []
    for e in log:
        f = e.get("file")
        url = e["url"]
        low = url.split("?")[0].lower()
        if not f or not (folder / f).exists():
            if e.get("kind") in ("stream",) or low.endswith((".mp4", ".mp3")):
                media.append((url.split("?")[0].rsplit("/", 1)[-1], "(chưa tải)"))
            continue
        m = GETITEM.search(url)
        if m:
            code = m.group(2)
            cm = CODE.match(code)
            if cm:
                lesson, kind, n = cm.group(1), cm.group(2), int(cm.group(3))
                try:
                    data = json.loads((folder / f).read_text("utf-8"))
                except Exception:
                    continue
                items.setdefault(lesson, []).append({"code": code, "kind": kind, "n": n, "data": data, "item_id": m.group(1)})
            continue
        if e.get("kind") == "media" or low.endswith((".mp3", ".mp4", ".m4a", ".wav")):
            media.append((f, url.split("?")[0]))
        elif e.get("kind") == "image" and low.endswith((".jpg", ".jpeg", ".png")) and re.search(r"/graphics|/media/", low):
            images.append((f, low.rsplit("/", 1)[-1]))
        elif low.endswith(".js") and re.search(r"/content/|/localization/content/", low):
            lang = "VI" if "/vie/" in low else "EN"
            texts.append((lang, low.rsplit("/", 1)[-1], content_strings((folder / f).read_text("utf-8", errors="ignore"))))
    return items, images, media, texts


def build(folder, out_pdf, out_txt):
    items, images, media, texts = load_folder(folder)
    title = re.sub(r"^\d+_", "", folder.name).replace("_", " ")
    S = {
        "title": ParagraphStyle("t", fontName="UF-B", fontSize=20, leading=25, spaceAfter=6),
        "h1": ParagraphStyle("h1", fontName="UF-B", fontSize=14, leading=18, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1a4f8b")),
        "h2": ParagraphStyle("h2", fontName="UF-B", fontSize=11, leading=15, spaceBefore=8, spaceAfter=3),
        "p": ParagraphStyle("p", fontName="UF", fontSize=10.5, leading=15),
        "instr": ParagraphStyle("i", fontName="UF", fontSize=9.5, leading=13, textColor=colors.HexColor("#555555"), spaceAfter=3),
        "q": ParagraphStyle("q", fontName="UF-B", fontSize=10.5, leading=15, spaceBefore=4),
        "opt": ParagraphStyle("o", fontName="UF", fontSize=10.5, leading=14, leftIndent=14),
        "ok": ParagraphStyle("ok", fontName="UF-B", fontSize=10.5, leading=14, leftIndent=14, textColor=colors.HexColor("#1b7a34")),
        "small": ParagraphStyle("s", fontName="UF", fontSize=8.5, leading=11, textColor=colors.grey),
    }
    flow, txt = [Paragraph(esc(title), S["title"]),
                 Paragraph("Tài liệu tự tạo để ôn tập cá nhân từ dữ liệu bài học đã ghi.", S["small"])], [title, ""]
    used_images = set()

    for lesson in sorted(items):
        flow.append(Paragraph(f"Lesson {esc(lesson)}", S["h1"]))
        txt += [f"== Lesson {lesson} ==", ""]
        for kind, label, note in (("p", "Practice", "✓ = đáp án đúng theo dữ liệu của web"),
                                  ("t", "Test", "Bài Test: dữ liệu không kèm đáp án (web chấm ở server)")):
            group = sorted((i for i in items[lesson] if i["kind"] == kind), key=lambda i: i["n"])
            if not group:
                continue
            flow += [Paragraph(label, S["h1"]), Paragraph(esc(note), S["small"])]
            txt += [f"-- {label} ({note}) --"]
            for it in group:
                block = [Paragraph(f"{esc(it['code'])}", S["h2"])]
                txt.append(f"[{it['code']}]")
                for b in describe_item(it["data"]):
                    if b[0] == "instr":
                        block.append(Paragraph(esc(b[1]), S["instr"])); txt.append(f"  ({b[1]})")
                    elif b[0] == "q":
                        block.append(Paragraph(esc(b[1]), S["q"])); txt.append(f"  {b[1]}")
                    elif b[0] == "blank":
                        block.append(Paragraph(esc(b[1]), S["small"])); txt.append(f"  {b[1]}")
                    elif b[0] == "opt":
                        mark = "✓ " if b[2] else "• "
                        block.append(Paragraph(mark + esc(b[1]), S["ok" if b[2] else "opt"]))
                        txt.append(f"    {'[x]' if b[2] else '[ ]'} {b[1]}")
                    else:
                        block.append(Paragraph(esc(b[1]), S["p"])); txt.append(f"  {b[1]}")
                for fname, orig in images:  # ảnh có tên bắt đầu bằng mã item -> đặt ngay dưới item
                    if orig.startswith(it["code"].lower()) and fname not in used_images:
                        used_images.add(fname)
                        try:
                            w, h = ImageReader(str(folder / fname)).getSize()
                            width = min(110 * mm, w * 0.75)
                            block += [Spacer(1, 3), Image(str(folder / fname), width=width, height=width * h / w)]
                        except Exception:
                            pass
                flow.append(KeepTogether(block))
                txt.append("")

    for lang, name, strs in texts:
        if not strs:
            continue
        head = "Nội dung bài (EN)" if lang == "EN" else "Bản dịch tiếng Việt"
        flow += [PageBreak(), Paragraph(f"{head} - {esc(name)}", S["h1"]),
                 Paragraph("Trích tự động từ file nội dung gốc; định dạng thô.", S["small"])]
        txt += ["", f"== {head} ({name}) =="]
        for s in strs:
            flow += [Paragraph(esc(s), S["p"]), Spacer(1, 4)]
            txt.append(s)

    rest = [i for i in images if i[0] not in used_images]
    if rest:
        flow += [PageBreak(), Paragraph("Hình ảnh khác trong bài", S["h1"])]
        for fname, orig in rest[:30]:
            try:
                w, h = ImageReader(str(folder / fname)).getSize()
                width = min(100 * mm, w * 0.75)
                flow += [Paragraph(esc(orig), S["small"]), Image(str(folder / fname), width=width, height=width * h / w), Spacer(1, 6)]
            except Exception:
                pass
    if media:
        flow += [Paragraph("Tệp âm thanh / video (mở cạnh PDF)", S["h1"])]
        txt += ["", "== Media =="]
        for f, orig in media:
            flow.append(Paragraph(f"{esc(f)}", S["p"])); txt.append(f)

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(out_pdf), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                      topMargin=16 * mm, bottomMargin=16 * mm, title=title).build(flow)
    out_txt.write_text("\n".join(txt), "utf-8")
    n = sum(len(v) for v in items.values())
    print(f"✓ {out_pdf}  ({n} item, {len(images)} ảnh, {len(media)} media, {sum(1 for t in texts if t[2])} file nội dung)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--all", action="store_true", help="path là out/record, xử lý mọi thư mục con")
    ap.add_argument("--out", default="out/pdf")
    a = ap.parse_args()
    setup_fonts()
    root = Path(a.path)
    folders = sorted(p for p in root.iterdir() if (p / "network_log.json").exists()) if a.all else [root]
    for f in folders:
        build(f, Path(a.out) / f"{f.name}.pdf", Path(a.out) / f"{f.name}.txt")


if __name__ == "__main__":
    main()

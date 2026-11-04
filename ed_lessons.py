# """
# ed_lessons.py - từ các thư mục đã ghi bằng ed_recorder.py, tạo hàng loạt bộ "1 file txt + 1 video" cho từng lesson.

# Chạy:
#     python ed_lessons.py out/record                 # mọi thư mục nhãn -> out/lessons/
#     python ed_lessons.py out/record/001_I3-U02-L01-College_Sports   # chỉ 1 thư mục
#     python ed_lessons.py out/record --move          # chuyển (thay vì sao chép) file video
#     python ed_lessons.py out/record --sentences     # mỗi câu một dòng thay vì mỗi lượt nói một dòng

# Kết quả: out/lessons/<nhãn>.txt và out/lessons/<nhãn>.mp4 (cùng tên -> mở cạnh nhau), kèm index.csv.
# Thêm bài mới: ghi bài bằng recorder rồi chạy lại lệnh trên. Bài đã có trong out/lessons được BỎ QUA (nhanh,
# không chép lại video); index.csv được gộp, không mất dòng cũ. Muốn làm lại một bài (vd ghi lại bằng recorder
# mới hơn) thì thêm --force.

# Nhận diện người nói:
#   - Tìm các nhãn dạng "Tên Nhân Vật:" (1-4 từ viết hoa + dấu hai chấm) trong văn bản EN, bất kể tên gì
#     (Carl Langford, Tina, Man, Woman, Dr. Smith...). Nhãn chỉ được tính là người nói khi xuất hiện đủ nhiều
#     (>= 2 tên khác nhau và >= 3 lần, hoặc 1 tên >= 4 lần); các nhãn như Note:, Example:, From:, Subject: bị loại.
#   - Bản dịch VI không có tên người nói, nên được ghép theo thứ tự câu với bản EN
#     (ưu tiên 1 dòng VI = 1 lượt nói nếu số dòng khớp; nếu không thì căn câu theo độ dài).
# """
import argparse, csv, html, json, math, re, shutil
from pathlib import Path

GETITEM = re.compile(r"GetItem/(\d+)/([A-Za-z0-9_]+)/(\d+)/(\d+)/(\d+)")
CODE = re.compile(r"^(.*?)([pt])(\d+)$")
TAG = re.compile(r"<[^>]+>")
BLOCK = re.compile(r"(?i)<\s*br\s*/?\s*>|</?\s*(?:p|div|li|tr|h\d)\b[^>]*>")
STR = re.compile(r'"((?:[^"\\\n]|\\.){25,})"|\'((?:[^\'\\\n]|\\.){25,})\'')
HON = r"(?:Dr|Mr|Mrs|Ms|Prof)\."
NAME_TOK = rf"(?:{HON}|[A-Z][A-Za-z'’\-]*)"
LABEL = re.compile(rf"(?<![A-Za-z0-9])({NAME_TOK}(?:[ \t]{NAME_TOK}){{0,3}})[ \t]*:[ \t\n]+")
NOT_SPEAKER = {"note", "notes", "example", "examples", "answer", "answers", "tip", "tips", "title", "subject",
               "date", "from", "to", "cc", "re", "sent", "hint", "task", "part", "step", "question", "sample",
               "dear", "ps", "p.s", "warning", "ad", "price", "time", "address", "phone", "email", "e-mail"}
ABBR = {"mr", "mrs", "ms", "dr", "prof", "st", "jr", "sr", "vs", "etc", "no"}


# ---------- văn bản ----------
def clean_text(s):
    s = BLOCK.sub("\n", str(s))
    s = html.unescape(TAG.sub("", s)).replace("\xa0", " ")
    s = re.sub(r"\\(['\"/\\])", r"\1", s)
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def js_strings(raw):
    """Lấy các chuỗi dài trong file .js/.json (giải mã \\uXXXX, \\" ...)."""
    out = []
    for m in STR.finditer(raw):
        body, single = (m.group(1), False) if m.group(1) else (m.group(2), True)
        try:
            body2 = body.replace("\\'", "'")
            if single:
                body2 = re.sub(r'(?<!\\)"', '\\"', body2)
            val = json.loads('"' + body2 + '"')
        except Exception:
            val = body
        val = clean_text(val)
        if len(val) >= 25 and " " in val and not val.startswith(("http", "function", "var ")):
            out.append(val)
    return out


def main_text(path):
    strs = js_strings(Path(path).read_text("utf-8", errors="ignore"))
    return max(strs, key=len) if strs else ""


def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    cuts = set()
    for m in re.finditer(r"[.!?…]+[\"”’')\]]*", text):
        e = m.end()
        if e >= len(text):
            continue
        w = re.search(r"([A-Za-zÀ-ỹ]+)$", text[:m.start()])
        w = w.group(1) if w else ""
        nxt = text[e]
        if nxt == " ":
            c = text[e + 1:e + 2]
            if c and (c.isupper() or c in "\"“‘'(" or c.isdigit()) and not (m.group().startswith(".") and w.lower() in ABBR):
                cuts.add(e)
        elif nxt.isupper() and len(w) >= 2:
            cuts.add(e)
    for m in re.finditer(r"[\"”]", text):  # nháy đóng dính liền chữ hoa: …đường"Khách mời…
        i = m.start()
        if 0 < i < len(text) - 1 and text[i - 1] not in " \"“‘'" and text[i + 1].isupper():
            cuts.add(i + 1)
    pos, out = 0, []
    for c in sorted(cuts):
        out.append(text[pos:c].strip())
        pos = c
    out.append(text[pos:].strip())
    return [s for s in out if s]


# ---------- người nói ----------
def find_speakers(text):
    """-> list[(speaker|None, utterance)] nếu là hội thoại, ngược lại None."""
    found = [m for m in LABEL.finditer(text) if m.group(1).strip().lower().rstrip(".") not in NOT_SPEAKER]
    names = [m.group(1).strip() for m in found]
    distinct = set(names)
    ok = (len(distinct) >= 2 and len(names) >= 3) or any(names.count(n) >= 4 for n in distinct)
    if not ok:
        return None
    utts = []
    head = text[:found[0].start()].strip()
    if head:
        utts.append((None, re.sub(r"\s+", " ", head)))
    for i, m in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(text)
        body = re.sub(r"\s+", " ", text[m.end():end]).strip()
        if body:
            utts.append((m.group(1).strip(), body))
    return utts


# ---------- căn câu EN <-> VI ----------
def align(en, vi):
    """Căn câu kiểu Gale-Church đơn giản. Trả về list[(list_idx_en, list_idx_vi)]."""
    n, m = len(en), len(vi)
    le, lv = [len(s) for s in en], [len(s) for s in vi]
    R = (sum(lv) + 1) / (sum(le) + 1)
    pre_e, pre_v = [0], [0]
    for x in le: pre_e.append(pre_e[-1] + x)
    for x in lv: pre_v.append(pre_v[-1] + x)
    beads = {(1, 1): 0.0, (1, 2): 0.7, (2, 1): 0.7, (2, 2): 1.2, (1, 0): 2.5, (0, 1): 2.5, (1, 3): 1.5, (3, 1): 1.5}
    INF = float("inf")
    D = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if D[i][j] == INF:
                continue
            for (a, b), pen in beads.items():
                ni, nj = i + a, j + b
                if ni > n or nj > m:
                    continue
                ea, vb = pre_e[ni] - pre_e[i], pre_v[nj] - pre_v[j]
                c = pen + abs(math.log((vb + 1) / (ea * R + 1)))
                if D[i][j] + c < D[ni][nj]:
                    D[ni][nj], back[ni][nj] = D[i][j] + c, (i, j)
    out, i, j = [], n, m
    while (i, j) != (0, 0):
        pi, pj = back[i][j]
        out.append((list(range(pi, i)), list(range(pj, j))))
        i, j = pi, pj
    return out[::-1]


def bilingual(en_text, vi_text, per_sentence=False):
    lines = []
    utts = find_speakers(en_text) if en_text else None
    if en_text and vi_text:
        vi_lines = [re.sub(r"\s+", " ", l).strip() for l in vi_text.split("\n") if l.strip()]
        if utts and len(vi_lines) == len(utts):  # 1 dòng VI = 1 lượt nói
            for (sp, en), vi in zip(utts, vi_lines):
                lines += [f"{sp}:" if sp else "(dẫn)", f"  EN: {en}", f"  VI: {vi}", ""]
            return lines, "khớp theo lượt nói"
    if utts:
        sent, spk = [], []
        for sp, u in utts:
            ss = split_sentences(u)
            sent += ss
            spk += [sp] * len(ss)
    else:
        sent = split_sentences(en_text) if en_text else []
        spk = [None] * len(sent)
    vis = split_sentences(vi_text) if vi_text else []
    if not sent:
        return [f"  VI: {s}" for s in vis], "chỉ có bản dịch"
    if not vis:
        if utts:
            for sp, u in utts:
                lines += [f"{sp}:" if sp else "(dẫn)", f"  EN: {u}", ""]
        else:
            lines += [f"  EN: {s}" for s in sent]
        return lines, "chỉ có tiếng Anh"
    beads = align(sent, vis)
    note = "căn câu tự động" + ("" if len(sent) != len(vis) else " (số câu khớp)")
    turns, cur = [], None  # mỗi lượt: [speaker, [en câu], [vi câu]]
    last_sp = spk[0]
    for ei, vj in beads:
        sp = spk[ei[0]] if ei else last_sp
        last_sp = sp
        en_s = [sent[k] for k in ei]
        vi_s = [vis[k] for k in vj]
        if per_sentence or cur is None or cur[0] != sp or not utts:
            if per_sentence and utts:
                pass
            cur = [sp, [], []]
            turns.append(cur)
        cur[1] += en_s
        cur[2] += vi_s
    prev = object()
    for sp, en_s, vi_s in turns:
        if utts and sp != prev:
            lines.append(f"{sp}:" if sp else "(dẫn)")
        prev = sp
        pad = "  " if utts else ""
        if en_s: lines.append(f"{pad}EN: {' '.join(en_s)}")
        if vi_s: lines.append(f"{pad}VI: {' '.join(vi_s)}")
        if not (per_sentence and utts) or True:
            lines.append("")
    return lines, note


# ---------- câu hỏi ----------
def describe_item(data):
    root = data.get("i") if isinstance(data, dict) and isinstance(data.get("i"), dict) else data
    out = []
    if not isinstance(root, dict):
        return [("raw", json.dumps(data, ensure_ascii=False)[:1500])]
    if root.get("ii"):
        out.append(("instr", clean_text(root["ii"])))
    qs = root.get("q")
    if isinstance(qs, list) and qs:
        for qi, q in enumerate(qs, 1):
            if q.get("qt"):
                out.append(("q", f"{qi}. {clean_text(q['qt'])}"))
            als = q.get("al") or []
            for ai, al in enumerate(als, 1):
                if len(als) > 1:
                    out.append(("blank", f"Ô {ai}"))
                for o in al.get("a") or []:
                    t = clean_text(o.get("txt", ""))
                    if t:
                        out.append(("opt", t, (str(o.get("c")) == "1") if "c" in o else None))
    else:
        out.append(("raw", json.dumps(root, ensure_ascii=False)[:1500]))
    return out


def has_key(data):
    return any(b[0] == "opt" and b[2] for b in describe_item(data))


# ---------- đọc thư mục ----------
def load(folder):
    log = json.loads((folder / "network_log.json").read_text("utf-8"))
    items, media, en, vi = {}, [], [], []
    for e in log:
        f, url = e.get("file"), e["url"]
        low = url.split("?")[0].lower()
        if not f or not (folder / f).exists():
            continue
        m = GETITEM.search(url)
        if m:
            cm = CODE.match(m.group(2))
            if cm:
                try:
                    data = json.loads((folder / f).read_text("utf-8"))
                except Exception:
                    continue
                items.setdefault(cm.group(1), {}).setdefault(m.group(2), []).append(data)
            continue
        if low.endswith((".mp4", ".webm", ".mp3", ".m4a")):
            media.append((folder / f, low))
        elif low.endswith(".js") and "/localization/content/" in low and "/vie/" in low:
            vi.append((low, folder / f))
        elif low.endswith(".js") and "/runtime/content/" in low:
            en.append((low, folder / f))
    return items, media, en, vi


def pick(files, code):
    for low, p in files:
        if code and code in low:
            return p
    return files[0][1] if files else None


def pick_video(media, code):
    vids = [m for m in media if m[1].endswith((".mp4", ".webm"))]
    pool = vids or media
    if not pool:
        return None
    pref = [m for m in pool if code and code in m[1]]
    return max(pref or pool, key=lambda m: m[0].stat().st_size)[0]


def build(folder, outdir, move, per_sentence, used, force=False):
    base = re.sub(r"^\d+_", "", folder.name)
    if not force and base not in used and (outdir / f"{base}.txt").exists():
        print(f"- {base}: đã có trong {outdir.name}, bỏ qua (dùng --force để làm lại)")
        return None
    items, media, en, vi = load(folder)
    k, name = 2, base
    while name in used:
        name, k = f"{base}_{k}", k + 1
    used.add(name)
    codes = sorted(items) or [""]
    code = codes[0]
    en_p, vi_p = pick(en, code), pick(vi, code)
    en_t, vi_t = (main_text(en_p) if en_p else ""), (main_text(vi_p) if vi_p else "")
    video = pick_video(media, code)

    txt = [base.replace("_", " "), f"Mã bài: {', '.join(c for c in codes if c) or '?'}"]
    vname = None
    if video:
        vname = f"{name}{video.suffix}"
        dst = outdir / vname
        (shutil.move if move else shutil.copy2)(str(video), str(dst))
        txt.append(f"Video kèm theo: {vname}")
    else:
        txt.append("Video kèm theo: (không có - bài này chưa ghi được video)")
    txt.append("")

    note = "-"
    if en_t or vi_t:
        lines, note = bilingual(en_t, vi_t, per_sentence)
        txt += ["==== NỘI DUNG BÀI (EN | VI) ====", f"({note})", ""] + lines
    for lesson in codes:
        for kind, label in (("p", "PRACTICE"), ("t", "TEST")):
            group = sorted(((int(CODE.match(c).group(3)), c) for c in items.get(lesson, {}) if CODE.match(c) and CODE.match(c).group(2) == kind))
            if not group:
                continue
            txt += [f"==== {label} ====", ""]
            for _, c in group:
                versions = items[lesson][c]
                data = next((d for d in versions if has_key(d)), versions[-1])  # ưu tiên bản có đáp án
                txt.append(f"[{c}]")
                for b in describe_item(data):
                    if b[0] == "instr": txt.append(f"  ({b[1]})")
                    elif b[0] == "q": txt.append(f"  {b[1]}")
                    elif b[0] == "blank": txt.append(f"  {b[1]}")
                    elif b[0] == "opt": txt.append(f"    {'[x]' if b[2] else '[ ]'} {b[1]}")
                    else: txt.append(f"  {b[1]}")
                txt.append("")
    (outdir / f"{name}.txt").write_text("\n".join(txt), "utf-8")
    n_items = sum(len(v) for d in items.values() for v in d.values())
    print(f"✓ {name}.txt  | video: {vname or 'không'} | {n_items} câu | nội dung: {note}")
    return [name, code, vname or "", n_items, bool(en_t), bool(vi_t), note]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", default="out/lessons")
    ap.add_argument("--move", action="store_true")
    ap.add_argument("--sentences", action="store_true", help="mỗi câu một dòng")
    ap.add_argument("--force", action="store_true", help="làm lại cả những bài đã có trong thư mục đích")
    a = ap.parse_args()
    root, outdir = Path(a.path), Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    folders = [root] if (root / "network_log.json").exists() else sorted(p for p in root.iterdir() if (p / "network_log.json").exists())
    rows, used = [], set()
    for f in folders:
        try:
            r = build(f, outdir, a.move, a.sentences, used, a.force)
            if r:
                rows.append(r)
        except Exception as e:
            print(f"✗ {f.name}: {e}")
    idx = outdir / "index.csv"
    merged = {}
    if idx.exists():  # giữ các dòng cũ, chỉ cập nhật/thêm dòng của lần chạy này
        with open(idx, newline="", encoding="utf-8-sig") as fh:
            for r in list(csv.reader(fh))[1:]:
                if r:
                    merged[r[0]] = r
    for r in rows:
        merged[r[0]] = [str(x) for x in r]
    with open(idx, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["ten", "ma_bai", "video", "so_cau", "co_EN", "co_VI", "ghi_chu"])
        w.writerows(merged[k] for k in sorted(merged))
    print(f"Xong: {len(rows)} bài mới/làm lại, tổng {len(merged)} bài trong {outdir}")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
compile_materials.py - Chương trình tự động biên soạn tài liệu học tiếng Anh chuẩn mực
từ 82 file bài học English Discoveries (Intermediate 2 & 3).
"""

import os
import glob
import re
import csv
import sys
from datetime import datetime
from lexicon_data import UNIT_TOPICS, LEXICON_DB

# Cấu hình đường dẫn
SRC_DIR = r"C:\my_projects\get_data_ed\out\lessons"
DEST_DIRS = [
    r"C:\my_projects\get_data_ed\out\tong hop",
    r"C:\my_projects\get_data_ed\out\tong_hop"
]

for d in DEST_DIRS:
    os.makedirs(d, exist_ok=True)

# Đọc metadata từ index.csv nếu có
INDEX_METADATA = {}
index_file = os.path.join(SRC_DIR, "index.csv")
if os.path.exists(index_file):
    with open(index_file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            INDEX_METADATA[row["ten"]] = row


def clean_line(s):
    return re.sub(r"\s+", " ", s).strip()


def clean_dictation(s):
    s = clean_line(s)
    # Loại bỏ số thứ tự câu sót lại ở cuối chuỗi sau dấu kết câu
    s = re.sub(r"(?<=[.!?])\s+\d+\.?\s*$", "", s).strip()
    return s


def find_sentence_in_content(word, content):
    w_clean = word.lower().strip()
    if w_clean == "mange by yourself":
        w_clean = "manage by yourself"
        
    stems = [w_clean, w_clean + "s", w_clean + "es"]
    
    if "hair done" in w_clean:
        stems.extend(["hair done", "had her hair done", "have her hair done", "had my hair done"])
    elif "conversation" in w_clean:
        stems.extend(["conversation", "conversations", "hold conversations", "holding conversations", "held a conversation"])
    elif "divorce" in w_clean:
        stems.extend(["divorced", "divorce", "getting divorced", "got divorced"])
    elif "spend" in w_clean or "spending" in w_clean:
        stems.extend(["spend", "spends", "spent", "spending", "spending time", "spends a lot of time"])
    elif "name for" in w_clean:
        stems.extend(["name for", "name for herself", "name for himself", "name for yourself", "made a name"])
    elif "upset" in w_clean:
        stems.extend(["upset", "handling the upset", "handled an upset", "handle an upset"])
    elif "cut" in w_clean:
        stems.extend(["cut", "cuts", "making cuts", "made cuts", "make cuts"])
    elif w_clean == "weigh yourself":
        stems.extend(["weigh myself", "weigh yourself", "weighed myself", "weighing myself", "weigh himself", "weighed himself"])
    elif "concentrat" in w_clean:
        stems.extend(["concentrate", "concentrates", "concentrating", "concentrated", "concentrating on", "concentrate on"])
        
    parts = w_clean.split()
    if len(parts) > 1:
        first = parts[0]
        rest = " ".join(parts[1:])
        past_map = {
            "break": ["broke", "broken"],
            "have": ["having", "had", "has"],
            "take": ["took", "taken"],
            "get": ["got", "gotten", "getting"],
            "run": ["ran"],
            "go": ["went", "gone"],
            "walk": ["walked"],
            "make": ["made", "making"],
            "hold": ["held", "holding", "holds"],
            "attend": ["attended"],
            "lead": ["led"],
            "open": ["opened"],
            "build": ["built"],
            "eat": ["ate", "eaten"],
            "pay": ["paid"],
            "handle": ["handled", "handling"],
            "concentrate": ["concentrated", "concentrating"]
        }
        if first in past_map:
            for p in past_map[first]:
                stems.append(f"{p} {rest}")
        stems.append(f"{first} {rest}s")
    else:
        stems.extend([w_clean + "d", w_clean + "ed", w_clean + "ted", w_clean + "ing", w_clean + "ting"])
        if w_clean.endswith("s"):
            stems.append(w_clean[:-1])
        if w_clean.endswith("es"):
            stems.append(w_clean[:-2])
            
    lines = content.splitlines()
    
    # Ưu tiên 1: Câu hoàn chỉnh kết thúc bằng dấu chấm/chấm than/hỏi chấm
    for l in lines:
        sl = l.strip()
        sl = re.sub(r"^\[\s*[x ]?\s*\]\s*", "", sl)
        sl = re.sub(r"^\d+\.\s*", "", sl)
        if len(sl.split()) < 4 or len(sl) > 180:
            continue
        if sl.lower() == w_clean or sl.lower() == w_clean + ".":
            continue
        if sl.startswith("(") or sl.startswith("====") or sl.startswith("Mã") or sl.startswith("Video") or sl.startswith("Ô"):
            continue
        if sl.endswith(".") or sl.endswith("?") or sl.endswith("!") or sl.endswith('."'):
            for st in stems:
                if re.search(rf"\b{re.escape(st)}\b", sl, re.I):
                    return clean_dictation(sl)
                    
    # Ưu tiên 2: Bất kỳ dòng nào phù hợp
    for l in lines:
        sl = l.strip()
        sl = re.sub(r"^\[\s*[x ]?\s*\]\s*", "", sl)
        sl = re.sub(r"^\d+\.\s*", "", sl)
        if len(sl.split()) < 4 or len(sl) > 180:
            continue
        if sl.lower() == w_clean or sl.lower() == w_clean + ".":
            continue
        if sl.startswith("(") or sl.startswith("====") or sl.startswith("Mã") or sl.startswith("Video") or sl.startswith("Ô"):
            continue
        for st in stems:
            if re.search(rf"\b{re.escape(st)}\b", sl, re.I):
                return clean_dictation(sl)
    return None


def parse_raw_file(fpath):
    with open(fpath, encoding="utf-8") as f:
        content = f.read()
    
    fname = os.path.basename(fpath)
    base_name = os.path.splitext(fname)[0]
    
    # Mã bài & video
    code_m = re.search(r"Mã bài:\s*([^\n]+)", content)
    code = code_m.group(1).strip() if code_m else INDEX_METADATA.get(base_name, {}).get("ma_bai", "-")
    
    video_m = re.search(r"Video kèm theo:\s*([^\n]+)", content)
    video = video_m.group(1).strip() if video_m else INDEX_METADATA.get(base_name, {}).get("video", "-")
    
    # NỘI DUNG BÀI
    nd_m = re.search(r"==== NỘI DUNG BÀI \(EN \| VI\) ====(.*?)(?:==== PRACTICE|$)", content, re.DOTALL)
    nd_text = nd_m.group(1).strip() if nd_m else ""
    
    # PRACTICE
    prac_m = re.search(r"==== PRACTICE ====(.*?)(?:==== TEST|$)", content, re.DOTALL)
    prac_text = prac_m.group(1).strip() if prac_m else ""
    
    # TEST
    test_m = re.search(r"==== TEST ====(.*?)$", content, re.DOTALL)
    test_text = test_m.group(1).strip() if test_m else ""
    
    # Tách các cặp hội thoại / văn bản EN - VI
    bilingual_blocks = []
    if nd_text:
        lines = nd_text.splitlines()
        curr_spk = None
        curr_en = []
        curr_vi = []
        state = None
        for l in lines:
            sl = l.strip()
            if not sl or sl.startswith("====") or sl.startswith("(căn câu") or sl == "(dẫn)":
                continue
            m_spk = re.match(r"^([A-Za-z0-9\s\.\-_,\'’]+):$", sl)
            if m_spk and not sl.startswith("EN:") and not sl.startswith("VI:"):
                if curr_en or curr_vi:
                    bilingual_blocks.append((curr_spk, clean_line(" ".join(curr_en)), clean_line(" ".join(curr_vi))))
                    curr_en, curr_vi = [], []
                curr_spk = m_spk.group(1).strip()
                state = None
                continue
            if sl.startswith("EN:"):
                if state == "VI" and (curr_en or curr_vi) and curr_spk is None:
                    bilingual_blocks.append((curr_spk, clean_line(" ".join(curr_en)), clean_line(" ".join(curr_vi))))
                    curr_en, curr_vi = [], []
                state = "EN"
                curr_en.append(sl[3:].strip())
            elif sl.startswith("VI:"):
                state = "VI"
                curr_vi.append(sl[3:].strip())
            else:
                if state == "EN":
                    curr_en.append(sl)
                elif state == "VI":
                    curr_vi.append(sl)
        if curr_en or curr_vi:
            bilingual_blocks.append((curr_spk, clean_line(" ".join(curr_en)), clean_line(" ".join(curr_vi))))
            
    # Tách bài tập Practice & Test
    def parse_exercises(text):
        if not text:
            return []
        raw_items = re.split(r"\n(?=\[[a-zA-Z0-9]+\])", text.strip())
        items = []
        for raw in raw_items:
            raw = raw.strip()
            if not raw:
                continue
            lines = raw.splitlines()
            qid = lines[0].strip("[] ")
            inst_m = re.search(r"\((.*?)\)", raw)
            inst = inst_m.group(1).strip() if inst_m else ""
            
            stem_lines = []
            answers = []
            options = []
            for l in lines[1:]:
                sl = l.strip()
                if sl.startswith("Ô "):
                    continue
                if sl.startswith("[x]"):
                    ans = sl[3:].strip()
                    answers.append(ans)
                    options.append(f"[x] {ans}")
                elif sl.startswith("[ ]"):
                    opt = sl[3:].strip()
                    options.append(f"[ ] {opt}")
                elif not sl.startswith("(") and sl:
                    stem_lines.append(sl)
                    
            if not answers and options:
                clean_opts = [o[3:].strip() for o in options if o[3:].strip() not in ["Definitions", "Words", "A", "B", "A and B", "True", "False"]]
                if clean_opts:
                    answers = clean_opts
                
            items.append({
                "qid": qid,
                "inst": inst,
                "stem": clean_line(" ".join(stem_lines)),
                "answers": answers,
                "options": options
            })
        return items

    prac_items = parse_exercises(prac_text)
    test_items = parse_exercises(test_text)
    
    # Trích xuất cặp từ - định nghĩa nếu là bài từ vựng
    vocab_pairs = []
    sections = re.findall(r"\(Match the words to the correct definitions.*?\)\n(.*?)(?=\n\[i2|\n\[i3|\n====|\Z)", content, re.DOTALL)
    for sec in sections:
        blocks = re.findall(r"Ô \d+\s*\n\s*\[ \]\s*([^\n]+)\s*\n\s*\[ \]\s*([^\n]+)", sec)
        for b1, b2 in blocks:
            b1 = b1.strip()
            b2 = b2.strip()
            if b1 not in ["Definitions", "Words", "A", "B"] and b2 not in ["Definitions", "Words", "A", "B"]:
                vocab_pairs.append((b2, b1))

    return {
        "fname": fname,
        "base_name": base_name,
        "code": code,
        "video": video,
        "content": content,
        "nd_text": nd_text,
        "bilingual_blocks": bilingual_blocks,
        "prac_items": prac_items,
        "test_items": test_items,
        "vocab_pairs": vocab_pairs
    }


def is_grammar_lesson(info):
    name = info["base_name"]
    content = info["content"]
    if any(k in name for k in [
        "Conditionals", "Past_Perfect", "Reported_Speech",
        "CausativesPermissives", "Modals", "Relative_Clauses"
    ]):
        return True
    if any(k in name for k in [
        "Introduction_Recycling", "City_of_Lakeview_Recycling_Tips", "Introduction_Movie_Making"
    ]):
        return True
    if "FORM:" in content and "DẠNG THỨC:" in content:
        return True
    return False


def build_grammar_section(info):
    if not is_grammar_lesson(info):
        return "Không có nội dung ngữ pháp riêng."
    
    b_blocks = info["bilingual_blocks"]
    prac = info["prac_items"]
    test = info["test_items"]
    
    out = []
    
    # 1. Trích xuất Tên cấu trúc / Dạng thức / Cách dùng
    out.append("#### Cấu trúc và Quy tắc Ngữ pháp Trọng tâm\n")
    if b_blocks:
        for spk, en, vi in b_blocks:
            spk_label = f"**[{spk}]** " if spk else ""
            out.append(f"- {spk_label}**Quy tắc:** {vi}")
            out.append(f"  - *English:* {en}")
    else:
        out.append("- Cấu trúc ngữ pháp trọng tâm được trình bày chi tiết trong tài liệu bài học.")
    out.append("")
    
    # 2. Ví dụ minh họa từ bài học
    out.append("#### Ví dụ Minh họa trong Bài học\n")
    ex_matches = re.findall(r'"([^"\n]{10,120})"', info["nd_text"])
    valid_ex = [e for e in ex_matches if len(e.split()) >= 3 and not e.startswith("căn câu")]
    if valid_ex:
        for idx, ex in enumerate(valid_ex[:8], 1):
            out.append(f"{idx}. *\"{ex.strip()}\"*")
    else:
        for idx, (spk, en, vi) in enumerate(b_blocks[:5], 1):
            out.append(f"{idx}. **EN:** {en}")
            out.append(f"   **VI:** {vi}")
    out.append("")
    
    # 3. Bài tập liên quan (Practice & Test)
    out.append("#### Bài tập Thực hành Trọng tâm (Trích từ Practice & Test)\n")
    all_ex = prac + test
    selected_ex = all_ex[:6]
    for idx, ex in enumerate(selected_ex, 1):
        out.append(f"##### Bài tập {idx} (`{ex['qid']}`)")
        if ex["inst"]:
            out.append(f"- **Yêu cầu:** {ex['inst']}")
        if ex["stem"]:
            out.append(f"- **Đề bài:** {ex['stem']}")
        if ex["answers"]:
            ans_str = ", ".join(f"`{a}`" for a in ex["answers"])
            out.append(f"- **Đáp án chính xác:** {ans_str}")
        elif ex["options"]:
            opts_str = " | ".join(ex["options"][:4])
            out.append(f"- **Các lựa chọn:** {opts_str}")
        out.append("")
        
    return "\n".join(out).strip()


def build_vocab_section(info):
    base_name = info["base_name"]
    unit_id = base_name[:6]
    unit_meta = UNIT_TOPICS.get(unit_id, {
        "title": "Chủ điểm bài học",
        "theme_categories": {"Từ vựng bài học": []},
        "confusing_words": []
    })
    
    words_data = [] # (word, pos, ipa, vi, example)
    
    # Trường hợp 1: Bài học từ vựng có sẵn matching pairs
    if info["vocab_pairs"]:
        for w, def_en in info["vocab_pairs"]:
            lex = LEXICON_DB.get(w, LEXICON_DB.get(w.lower(), None))
            if lex:
                pos, ipa, vi = lex
            else:
                pos = "Cụm từ / Từ"
                ipa = "-"
                vi = def_en
            ex_sent = find_sentence_in_content(w, info["content"])
            if not ex_sent:
                ex_sent = f"Trích từ bài học: {def_en}."
            words_data.append((w, pos, ipa, vi, ex_sent))
            
    # Trường hợp 2: Bài đọc / nghe / hội thoại có bilingual blocks
    elif info["bilingual_blocks"]:
        unit_words = []
        for cat, w_list in unit_meta["theme_categories"].items():
            unit_words.extend(w_list)
            
        found_words = []
        for spk, en, vi in info["bilingual_blocks"]:
            for w in unit_words:
                if w in found_words:
                    continue
                pattern = rf"\b{re.escape(w)}\b"
                if re.search(pattern, en, re.IGNORECASE):
                    lex = LEXICON_DB.get(w, LEXICON_DB.get(w.lower(), None))
                    if lex:
                        pos, ipa, vi_mean = lex
                    else:
                        pos = "Từ vựng bài học"
                        ipa = "-"
                        vi_mean = vi
                    words_data.append((w, pos, ipa, vi_mean, f"\"{en}\""))
                    found_words.append(w)
                    if len(words_data) >= 12:
                        break
            if len(words_data) >= 12:
                break
                
        # Nếu chưa đủ từ vựng, trích thêm các mẫu câu giao tiếp hoặc câu nổi bật
        if len(words_data) < 5:
            for spk, en, vi in info["bilingual_blocks"]:
                if 10 < len(en) < 90 and en not in [x[0] for x in words_data]:
                    words_data.append((en, "Cụm câu giao tiếp", "-", vi, f"\"{en}\""))
                if len(words_data) >= 8:
                    break
                    
    # Trường hợp 3: Bài ngữ pháp chuyên biệt
    else:
        unit_words = []
        for cat, w_list in unit_meta["theme_categories"].items():
            unit_words.extend(w_list)
        found = []
        for w in unit_words:
            if re.search(rf"\b{re.escape(w)}\b", info["content"], re.I):
                lex = LEXICON_DB.get(w)
                if lex:
                    words_data.append((w, lex[0], lex[1], lex[2], f"Xuất hiện trong ngữ cảnh Unit: {unit_meta['title']}"))
                    found.append(w)
            if len(words_data) >= 8:
                break
                
        if len(words_data) < 3 and info["prac_items"]:
            for p in info["prac_items"]:
                for a in p["answers"]:
                    if a not in [x[0] for x in words_data] and len(a) > 2 and a not in ["will", "can", "may"]:
                        lex = LEXICON_DB.get(a.lower())
                        if lex:
                            words_data.append((a, lex[0], lex[1], lex[2], p["stem"]))
                        else:
                            words_data.append((a, "Từ khóa trong bài", "-", "Từ xuất hiện trong bài tập", p["stem"]))
                if len(words_data) >= 6:
                    break

    out = []
    out.append("#### Bảng Từ vựng Trọng tâm\n")
    out.append("| Từ / Cụm từ | Loại từ | IPA | Nghĩa tiếng Việt | Ví dụ trong bài |")
    out.append("| :--- | :--- | :--- | :--- | :--- |")
    
    if words_data:
        for w, pos, ipa, vi, ex in words_data:
            ex_clean = ex.replace("|", "/").replace("\n", " ").strip()
            if len(ex_clean) > 130:
                ex_clean = ex_clean[:127] + "..."
            out.append(f"| **{w}** | *{pos}* | `{ipa}` | {vi} | {ex_clean} |")
    else:
        out.append("| - | - | - | Không có nội dung từ vựng riêng | - |")
    out.append("")
    
    # Phân loại theo chủ đề
    out.append("#### Phân loại Từ vựng theo Chủ đề\n")
    themes = unit_meta.get("theme_categories", {})
    if themes:
        for cat_name, word_list in themes.items():
            wl_str = ", ".join(f"`{w}`" for w in word_list[:8])
            out.append(f"- **{cat_name}:** {wl_str}")
    else:
        out.append(f"- **Chủ đề chính:** `{unit_meta.get('title', 'Tiếng Anh giao tiếp')}`")
    out.append("")
    
    # Danh sách từ khó / dễ nhầm
    out.append("#### Danh sách Từ khó & Dễ nhầm lẫn\n")
    confusing = unit_meta.get("confusing_words", [])
    if confusing:
        for item in confusing:
            out.append(item)
    else:
        out.append("- Lưu ý ngữ cảnh sử dụng và kết hợp từ (collocations) tự nhiên trong các bài tập.")
    out.append("")
    
    return "\n".join(out).strip()


def generate_lesson_markdown(info):
    base = info["base_name"]
    parts = base.split("-")
    level = "Intermediate 2" if parts[0] == "I2" else "Intermediate 3"
    
    unit_num = f"Unit {int(parts[1][1:])}" if len(parts) > 1 and parts[1][1:].isdigit() else (parts[1] if len(parts) > 1 else "")
    lesson_num = f"Lesson {int(parts[2][1:])}" if len(parts) > 2 and parts[2][1:].isdigit() else (parts[2] if len(parts) > 2 else "")
    raw_title = " ".join(parts[3:]).replace("_", " ") if len(parts) > 3 else base
    
    title_display = f"{level} - {unit_num} - {lesson_num}: {raw_title}"
    unit_id = base[:6]
    topic_info = UNIT_TOPICS.get(unit_id, {}).get("title", "English Discoveries")
    
    grammar_section = build_grammar_section(info)
    vocab_section = build_vocab_section(info)
    
    md_lines = []
    md_lines.append(f"# {title_display}")
    md_lines.append("")
    md_lines.append(f"- **Tên file gốc:** `{info['fname']}`")
    md_lines.append(f"- **Mã bài học:** `{info['code']}` | **Media đính kèm:** `{info['video']}`")
    md_lines.append(f"- **Chủ đề Unit:** {topic_info}")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("### 1. NGỮ PHÁP")
    md_lines.append("")
    md_lines.append(grammar_section)
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("### 2. TỪ VỰNG")
    md_lines.append("")
    md_lines.append(vocab_section)
    md_lines.append("")
    
    return "\n".join(md_lines)


def update_progress(done_count, total_count, recent_files):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    percent = (done_count / total_count) * 100
    status_text = "ĐANG TIẾN HÀNH" if done_count < total_count else "ĐÃ HOÀN THÀNH 100%"
    
    content = []
    content.append("# BÁO CÁO TIẾN ĐỘ BIÊN SOẠN TÀI LIỆU")
    content.append("")
    content.append(f"- **Trạng thái:** **{status_text}**")
    content.append(f"- **Tiến độ hiện tại:** **{done_count} / {total_count} file** ({percent:.1f}%)")
    content.append(f"- **Thời gian cập nhật:** `{timestamp}`")
    content.append("")
    content.append("### Danh sách các file vừa hoàn thành trong đợt:")
    for f in recent_files[-10:]:
        content.append(f"- [x] `{f}`")
    content.append("")
    content.append("---")
    content.append("*Hệ thống tự động cập nhật sau mỗi 10 file bài học và sau khi hoàn tất toàn bộ danh sách.*")
    
    out_str = "\n".join(content)
    for d in DEST_DIRS:
        prog_path = os.path.join(d, "_tien_do.md")
        with open(prog_path, "w", encoding="utf-8") as pf:
            pf.write(out_str)


def main():
    print("=== BẮT ĐẦU QUY TRÌNH BIÊN SOẠN TÀI LIỆU TIẾNG ANH ===")
    
    txt_files = sorted(glob.glob(os.path.join(SRC_DIR, "*.txt")))
    total_files = len(txt_files)
    print(f"Tổng số file .txt nguồn: {total_files}")
    
    generated_mds = []
    recent_done = []
    
    # 2. Xử lý từng file một
    for idx, fpath in enumerate(txt_files, 1):
        info = parse_raw_file(fpath)
        md_content = generate_lesson_markdown(info)
        out_name = f"{info['base_name']}.md"
        
        for d in DEST_DIRS:
            target_path = os.path.join(d, out_name)
            with open(target_path, "w", encoding="utf-8") as out_f:
                out_f.write(md_content)
                
        generated_mds.append(out_name)
        recent_done.append(out_name)
        print(f"[{idx:02d}/{total_files:02d}] Đã xử lý: {out_name}")
        
        # 4. Sau mỗi 10 file hoặc file cuối cùng: cập nhật _tien_do.md
        if idx % 10 == 0 or idx == total_files:
            update_progress(idx, total_files, recent_done)
            print(f">>> Đã cập nhật _tien_do.md ({idx}/{total_files} file)")
            recent_done = []
            
    # 5. Đối chiếu số file .md với số file .txt
    print("\n=== ĐỐI CHIẾU KIỂM TRA SỐ LƯỢNG ===")
    missing_files = []
    for fpath in txt_files:
        expected_md = f"{os.path.splitext(os.path.basename(fpath))[0]}.md"
        if expected_md not in generated_mds:
            missing_files.append(expected_md)
            
    print(f"Tổng số file .txt nguồn: {total_files}")
    print(f"Tổng số file .md đã tạo: {len(generated_mds)}")
    
    if missing_files:
        print(f"CẢNH BÁO: Còn thiếu {len(missing_files)} file: {missing_files}")
        sys.exit(1)
    else:
        print("XÁC NHẬN: Số lượng file hoàn toàn trùng khớp 82/82!")

    # 6. Gộp tất cả file .md thành FULL_KHOA.md
    print("\n=== ĐANG GỘP TẤT CẢ FILE THÀNH FULL_KHOA.MD ===")
    header = (
        "# TỔNG HỢP TOÀN BỘ GIÁO TRÌNH TIẾNG ANH - ENGLISH DISCOVERIES\n\n"
        "## Intermediate 2 & Intermediate 3 (Toàn bộ 82 Bài học)\n\n"
        f"- **Ngày biên soạn:** {datetime.now().strftime('%d/%m/%Y')}\n"
        f"- **Tổng số bài:** {len(generated_mds)} bài học\n\n"
    )
    
    lesson_contents = []
    for md_name in sorted(generated_mds):
        p = os.path.join(DEST_DIRS[0], md_name)
        with open(p, encoding="utf-8") as f:
            lesson_contents.append(f.read().strip())
            
    full_content = header + "---\n\n" + "\n\n---\n\n".join(lesson_contents)
    
    for d in DEST_DIRS:
        full_path = os.path.join(d, "FULL_KHOA.md")
        with open(full_path, "w", encoding="utf-8") as ff:
            ff.write(full_content)
        print(f"Đã tạo thành công: {full_path} (Kích thước: {len(full_content):,} ký tự)")
        
    print("\n=== HOÀN TẤT TOÀN BỘ QUY TRÌNH THÀNH CÔNG RỰC RỠ! ===")


if __name__ == "__main__":
    main()

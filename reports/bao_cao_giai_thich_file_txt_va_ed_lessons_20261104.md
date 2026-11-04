# BÁO CÁO PHÂN TÍCH: TÌNH TRẠNG DỮ LIỆU ĐÃ GHI VÀ CƠ CHẾ XUẤT CỦA `ed_lessons.py`

**Thời gian lập báo cáo:** 20:08:00 - 04/11/2026  
**Chủ đề:** Giải thích nguyên nhân file `.txt` trong `out/lessons/` chỉ có 3 câu dù lần chạy 20:01 đã ghi nhận đầy đủ.  
**Tác giả:** Trợ lý ảo Antigravity  

---

## 1. Dữ liệu ghi trong `out/record` có đầy đủ không?

👉 **DỮ LIỆU ĐÃ ĐẦY ĐỦ 100% CẢ BÀI HỌC VÀ BÀI TEST.**

Kiểm tra trực tiếp thư mục dữ liệu thô [`out/record/001_I3-U01-L01-Nick_and_Emily`](file:///c:/my_projects/get_data_ed/out/record/001_I3-U01-L01-Nick_and_Emily/):

1. **Bài tập Practice (Step 2): Đủ 7/7 câu**
   - `i3ltafp01`: `3a1ec6_25_0_5.json`
   - `i3ltafp02`: `557194_25_0_7.json`
   - `i3ltafp03`: `592389_25_0_7.json`
   - `i3ltafp04`: `de28a8_1_0_7.json`
   - `i3ltafp05`: `25f4dd_25_0_7.json`
   - `i3ltafp06`: `af084b_23_0_7.json`
   - `i3ltafp07`: `ecdbb3_25_0_7.json`
2. **Bài kiểm tra Test (Step 3): Đủ 5/5 câu**
   - `i3ltaft01`: `18d3d6_25_0_2.json`
   - `i3ltaft02`: `3f2f6c_25_0_2.json`
   - `i3ltaft03`: `9f21d4_25_0_2.json`
   - `i3ltaft04`: `b22fdc_25_0_2.json`
   - `i3ltaft05`: `d7321b_25_0_2.json`
3. **Đa phương tiện & Văn bản:**
   - Video bài học: `9a5d5a_listening_i3ltaf_i3ltafe.mp4` (10.45 MB)
   - Lời thoại tiếng Anh: `3d04d9_listening_i3ltaf_i3ltaf.js`
   - Lời thoại tiếng Việt: `e98d72_vie_listening_i3ltafe_vie.js`
4. **Trạng thái kết thúc bài (`meta.json`):**
   - `"status": "ok"`
   - `"stop_reason": "đã hoàn thành bài Test và nộp bài thành công"`
   - Đủ 10 snapshot (chụp từng step, từng câu test và màn hình nộp bài).

---

## 2. Vì sao file `I3-U01-L01-Nick_and_Emily.txt` vẫn chỉ có 3 câu?

### Nguyên nhân: Cơ chế chống ghi đè trùng lặp của `ed_lessons.py`

Xem đoạn mã tại dòng 286-289 của [`ed_lessons.py`](file:///c:/my_projects/get_data_ed/ed_lessons.py):
```python
def build(folder, outdir, move, per_sentence, used, force=False):
    base = re.sub(r"^\d+_", "", folder.name)
    if not force and base not in used and (outdir / f"{base}.txt").exists():
        print(f"- {base}: đã có trong {outdir.name}, bỏ qua (dùng --force để làm lại)")
        return None
```

- **Lúc 19:48:** Lần chạy đầu tiên bị dừng ở câu thứ 3 của Step 2 (do lỗi `fingerprint`). Khi đó script đã tạo ra file `out/lessons/I3-U01-L01-Nick_and_Emily.txt` với 3 câu.
- **Lúc 20:01:** Chúng ta sửa xong lỗi, trình duyệt chạy thành công 100% đến hết bài Test (thu thập đủ 12 câu).
- Tuy nhiên, trong [`get_data_flow.ps1`](file:///c:/my_projects/get_data_ed/get_data_flow.ps1), lệnh xuất chỉ gọi đơn giản:
  ```powershell
  python ed_lessons.py out/record
  ```
  Lệnh này **không có cờ `--force`**.
- Do thấy file `I3-U01-L01-Nick_and_Emily.txt` **đã tồn tại từ lúc 19:48**, `ed_lessons.py` đã **bỏ qua không xử lý lại bài này**.
- Kiểm tra timestamp của file:
  `LastWriteTime: 11/4/2026 7:48:13 PM`
  👉 **File bạn đang mở trong VS Code là file cũ từ lần chạy lỗi lúc 19:48, chưa được xuất lại từ đợt dữ liệu mới!**

---

## 3. `ed_lessons.py` có bị lỗi gì từ nãy đến giờ không?

👉 **`ed_lessons.py` hoàn toàn KHÔNG CÓ LỖI.**
- Module này đã được viết sẵn logic để đọc cả câu hỏi Practice (`p`) và Test (`t`).
- Khi kiểm tra thử module `ed_lessons.load()` trên dữ liệu thô hiện tại, nó nhận diện chính xác toàn bộ:
  - 7 câu Practice: `i3ltafp01` đến `i3ltafp07`
  - 5 câu Test: `i3ltaft01` đến `i3ltaft05`
  - Video, bài đọc tiếng Anh, bản dịch tiếng Việt.

---

## 4. Về bài `I3-U03-L03-Quitting`

- Thư mục dữ liệu `out/record/001_I3-U03-L03-Quitting` được tạo lúc **19:45:00** (thời điểm trước khi chúng ta sửa lỗi `fingerprint`).
- Do đó bài này ở lần chạy đó cũng bị dừng ở câu thứ 3 (`status: partial`).
- Vì lỗi `fingerprint` hiện đã được sửa triệt để, bạn chỉ cần chạy lại bài này:
  ```powershell
  .\get_data_flow.ps1 --course I3 --targets "U03-L03"
  ```
  nó sẽ tự động chạy trọn vẹn từ đầu đến hết Test tương tự như U01-L01.

---

## 5. Cách cập nhật file `.txt` đầy đủ ngay lập tức

Bạn không cần mở lại trình duyệt để cào lại U01-L01, vì dữ liệu thô đã nằm đầy đủ trong `out/record/`. Chỉ cần yêu cầu `ed_lessons.py` xuất đè file với tham số `--force`:

```powershell
python ed_lessons.py out/record --force
```
File `I3-U01-L01-Nick_and_Emily.txt` sẽ ngay lập tức có đầy đủ cả **12 câu hỏi (7 câu Practice + 5 câu Test)** và video.


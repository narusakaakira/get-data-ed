# BÁO CÁO PHÂN TÍCH LỖI: `confirmModal` CHE PHỦ NÚT LOGIN KHI TRANH PHIÊN (19:36:37)

**Thời gian lập báo cáo:** 19:41:00 - 04/11/2026  
**File nhật ký liên quan:** Lần chạy lệnh `.\get_data_flow.ps1 --course I3 --targets "U03-L03" -NoExport`  
**Tác giả:** Trợ lý ảo Antigravity

---

## 1. Mô tả lỗi

Khi bạn chủ động mở thêm một profile Chrome khác để thử nghiệm tình huống tranh phiên giữa 2 máy / 2 trình duyệt, script tự động chiếm phiên gặp lỗi `TimeoutError` sau 30 giây:

```text
[Thử lại 1/3] Chưa thấy danh sách Unit (URL hiện tại: https://ed22.engdis.com/ptithcm#/login). Đang thử kết nối lại...
Phát hiện bị đưa về trang đăng nhập, tiến hành chiếm lại phiên...
Traceback (most recent call last):
  ...
  File "C:\my_projects\get_data_ed\ed_recorder_autologin_v3.py", line 89, in auto_login
    await page.get_by_role("button", name="Login", exact=True).click()
playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
```

Nhìn vào **Call log chi tiết của Playwright**:
```text
waiting for element to be visible, enabled and stable
  - element is visible, enabled and stable
  - scrolling into view if needed
  - done scrolling
  - <div class="modal confirmPopup__main rtlAware layout__confirmModal modal--noModalHeader">…</div> 
    from <div id="confirmModal" class="modalW modalW_confirm">…</div> subtree intercepts pointer events
```

---

## 2. Phân tích nguyên nhân gốc rễ

1. **Popup cảnh báo đã mở sẵn từ trước:**
   - Khi profile Chrome thứ hai đăng nhập, phiên của profile tự động lập tức bị hủy và trang tự văng về `#/login`.
   - Ngay tại thời điểm tải lại trang đăng nhập, máy chủ ED22 **ngay lập tức hiển thị popup modal `#confirmModal`** ("You are already logged in on another device...") kèm theo nút **"Login on This Device"** (`#btnOk`).
   - Modal này là một lớp phủ toàn màn hình (`z-index` cao) nằm đè lên trên form đăng nhập và nút `Login`.

2. **Thứ tự xử lý trong hàm `auto_login()` bị ngược:**
   - Thứ tự code cũ:
     1. Điền username (`#user`).
     2. Điền password (`#pass`).
     3. **Bấm nút `Login` (`#submit1`)** *(bị kẹt tại đây)*.
     4. Mới gọi `handle_already_logged_in()` để bấm `#btnOk`.
   - Vì popup `#confirmModal` đang đè lên trên nút `Login`, Playwright kích hoạt cơ chế bảo vệ: không click vào phần tử nếu bị phần tử khác che khuất con trỏ chuột (`intercepts pointer events`).
   - Playwright chờ 30 giây để popup biến mất rồi mới click, nhưng popup không tự biến mất nếu chưa có ai bấm `#btnOk`.
   - Kết quả: Timeout ở dòng click `Login`, code **không bao giờ chạy tới dòng bấm `#btnOk`**.

---

## 3. Giải pháp khắc phục trong `ed_recorder_autologin_v3.py`

1. **Đưa việc kiểm tra popup lên ĐẦU TIÊN:**
   - Ngay khi hàm `auto_login()` được gọi, lập tức kiểm tra xem `#confirmModal` hoặc `#btnOk` có đang mở sẵn không.
   - Nếu có sẵn: **Bấm ngay nút `#btnOk` bằng lệnh JavaScript (`force=True` / `evaluate`)** để chiếm lại phiên. Không cần điền form hay bấm nút `Login` nữa.
2. **Kiểm tra lặp lại trước khi click Login:**
   - Trước khi click `Login`, kiểm tra lại 1 lần nữa nếu popup vừa bật lên giữa chừng.
3. **Sử dụng `force=True` và fallback JavaScript click cho nút Login:**
   - Đảm bảo nếu có bất kỳ overlay vô hình nào cũng không làm kẹt tiến trình click của Playwright.


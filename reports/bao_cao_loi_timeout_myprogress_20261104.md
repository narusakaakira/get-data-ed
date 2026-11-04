# BÁO CÁO PHÂN TÍCH NGUYÊN NHÂN LỖI TIMEOUT TẠI `open_progress` (19:19:20)

**Thời gian lập báo cáo:** 19:25:00 - 04/11/2026  
**File nhật ký liên quan:** [`logs/run_20261104_191920.log`](file:///c:/my_projects/get_data_ed/logs/run_20261104_191920.log)  
**Tác giả:** Trợ lý ảo Antigravity

---

## 1. Tóm tắt lỗi

Trong lần chạy lúc **19:19:20**, quá trình chạy tự động bị dừng lại với thông báo lỗi:

```text
Traceback (most recent call last):
  File "C:\my_projects\get_data_ed\ed_recorder_autologin_v3.py", line 298, in <module>
    asyncio.run(main())
  File "C:\my_projects\get_data_ed\ed_recorder_autologin_v3.py", line 272, in main
    await run_auto(ctx, page, cfg, rec)
  File "C:\my_projects\get_data_ed\ed_operation.py", line 449, in run_auto
    jobs, skipped = await build_jobs(page, cfg)
  File "C:\my_projects\get_data_ed\ed_operation.py", line 170, in build_jobs
    await open_progress(page, cfg)
  File "C:\my_projects\get_data_ed\ed_operation.py", line 157, in open_progress
    await page.wait_for_selector(SEL_UNIT, timeout=30000)
playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".myProgress__unitW") to be visible
```

---

## 2. Câu hỏi cốt lõi: Tại sao trước đó không có lỗi mà sau khi cập nhật `ed_operation.py` lại xuất hiện?

### 2.1. Kiểm tra mã nguồn (Code Diff)
Kiểm tra đối chiếu các thay đổi vừa thực hiện trên [`ed_operation.py`](file:///c:/my_projects/get_data_ed/ed_operation.py):
- Các phần được sửa đổi:
  - Cập nhật các bộ chọn: `START_TEST_SEL`, `SUBMIT_TEST_SEL`, mở rộng `NEXT_SEL` và `STATE_JS`.
  - Bổ sung hàm xử lý hộp thoại nộp bài test: `handle_submit_confirmation`.
  - Cập nhật hàm điều khiển bài học: `walk(lp, rec, cfg)`.
  - Cập nhật xử lý sự kiện: `on_dialog` trong `run_auto`.
- **Các hàm liên quan trực tiếp đến vị trí lỗi:**
  - `open_progress(page, cfg)`
  - `build_jobs(page, cfg)`
  - `expand_unit(page, ui)`
  - Bộ chọn `SEL_UNIT = ".myProgress__unitW"`
  👉 **Các hàm và bộ chọn này GIỮ NGUYÊN 100%, không bị thay đổi một ký tự nào so với các lần chạy thành công trước đó.**

Hơn nữa, tiến trình thực thi còn **chưa kịp gọi đến hàm `walk()`** (hàm chứa các logic mới về Test) vì đã bị dừng ngay từ bước quét danh sách bài ở trang tiến trình học (`build_jobs`).

---

### 2.2. Điểm khác biệt duy nhất giữa lần chạy này và các lần trước

So sánh dòng log khởi động giữa lần chạy trước (`18:58:23`) và lần chạy bị lỗi (`19:19:20`):

| Thời điểm | Log đăng nhập ban đầu | Kết quả đăng nhập |
| :--- | :--- | :--- |
| **18:58:23** | `[cấu hình] tài khoản=... | khóa=I3` <br>`Đã chuyển đến khoá I3...` | Đăng nhập trực tiếp, không có cảnh báo nào |
| **19:19:20** | `[cấu hình] tài khoản=... | khóa=I3` <br>🔴 **`Tài khoản đang đăng nhập ở thiết bị khác -> chiếm phiên trên máy này.`** <br>`Đã đăng nhập tự động.` <br>`Đã chuyển đến khoá I3...` | **Kích hoạt cơ chế chiếm phiên từ thiết bị khác** |

### 2.3. Nguyên nhân gốc rễ (Root Cause)

1. **Phiên đăng nhập song song từ bên ngoài:**
   - Trong khoảng thời gian từ **19:01 đến 19:07**, bạn đã mở trình duyệt để kiểm tra DevTools và chụp các ảnh màn hình về các phần tử của bài Test.
   - Phiên đăng nhập thủ công này vẫn còn hiệu lực trên máy chủ của `engdis.com`.
   - Khi chạy script lúc **19:19:20**, hệ thống ED22 phát hiện tài khoản đang được mở ở một phiên khác nên đã bật popup cảnh báo: *"You are already logged in on another device"*.

2. **Xung đột điều hướng (Race Condition) trong Angular SPA:**
   - Khi script kích hoạt nút **"Login on This Device"** (`#btnOk`):
     - Server thực hiện vô hiệu hóa phiên cũ và cấp quyền cho phiên mới.
     - Sau khi popup đóng, ứng dụng Angular đang trong quá trình tải dữ liệu người dùng và tự động định tuyến (route) về trang chủ (`#/home`).
   - Cùng thời điểm đó, script gọi ngay lệnh điều hướng đến khóa học:
     ```python
     await page.goto("https://ed22.engdis.com/ptithcm#/MyProgress/Course/45441/Unit/")
     ```
   - Trong Single Page Application (SPA) sử dụng Hash Routing (`#/`), việc `goto` ngay khi Angular chưa hoàn thành tiến trình khởi tạo trạng thái người dùng (User Session / State) khiến router của Angular hủy bỏ điều hướng hoặc tự động đẩy người dùng ngược trở lại trang chủ (`#/home`).
   - Khi trang thực tế đang hiển thị trang chủ (`#/home`) hoặc đang kẹt ở màn hình tải (loading spinner), phần tử `.myProgress__unitW` (chỉ tồn tại trên trang MyProgress) **không hề xuất hiện**.
   - Sau 30.000ms (30 giây) không thấy phần tử, Playwright ném lỗi `TimeoutError: Page.wait_for_selector: Timeout 30000ms exceeded`.

---

## 3. Kết luận

- Việc xuất hiện lỗi ở lần chạy này là do **tài khoản bị trùng phiên đăng nhập** (do vừa mở trình duyệt thủ công trước đó), kích hoạt popup "You are already logged in..." dẫn đến xung đột điều hướng trong Angular SPA.
- Lỗi **không xuất phát từ các đoạn code vừa được sửa đổi trong `ed_operation.py`**, vì đoạn code bị lỗi (`open_progress`) hoàn toàn không bị can thiệp.

---

## 4. Phương án xử lý đề xuất (Chờ phê duyệt)

> [!NOTE]
> Theo đúng yêu cầu, **không có bất kỳ file hoạt động nào của dự án bị chỉnh sửa**. Dưới đây là các phương án đề xuất để bạn xem xét:

### Phương án 1 (Thao tác người dùng - không cần sửa code):
- Đảm bảo đóng hoàn toàn các tab trình duyệt web ED22 đang mở thủ công bên ngoài trước khi chạy script.
- Chờ khoảng 1-2 phút hoặc chạy lại lệnh, khi không còn bị cảnh báo *"chiếm phiên trên máy này"*, trang sẽ tải lại trang MyProgress bình thường.

### Phương án 2 (Cải tiến code để tăng tính bền vững - cần bạn phê duyệt):
Nếu bạn cho phép chỉnh sửa, chúng ta có thể bổ sung cơ chế kiểm tra trạng thái điều hướng chắc chắn hơn:
1. Trong `goto_course` hoặc `open_progress`: Kiểm tra nếu sau khi điều hướng mà URL vẫn bị kẹt ở `#/home` hoặc chưa thấy `.myProgress__unitW`, tự động reload hoặc chờ Angular ổn định rồi điều hướng lại lần 2.
2. Tăng thời gian chờ ổn định sau khi click *"Login on This Device"* để Angular hoàn tất phiên trước khi chuyển trang.


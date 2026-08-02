# Báo cáo kỹ thuật cuối kỳ

> **Trạng thái:** khung tài liệu lập ở mốc KT1. Nội dung từng chương viết ở mốc Cuối kỳ, sau khi hệ thống hoàn thiện và đã chạy kiểm thử.

Mười chương dưới đây ánh xạ một-một với 10 tiêu chí rubric Cuối kỳ (`Prompt.md` mục 13). Cột **Nguồn** ghi rõ lấy nội dung từ đâu, để khi viết không phải dựng lại từ đầu.

## Mục lục

| Chương | Tiêu chí rubric | Nội dung sẽ viết | Nguồn |
|---|---|---|---|
| **1. Hoàn thiện chức năng** | #1 | Danh sách toàn bộ chức năng đã làm, đối chiếu với yêu cầu mục 3 và mục 8 đặc tả. Nêu rõ chức năng nào đã hoàn thiện, chức năng nào cắt bỏ và vì sao | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) mục 2 và 7; ảnh chụp màn hình hệ thống chạy thật |
| **2. Chất lượng kiến trúc và mã nguồn** | #2 | Ba nguyên tắc kiến trúc và cách chúng được cưỡng chế trong mã nguồn. Đặc biệt nhấn mạnh chiều phụ thuộc một hướng `services/` không import `ai/` — chứng minh bằng cách trích danh sách import | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) mục 6; mã nguồn `backend/app/` |
| **3. Chất lượng cơ sở dữ liệu** | #3 | Mô hình 18 bảng, các ràng buộc bắt buộc và hậu quả nếu thiếu, chỉ mục và lý do chọn, cơ chế sao lưu | [`erd.md`](erd.md); [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) mục 5 |
| **4. Chất lượng giao diện và trải nghiệm** | #4 | Ảnh chụp các màn hình chính theo từng vai trò. Cách xử lý thông báo lỗi tiếng Việt và xác nhận trước hành động hủy/xóa | Ảnh chụp màn hình; [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) mục 3 |
| **5. Chất lượng chức năng AI** | #5 | Ba chức năng AI: đầu vào, prompt, output schema, ví dụ kết quả thật. Kết quả 3 vòng tối ưu prompt kèm so sánh output trước và sau | [`ai_prompt_log.md`](ai_prompt_log.md); [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) mục 7; [`test_report.md`](test_report.md) ca 6–9 |
| **6. Bảo mật, riêng tư và đạo đức AI** | #6 | Hash mật khẩu, phân quyền hai lớp, quản lý khóa API, lọc dữ liệu cá nhân trước khi gửi lên AI, dòng cảnh báo bắt buộc, guardrail hai tầng | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) mục 4.1 và 7.6 |
| **7. Hiệu năng và độ ổn định** | #7 | Phân trang, chỉ mục, cache tóm tắt AI. Cơ chế xử lý lỗi AI và bằng chứng AI hỏng không làm sập hệ thống | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) mục 3 và 7.5; [`test_report.md`](test_report.md) ca 6 |
| **8. Triển khai và đóng gói** | #8 | Hướng dẫn cài đặt, biến môi trường, dữ liệu mẫu. Dockerfile nếu có | [`README.md`](../README.md) mục 5; `backend/.env.example` |
| **9. Báo cáo kỹ thuật đầy đủ** | #9 | Tổng hợp toàn bộ tài liệu thành một bản in được. Bao gồm bảng 10 sai khác so với đặc tả gốc kèm lý do | Toàn bộ `docs/` |
| **10. Thuyết trình và demo** | #10 | Kịch bản demo bám 5 luồng dữ liệu chính, thứ tự trình bày, dữ liệu mẫu cần chuẩn bị trước, phương án dự phòng nếu API AI lỗi lúc demo | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) mục 7.1; `database/seed_data.sql` |

## Lưu ý khi viết báo cáo

**Chương 6 phải tự viết, không để AI viết hộ mà không đọc lại.** `Prompt.md` mục 15 cảnh báo rõ điều này: đây là phần hội đồng thường hỏi trực tiếp khi bảo vệ. Cần nắm được **lý do thiết kế**, không chỉ nội dung — ví dụ trả lời được câu hỏi *"tại sao `disclaimer_vi` là hằng số trong mã nguồn thay vì lấy từ output của AI?"*

**Chương 2 và chương 9 cần trả lời được câu hỏi về các chỗ lệch đặc tả.** Bảng 10 sai khác ở mục 9 của [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) đã ghi sẵn lý do từng điểm. Hai điểm dễ bị hỏi nhất:

- **Bỏ trạng thái `rescheduled`** — vì đổi lịch là *sự kiện*, đã lưu ở `appointment_history`; vừa làm trạng thái vừa ghi lịch sử sẽ khiến một buổi hẹn sinh nhiều dòng và dễ đếm trùng doanh thu.
- **Chuyển `appointment_id` từ `invoices` xuống `invoice_items`** — vì mục 3.7 yêu cầu gộp nhiều lịch hẹn vào một hóa đơn, mà một cột đơn ở `invoices` chỉ diễn đạt được quan hệ 1-1. Đây là mâu thuẫn có sẵn trong đặc tả gốc.

**Chương 10 cần chuẩn bị phương án dự phòng.** Nếu API AI lỗi hoặc mất mạng lúc demo, hệ thống vẫn phải chạy được phần quản lý — đây chính là lúc chứng minh nguyên tắc "AI không phải nghiệp vụ lõi" một cách thuyết phục nhất.

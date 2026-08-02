# Đối chiếu rubric KT1

Bảng ánh xạ 10 tiêu chí chấm điểm mốc KT1 (`Prompt.md` mục 13) với vị trí cụ thể trong bộ tài liệu. Dùng bảng này để tự kiểm tra trước khi nộp, và để chỉ nhanh cho hội đồng khi được hỏi.

Cột **Trạng thái** chỉ được đánh ✅ sau khi đã mở file và xác nhận nội dung có thật ở đúng mục đó.

| # | Tiêu chí | File | Mục cụ thể | Trạng thái |
|---|---|---|---|---|
| 1 | Phân tích đúng bài toán | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) | Mục 1 — bối cảnh và ba vấn đề của cách làm thủ công; mục 1.1 nguyên tắc thiết kế; mục 1.2 bảng trong/ngoài phạm vi | ✅ |
| 2 | Yêu cầu chức năng đầy đủ | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) | Mục 2, tám tiểu mục 2.1–2.8 ứng với mục 3.1–3.8 đặc tả | ✅ |
| 3 | Yêu cầu phi chức năng | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) | Mục 3 — sáu nhóm, mỗi nhóm kèm **cách hiện thực cụ thể** chứ không chỉ chép lại yêu cầu | ✅ |
| 4 | Actor và use case | [`use_case.md`](use_case.md) · [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) | `use_case.md`: 5 actor, sơ đồ, 20 use case, đặc tả chi tiết 4 UC kèm 17 quy tắc nghiệp vụ. `phan_tich_thiet_ke.md` mục 4: phân quyền hai lớp và ma trận quyền 13 dòng | ✅ |
| 5 | Thiết kế cơ sở dữ liệu (ERD) | [`erd.mmd`](erd.mmd) · [`erd.md`](erd.md) · [`erd.png`](erd.png) · [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) | Sơ đồ 18 thực thể / 30 quan hệ / 30 khóa ngoại; `erd.md` giải thích 6 nhóm bảng, 5 ràng buộc kèm hậu quả nếu thiếu, 6 chỉ mục; `phan_tich_thiet_ke.md` mục 5 bảng 18 bảng đầy đủ trường | ✅ |
| 6 | Kiến trúc hệ thống | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) | Mục 6 — ba nguyên tắc nền, bảng công nghệ, cây thư mục, 12 biến môi trường | ✅ |
| 7 | Vị trí ứng dụng AI | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) | Mục 7.1 năm luồng dữ liệu, nêu rõ bước nào có AI và bước nào không; mục 6.1 nguyên tắc cô lập `services/` không import `ai/` | ✅ |
| 8 | Prompt và luồng gọi AI sơ bộ | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) | Mục 7.3 — ba chức năng AI, mỗi chức năng có system prompt, user prompt template và output schema JSON; mục 7.4 guardrail hai tầng; mục 7.5 bảng xử lý lỗi và giá trị dự phòng | ✅ |
| 9 | Minh chứng dùng AI trong phân tích thiết kế | [`ai_prompt_log.md`](ai_prompt_log.md) | Bảng 7 cột theo mẫu mục 11.2, **7 dòng** của phiên KT1. Trong đó 3 dòng ghi nhận sinh viên bác bỏ hoặc sửa đề xuất của AI, 2 dòng ghi AI phát hiện lỗi (một trong đặc tả gốc, một của chính AI) | ✅ |
| 10 | Tài liệu PTTK có cấu trúc và kế hoạch | [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) · [`README.md`](../README.md) | Tài liệu PTTK 9 mục có mục lục và liên kết chéo; `README.md` mục 7 bảng lộ trình 4 mốc kèm trạng thái | ✅ |

## Sản phẩm nộp mốc KT1

| File | Mô tả |
|---|---|
| `docs/phan_tich_thiet_ke.md` | Tài liệu phân tích & thiết kế, 9 mục |
| `docs/use_case.md` + `docs/use_case.png` | Actor, use case, sơ đồ |
| `docs/erd.mmd` + `docs/erd.md` + `docs/erd.png` | Thiết kế CSDL |
| `docs/ai_prompt_log.md` | Nhật ký sử dụng AI |
| `docs/test_report.md` | Khung báo cáo kiểm thử, 12 ca đã liệt kê |
| `docs/final_report.md` | Khung báo cáo cuối kỳ, mục lục 10 chương |
| `docs/rubric_kt1.md` | Tài liệu này |
| `README.md` | Hướng dẫn dự án |
| `backend/.env.example` | 12 biến môi trường, giá trị giả |
| Khung thư mục `backend/`, `frontend/`, `database/` | Theo `Prompt.md` mục 7.2 |

**Mã nguồn nghiệp vụ: chưa có** — đúng phạm vi mốc KT1. `Prompt.md` mục 14.3 yêu cầu không nhảy sang phần AI trước khi phần quản lý chạy ổn định, và mục 12 xác định KT1 là mốc tài liệu.

## Số liệu nhất quán toàn bộ tài liệu

Các con số dưới đây phải giống nhau ở mọi file nhắc tới. Dùng để rà soát nhanh khi sửa tài liệu về sau.

| Đại lượng | Giá trị |
|---|---|
| Số bảng CSDL | **18** (14 theo mục 6.1 đặc tả + 4 bảng thêm) |
| Số thực thể / quan hệ / khóa ngoại trong ERD | **18 / 30 / 30** |
| Số vai trò người dùng | **4** (`admin`, `receptionist`, `staff`, `owner`) |
| Số use case | **20** |
| Số chức năng AI | **3** |
| Số sai khác so với đặc tả gốc | **10** |
| Số biến môi trường | **12** |
| Số ca kiểm thử đã liệt kê | **12** |
| Số file test dự kiến | **7** |

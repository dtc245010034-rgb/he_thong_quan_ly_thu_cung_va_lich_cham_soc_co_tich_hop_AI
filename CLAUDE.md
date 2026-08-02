# CLAUDE.md

Hướng dẫn cho Claude Code khi làm việc trong dự án này.

## Dự án là gì

Đồ án môn học **Triển khai phần mềm** và **Ứng dụng AI**: hệ thống quản lý cửa hàng dịch vụ thú cưng, có tích hợp 3 chức năng AI tạo sinh. Đề bài gốc nằm ở [`Prompt.md`](Prompt.md) — **đây là nguồn yêu cầu, không được sửa**.

Sinh viên: `DTC245010034`. Ngôn ngữ làm việc và toàn bộ tài liệu: **tiếng Việt**.

## Đọc gì trước khi bắt đầu

Theo đúng thứ tự:

1. [`docs/superpowers/specs/2026-08-02-pet-care-system-design.md`](docs/superpowers/specs/2026-08-02-pet-care-system-design.md) — thiết kế đã duyệt cho toàn hệ thống
2. Kế hoạch của mốc đang làm trong `docs/superpowers/plans/`
3. `git log --oneline -20` — xem đã làm tới đâu

## Trạng thái hiện tại

| Mốc | Nhánh | Trạng thái |
|---|---|---|
| KT1 — Tài liệu PTTK | `kt1-tai-lieu-pttk` | ✅ Xong, 7 commit, đã push |
| KT2-A — Nền tảng | `kt2a-nen-tang` | ✅ Xong, 10 commit, 46 test xanh, đã push |
| **KT2-B — Nghiệp vụ lõi** | `kt2b-nghiep-vu-loi` | 🔨 **Đang làm** — kế hoạch xong, chưa chạy task nào |
| KT2-C — Tài chính & cổng | — | ⬜ Chưa lập kế hoạch |
| KT3 — Tích hợp AI | — | ⬜ Chưa lập kế hoạch |
| Cuối kỳ | — | ⬜ |

**Việc tiếp theo:** Task 1 của [`docs/superpowers/plans/2026-08-02-kt2b-nghiep-vu-loi.md`](docs/superpowers/plans/2026-08-02-kt2b-nghiep-vu-loi.md) — tầng service và phân quyền lớp 2.

Mỗi nhánh tách từ nhánh trước đó, không tách từ `master`. Khi mở PR nhớ chọn base là nhánh cha.

## Lệnh hay dùng

Python **không có** trong `PATH` của tiến trình chạy sẵn — phải gọi bằng đường dẫn đầy đủ:

```powershell
# Chạy test (từ thư mục gốc dự án)
venv\Scripts\python.exe -m pytest

# Chạy một file test
venv\Scripts\python.exe -m pytest backend/tests/test_auth.py

# Khởi tạo và nạp dữ liệu mẫu
venv\Scripts\python.exe -m flask --app backend.app.main init-db
venv\Scripts\python.exe -m flask --app backend.app.main seed-db

# Chạy ứng dụng
venv\Scripts\python.exe -m flask --app backend.app.main run
```

Môi trường: Python **3.14.6**, cài qua Python Manager của winget ở `%LOCALAPPDATA%\Python\bin`.

Tài khoản demo sau khi `seed-db`: `admin`, `letan`, `groomer1`, `groomer2`, `chunuoi1`, `chunuoi2` — mật khẩu đều là `demo1234`.

## Quy ước bắt buộc

**Quy trình.** Dùng bộ skill Superpowers ở `C:\vscode\skills`. Thứ tự: `brainstorming` → `writing-plans` → `executing-plans`. Khi viết mã: **`test-driven-development`, không có ngoại lệ** — viết test, chạy cho thấy nó **đỏ**, rồi mới viết mã. Bỏ bước xem test đỏ là không còn là TDD.

**Kiến trúc.** Ba ràng buộc không được vi phạm:

1. **`services/` KHÔNG được import `ai/`.** Đây là cách biến yêu cầu "AI sập thì hệ thống vẫn chạy" thành thứ kiểm chứng được. Kiểm tra: `Select-String -Path backend\app\services\*.py -Pattern "from backend.app.ai"` phải không ra kết quả.
2. **Logic nghiệp vụ nằm ở `services/`, không nằm trong route.** Scheduler ở KT3 chạy ngoài ngữ cảnh HTTP request nên không gọi lại được logic đặt trong route.
3. **Mọi hàm service công khai nhận tham số `current_user`** và tự lọc theo quyền sở hữu dữ liệu. Đây là phân quyền lớp 2 — decorator `require_role` chỉ là lớp 1 và không đủ.

**Mã nguồn.** Comment tiếng Việt, đủ để sinh viên **giải thích được khi bảo vệ** — `Prompt.md` mục 1 cấm viết kiểu hộp đen. Không mở rộng phạm vi ngoài đặc tả.

**Bảo mật.** Không bao giờ tạo `backend/.env` thật rồi để lại. Khóa API chỉ đọc từ biến môi trường, không lưu vào CSDL. Không commit `.env` hay `*.db`.

**Commit.** Message tiếng Việt mô tả *tại sao*, không chỉ *cái gì*. Kết thúc bằng:
```
Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
```
Message nhiều dòng phải ghi ra file rồi `git commit -F <file>` — here-string của PowerShell vỡ khi nội dung có dấu ngoặc kép.

## Cạm bẫy đã gặp

| Bẫy | Cách tránh |
|---|---|
| `Get-Content` của PowerShell 5.1 đọc file UTF-8 bằng bảng mã ANSI, làm hỏng tiếng Việt | Luôn thêm `-Encoding UTF8`, hoặc dùng công cụ đọc file thay vì PowerShell |
| `database/seed_data.sql` hỏng vì dấu `;` trong dòng chú thích | Hàm nạp cắt câu theo `;`. Không dùng dấu này ở bất kỳ đâu ngoài dấu kết câu |
| `Model.query.get()` sinh cảnh báo trên SQLAlchemy 2.x | Dùng `db.session.get(Model, id)` và `db.session.execute(db.select(...))` |
| Bảng có 2 khóa ngoại cùng trỏ về `users` | Phải chỉ định `foreign_keys=` cho từng quan hệ |

## Nhật ký AI — bắt buộc cập nhật

[`docs/ai_prompt_log.md`](docs/ai_prompt_log.md) là **minh chứng chấm điểm bắt buộc** (rubric KT1#9, KT2#9, KT3#4 và #9). Sau mỗi mốc phải ghi thêm dòng mới.

Cột "Đã kiểm chứng/chỉnh sửa" phải mô tả **hành động cụ thể của sinh viên** — đặc biệt là những lần sinh viên **bác bỏ hoặc sửa** đề xuất của AI. Đó là thứ phân biệt "dùng AI có kiểm soát" với "copy nguyên output", và chấm cao hơn hẳn.

KT3 yêu cầu **tối thiểu 3 vòng tối ưu prompt**, mỗi vòng một dòng riêng kèm so sánh output trước và sau.

## Điều KHÔNG được làm hộ sinh viên

`Prompt.md` mục 15 cảnh báo: **không để AI viết phần đánh giá đạo đức AI mà sinh viên không đọc lại** — hội đồng hỏi trực tiếp phần này khi bảo vệ. Khi làm tới mục đó, phải nhắc sinh viên tự đọc và tự nắm lý do thiết kế.

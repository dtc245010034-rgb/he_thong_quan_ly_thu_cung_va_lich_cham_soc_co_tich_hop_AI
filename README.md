# Hệ thống Quản lý Thú cưng & Lịch chăm sóc tích hợp AI

Đồ án môn học *Triển khai phần mềm* và *Ứng dụng AI*.

## 1. Giới thiệu

Hệ thống quản lý cho cửa hàng dịch vụ thú cưng: hồ sơ chủ nuôi và thú cưng, danh mục dịch vụ và bảng giá, đặt/đổi/hủy lịch spa–tắm–grooming có kiểm tra trùng giờ, hồ sơ chăm sóc, nhắc lịch tiêm phòng, hóa đơn, thanh toán và báo cáo doanh thu.

Bổ sung lên trên là một lớp AI tạo sinh làm ba việc: sinh tin nhắn nhắc lịch, tóm tắt hồ sơ chăm sóc, và trả lời câu hỏi chăm sóc thú cưng ở mức tham khảo.

> **Nguyên tắc xuyên suốt:** AI là lớp hỗ trợ nghiệp vụ, không phải nghiệp vụ lõi. Nếu dịch vụ AI sập, hết hạn mức hoặc bị tắt, thì đặt lịch, ghi hồ sơ, lập hóa đơn và thanh toán vẫn hoạt động bình thường. Nguyên tắc này được cưỡng chế bằng cấu trúc mã nguồn: tầng `services/` không import gì từ `ai/`.

> **AI không chẩn đoán bệnh và không thay thế bác sĩ thú y.** Mọi kết quả AI liên quan sức khỏe đều kèm dòng cảnh báo, và hệ thống chủ động từ chối tư vấn chuyên sâu khi phát hiện dấu hiệu bất thường.

## 2. Tính năng

**Nghiệp vụ quản lý**

- Quản lý chủ nuôi và thú cưng, có tìm kiếm theo tên/số điện thoại và xóa mềm
- Danh mục dịch vụ, bảng giá, gói dịch vụ combo, lưu lịch sử thay đổi giá
- Đặt / đổi / hủy lịch hẹn, **chống trùng khung giờ nhân viên**, hủy lịch bắt buộc có lý do
- Hồ sơ chăm sóc sau mỗi buổi hẹn, có trường cân nặng để theo dõi xu hướng
- Nhắc lịch tiêm phòng theo ngày đến hạn
- Hóa đơn từ một hoặc nhiều lịch hẹn, giảm giá, thanh toán từng phần
- Thống kê lượt dịch vụ, doanh thu theo thời gian / loại dịch vụ / nhân viên, tỉ lệ khách quay lại
- Bốn vai trò: Quản lý, Lễ tân, Nhân viên chăm sóc, Chủ nuôi (cổng tự phục vụ, chỉ đọc)

**Lớp AI**

- Sinh tin nhắn nhắc lịch chăm sóc và tiêm phòng, chạy tự động hằng ngày
- Tóm tắt hồ sơ chăm sóc, tự gắn cờ khi phát hiện dấu hiệu bất thường lặp lại
- Trả lời câu hỏi chăm sóc ở mức tham khảo, có guardrail hai tầng chặn tư vấn y tế chuyên sâu

## 3. Công nghệ

| Lớp | Lựa chọn |
|---|---|
| Backend | Flask + SQLAlchemy |
| Giao diện | Jinja2 + Bootstrap 5, render phía server |
| Biểu đồ | Chart.js (file tĩnh cục bộ) |
| CSDL | SQLite |
| Xác thực | Session cookie có hết hạn, mật khẩu hash bcrypt |
| Lập lịch | APScheduler `BackgroundScheduler` |
| AI | Gemini API qua lớp provider |
| Kiểm thử | pytest + SQLite in-memory |

## 4. Cấu trúc thư mục

```
├── backend/
│   ├── app/
│   │   ├── main.py          # app factory: đăng ký blueprint, db, scheduler
│   │   ├── config.py        # đọc .env, không hardcode key
│   │   ├── models/          # SQLAlchemy — 18 bảng
│   │   ├── services/        # logic nghiệp vụ thuần Python, không biết Flask request
│   │   ├── routers/         # blueprint Jinja mỏng: form → service → render
│   │   ├── auth/            # login session, decorator phân quyền
│   │   ├── schemas/         # kiểm tra dữ liệu đầu vào
│   │   ├── ai/              # client, 3 chức năng AI, guardrails, prompts/
│   │   └── scheduler.py     # job nhắc lịch hằng ngày
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── templates/           # Jinja2
│   └── static/              # Bootstrap, Chart.js, css
├── database/
│   └── seed_data.sql        # dữ liệu mẫu để demo
├── docs/                    # tài liệu — xem mục 6
└── README.md
```

## 5. Cài đặt và chạy

> **Trạng thái:** dự án đang ở mốc KT1 (phân tích & thiết kế). Mã nguồn được xây dựng từ KT2, nên các bước dưới đây áp dụng từ KT2 trở đi.

```bash
# 1. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Cài thư viện
pip install -r backend/requirements.txt

# 3. Tạo file cấu hình
copy backend\.env.example backend\.env      # Windows
# cp backend/.env.example backend/.env      # macOS / Linux
```

Mở `backend/.env` và điền `GEMINI_API_KEY`. Kiểm tra lại tên model đang khả dụng tại thời điểm chạy — giá trị `AI_MODEL` trong `.env.example` chỉ là gợi ý, danh mục model thay đổi theo thời gian.

> ⚠️ **Không bao giờ commit file `backend/.env` chứa khóa thật.** File này đã được `.gitignore` loại trừ. Chỉ commit `.env.example` với giá trị giả.

```bash
# 4. Khởi tạo CSDL và nạp dữ liệu mẫu
python -m backend.app.main --init-db
sqlite3 pet_care.db < database/seed_data.sql

# 5. Chạy ứng dụng
flask --app backend.app.main run
```

Mở trình duyệt tại `http://127.0.0.1:5000`.

```bash
# Chạy kiểm thử
pytest backend/tests -v
```

Toàn bộ test AI dùng dữ liệu giả lập, **không gọi API thật** — chạy được khi không có mạng và không tiêu tốn hạn mức.

## 6. Tài liệu

| File | Nội dung |
|---|---|
| [`docs/phan_tich_thiet_ke.md`](docs/phan_tich_thiet_ke.md) | Tài liệu phân tích & thiết kế chính: bài toán, yêu cầu chức năng và phi chức năng, phân quyền, CSDL, kiến trúc, lớp AI, kế hoạch kiểm thử, và bảng 10 sai khác so với đặc tả gốc |
| [`docs/use_case.md`](docs/use_case.md) | 5 actor, 20 use case, sơ đồ, và đặc tả chi tiết 4 use case phức tạp nhất |
| [`docs/use_case.png`](docs/use_case.png) | Ảnh render sơ đồ use case |
| [`docs/erd.md`](docs/erd.md) | Giải thích ERD: 6 nhóm bảng, ràng buộc dữ liệu, chỉ mục đề xuất, 4 bảng thêm và lý do |
| [`docs/erd.mmd`](docs/erd.mmd) | Sơ đồ ERD dạng Mermaid (18 thực thể, 30 quan hệ) |
| [`docs/erd.png`](docs/erd.png) | Ảnh render ERD |
| [`docs/ai_prompt_log.md`](docs/ai_prompt_log.md) | Nhật ký sử dụng AI xuyên suốt các mốc |
| [`docs/test_report.md`](docs/test_report.md) | Báo cáo kiểm thử — điền kết quả ở KT3 |
| [`docs/final_report.md`](docs/final_report.md) | Báo cáo kỹ thuật cuối kỳ — viết ở mốc Cuối kỳ |
| [`docs/rubric_kt1.md`](docs/rubric_kt1.md) | Đối chiếu 10 tiêu chí rubric KT1 với vị trí trong tài liệu |

## 7. Lộ trình

| Mốc | Nội dung | Trạng thái |
|---|---|---|
| **KT1** | Phân tích & thiết kế: tài liệu PTTK, use case, ERD, xác định vị trí AI, nhật ký AI | ✅ Hoàn thành |
| **KT2** | Models 18 bảng → xác thực và phân quyền hai lớp → CRUD chủ nuôi/thú cưng → dịch vụ và gói → lịch hẹn kèm chống trùng → hồ sơ chăm sóc → tiêm phòng → hóa đơn/thanh toán → thống kê → cổng chủ nuôi | ⬜ Chưa bắt đầu |
| **KT3** | Lớp gọi AI + 3 chức năng AI + guardrail + scheduler → tối thiểu 3 vòng tối ưu prompt → kiểm thử | ⬜ Chưa bắt đầu |
| **Cuối kỳ** | Rà soát bảo mật và đạo đức AI, đóng gói Docker, báo cáo kỹ thuật, kịch bản demo | ⬜ Chưa bắt đầu |

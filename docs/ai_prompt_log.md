# Nhật ký sử dụng AI

Tài liệu này ghi lại mọi lần sử dụng AI tạo sinh trong quá trình làm đồ án, theo mẫu `Prompt.md` mục 11.2. Đây là **minh chứng bắt buộc chấm điểm** (rubric KT1 tiêu chí 9, KT2 tiêu chí 9, KT3 tiêu chí 4 và 9).

## Quy ước ghi

- **Ghi ngay sau mỗi lần dùng AI**, không ghi hồi tố cuối kỳ. Ghi hồi tố sẽ mất chi tiết về những chỗ đã sửa lại kết quả của AI — mà đó lại là phần có giá trị nhất.
- Cột **Prompt (rút gọn)** ghi 1–2 câu tóm ý, không chép nguyên văn hàng nghìn ký tự.
- Cột **Đã kiểm chứng/chỉnh sửa** phải mô tả **hành động cụ thể của người làm**: đã đối chiếu với cái gì, đã sửa chỗ nào, đã bác bỏ đề xuất nào. Không ghi chung chung kiểu "đã kiểm tra".
- Cột **Người thực hiện** ghi mã sinh viên; thay bằng họ tên đầy đủ khi in nộp.

## Ý nghĩa các cột

| Cột | Nội dung |
|---|---|
| Ngày | Ngày thực hiện |
| Giai đoạn | KT1 / KT2 / KT3 / Cuối kỳ |
| Mục đích | Dùng AI để làm gì |
| Prompt (rút gọn) | Tóm tắt yêu cầu đã đưa cho AI |
| Phản hồi AI (tóm tắt) | AI trả về gì |
| Đã kiểm chứng/chỉnh sửa | Người làm đã đối chiếu, sửa, hoặc bác bỏ những gì |
| Người thực hiện | Mã sinh viên |

---

## Bảng nhật ký

| Ngày | Giai đoạn | Mục đích | Prompt (rút gọn) | Phản hồi AI (tóm tắt) | Đã kiểm chứng/chỉnh sửa | Người thực hiện |
|---|---|---|---|---|---|---|
| 2026-08-02 | KT1 | Phân tích đặc tả, xác định phạm vi hai hạng mục tùy chọn | Đọc `Prompt.md`, xác định phần nào bắt buộc và phần nào mục 15 cho phép bỏ | AI khuyến nghị **bỏ cả hai** phần mở rộng (cổng chủ nuôi tự phục vụ và gói dịch vụ) để giảm tải, lập luận rằng cả hai đều nằm ngoài lõi bắt buộc | **Bác bỏ khuyến nghị.** Quyết định giữ cả hai vì muốn đồ án đầy đủ hơn. Yêu cầu AI thiết kế sao cho hai phần này tách module rõ để cắt được nếu deadline gấp | DTC245010034 |
| 2026-08-02 | KT1 | Chọn công nghệ frontend | So sánh Jinja2, React SPA, và phương án lai; nêu chi phí và rủi ro từng hướng | AI phân tích ba hướng, ban đầu khuyến nghị Jinja2 vì rẻ nhất và an toàn nhất khi bảo vệ | **Đổi lựa chọn 3 lần trước khi chốt.** Ban đầu chọn phương án lai; sau đó yêu cầu AI phân tích lại React SPA; đối chiếu 40 tiêu chí rubric mục 13 thì thấy không tiêu chí nào thưởng điểm cho SPA, nên chốt Jinja2 | DTC245010034 |
| 2026-08-02 | KT1 | Kiểm tra cấu trúc thư mục có buộc phải lệch mục 7.2 không | Cây thư mục mục 7.2 giả định frontend tách riêng; hỏi cách xử lý khi chọn Jinja2 | AI đề xuất **bỏ hẳn hai thư mục `backend/` và `frontend/`**, dùng cấu trúc phẳng vì cho rằng `frontend/` sẽ thành thư mục rỗng vô nghĩa | **Phản đối đề xuất** vì muốn bám đặc tả. Sau khi bị phản đối, AI đưa ra phương án thứ ba: giữ nguyên cây 7.2, cho `frontend/` chứa `templates/` và `static/`, Flask trỏ tới bằng một dòng cấu hình. **Phương án cuối cùng chỉ có được nhờ phản đối này** | DTC245010034 |
| 2026-08-02 | KT1 | Rà soát mô hình dữ liệu mục 6.1 trước khi vẽ ERD | Đối chiếu 14 bảng mục 6.1 với các yêu cầu chức năng mục 3 xem có thiếu gì không | AI phát hiện **mâu thuẫn trong chính đặc tả gốc**: mục 3.7 yêu cầu lập hóa đơn từ *"1 hoặc nhiều lịch hẹn"* nhưng mục 6.1 chỉ cho `invoices` một cột `appointment_id`, tức quan hệ 1-1, không gộp được nhiều lịch hẹn | Đọc lại mục 3.7 và 6.1, **xác nhận mâu thuẫn có thật**. Duyệt phương án chuyển `appointment_id` xuống `invoice_items` và cho phép NULL. Yêu cầu ghi vào mục "Sai khác so với đặc tả" để trả lời được khi bảo vệ | DTC245010034 |
| 2026-08-02 | KT1 | Tự rà soát tài liệu thiết kế sau khi viết xong | Yêu cầu AI đọc lại tài liệu vừa viết, tìm placeholder, mâu thuẫn nội bộ, chỗ diễn đạt mơ hồ | AI **tự phát hiện ba lỗi của chính mình**: (1) đếm sai số bảng mục 6.1 — nói 13 trong khi thực tế là 14, làm tổng số bảng sai; (2) công thức chia giá gói dịch vụ mơ hồ khi số lượng lớn hơn 1 và không xử lý làm tròn; (3) một quan hệ trong sơ đồ ERD bị vẽ ngược chiều | Đối chiếu lại bảng mục 6.1, **đếm tay xác nhận đúng 14 bảng** nên tổng là 18 chứ không phải 17. Duyệt cả ba sửa đổi trước khi commit | DTC245010034 |
| 2026-08-02 | KT1 | Lập kế hoạch triển khai chi tiết cho mốc KT1 | Chia công việc KT1 thành các task nhỏ, mỗi task có bước kiểm chứng đếm được | AI chia 7 task, mỗi task một commit. Tự rà soát kế hoạch và phát hiện thêm ba chỗ không nhất quán: số quan hệ ERD ghi 30 nhưng đếm thực tế 29 (thiếu quan hệ cho khóa ngoại `created_by`); bảng tổng kết ghi 8 file nhưng liệt kê 9; sơ đồ ERD trong kế hoạch khác sơ đồ trong tài liệu thiết kế | Kiểm tra lại bằng lệnh đếm tự động: xác nhận sau khi sửa thì 18 thực thể, 30 quan hệ, 30 khóa ngoại **khớp nhau**. Duyệt kế hoạch | DTC245010034 |
| 2026-08-02 | KT1 | Sinh sơ đồ use case | Vẽ sơ đồ 20 use case cho 5 actor bằng Mermaid | Bản đầu tiên **render ra sai**: chữ tiếng Việt bị hỏng mã và bố cục rối do dồn 20 use case vào một khối duy nhất, đường nối cắt chéo khắp sơ đồ | Yêu cầu sửa. AI xác định nguyên nhân hỏng mã là do PowerShell đọc file UTF-8 bằng bảng mã ANSI, và bố cục hỏng do thiếu phân nhóm. Bản sửa nhóm use case theo lĩnh vực nghiệp vụ, render lại và **kiểm tra bằng mắt trên ảnh xuất ra** trước khi duyệt | DTC245010034 |

---

## Ghi chú cho các mốc sau

- **KT2:** ghi lại mỗi lần dùng AI sinh mã nguồn (models, phân quyền, chống trùng lịch, tính hóa đơn). Nêu rõ chỗ nào phải sửa lại vì AI viết sai hoặc phức tạp hóa.
- **KT3:** rubric tiêu chí 4 yêu cầu **tối thiểu 3 vòng tối ưu prompt**. Mỗi vòng ghi một dòng riêng, kèm so sánh output trước và sau. Rubric tiêu chí 9 yêu cầu ghi lại việc dùng AI để review mã nguồn — nêu rõ AI phát hiện lỗi gì và đã refactor những gì.
- **Cuối kỳ:** `Prompt.md` mục 15 cảnh báo **không được để AI viết hộ phần đánh giá đạo đức AI mà không đọc lại**, vì hội đồng thường hỏi trực tiếp phần này khi bảo vệ. Đọc kỹ mục 7.6 của [`phan_tich_thiet_ke.md`](phan_tich_thiet_ke.md) và tự nắm được **lý do thiết kế**, không chỉ nội dung.

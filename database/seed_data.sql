-- Dữ liệu mẫu cho demo.
--
-- Mọi tài khoản dùng chung mật khẩu: demo1234
-- Chuỗi hash dưới đây là bcrypt thật, sinh bằng hàm hash_password trong
-- backend/app/auth/password.py.
--
-- LƯU Ý: không được dùng dấu chấm phẩy ở BẤT KỲ đâu trong file này ngoài dấu
-- kết thúc câu lệnh — kể cả trong chú thích. Hàm nạp ở backend/tests/test_seed.py
-- tách câu lệnh theo dấu này, nên một dấu chấm phẩy lạc trong chú thích cũng
-- làm phần còn lại của dòng bị hiểu thành câu lệnh SQL và gây lỗi cú pháp.

-- ============================================================
-- Chủ nuôi (6)
-- ============================================================
INSERT INTO owners (id, full_name, phone, email, address, is_deleted, created_at) VALUES
 (1, 'Nguyễn Văn An',   '0901000001', 'an.nguyen@example.com',   ' 12 Lê Lợi, TP Thái Nguyên',      0, '2026-01-05 09:00:00'),
 (2, 'Trần Thị Bình',   '0901000002', 'binh.tran@example.com',   '45 Hoàng Văn Thụ, TP Thái Nguyên', 0, '2026-01-12 10:30:00'),
 (3, 'Lê Minh Cường',   '0901000003', 'cuong.le@example.com',    '78 Phan Đình Phùng, TP Thái Nguyên', 0, '2026-02-02 14:15:00'),
 (4, 'Phạm Thu Dung',   '0901000004', 'dung.pham@example.com',   '9 Bắc Kạn, TP Thái Nguyên',        0, '2026-02-20 08:45:00'),
 (5, 'Hoàng Văn Em',    '0901000005', 'em.hoang@example.com',    '156 Cách Mạng Tháng 8, TP Thái Nguyên', 0, '2026-03-01 16:00:00'),
 (6, 'Vũ Thị Giang',    '0901000006', 'giang.vu@example.com',    '23 Quang Trung, TP Thái Nguyên',   0, '2026-03-18 11:20:00');

-- ============================================================
-- Tài khoản (6) — đủ 4 vai trò.
-- Hai tài khoản owner trỏ về hai chủ nuôi KHÁC NHAU, cần cho ca kiểm thử
-- truy cập chéo dữ liệu ở KT2-B.
-- ============================================================
INSERT INTO users (id, username, password_hash, role, full_name, owner_id, is_active, created_at) VALUES
 (1, 'admin',    '$2b$12$JYfhp847aoB3fmUDJeqf9.s0EVN/OCISsd4N6vBoyXbTtLJBM2jOW', 'ADMIN',        'Quản lý cửa hàng',   NULL, 1, '2026-01-01 08:00:00'),
 (2, 'letan',    '$2b$12$JYfhp847aoB3fmUDJeqf9.s0EVN/OCISsd4N6vBoyXbTtLJBM2jOW', 'RECEPTIONIST', 'Đỗ Thị Hạnh',        NULL, 1, '2026-01-01 08:00:00'),
 (3, 'groomer1', '$2b$12$JYfhp847aoB3fmUDJeqf9.s0EVN/OCISsd4N6vBoyXbTtLJBM2jOW', 'STAFF',        'Ngô Văn Khoa',       NULL, 1, '2026-01-01 08:00:00'),
 (4, 'groomer2', '$2b$12$JYfhp847aoB3fmUDJeqf9.s0EVN/OCISsd4N6vBoyXbTtLJBM2jOW', 'STAFF',        'Bùi Thị Lan',        NULL, 1, '2026-01-01 08:00:00'),
 (5, 'chunuoi1', '$2b$12$JYfhp847aoB3fmUDJeqf9.s0EVN/OCISsd4N6vBoyXbTtLJBM2jOW', 'OWNER',        'Nguyễn Văn An',      1,    1, '2026-01-06 09:00:00'),
 (6, 'chunuoi2', '$2b$12$JYfhp847aoB3fmUDJeqf9.s0EVN/OCISsd4N6vBoyXbTtLJBM2jOW', 'OWNER',        'Trần Thị Bình',      2,    1, '2026-01-13 09:00:00');

-- ============================================================
-- Thú cưng (9)
-- Bé số 3 (Nâu) là ca sụt cân liên tục — xem khối care_records.
-- ============================================================
INSERT INTO pets (id, owner_id, name, species, breed, gender, birth_date, weight, color, notes, is_deleted, created_at) VALUES
 (1, 1, 'Mực',   'chó', 'Phú Quốc',      'đực', '2023-04-10', 18.50, 'đen',       'Sợ tiếng máy sấy, cần dỗ trước khi sấy', 0, '2026-01-05 09:10:00'),
 (2, 1, 'Vàng',  'chó', 'Cỏ',            'cái', '2024-06-22', 12.00, 'vàng',      'Hiền, dễ chăm',                          0, '2026-01-05 09:15:00'),
 (3, 2, 'Nâu',   'chó', 'Poodle',        'đực', '2022-09-15',  7.00, 'nâu',       'Dị ứng thức ăn hạt gà, theo dõi cân nặng', 0, '2026-01-12 10:40:00'),
 (4, 2, 'Miu',   'mèo', 'Anh lông ngắn', 'cái', '2023-11-30',  4.20, 'xám',       'Cào mạnh khi cắt móng',                  0, '2026-01-12 10:45:00'),
 (5, 3, 'Bông',  'chó', 'Bichon',        'cái', '2024-01-08',  5.80, 'trắng',     'Lông dễ rối, cần chải kỹ',               0, '2026-02-02 14:25:00'),
 (6, 3, 'Tí',    'mèo', 'Ta',            'đực', '2023-07-19',  3.90, 'vàng vằn',  'Nhút nhát',                              0, '2026-02-02 14:30:00'),
 (7, 4, 'Kem',   'chó', 'Corgi',         'cái', '2023-02-14', 11.30, 'nâu trắng', 'Da nhạy cảm, dùng sữa tắm dịu nhẹ',      0, '2026-02-20 08:55:00'),
 (8, 5, 'Lu',    'chó', 'Husky',         'đực', '2022-12-05', 24.00, 'đen trắng', 'Rụng lông nhiều theo mùa',               0, '2026-03-01 16:10:00'),
 (9, 6, 'Nhung', 'mèo', 'Ba Tư',         'cái', '2024-03-27',  3.50, 'trắng kem', 'Lông dài, dễ vón cục',                   0, '2026-03-18 11:30:00');

-- ============================================================
-- Dịch vụ (6) — trải đủ 4 danh mục
-- ============================================================
INSERT INTO services (id, name, category, price, duration_minutes, description, is_active, created_at) VALUES
 (1, 'Tắm cơ bản',        'TAM',      150000, 45,  'Tắm, sấy khô, vệ sinh tai',                 1, '2026-01-01 08:00:00'),
 (2, 'Tắm dưỡng lông',    'TAM',      220000, 60,  'Tắm kèm dầu xả dưỡng lông',                 1, '2026-01-01 08:00:00'),
 (3, 'Spa thư giãn',      'SPA',      350000, 90,  'Massage, ngâm khoáng, dưỡng da',            1, '2026-01-01 08:00:00'),
 (4, 'Cắt tỉa tạo kiểu',  'GROOMING', 280000, 75,  'Cắt tỉa lông theo kiểu, tỉa móng',          1, '2026-01-01 08:00:00'),
 (5, 'Cắt móng, vệ sinh', 'GROOMING', 80000,  20,  'Cắt móng, vệ sinh tai mắt',                 1, '2026-01-01 08:00:00'),
 (6, 'Trông giữ theo ngày','KHAC',    200000, 480, 'Trông giữ trong ngày, có cho ăn',           1, '2026-01-01 08:00:00');

-- ============================================================
-- Gói dịch vụ (2) và các dịch vụ trong gói
-- Gói luôn rẻ hơn tổng giá mua lẻ.
-- ============================================================
INSERT INTO service_packages (id, name, description, package_price, is_active, created_at) VALUES
 (1, 'Combo sạch đẹp',   'Tắm cơ bản kèm cắt tỉa tạo kiểu',        380000, 1, '2026-01-01 08:00:00'),
 (2, 'Combo chăm sóc kỹ','Tắm dưỡng lông, spa thư giãn, cắt móng', 580000, 1, '2026-01-01 08:00:00');

INSERT INTO package_items (id, package_id, service_id, quantity) VALUES
 (1, 1, 1, 1),
 (2, 1, 4, 1),
 (3, 2, 2, 1),
 (4, 2, 3, 1),
 (5, 2, 5, 1);

-- ============================================================
-- Lịch sử giá — chứng minh yêu cầu mục 3.3 hoạt động
-- ============================================================
INSERT INTO service_price_history (id, service_id, old_price, new_price, changed_by, changed_at) VALUES
 (1, 1, 130000, 150000, 1, '2026-02-01 09:00:00'),
 (2, 4, 250000, 280000, 1, '2026-03-01 09:00:00');

-- ============================================================
-- Lịch hẹn (10) — trải đủ 4 trạng thái
-- ============================================================
INSERT INTO appointments (id, pet_id, service_id, staff_id, scheduled_at, ends_at, status, notes, created_by, created_at) VALUES
 (1,  3, 1, 3, '2026-04-05 09:00:00', '2026-04-05 09:45:00', 'COMPLETED', 'Khách quen',              2, '2026-04-01 10:00:00'),
 (2,  3, 1, 3, '2026-05-10 09:00:00', '2026-05-10 09:45:00', 'COMPLETED', NULL,                      2, '2026-05-05 10:00:00'),
 (3,  3, 4, 4, '2026-06-14 14:00:00', '2026-06-14 15:15:00', 'COMPLETED', 'Cắt ngắn cho mùa hè',     2, '2026-06-10 09:00:00'),
 (4,  3, 1, 3, '2026-07-19 09:00:00', '2026-07-19 09:45:00', 'COMPLETED', 'Chủ nuôi lo bé sút cân',  2, '2026-07-15 08:30:00'),
 (5,  1, 2, 3, '2026-06-20 10:00:00', '2026-06-20 11:00:00', 'COMPLETED', NULL,                      2, '2026-06-15 09:00:00'),
 (6,  4, 5, 4, '2026-07-02 15:00:00', '2026-07-02 15:20:00', 'COMPLETED', NULL,                      2, '2026-06-28 14:00:00'),
 (7,  7, 3, 4, '2026-08-08 09:00:00', '2026-08-08 10:30:00', 'CONFIRMED', 'Da nhạy cảm, dùng sữa dịu', 2, '2026-08-01 09:00:00'),
 (8,  8, 1, 3, '2026-08-09 14:00:00', '2026-08-09 14:45:00', 'PENDING',   NULL,                      2, '2026-08-02 08:00:00'),
 (9,  5, 4, 4, '2026-08-12 10:00:00', '2026-08-12 11:15:00', 'PENDING',   NULL,                      2, '2026-08-02 08:10:00'),
 (10, 9, 2, 3, '2026-07-25 09:00:00', '2026-07-25 10:00:00', 'CANCELLED', 'Thú cưng ốm',             2, '2026-07-20 09:00:00');

-- Lịch sử đổi lịch của lịch hẹn số 7
INSERT INTO appointment_history (id, appointment_id, old_time, new_time, reason, changed_by, changed_at) VALUES
 (1, 7, '2026-08-06 09:00:00', '2026-08-08 09:00:00', 'khach_yeu_cau', 2, '2026-08-03 10:15:00');

-- ============================================================
-- Hồ sơ chăm sóc — trải 4 tháng
--
-- Bé số 3 (Nâu) có 4 bản ghi cân nặng GIẢM LIÊN TỤC: 8.5 -> 8.1 -> 7.6 -> 7.0
-- Đây là dữ liệu để chức năng tóm tắt AI ở KT3 bật cờ cảnh báo khi demo.
-- ============================================================
INSERT INTO care_records (id, pet_id, appointment_id, staff_id, record_date, weight_at_visit, condition_notes, treatment_notes, next_recommendation, created_at) VALUES
 (1, 3, 1, 3, '2026-04-05', 8.50, 'Da lông bình thường, bé linh hoạt',            'Tắm, sấy, vệ sinh tai',        'Duy trì lịch tắm hàng tháng',                    '2026-04-05 09:50:00'),
 (2, 3, 2, 3, '2026-05-10', 8.10, 'Lông hơi khô, bé ăn ít hơn theo lời chủ',      'Tắm, dưỡng lông nhẹ',          'Theo dõi khẩu phần ăn',                          '2026-05-10 09:50:00'),
 (3, 3, 3, 4, '2026-06-14', 7.60, 'Lông xơ, da khô nhẹ, bé kém hoạt bát hơn',     'Cắt tỉa ngắn, dưỡng da',       'Nên cho bé khám dinh dưỡng',                     '2026-06-14 15:20:00'),
 (4, 3, 4, 3, '2026-07-19', 7.00, 'Tiếp tục sút cân, bụng hóp, lông rụng nhiều',  'Tắm nhẹ, không dùng hóa chất', 'Khuyến nghị đưa bé đi khám bác sĩ thú y sớm',    '2026-07-19 09:50:00'),
 (5, 1, 5, 3, '2026-06-20', 18.70, 'Da lông tốt, bé khỏe',                        'Tắm dưỡng lông',               'Giữ nguyên chế độ chăm sóc',                     '2026-06-20 11:05:00'),
 (6, 4, 6, 4, '2026-07-02', 4.30,  'Móng dài, tai sạch',                          'Cắt móng, vệ sinh tai',        'Cắt móng lại sau 6 tuần',                        '2026-07-02 15:25:00');

-- ============================================================
-- Lịch tiêm phòng — có mũi đã tiêm, sắp đến hạn, và quá hạn
-- Trạng thái sắp đến hạn / quá hạn KHÔNG lưu ở đây, tính lúc truy vấn.
-- ============================================================
INSERT INTO vaccination_schedules (id, pet_id, vaccine_name, last_date, next_due_date, is_done, created_at) VALUES
 (1, 1, 'Dại',           '2025-08-10', '2026-08-10', 0, '2026-01-05 09:20:00'),
 (2, 1, '7 bệnh',        '2025-06-01', '2026-06-01', 1, '2026-01-05 09:22:00'),
 (3, 3, 'Dại',           '2025-07-15', '2026-07-15', 0, '2026-01-12 10:50:00'),
 (4, 4, 'Bệnh dại mèo',  '2025-12-20', '2026-12-20', 0, '2026-01-12 10:52:00'),
 (5, 7, 'Dại',           '2026-01-30', '2027-01-30', 0, '2026-02-20 09:00:00'),
 (6, 8, '7 bệnh',        '2025-09-05', '2026-09-05', 0, '2026-03-01 16:20:00');

-- ============================================================
-- Hóa đơn — một hóa đơn GỘP HAI lịch hẹn, chứng minh yêu cầu mục 3.7
-- ============================================================
INSERT INTO invoices (id, owner_id, invoice_number, issue_date, discount_amount, total_amount, payment_status, created_by, created_at) VALUES
 (1, 2, 'HD-2026-0001', '2026-06-14', 0,     430000, 'DA_THANH_TOAN',   2, '2026-06-14 15:30:00'),
 (2, 1, 'HD-2026-0002', '2026-06-20', 20000, 200000, 'MOT_PHAN',        2, '2026-06-20 11:10:00'),
 (3, 2, 'HD-2026-0003', '2026-07-19', 0,     150000, 'CHUA_THANH_TOAN', 2, '2026-07-19 09:55:00');

-- Hóa đơn 1 gộp lịch hẹn 2 và 3 của cùng chủ nuôi
INSERT INTO invoice_items (id, invoice_id, service_id, appointment_id, package_id, quantity, unit_price, line_total) VALUES
 (1, 1, 1, 2, NULL, 1, 150000, 150000),
 (2, 1, 4, 3, NULL, 1, 280000, 280000),
 (3, 2, 2, 5, NULL, 1, 220000, 220000),
 (4, 3, 1, 4, NULL, 1, 150000, 150000);

INSERT INTO payments (id, invoice_id, amount, payment_date, method, received_by, created_at) VALUES
 (1, 1, 430000, '2026-06-14', 'tien_mat',     2, '2026-06-14 15:35:00'),
 (2, 2, 100000, '2026-06-20', 'chuyen_khoan', 2, '2026-06-20 11:15:00');

-- ============================================================
-- Cấu hình ứng dụng — KHÓA API KHÔNG BAO GIỜ LƯU Ở ĐÂY
-- ============================================================
INSERT INTO app_settings (key, value, updated_by, updated_at) VALUES
 ('ai_enabled', 'true',             1, '2026-01-01 08:00:00'),
 ('ai_model',   'gemini-1.5-flash', 1, '2026-01-01 08:00:00');

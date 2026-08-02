# KT2-B — Nghiệp vụ lõi: Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dựng toàn bộ nghiệp vụ quản lý: CRUD chủ nuôi và thú cưng kèm **phân quyền lớp 2**, danh mục dịch vụ và gói, đặt/đổi/hủy lịch kèm **chống trùng lịch**, hồ sơ chăm sóc, và nhắc tiêm phòng.

**Architecture:** Toàn bộ quy tắc nghiệp vụ nằm ở `backend/app/services/`. Route chỉ nhận form, gọi service, render. Mọi hàm service nhận tham số `current_user` và tự lọc dữ liệu theo quyền sở hữu — đây là lớp phân quyền thứ hai mà decorator không làm được.

**Tech Stack:** Như KT2-A. Không thêm thư viện mới.

## Global Constraints

- **Nguồn sự thật:** [`docs/phan_tich_thiet_ke.md`](../../phan_tich_thiet_ke.md) và [spec thiết kế](../specs/2026-08-02-pet-care-system-design.md). Phát hiện tài liệu sai thì dừng lại báo, không tự sửa lệch.
- **TDD bắt buộc.** REQUIRED SUB-SKILL: `superpowers:test-driven-development`. Mỗi task có bước chạy test để **thấy nó đỏ** trước khi viết mã — không được bỏ qua.
- **`services/` KHÔNG được import `ai/`.** Ràng buộc kiến trúc xuyên suốt; Task 10 có lệnh kiểm tra tự động.
- **Mọi hàm service nhận `current_user`** và tự lọc theo quyền sở hữu. Không có ngoại lệ.
- **Không đụng tới `ai/`, hóa đơn, thanh toán, thống kê, cổng chủ nuôi** — những phần đó thuộc KT2-C và KT3.
- **Thông báo lỗi bằng tiếng Việt**, nêu rõ nguyên nhân và cách khắc phục.
- **Mỗi task kết thúc bằng 1 commit**, message tiếng Việt, kết thúc bằng `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- **Lệnh chạy:** `venv\Scripts\python.exe -m pytest` từ thư mục gốc dự án.

### Điều kiện tiên quyết

KT2-A đã xong: 46 test xanh, 18 bảng, đăng nhập và `require_role` hoạt động. Kiểm tra bằng `venv\Scripts\python.exe -m pytest` trước khi bắt đầu.

### Sai khác so với tài liệu thiết kế

| Sai khác | Lý do |
|---|---|
| Thêm `backend/app/services/errors.py` | Tầng service cần báo lỗi nghiệp vụ lên route mà không phụ thuộc Flask. Định nghĩa 3 lớp ngoại lệ riêng, route dịch sang mã HTTP. Nếu service `abort(403)` trực tiếp thì nó phụ thuộc Flask và không test được ngoài ngữ cảnh request |

---

## File Structure

| File | Trách nhiệm | Task |
|---|---|---|
| `backend/app/services/errors.py` | 3 lớp ngoại lệ nghiệp vụ | 1 |
| `backend/app/services/owner_service.py` | CRUD chủ nuôi + lọc quyền sở hữu | 1 |
| `backend/app/services/pet_service.py` | CRUD thú cưng + lọc quyền sở hữu | 1 |
| `backend/app/services/activity_log_service.py` | Ghi nhật ký thao tác | 1 |
| `backend/app/routers/owners.py`, `pets.py` | Blueprint CRUD | 2 |
| `frontend/templates/owners/`, `pets/` | Giao diện danh sách và biểu mẫu | 2 |
| `backend/app/services/catalog_service.py` | Dịch vụ, gói, ghi lịch sử giá | 3 |
| `backend/app/routers/catalog.py` | Blueprint danh mục | 3 |
| `backend/app/services/appointment_service.py` | Đặt lịch, chống trùng | 4 |
| — (bổ sung cùng file) | Đổi lịch, hủy lịch | 5 |
| `backend/app/routers/appointments.py` | Blueprint lịch hẹn | 6 |
| `backend/app/services/care_record_service.py` | Hồ sơ chăm sóc | 7 |
| `backend/app/services/vaccination_service.py` | Lịch tiêm, tính trạng thái | 8 |
| `backend/app/routers/home.py` | Trang chủ, điều hướng theo vai trò | 9 |

---

### Task 1: Tầng service và phân quyền lớp 2

**Đây là task quan trọng nhất của KT2-B.** Lớp phân quyền thứ hai là thứ chặn lỗ hổng đổi `?pet_id=5` thành `?pet_id=6` để xem hồ sơ nhà khác. Decorator `require_role` ở KT2-A không làm được việc này vì nó chỉ biết vai trò, không biết bản ghi đang truy cập thuộc về ai.

**Files:**
- Create: `backend/app/services/__init__.py`, `errors.py`, `owner_service.py`, `pet_service.py`, `activity_log_service.py`
- Create: `backend/tests/test_owner_service.py`, `backend/tests/test_pet_service.py`
- Delete: `backend/app/services/.gitkeep`

**Interfaces:**
- Produces:
  - `errors.py`: `QuyenTruyCapBiTuChoi(Exception)`, `DuLieuKhongHopLe(Exception)`, `TrungLichHen(Exception)`
  - `owner_service.danh_sach(current_user, tu_khoa=None) -> list[Owner]`
  - `owner_service.lay_theo_id(owner_id, current_user) -> Owner`
  - `owner_service.tao(du_lieu: dict, current_user) -> Owner`
  - `owner_service.cap_nhat(owner_id, du_lieu: dict, current_user) -> Owner`
  - `owner_service.xoa_mem(owner_id, current_user) -> dict` (trả số bản ghi liên quan)
  - `pet_service.danh_sach(current_user, owner_id=None, tu_khoa=None) -> list[Pet]`
  - `pet_service.lay_theo_id(pet_id, current_user) -> Pet`
  - `pet_service.tao / cap_nhat / xoa_mem` — cùng dạng chữ ký
  - `activity_log_service.ghi(current_user, action, entity_type, entity_id, detail=None)`

- [ ] **Step 1: Viết test đỏ cho `owner_service`**

`backend/tests/test_owner_service.py`:

```python
"""Kiểm thử service chủ nuôi, đặc biệt là phân quyền lớp 2."""
import pytest

from backend.app.models import ActivityLog, Owner, Pet, User, UserRole
from backend.app.services import owner_service
from backend.app.services.errors import QuyenTruyCapBiTuChoi


@pytest.fixture
def du_lieu(session):
    """Hai chủ nuôi, mỗi người một tài khoản owner riêng, cộng một lễ tân."""
    chu_a = Owner(full_name='Chủ A', phone='0900000001')
    chu_b = Owner(full_name='Chủ B', phone='0900000002')
    session.add_all([chu_a, chu_b])
    session.flush()

    tk_a = User(username='a', password_hash='h', role=UserRole.OWNER,
                owner_id=chu_a.id)
    tk_b = User(username='b', password_hash='h', role=UserRole.OWNER,
                owner_id=chu_b.id)
    le_tan = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add_all([tk_a, tk_b, le_tan])
    session.flush()

    pet_a = Pet(owner_id=chu_a.id, name='Mực', species='chó')
    session.add(pet_a)
    session.flush()
    return {'chu_a': chu_a, 'chu_b': chu_b, 'tk_a': tk_a, 'tk_b': tk_b,
            'le_tan': le_tan, 'pet_a': pet_a}


def test_le_tan_xem_duoc_tat_ca_chu_nuoi(session, du_lieu):
    ds = owner_service.danh_sach(du_lieu['le_tan'])
    assert len(ds) == 2


def test_chu_nuoi_chi_xem_duoc_ho_so_cua_minh(session, du_lieu):
    """Lớp 2: vai trò owner hợp lệ nhưng chỉ thấy dữ liệu của mình."""
    ds = owner_service.danh_sach(du_lieu['tk_a'])
    assert [o.full_name for o in ds] == ['Chủ A']


def test_chu_nuoi_a_truy_cap_ho_so_chu_b_bi_tu_choi(session, du_lieu):
    """LỖ HỔNG PHẢI CHẶN: đổi tham số id để xem hồ sơ nhà khác."""
    with pytest.raises(QuyenTruyCapBiTuChoi):
        owner_service.lay_theo_id(du_lieu['chu_b'].id, du_lieu['tk_a'])


def test_chu_nuoi_khong_duoc_tao_chu_nuoi_moi(session, du_lieu):
    with pytest.raises(QuyenTruyCapBiTuChoi):
        owner_service.tao({'full_name': 'X', 'phone': '0900000009'},
                          du_lieu['tk_a'])


def test_le_tan_tao_chu_nuoi_va_ghi_nhat_ky(session, du_lieu):
    chu = owner_service.tao({'full_name': 'Chủ C', 'phone': '0900000003'},
                            du_lieu['le_tan'])
    session.flush()
    assert chu.id is not None
    log = session.query(ActivityLog).filter_by(entity_type='owners',
                                               entity_id=chu.id).one()
    assert log.action == 'tao_chu_nuoi'
    assert log.actor_user_id == du_lieu['le_tan'].id


def test_tim_kiem_theo_so_dien_thoai(session, du_lieu):
    ds = owner_service.danh_sach(du_lieu['le_tan'], tu_khoa='0900000002')
    assert [o.full_name for o in ds] == ['Chủ B']


def test_xoa_mem_canh_bao_so_ban_ghi_lien_quan(session, du_lieu):
    """Mục 3.2: xóa chủ nuôi còn thú cưng phải cảnh báo, không xóa cứng."""
    kq = owner_service.xoa_mem(du_lieu['chu_a'].id, du_lieu['le_tan'])
    session.flush()

    assert kq['so_thu_cung'] == 1
    assert du_lieu['chu_a'].is_deleted is True
    assert session.query(Owner).count() == 2  # vẫn còn trong CSDL
    assert len(owner_service.danh_sach(du_lieu['le_tan'])) == 1
```

- [ ] **Step 2: Viết test đỏ cho `pet_service`**

`backend/tests/test_pet_service.py` — dùng lại fixture tương đương, phủ:

| Test | Nội dung |
|---|---|
| `test_le_tan_xem_duoc_tat_ca_thu_cung` | Lễ tân thấy toàn bộ |
| `test_chu_nuoi_chi_xem_duoc_thu_cung_cua_minh` | Chủ nuôi A chỉ thấy thú cưng nhà mình |
| `test_chu_nuoi_a_truy_cap_thu_cung_nha_b_bi_tu_choi` | **Ca lỗ hổng chính** — `pytest.raises(QuyenTruyCapBiTuChoi)` |
| `test_nhan_vien_xem_duoc_thu_cung_de_phuc_vu` | Vai trò `staff` xem được (cần cho hồ sơ chăm sóc) |
| `test_loc_thu_cung_theo_chu_nuoi` | Tham số `owner_id` lọc đúng |
| `test_thu_cung_da_xoa_mem_khong_hien_trong_danh_sach` | Xóa mềm hoạt động |

- [ ] **Step 3: Chạy test, xác nhận ĐỎ**

```powershell
venv\Scripts\python.exe -m pytest backend/tests/test_owner_service.py backend/tests/test_pet_service.py
```
Kỳ vọng: `ModuleNotFoundError: No module named 'backend.app.services.owner_service'`.

- [ ] **Step 4: Viết `errors.py`**

```python
"""Ngoại lệ nghiệp vụ.

Tầng service không import Flask, nên không gọi abort() được. Thay vào đó
nó ném các ngoại lệ dưới đây và route dịch sang mã HTTP tương ứng. Nhờ vậy
service gọi được cả từ route lẫn từ scheduler (chạy ngoài ngữ cảnh request).
"""


class QuyenTruyCapBiTuChoi(Exception):
    """Người dùng không có quyền trên bản ghi này. Route dịch thành 403."""


class DuLieuKhongHopLe(Exception):
    """Dữ liệu đầu vào sai. Route hiển thị lại biểu mẫu kèm thông báo."""


class TrungLichHen(Exception):
    """Khung giờ đã có lịch khác của cùng nhân viên. Route hiển thị xung đột."""
```

- [ ] **Step 5: Viết `activity_log_service.py`**

Một hàm `ghi(current_user, action, entity_type, entity_id, detail=None)` tạo bản ghi `ActivityLog` và `db.session.add`. Không `commit` — để hàm gọi quyết định ranh giới giao dịch.

- [ ] **Step 6: Viết `owner_service.py`**

Quy tắc phân quyền, viết thành một hàm dùng chung trong file:

```python
def _kiem_tra_quyen_tren_chu_nuoi(owner_id, current_user):
    """Chủ nuôi chỉ thao tác được trên hồ sơ của chính mình."""
    if current_user.role == UserRole.OWNER and current_user.owner_id != owner_id:
        raise QuyenTruyCapBiTuChoi(
            'Bạn không có quyền xem hồ sơ của chủ nuôi khác'
        )
```

- `danh_sach`: lọc `is_deleted == False`; nếu `current_user.role` là `OWNER` thì thêm điều kiện `id == current_user.owner_id`. Tham số `tu_khoa` lọc theo `full_name` hoặc `phone` bằng `like`.
- `lay_theo_id`: lấy bản ghi, gọi `_kiem_tra_quyen_tren_chu_nuoi`, ném `DuLieuKhongHopLe` nếu không tồn tại hoặc đã xóa mềm.
- `tao`, `cap_nhat`, `xoa_mem`: chỉ `ADMIN` và `RECEPTIONIST` được gọi; vai trò khác ném `QuyenTruyCapBiTuChoi`. Đều gọi `activity_log_service.ghi`.
- `xoa_mem`: đặt `is_deleted = True`, `deleted_at = datetime.now()`, trả `dict` gồm `so_thu_cung`, `so_lich_hen`, `so_hoa_don` để route hiển thị cảnh báo (mục 3.2).

- [ ] **Step 7: Viết `pet_service.py`** — cùng khuôn, quyền kiểm tra qua `pet.owner_id`.

- [ ] **Step 8: Chạy test, xác nhận XANH**

```powershell
venv\Scripts\python.exe -m pytest
```
Kỳ vọng: 59 passed (46 của KT2-A + 13 mới).

- [ ] **Step 9: Commit**

Message: thêm tầng service với phân quyền lớp 2 lọc theo quyền sở hữu dữ liệu; ca chủ nuôi A truy cập dữ liệu nhà B bị từ chối.

---

### Task 2: Giao diện CRUD chủ nuôi và thú cưng

**Files:**
- Create: `backend/app/routers/__init__.py`, `owners.py`, `pets.py`
- Create: `frontend/templates/owners/list.html`, `form.html`, `detail.html`
- Create: `frontend/templates/pets/list.html`, `form.html`, `detail.html`
- Modify: `frontend/templates/base.html` (thêm thanh điều hướng), `backend/app/main.py`
- Create: `backend/tests/test_routes_owners.py`
- Delete: `backend/app/routers/.gitkeep`

**Interfaces:**
- Consumes: toàn bộ hàm của `owner_service`, `pet_service` từ Task 1.
- Produces: blueprint `owners_bp` (`url_prefix='/chu-nuoi'`), `pets_bp` (`url_prefix='/thu-cung'`).

- [ ] **Step 1: Viết test đỏ**

`backend/tests/test_routes_owners.py` phủ:

| Test | Kỳ vọng |
|---|---|
| `test_chua_dang_nhap_bi_chuyen_huong` | `GET /chu-nuoi` → 302 về `/dang-nhap` |
| `test_le_tan_xem_duoc_danh_sach` | 200, có tên chủ nuôi trong HTML |
| `test_nhan_vien_khong_sua_duoc_chu_nuoi` | `GET /chu-nuoi/1/sua` → 403 |
| `test_chu_nuoi_a_mo_ho_so_nha_b_bi_403` | **Ca lỗ hổng, kiểm chứng qua HTTP thật** |
| `test_tao_chu_nuoi_qua_bieu_mau` | POST hợp lệ → 302, bản ghi xuất hiện trong CSDL |
| `test_tao_thieu_so_dien_thoai_bao_loi_tieng_viet` | POST thiếu trường → 200, HTML chứa thông báo tiếng Việt |

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

- [ ] **Step 3: Viết blueprint**

Bảng route cần đăng ký:

| Blueprint | Route | Hàm view | Quyền |
|---|---|---|---|
| `owners_bp` | `GET /chu-nuoi` | `danh_sach_chu_nuoi` | 4 vai trò (service tự lọc) |
| | `GET /chu-nuoi/<int:owner_id>` | `chi_tiet_chu_nuoi` | 4 vai trò |
| | `GET, POST /chu-nuoi/them` | `them_chu_nuoi` | admin, receptionist |
| | `GET, POST /chu-nuoi/<int:owner_id>/sua` | `sua_chu_nuoi` | admin, receptionist |
| | `POST /chu-nuoi/<int:owner_id>/xoa` | `xoa_chu_nuoi` | admin, receptionist |
| `pets_bp` | `GET /thu-cung` | `danh_sach_thu_cung` | 4 vai trò |
| | `GET /thu-cung/<int:pet_id>` | `chi_tiet_thu_cung` | 4 vai trò |
| | `GET, POST /thu-cung/them` | `them_thu_cung` | admin, receptionist |
| | `GET, POST /thu-cung/<int:pet_id>/sua` | `sua_thu_cung` | admin, receptionist |
| | `POST /thu-cung/<int:pet_id>/xoa` | `xoa_thu_cung` | admin, receptionist |

**Xử lý ngoại lệ:** đăng ký `errorhandler` cấp ứng dụng trong `main.py`:
```python
@app.errorhandler(QuyenTruyCapBiTuChoi)
def _xu_ly_tu_choi_quyen(e):
    return render_template('errors/403.html', thong_diep=str(e)), 403
```
Nhờ vậy mỗi route không phải tự bắt ngoại lệ, và ngoại lệ nghiệp vụ luôn thành đúng mã HTTP.

- [ ] **Step 4: Viết template**

`base.html` bổ sung thanh điều hướng hiển thị theo vai trò: mục Chủ nuôi và Thú cưng cho mọi vai trò; mục Dịch vụ chỉ hiện với `admin`. Dùng biến `current_user` đưa vào mọi template qua `app.context_processor`.

Mỗi màn hình danh sách có ô tìm kiếm. Nút xóa có hộp thoại xác nhận (`onsubmit="return confirm(...)"`) theo yêu cầu trải nghiệm mục 4.

- [ ] **Step 5: Chạy test, xác nhận XANH** — kỳ vọng 65 passed.

- [ ] **Step 6: Commit**

---

### Task 3: Danh mục dịch vụ và gói

**Files:**
- Create: `backend/app/services/catalog_service.py`, `backend/app/routers/catalog.py`
- Create: `frontend/templates/catalog/services.html`, `service_form.html`, `packages.html`, `package_form.html`
- Create: `backend/tests/test_catalog_service.py`

**Interfaces:**
- Produces: `catalog_service.danh_sach_dich_vu(current_user, chi_dang_hoat_dong=True)`, `.tao_dich_vu(du_lieu, current_user)`, `.cap_nhat_dich_vu(service_id, du_lieu, current_user)`, `.danh_sach_goi(current_user)`, `.tao_goi(du_lieu, danh_sach_item, current_user)`.

- [ ] **Step 1: Viết test đỏ**

Ca quan trọng nhất:

```python
def test_doi_gia_tu_dong_ghi_lich_su(session, admin):
    """Yêu cầu mục 3.3: đổi giá phải lưu lịch sử, không sửa đè."""
    dv = catalog_service.tao_dich_vu(
        {'name': 'Tắm', 'category': ServiceCategory.TAM,
         'price': Decimal('150000'), 'duration_minutes': 45}, admin)
    session.flush()

    catalog_service.cap_nhat_dich_vu(dv.id, {'price': Decimal('180000')}, admin)
    session.flush()

    ls = session.query(ServicePriceHistory).filter_by(service_id=dv.id).all()
    assert len(ls) == 1
    assert ls[0].old_price == Decimal('150000')
    assert ls[0].new_price == Decimal('180000')
    assert ls[0].changed_by == admin.id
    assert dv.price == Decimal('180000')


def test_cap_nhat_khong_doi_gia_thi_khong_ghi_lich_su(session, admin):
    """Chỉ ghi lịch sử khi giá thực sự đổi, tránh làm bẩn bảng."""
    ...


def test_le_tan_khong_duoc_doi_gia(session, le_tan):
    """Mục 3.1: chỉ quản lý được cấu hình dịch vụ và giá."""
    with pytest.raises(QuyenTruyCapBiTuChoi):
        catalog_service.cap_nhat_dich_vu(1, {'price': Decimal('1')}, le_tan)


def test_gia_goi_phai_re_hon_tong_gia_le(session, admin):
    """Gói combo đắt hơn mua lẻ là vô nghĩa về nghiệp vụ."""
    with pytest.raises(DuLieuKhongHopLe):
        catalog_service.tao_goi({'name': 'Gói dở', 'package_price': Decimal('999999')},
                                [...], admin)
```

- [ ] **Step 2–5:** chạy đỏ → viết `catalog_service` và blueprint `catalog_bp` (`url_prefix='/dich-vu'`, toàn bộ route yêu cầu vai trò `admin`) → chạy xanh → commit.

Kỳ vọng sau task: 72 passed.

---

### Task 4: Đặt lịch và chống trùng lịch

**Đây là logic nghiệp vụ phức tạp nhất của cả dự án**, và là ca kiểm thử bắt buộc ở mục 10 đặc tả.

**Files:**
- Create: `backend/app/services/appointment_service.py`, `backend/tests/test_appointment_service.py`

**Interfaces:**
- Produces: `appointment_service.dat_lich(du_lieu: dict, current_user) -> Appointment`, `appointment_service.danh_sach(current_user, tu_ngay=None, den_ngay=None, trang_thai=None, staff_id=None) -> list[Appointment]`, `appointment_service.xac_nhan(appointment_id, current_user)`, `appointment_service.hoan_thanh(appointment_id, current_user)`.

- [ ] **Step 1: Viết test đỏ**

```python
"""Kiểm thử đặt lịch và chống trùng lịch."""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from backend.app.models import AppointmentStatus, Service, ServiceCategory
from backend.app.services import appointment_service
from backend.app.services.errors import TrungLichHen


def test_dat_lich_hop_le_tinh_dung_gio_ket_thuc(session, du_lieu):
    """ends_at = scheduled_at + duration_minutes của dịch vụ."""
    lh = appointment_service.dat_lich({
        'pet_id': du_lieu['pet'].id,
        'service_id': du_lieu['dv_45p'].id,
        'staff_id': du_lieu['nv'].id,
        'scheduled_at': datetime(2026, 9, 1, 9, 0),
    }, du_lieu['le_tan'])
    session.flush()

    assert lh.ends_at == datetime(2026, 9, 1, 9, 45)
    assert lh.status == AppointmentStatus.PENDING


def test_dat_trung_khung_gio_nhan_vien_bi_chan(session, du_lieu):
    """CA KIỂM THỬ BẮT BUỘC mục 10: trùng lịch nhân viên phải bị chặn."""
    appointment_service.dat_lich({
        'pet_id': du_lieu['pet'].id, 'service_id': du_lieu['dv_45p'].id,
        'staff_id': du_lieu['nv'].id,
        'scheduled_at': datetime(2026, 9, 1, 9, 0),
    }, du_lieu['le_tan'])
    session.flush()

    # Lịch mới bắt đầu lúc 9:30, chồng lên lịch cũ (9:00-9:45).
    with pytest.raises(TrungLichHen):
        appointment_service.dat_lich({
            'pet_id': du_lieu['pet2'].id, 'service_id': du_lieu['dv_45p'].id,
            'staff_id': du_lieu['nv'].id,
            'scheduled_at': datetime(2026, 9, 1, 9, 30),
        }, du_lieu['le_tan'])


def test_lich_ke_sat_nhau_khong_bi_coi_la_trung(session, du_lieu):
    """Lịch cũ 9:00-9:45, lịch mới bắt đầu đúng 9:45 — hợp lệ, không chồng lấn.

    Đây là ca biên dễ làm sai: nếu điều kiện dùng <= thay vì < thì lịch kề
    sát nhau bị chặn oan, nhân viên mất chỗ trống hợp lệ.
    """
    appointment_service.dat_lich({...9:00...}, du_lieu['le_tan'])
    session.flush()
    lh2 = appointment_service.dat_lich({...9:45...}, du_lieu['le_tan'])
    session.flush()
    assert lh2.id is not None


def test_lich_da_huy_khong_chan_lich_moi(session, du_lieu):
    """Chỉ lịch pending/confirmed mới chặn. Lịch cancelled thì không."""
    ...


def test_lich_khong_gan_nhan_vien_khong_kiem_tra_trung(session, du_lieu):
    """staff_id rỗng thì bỏ qua kiểm tra trùng."""
    ...


def test_trung_gio_nhung_khac_nhan_vien_van_dat_duoc(session, du_lieu):
    """Hai nhân viên khác nhau phục vụ cùng khung giờ là bình thường."""
    ...


def test_dat_lich_o_qua_khu_bi_chan(session, du_lieu):
    with pytest.raises(DuLieuKhongHopLe):
        appointment_service.dat_lich({...ngày đã qua...}, du_lieu['le_tan'])


def test_chu_nuoi_khong_duoc_dat_lich(session, du_lieu):
    """Mục 3.4: đặt lịch là việc của lễ tân."""
    with pytest.raises(QuyenTruyCapBiTuChoi):
        appointment_service.dat_lich({...}, du_lieu['tk_chu_nuoi'])
```

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

- [ ] **Step 3: Viết `appointment_service.dat_lich`**

Truy vấn chống trùng — **viết đúng như sau**:

```python
def _tim_lich_trung(staff_id, bat_dau, ket_thuc, bo_qua_id=None):
    """Tìm lịch hẹn chồng khung giờ của cùng một nhân viên.

    Điều kiện chồng lấn: bat_dau < old_end AND old_start < ket_thuc.
    Dùng dấu < chứ KHÔNG dùng <=, để hai lịch kề sát nhau (lịch cũ kết thúc
    đúng lúc lịch mới bắt đầu) không bị coi là trùng.

    bo_qua_id dùng khi đổi lịch: bản ghi đang sửa không được tự chặn chính nó.
    """
    if staff_id is None:
        return None

    dieu_kien = [
        Appointment.staff_id == staff_id,
        Appointment.status.in_([AppointmentStatus.PENDING,
                                AppointmentStatus.CONFIRMED]),
        Appointment.scheduled_at < ket_thuc,
        bat_dau < Appointment.ends_at,
    ]
    if bo_qua_id is not None:
        dieu_kien.append(Appointment.id != bo_qua_id)

    return db.session.execute(
        db.select(Appointment).where(*dieu_kien)
    ).scalars().first()
```

`dat_lich` gọi hàm này; nếu tìm thấy thì ném `TrungLichHen` với thông điệp tiếng Việt nêu rõ nhân viên nào bận khung giờ nào.

- [ ] **Step 4: Chạy test, xác nhận XANH** — kỳ vọng 80 passed.

- [ ] **Step 5: Commit**

---

### Task 5: Đổi lịch và hủy lịch

**Files:**
- Modify: `backend/app/services/appointment_service.py`
- Create: `backend/tests/test_doi_huy_lich.py`

**Interfaces:**
- Produces: `appointment_service.doi_lich(appointment_id, gio_moi: datetime, ly_do: str, current_user) -> Appointment`, `appointment_service.huy_lich(appointment_id, ly_do: str, mo_ta: str | None, current_user) -> Appointment`.

Danh sách lý do hủy hợp lệ (mục 3.4): `khach_yeu_cau`, `nhan_vien_ban`, `thu_cung_om`, `khac`.

- [ ] **Step 1: Viết test đỏ**

| Test | Nội dung |
|---|---|
| `test_doi_lich_cap_nhat_tai_cho_va_ghi_lich_su` | Cùng `id`, `scheduled_at` mới, đúng **1** dòng `appointment_history` |
| `test_doi_lich_dua_trang_thai_ve_pending` | Lịch `confirmed` sau khi đổi quay về `pending` |
| `test_doi_lich_tinh_lai_gio_ket_thuc` | `ends_at` cập nhật theo giờ mới |
| `test_doi_lich_sang_gio_da_bi_chiem_bi_chan` | Ném `TrungLichHen`, lịch cũ **giữ nguyên** |
| `test_doi_lich_khong_tu_chan_chinh_no` | Đổi sang giờ chồng chính nó → **không** báo trùng (nhờ `bo_qua_id`) |
| `test_lich_da_hoan_thanh_khong_doi_duoc` | Ném `DuLieuKhongHopLe` |
| `test_huy_lich_khong_ly_do_bi_chan` | **Ca kiểm thử mục 10** — ném `DuLieuKhongHopLe` |
| `test_huy_ly_do_khac_bat_buoc_nhap_mo_ta` | Chọn `khac` mà không nhập mô tả → bị chặn |
| `test_lich_da_hoan_thanh_khong_huy_duoc` | Ném `DuLieuKhongHopLe` |
| `test_huy_lich_ghi_nhat_ky` | Có dòng `ActivityLog` với `action='huy_lich_hen'` |

- [ ] **Step 2–4:** chạy đỏ → viết `doi_lich` và `huy_lich` → chạy xanh (kỳ vọng 90 passed) → commit.

**Lưu ý cho người triển khai:** `doi_lich` **cập nhật bản ghi tại chỗ**, không tạo bản ghi mới, và enum không có `rescheduled`. Xem lý do ở [`phan_tich_thiet_ke.md`](../../phan_tich_thiet_ke.md) mục 9 dòng ⑥.

---

### Task 6: Giao diện lịch hẹn

**Files:**
- Create: `backend/app/routers/appointments.py`
- Create: `frontend/templates/appointments/list.html`, `form.html`, `detail.html`, `reschedule.html`, `cancel.html`
- Create: `backend/tests/test_routes_appointments.py`

Bảng route:

| Route | Hàm view | Quyền |
|---|---|---|
| `GET /lich-hen` | `danh_sach_lich_hen` | 4 vai trò (service lọc: nhân viên chỉ thấy lịch mình, chủ nuôi chỉ thấy lịch thú cưng mình) |
| `GET, POST /lich-hen/dat` | `dat_lich_hen` | admin, receptionist |
| `GET /lich-hen/<int:id>` | `chi_tiet_lich_hen` | 4 vai trò |
| `GET, POST /lich-hen/<int:id>/doi` | `doi_lich_hen` | admin, receptionist |
| `GET, POST /lich-hen/<int:id>/huy` | `huy_lich_hen` | admin, receptionist |
| `POST /lich-hen/<int:id>/xac-nhan` | `xac_nhan_lich_hen` | admin, receptionist |
| `POST /lich-hen/<int:id>/hoan-thanh` | `hoan_thanh_lich_hen` | admin, receptionist, staff |

Màn hình danh sách có bộ lọc theo ngày, trạng thái, nhân viên. Biểu mẫu hủy dùng `<select>` với đúng 4 lý do; chọn `khac` thì hiện ô nhập mô tả (JS đơn giản, có kiểm tra lại ở tầng service).

Khi bắt `TrungLichHen`, màn hình hiển thị **nhân viên nào bận khung giờ nào**, không chỉ báo "trùng lịch" chung chung.

Kỳ vọng sau task: 97 passed.

---

### Task 7: Hồ sơ chăm sóc

**Files:**
- Create: `backend/app/services/care_record_service.py`, `backend/app/routers/care_records.py`
- Create: `frontend/templates/care_records/form.html`, `list.html`
- Create: `backend/tests/test_care_record_service.py`

**Interfaces:**
- Produces: `care_record_service.ghi_ho_so(du_lieu, current_user) -> CareRecord`, `.danh_sach_theo_thu_cung(pet_id, current_user) -> list[CareRecord]`.

Ca kiểm thử bắt buộc:

| Test | Nội dung |
|---|---|
| `test_ghi_ho_so_day_du_truong` | Thành công |
| `test_thieu_can_nang_bao_loi_ro_rang` | **Ca mục 10** — ném `DuLieuKhongHopLe`, thông điệp nêu rõ trường nào thiếu |
| `test_thieu_ngay_bao_loi_ro_rang` | Tương tự |
| `test_nhan_vien_chi_ghi_ho_so_cho_lich_cua_minh` | Nhân viên khác → `QuyenTruyCapBiTuChoi` |
| `test_chi_ghi_ho_so_cho_lich_da_hoan_thanh` | Lịch `pending` → `DuLieuKhongHopLe` |
| `test_ghi_ho_so_xoa_cache_tom_tat_ai` | `pets.ai_summary_cache` bị đặt lại `None` — **quan trọng cho KT3**, nếu không thì tóm tắt AI hiển thị dữ liệu cũ sau khi có hồ sơ mới |

Kỳ vọng sau task: 103 passed.

---

### Task 8: Lịch tiêm phòng

**Files:**
- Create: `backend/app/services/vaccination_service.py`, `backend/app/routers/vaccinations.py`
- Create: `frontend/templates/vaccinations/list.html`, `form.html`
- Create: `backend/tests/test_vaccination_service.py`

**Interfaces:**
- Produces: `vaccination_service.tinh_trang_thai(lich, hom_nay) -> str` (trả `'da_tiem'`, `'qua_han'`, `'sap_den_han'`, `'binh_thuong'`), `.danh_sach_sap_den_han(current_user, so_ngay=None)`, `.tao(du_lieu, current_user)`, `.danh_dau_da_tiem(vaccination_id, current_user)`.

Ca kiểm thử:

| Test | Nội dung |
|---|---|
| `test_da_tiem_thi_tra_da_tiem` | `is_done=True` → `'da_tiem'`, **bất kể** ngày đến hạn |
| `test_qua_han_khi_ngay_den_han_da_qua` | `next_due_date` < hôm nay → `'qua_han'` |
| `test_sap_den_han_trong_nguong_cau_hinh` | Trong `VACCINE_DUE_SOON_DAYS` ngày → `'sap_den_han'` |
| `test_ngoai_nguong_thi_binh_thuong` | Xa hơn ngưỡng → `'binh_thuong'` |
| `test_trang_thai_khong_luu_vao_csdl` | Bảng không có cột `status` — giữ ràng buộc sai khác ④ |
| `test_danh_dau_da_tiem_tao_lich_ke_tiep` | Đánh dấu xong thì `last_date` cập nhật và sinh kỳ tiếp theo |

**Lưu ý:** `tinh_trang_thai` nhận `hom_nay` làm tham số thay vì gọi `date.today()` bên trong. Nếu gọi ngày hiện tại bên trong hàm thì test phụ thuộc ngày chạy máy và sẽ đỏ vào một ngày nào đó trong tương lai.

Kỳ vọng sau task: 109 passed.

---

### Task 9: Trang chủ và điều hướng theo vai trò

**Files:**
- Create: `backend/app/routers/home.py`, `frontend/templates/home.html`, `frontend/templates/errors/403.html`, `404.html`
- Modify: `frontend/templates/base.html`
- Create: `backend/tests/test_home.py`

- [ ] Route `GET /` chuyển hướng theo vai trò và hiển thị bảng tóm tắt phù hợp: quản lý thấy số liệu tổng quan, lễ tân thấy lịch hôm nay và danh sách tiêm sắp đến hạn, nhân viên thấy lịch của mình, chủ nuôi thấy thú cưng của mình.
- [ ] Trang lỗi 403 và 404 bằng tiếng Việt, có nút quay về trang chủ.
- [ ] Test: mỗi vai trò đăng nhập vào `/` đều nhận 200 và thấy đúng khối nội dung của mình; chưa đăng nhập thì 302.

Kỳ vọng sau task: 114 passed.

---

### Task 10: Rà soát và kiểm chứng đầu-cuối

- [ ] **Step 1: Kiểm tra ràng buộc kiến trúc**

```powershell
Select-String -Path backend\app\services\*.py -Pattern "from backend.app.ai|import ai"
```
Phải **không có kết quả**. Đây là ràng buộc "AI không phải nghiệp vụ lõi" — ở KT2-B thư mục `ai/` còn rỗng nên lệnh này chưa có gì để bắt, nhưng chạy từ bây giờ để tạo thói quen và để KT3 không vi phạm.

- [ ] **Step 2: Kiểm tra mọi hàm service đều nhận `current_user`**

```powershell
Select-String -Path backend\app\services\*.py -Pattern "^def " -Context 0,3
```
Đọc kết quả, xác nhận mọi hàm công khai (không bắt đầu bằng `_`) đều có tham số `current_user`. Hàm nào thiếu là một lỗ hổng phân quyền.

- [ ] **Step 3: Kiểm chứng thủ công**

Khởi tạo CSDL, nạp dữ liệu mẫu, chạy ứng dụng. Kịch bản bắt buộc chạy qua:

1. Đăng nhập `letan` → đặt lịch cho thú cưng bất kỳ với nhân viên `groomer1` lúc 9:00.
2. Đặt tiếp lịch khác cho `groomer1` lúc 9:30 → **phải bị chặn**, và thông báo nêu rõ nhân viên nào bận khung giờ nào.
3. Đặt lịch cho `groomer2` lúc 9:30 → **thành công** (khác nhân viên).
4. Đổi lịch đầu sang hôm sau, nhập lý do → kiểm tra màn hình chi tiết hiển thị đúng 1 dòng lịch sử.
5. Hủy lịch không chọn lý do → **phải bị chặn**.
6. Đăng nhập `chunuoi1` → đổi tham số URL sang `pet_id` của thú cưng nhà `chunuoi2` → **phải nhận 403**.
7. Đăng nhập `groomer1` → mở màn hình dịch vụ → **phải nhận 403**.

- [ ] **Step 4: Xóa `backend/.env` và `pet_care.db`**, chạy lại lệnh kiểm tra an toàn:

```powershell
git ls-files | Select-String -Pattern '\.env$|\.db$'
```

- [ ] **Step 5: Cập nhật `docs/ai_prompt_log.md`** với các dòng của KT2-B.

- [ ] **Step 6: Commit và mở PR.**

---

## Kết quả mong đợi sau 10 task

| Hạng mục | Số lượng |
|---|---|
| Commit | 10 |
| Test | 114, tất cả xanh (46 kế thừa từ KT2-A + 68 mới) |
| Chạy được | Toàn bộ nghiệp vụ quản lý trừ hóa đơn, thống kê, cổng chủ nuôi |
| Ca kiểm thử mục 10 đã phủ | Đặt lịch trùng bị chặn · hủy lịch thiếu lý do bị chặn · hồ sơ thiếu cân nặng bị chặn · phân quyền 403 |
| Chưa làm (để KT2-C) | Hóa đơn, thanh toán, thống kê, cổng chủ nuôi |

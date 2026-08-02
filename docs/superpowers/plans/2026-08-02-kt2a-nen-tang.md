# KT2-A — Nền tảng: Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dựng nền tảng chạy được của hệ thống: cấu hình, app factory, 18 model SQLAlchemy, xác thực bằng session, phân quyền theo vai trò, và dữ liệu mẫu — để KT2-B có chỗ gắn nghiệp vụ vào.

**Architecture:** Flask app factory + Flask-SQLAlchemy. Instance `db` đặt ở `extensions.py` để `models/` và `main.py` cùng import được mà không tạo vòng lặp. Xác thực bằng session cookie, mật khẩu hash bcrypt. Phân quyền lớp 1 (theo vai trò) làm ở mốc này; lớp 2 (theo quyền sở hữu dữ liệu) làm ở KT2-B khi đã có tầng service.

**Tech Stack:** Python 3.13, Flask, Flask-SQLAlchemy, python-dotenv, bcrypt, pytest.

## Global Constraints

- **Nguồn sự thật:** [`docs/superpowers/specs/2026-08-02-pet-care-system-design.md`](../specs/2026-08-02-pet-care-system-design.md) và [`docs/phan_tich_thiet_ke.md`](../../phan_tich_thiet_ke.md). Tên bảng, tên trường, tên biến môi trường phải khớp **nguyên văn**. Phát hiện tài liệu sai thì dừng lại báo, không tự sửa lệch.
- **18 bảng**, không thêm không bớt. Tên bảng và trường viết `snake_case` đúng như spec mục 3.1.
- **4 vai trò:** `admin`, `receptionist`, `staff`, `owner`.
- **TDD bắt buộc.** REQUIRED SUB-SKILL: `superpowers:test-driven-development`. Không viết mã sản xuất khi chưa có test đỏ. Mỗi task đều có bước "chạy test để thấy nó đỏ" — **không được bỏ qua**.
- **Không viết mã ngoài phạm vi KT2-A.** Không đụng tới `ai/`, không viết CRUD nghiệp vụ, không viết template giao diện ngoài trang đăng nhập.
- **`services/` không được import `ai/`** — ràng buộc kiến trúc xuyên suốt dự án.
- **Tuyệt đối không tạo `.env` thật, không commit khóa API.**
- **Mỗi task kết thúc bằng 1 commit**, message tiếng Việt, kết thúc bằng `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
- **Lệnh chạy từ thư mục gốc dự án**, dùng PowerShell.

### Điều kiện tiên quyết

Python 3.13 đã cài và có trong `PATH`. Kiểm tra bằng `python --version` trước khi bắt đầu Task 1. Nếu chưa có, **dừng lại** — không có Python thì không chạy được test, mà không chạy được test thì không phải TDD.

### Sai khác so với tài liệu thiết kế

| Sai khác | Lý do |
|---|---|
| Thêm `backend/app/extensions.py` chứa instance `db` | Mẫu chuẩn của Flask-SQLAlchemy. Nếu đặt `db` trong `main.py` thì `models/` phải import `main.py`, mà `main.py` lại import `models/` — vòng lặp import. File này chỉ có 3 dòng, không chứa logic |
| `requirements.txt` được ghim phiên bản ở Task 1 | Tài liệu KT1 để trống phiên bản vì chưa cài. Ghim lại sau khi cài thật để dự án tái lập được (rubric Cuối kỳ #8) |

---

## File Structure

| File | Trách nhiệm | Task |
|---|---|---|
| `backend/app/extensions.py` | Instance `db` dùng chung | 1 |
| `backend/app/config.py` | Đọc `.env`, lớp cấu hình cho chạy thật và chạy test | 1 |
| `backend/app/main.py` | App factory `create_app()` | 1 |
| `backend/tests/conftest.py` | Fixture `app`, `client`, `session` | 1 |
| `backend/app/models/__init__.py` | Gom export toàn bộ model | 2–6 |
| `backend/app/models/user.py` | `User`, `UserRole` | 2 |
| `backend/app/models/owner.py` | `Owner` (xóa mềm) | 2 |
| `backend/app/models/pet.py` | `Pet` (xóa mềm, cache tóm tắt AI) | 2 |
| `backend/app/models/catalog.py` | `Service`, `ServiceCategory`, `ServicePackage`, `PackageItem`, `ServicePriceHistory` | 3 |
| `backend/app/models/appointment.py` | `Appointment`, `AppointmentStatus`, `AppointmentHistory`, `CareRecord`, `VaccinationSchedule` | 4 |
| `backend/app/models/billing.py` | `Invoice`, `PaymentStatus`, `InvoiceItem`, `Payment` | 5 |
| `backend/app/models/system.py` | `AiInteractionLog`, `ActivityLog`, `AppSetting`, `Notification` | 6 |
| `backend/app/auth/password.py` | Hash và kiểm tra mật khẩu | 7 |
| `backend/app/auth/routes.py` | Trang đăng nhập, đăng xuất | 7 |
| `backend/app/auth/decorators.py` | `require_role`, `current_user` | 8 |
| `frontend/templates/base.html`, `auth/login.html` | Giao diện tối thiểu | 7 |
| `database/seed_data.sql` | Dữ liệu mẫu | 9 |
| `backend/app/cli.py` | Lệnh `init-db`, `seed-db` | 9 |

---

### Task 1: Cấu hình, app factory, hạ tầng kiểm thử

**Files:**
- Create: `backend/app/__init__.py`, `backend/app/extensions.py`, `backend/app/config.py`, `backend/app/main.py`
- Create: `backend/tests/__init__.py`, `backend/tests/conftest.py`, `backend/tests/test_config.py`
- Modify: `backend/requirements.txt` (ghim phiên bản)
- Create: `pytest.ini`

**Interfaces:**
- Produces: `create_app(config_name='default') -> Flask`; `db` (đối tượng `SQLAlchemy`); fixture pytest `app`, `client`, `session`. Mọi task sau đều dùng.

- [ ] **Step 1: Cài thư viện và ghim phiên bản**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install Flask Flask-SQLAlchemy python-dotenv bcrypt APScheduler pytest
pip freeze | Select-String -Pattern "^(Flask|Flask-SQLAlchemy|python-dotenv|bcrypt|APScheduler|pytest)==" | Set-Content -Path backend\requirements.txt -Encoding utf8
Get-Content backend\requirements.txt
```

Thêm dòng `google-generativeai` (chưa ghim) vào cuối `backend/requirements.txt` kèm chú thích `# dùng từ KT3`. Chưa cài ở mốc này vì KT2 không gọi AI.

- [ ] **Step 2: Tạo `pytest.ini` ở thư mục gốc**

```ini
[pytest]
testpaths = backend/tests
python_files = test_*.py
addopts = -v
```

- [ ] **Step 3: Viết test đỏ cho cấu hình**

`backend/tests/test_config.py`:

```python
"""Kiểm thử app factory và cấu hình."""
from backend.app.main import create_app


def test_create_app_che_do_test_bat_co_testing():
    """App tạo ở chế độ 'testing' phải bật cờ TESTING."""
    app = create_app('testing')
    assert app.config['TESTING'] is True


def test_che_do_test_dung_csdl_trong_bo_nho():
    """Chế độ test phải dùng SQLite in-memory, không đụng file CSDL thật."""
    app = create_app('testing')
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'


def test_app_tro_dung_thu_muc_frontend():
    """Template và static phải trỏ sang frontend/ theo thiết kế mục 6.3."""
    app = create_app('testing')
    assert app.template_folder.replace('\\', '/').endswith('frontend/templates')
    assert app.static_folder.replace('\\', '/').endswith('frontend/static')


def test_thoi_han_phien_doc_tu_cau_hinh():
    """Phiên đăng nhập phải có hạn, lấy từ JWT_EXPIRE_MINUTES."""
    app = create_app('testing')
    assert app.permanent_session_lifetime.total_seconds() == 60 * 60
```

- [ ] **Step 4: Chạy test, xác nhận nó ĐỎ**

```powershell
pytest backend/tests/test_config.py
```
Kỳ vọng: `ModuleNotFoundError: No module named 'backend.app.main'` — đỏ vì chưa có mã, không phải đỏ vì gõ sai.

- [ ] **Step 5: Viết mã tối thiểu cho xanh**

`backend/__init__.py` và `backend/app/__init__.py`: file rỗng (đánh dấu package).

`backend/app/extensions.py`:
```python
"""Các đối tượng mở rộng dùng chung.

Tách riêng để models/ và main.py cùng import được mà không tạo vòng lặp import.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

`backend/app/config.py`:
```python
"""Cấu hình ứng dụng, đọc từ biến môi trường.

Không hardcode khóa API hay mật khẩu ở đây (yêu cầu bảo mật mục 9 đặc tả).
"""
import os
from datetime import timedelta

from dotenv import load_dotenv

# Nạp backend/.env nếu có. File này KHÔNG được commit.
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


class Config:
    """Cấu hình dùng khi chạy thật."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'change_me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///./pet_care.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Phiên đăng nhập có hết hạn — yêu cầu bảo mật mục 4 đặc tả.
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.getenv('JWT_EXPIRE_MINUTES', '60'))
    )

    # Ngưỡng nhắc lịch, dùng từ KT3.
    REMINDER_APPOINTMENT_DAYS = int(os.getenv('REMINDER_APPOINTMENT_DAYS', '2'))
    VACCINE_DUE_SOON_DAYS = int(os.getenv('VACCINE_DUE_SOON_DAYS', '7'))


class TestingConfig(Config):
    """Cấu hình khi chạy pytest: CSDL nằm trong bộ nhớ, không đụng file thật."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


CONFIG_MAP = {
    'default': Config,
    'testing': TestingConfig,
}
```

`backend/app/main.py`:
```python
"""App factory.

Giao diện render phía server bằng Jinja2, nên Flask được trỏ sang thư mục
frontend/ nằm ngoài package — theo cấu trúc mục 7.2 đặc tả.
"""
import os

from flask import Flask

from backend.app.config import CONFIG_MAP
from backend.app.extensions import db

# backend/app/main.py -> lùi 3 cấp là thư mục gốc dự án
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_app(config_name='default'):
    """Tạo và cấu hình ứng dụng Flask."""
    app = Flask(
        __name__,
        template_folder=os.path.join(_PROJECT_ROOT, 'frontend', 'templates'),
        static_folder=os.path.join(_PROJECT_ROOT, 'frontend', 'static'),
    )
    app.config.from_object(CONFIG_MAP[config_name])

    db.init_app(app)

    return app
```

- [ ] **Step 6: Chạy test, xác nhận nó XANH**

```powershell
pytest backend/tests/test_config.py
```
Kỳ vọng: 4 passed, không có cảnh báo.

- [ ] **Step 7: Viết `conftest.py`**

`backend/tests/conftest.py`:
```python
"""Fixture dùng chung cho toàn bộ test."""
import pytest

from backend.app.extensions import db as _db
from backend.app.main import create_app


@pytest.fixture
def app():
    """Ứng dụng ở chế độ test, CSDL sạch cho mỗi test."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def session(app):
    """Phiên làm việc với CSDL."""
    return _db.session


@pytest.fixture
def client(app):
    """Client giả lập trình duyệt, dùng cho test route."""
    return app.test_client()
```

`backend/tests/__init__.py`: file rỗng.

- [ ] **Step 8: Chạy toàn bộ test**

```powershell
pytest
```
Kỳ vọng: 4 passed. Fixture chưa có test nào dùng nên chưa chứng minh được gì — Task 2 sẽ dùng và qua đó kiểm chứng.

- [ ] **Step 9: Commit**

```powershell
git add -A
git commit -F <file message>
```
Nội dung message: dựng app factory, cấu hình đọc `.env`, hạ tầng pytest với CSDL in-memory; ghim phiên bản thư viện.

---

### Task 2: Model nền — `users`, `owners`, `pets`

**Files:**
- Create: `backend/app/models/__init__.py`, `backend/app/models/user.py`, `backend/app/models/owner.py`, `backend/app/models/pet.py`
- Create: `backend/tests/test_models_nen.py`
- Delete: `backend/app/models/.gitkeep`

**Interfaces:**
- Consumes: `db` từ `backend.app.extensions`.
- Produces: `User`, `UserRole`, `Owner`, `Pet`. `UserRole` là enum Python với 4 giá trị `ADMIN='admin'`, `RECEPTIONIST='receptionist'`, `STAFF='staff'`, `OWNER='owner'`. `Owner.query_active()` và `Pet.query_active()` trả truy vấn đã lọc `is_deleted == False`.

- [ ] **Step 1: Viết test đỏ**

`backend/tests/test_models_nen.py`:

```python
"""Kiểm thử ba model nền: users, owners, pets."""
import pytest
from sqlalchemy.exc import StatementError

from backend.app.models import Owner, Pet, User, UserRole


def test_tao_owner_va_pet_lien_ket_dung(session):
    """Thú cưng gắn với đúng một chủ nuôi."""
    chu = Owner(full_name='Nguyễn Văn A', phone='0900000001')
    session.add(chu)
    session.flush()

    cun = Pet(owner_id=chu.id, name='Mực', species='chó')
    session.add(cun)
    session.flush()

    assert cun.owner.full_name == 'Nguyễn Văn A'
    assert chu.pets[0].name == 'Mực'


def test_role_khong_hop_le_bi_chan(session):
    """role phải là enum kiểm soát, không nhận text tự do (ràng buộc mục 5.3)."""
    u = User(username='x', password_hash='h', role='giam_doc')
    session.add(u)
    with pytest.raises(StatementError):
        session.flush()


def test_bon_vai_tro_deu_hop_le(session):
    """Đủ 4 vai trò theo thiết kế."""
    for i, role in enumerate(UserRole):
        session.add(User(username=f'u{i}', password_hash='h', role=role))
    session.flush()
    assert session.query(User).count() == 4


def test_nhan_vien_khong_gan_owner_id(session):
    """Tài khoản nhân viên có owner_id rỗng; tài khoản chủ nuôi thì trỏ về hồ sơ."""
    chu = Owner(full_name='Trần Thị B', phone='0900000002')
    session.add(chu)
    session.flush()

    le_tan = User(username='letan', password_hash='h', role=UserRole.RECEPTIONIST)
    tk_chu = User(username='chub', password_hash='h', role=UserRole.OWNER, owner_id=chu.id)
    session.add_all([le_tan, tk_chu])
    session.flush()

    assert le_tan.owner_id is None
    assert tk_chu.owner.full_name == 'Trần Thị B'


def test_query_active_loai_bo_ban_ghi_da_xoa_mem(session):
    """Xóa mềm: bản ghi đã xóa không xuất hiện trong truy vấn mặc định."""
    con_dung = Owner(full_name='Còn dùng', phone='0900000003')
    da_xoa = Owner(full_name='Đã xóa', phone='0900000004', is_deleted=True)
    session.add_all([con_dung, da_xoa])
    session.flush()

    ten = [o.full_name for o in Owner.query_active().all()]
    assert ten == ['Còn dùng']
    assert session.query(Owner).count() == 2  # vẫn còn trong CSDL, chỉ bị ẩn


def test_pet_co_hai_cot_cache_tom_tat_ai(session):
    """Hai cột cache tóm tắt AI tồn tại và mặc định rỗng (thiết kế mục 5.1)."""
    chu = Owner(full_name='C', phone='0900000005')
    session.add(chu)
    session.flush()
    p = Pet(owner_id=chu.id, name='Vàng', species='mèo')
    session.add(p)
    session.flush()

    assert p.ai_summary_cache is None
    assert p.ai_summary_cached_at is None
```

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

```powershell
pytest backend/tests/test_models_nen.py
```
Kỳ vọng: `ImportError: cannot import name 'Owner' from 'backend.app.models'`.

- [ ] **Step 3: Viết model**

`backend/app/models/user.py`:
```python
"""Model tài khoản đăng nhập.

Một bảng users duy nhất cho cả 4 vai trò, kể cả chủ nuôi — để chỉ có một
luồng đăng nhập và một chỗ kiểm tra quyền (thiết kế mục 9 sai khác ①).
"""
import enum
from datetime import datetime

from backend.app.extensions import db


class UserRole(enum.Enum):
    """Bốn vai trò của hệ thống."""

    ADMIN = 'admin'
    RECEPTIONIST = 'receptionist'
    STAFF = 'staff'
    OWNER = 'owner'


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # native_enum=False sinh ràng buộc CHECK trên SQLite -> chặn được text tự do.
    role = db.Column(db.Enum(UserRole, native_enum=False, validate_strings=True),
                     nullable=False)
    full_name = db.Column(db.String(128))
    # Rỗng với nhân viên; trỏ về hồ sơ chủ nuôi với vai trò owner.
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    owner = db.relationship('Owner', back_populates='user_accounts')
```

`backend/app/models/owner.py`:
```python
"""Model chủ nuôi. Dùng xóa mềm để không làm hỏng hóa đơn cũ."""
from datetime import datetime

from backend.app.extensions import db


class Owner(db.Model):
    __tablename__ = 'owners'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(128))
    address = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    deleted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pets = db.relationship('Pet', back_populates='owner')
    user_accounts = db.relationship('User', back_populates='owner')

    @classmethod
    def query_active(cls):
        """Truy vấn chỉ lấy bản ghi chưa bị xóa mềm (ràng buộc mục 5.3)."""
        return cls.query.filter_by(is_deleted=False)
```

`backend/app/models/pet.py`:
```python
"""Model thú cưng.

Hai cột ai_summary_cache và ai_summary_cached_at phục vụ chức năng tóm tắt
AI ở KT3: cache 24 giờ, xóa khi có hồ sơ chăm sóc mới.
"""
from datetime import datetime

from backend.app.extensions import db


class Pet(db.Model):
    __tablename__ = 'pets'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    species = db.Column(db.String(32), nullable=False)
    breed = db.Column(db.String(64))
    gender = db.Column(db.String(16))
    birth_date = db.Column(db.Date)
    weight = db.Column(db.Numeric(6, 2))
    color = db.Column(db.String(32))
    photo_url = db.Column(db.String(255))
    notes = db.Column(db.Text)
    ai_summary_cache = db.Column(db.Text)
    ai_summary_cached_at = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    deleted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    owner = db.relationship('Owner', back_populates='pets')

    @classmethod
    def query_active(cls):
        """Truy vấn chỉ lấy thú cưng chưa bị xóa mềm."""
        return cls.query.filter_by(is_deleted=False)
```

`backend/app/models/__init__.py`:
```python
"""Gom toàn bộ model để import một chỗ và để create_all() thấy đủ bảng."""
from backend.app.models.owner import Owner
from backend.app.models.pet import Pet
from backend.app.models.user import User, UserRole

__all__ = ['Owner', 'Pet', 'User', 'UserRole']
```

Xóa `backend/app/models/.gitkeep`.

- [ ] **Step 4: Đăng ký model vào app factory**

Trong `backend/app/main.py`, thêm ngay sau `db.init_app(app)`:
```python
    # Import để SQLAlchemy biết đủ bảng khi gọi create_all().
    from backend.app import models  # noqa: F401
```

- [ ] **Step 5: Chạy test, xác nhận XANH**

```powershell
pytest
```
Kỳ vọng: 10 passed (4 của Task 1 + 6 của Task 2).

- [ ] **Step 6: Commit**

Message: thêm 3 model nền users/owners/pets, enum 4 vai trò có ràng buộc CHECK, xóa mềm qua `query_active()`.

---

### Task 3: Model danh mục dịch vụ

**Files:**
- Create: `backend/app/models/catalog.py`, `backend/tests/test_models_danh_muc.py`
- Modify: `backend/app/models/__init__.py`

**Interfaces:**
- Produces: `Service`, `ServiceCategory` (enum: `TAM='tam'`, `SPA='spa'`, `GROOMING='grooming'`, `KHAC='khac'`), `ServicePackage`, `PackageItem`, `ServicePriceHistory`.

- [ ] **Step 1: Viết test đỏ**

`backend/tests/test_models_danh_muc.py`:

```python
"""Kiểm thử model danh mục dịch vụ, gói dịch vụ và lịch sử giá."""
from decimal import Decimal

import pytest
from sqlalchemy.exc import StatementError

from backend.app.models import (PackageItem, Service, ServiceCategory,
                                ServicePackage, ServicePriceHistory, User, UserRole)


def test_tao_dich_vu(session):
    dv = Service(name='Tắm cơ bản', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add(dv)
    session.flush()
    assert dv.is_active is True


def test_danh_muc_khong_hop_le_bi_chan(session):
    dv = Service(name='X', category='matxa', price=Decimal('1'), duration_minutes=1)
    session.add(dv)
    with pytest.raises(StatementError):
        session.flush()


def test_goi_dich_vu_lien_ket_nhieu_dich_vu(session):
    """Gói combo nối n-n với dịch vụ qua package_items."""
    tam = Service(name='Tắm', category=ServiceCategory.TAM,
                  price=Decimal('150000'), duration_minutes=45)
    cat = Service(name='Cắt tỉa', category=ServiceCategory.GROOMING,
                  price=Decimal('250000'), duration_minutes=60)
    session.add_all([tam, cat])
    session.flush()

    goi = ServicePackage(name='Combo sạch đẹp', package_price=Decimal('350000'))
    session.add(goi)
    session.flush()
    session.add_all([
        PackageItem(package_id=goi.id, service_id=tam.id, quantity=1),
        PackageItem(package_id=goi.id, service_id=cat.id, quantity=1),
    ])
    session.flush()

    assert len(goi.items) == 2
    assert sum(i.service.price * i.quantity for i in goi.items) == Decimal('400000')
    assert goi.package_price < Decimal('400000')  # gói phải rẻ hơn mua lẻ


def test_lich_su_gia_ghi_nhan_nguoi_doi(session):
    """Đổi giá phải lưu lịch sử, không sửa đè (yêu cầu mục 3.3 đặc tả)."""
    admin = User(username='ad', password_hash='h', role=UserRole.ADMIN)
    dv = Service(name='Tắm', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add_all([admin, dv])
    session.flush()

    ls = ServicePriceHistory(service_id=dv.id, old_price=Decimal('150000'),
                             new_price=Decimal('180000'), changed_by=admin.id)
    session.add(ls)
    session.flush()

    assert dv.price_history[0].old_price == Decimal('150000')
    assert dv.price_history[0].changed_by_user.username == 'ad'
```

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

```powershell
pytest backend/tests/test_models_danh_muc.py
```
Kỳ vọng: `ImportError: cannot import name 'Service'`.

- [ ] **Step 3: Viết `backend/app/models/catalog.py`**

Bốn model theo đúng trường ở thiết kế mục 5.1 hàng 4–7:

- `ServiceCategory(enum.Enum)`: `TAM`, `SPA`, `GROOMING`, `KHAC`.
- `Service`: `id`, `name` (bắt buộc), `category` (`db.Enum(..., native_enum=False, validate_strings=True)`, bắt buộc), `price` (`db.Numeric(12, 2)`, bắt buộc), `duration_minutes` (`db.Integer`, bắt buộc), `description` (`db.Text`), `is_active` (`db.Boolean`, mặc định `True`), `created_at`. Quan hệ `price_history` trỏ tới `ServicePriceHistory`.
- `ServicePackage`: `id`, `name`, `description`, `package_price` (`db.Numeric(12, 2)`), `is_active`, `created_at`. Quan hệ `items` trỏ tới `PackageItem`.
- `PackageItem`: `id`, `package_id` (FK→`service_packages.id`), `service_id` (FK→`services.id`), `quantity` (`db.Integer`, mặc định 1). Quan hệ `service` và `package`.
- `ServicePriceHistory`: `id`, `service_id` (FK), `old_price`, `new_price` (`db.Numeric(12, 2)`), `changed_by` (FK→`users.id`), `changed_at` (mặc định `datetime.now`). Quan hệ `changed_by_user` trỏ tới `User`.

Mỗi lớp có docstring tiếng Việt một dòng nêu vai trò. Cập nhật `models/__init__.py` để export 5 tên mới.

- [ ] **Step 4: Chạy test, xác nhận XANH**

```powershell
pytest
```
Kỳ vọng: 14 passed.

- [ ] **Step 5: Commit**

Message: thêm model danh mục dịch vụ, gói combo n-n, lịch sử giá theo yêu cầu mục 3.3.

---

### Task 4: Model lịch hẹn, hồ sơ chăm sóc, tiêm phòng

**Files:**
- Create: `backend/app/models/appointment.py`, `backend/tests/test_models_lich_hen.py`
- Modify: `backend/app/models/__init__.py`

**Interfaces:**
- Produces: `Appointment`, `AppointmentStatus` (enum: `PENDING='pending'`, `CONFIRMED='confirmed'`, `COMPLETED='completed'`, `CANCELLED='cancelled'` — **không có** `rescheduled`, xem sai khác ⑥), `AppointmentHistory`, `CareRecord`, `VaccinationSchedule`.

- [ ] **Step 1: Viết test đỏ**

`backend/tests/test_models_lich_hen.py`:

```python
"""Kiểm thử model lịch hẹn, lịch sử đổi lịch, hồ sơ chăm sóc, lịch tiêm."""
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError, StatementError

from backend.app.models import (Appointment, AppointmentHistory, AppointmentStatus,
                                CareRecord, Owner, Pet, Service, ServiceCategory,
                                User, UserRole, VaccinationSchedule)


@pytest.fixture
def du_lieu_co_ban(session):
    """Một chủ nuôi, một thú cưng, một dịch vụ, một nhân viên."""
    chu = Owner(full_name='A', phone='0900000001')
    nv = User(username='nv', password_hash='h', role=UserRole.STAFF)
    dv = Service(name='Tắm', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add_all([chu, nv, dv])
    session.flush()
    pet = Pet(owner_id=chu.id, name='Mực', species='chó')
    session.add(pet)
    session.flush()
    return {'chu': chu, 'nv': nv, 'dv': dv, 'pet': pet}


def test_lich_hen_mac_dinh_o_trang_thai_pending(session, du_lieu_co_ban):
    d = du_lieu_co_ban
    bat_dau = datetime(2026, 9, 1, 9, 0)
    lh = Appointment(pet_id=d['pet'].id, service_id=d['dv'].id, staff_id=d['nv'].id,
                     scheduled_at=bat_dau, ends_at=bat_dau + timedelta(minutes=45),
                     created_by=d['nv'].id)
    session.add(lh)
    session.flush()
    assert lh.status == AppointmentStatus.PENDING


def test_enum_khong_co_gia_tri_rescheduled(session):
    """Thiết kế bỏ 'rescheduled' — đổi lịch là sự kiện, ghi ở appointment_history."""
    gia_tri = {s.value for s in AppointmentStatus}
    assert gia_tri == {'pending', 'confirmed', 'completed', 'cancelled'}


def test_trang_thai_khong_hop_le_bi_chan(session, du_lieu_co_ban):
    d = du_lieu_co_ban
    bat_dau = datetime(2026, 9, 1, 9, 0)
    lh = Appointment(pet_id=d['pet'].id, service_id=d['dv'].id,
                     scheduled_at=bat_dau, ends_at=bat_dau + timedelta(minutes=45),
                     status='rescheduled', created_by=d['nv'].id)
    session.add(lh)
    with pytest.raises(StatementError):
        session.flush()


def test_lich_su_doi_lich_luu_gio_cu_gio_moi_va_ly_do(session, du_lieu_co_ban):
    d = du_lieu_co_ban
    cu = datetime(2026, 9, 1, 9, 0)
    moi = datetime(2026, 9, 2, 14, 0)
    lh = Appointment(pet_id=d['pet'].id, service_id=d['dv'].id, staff_id=d['nv'].id,
                     scheduled_at=cu, ends_at=cu + timedelta(minutes=45),
                     created_by=d['nv'].id)
    session.add(lh)
    session.flush()

    session.add(AppointmentHistory(appointment_id=lh.id, old_time=cu, new_time=moi,
                                   reason='khach_yeu_cau', changed_by=d['nv'].id))
    session.flush()

    assert len(lh.history) == 1
    assert lh.history[0].old_time == cu
    assert lh.history[0].new_time == moi


def test_ho_so_cham_soc_bat_buoc_co_ngay_va_can_nang(session, du_lieu_co_ban):
    """record_date và weight_at_visit không được rỗng (ca kiểm thử mục 10)."""
    d = du_lieu_co_ban
    hs = CareRecord(pet_id=d['pet'].id, staff_id=d['nv'].id, record_date=None,
                    weight_at_visit=None)
    session.add(hs)
    # Bắt đúng IntegrityError, không bắt Exception chung — bắt chung thì một lỗi
    # gõ sai tên trường cũng làm test xanh, mà như vậy test không chứng minh gì.
    with pytest.raises(IntegrityError):
        session.flush()


def test_lich_tiem_chi_luu_co_da_tiem(session, du_lieu_co_ban):
    """Không lưu cứng 'sắp đến hạn'/'quá hạn' — hai giá trị đó tính lúc truy vấn."""
    d = du_lieu_co_ban
    lt = VaccinationSchedule(pet_id=d['pet'].id, vaccine_name='Dại',
                             last_date=date(2026, 1, 10),
                             next_due_date=date(2027, 1, 10))
    session.add(lt)
    session.flush()

    assert lt.is_done is False
    assert not hasattr(lt, 'status')
```

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

```powershell
pytest backend/tests/test_models_lich_hen.py
```
Kỳ vọng: `ImportError: cannot import name 'Appointment'`.

- [ ] **Step 3: Viết `backend/app/models/appointment.py`**

Theo trường ở thiết kế mục 5.1 hàng 8–11:

- `AppointmentStatus(enum.Enum)`: đúng 4 giá trị, **không có** `rescheduled`.
- `Appointment`: `id`, `pet_id` (FK, bắt buộc), `service_id` (FK, bắt buộc), `staff_id` (FK→`users.id`, cho phép rỗng), `scheduled_at` (`db.DateTime`, bắt buộc), `ends_at` (`db.DateTime`, bắt buộc), `status` (enum, mặc định `PENDING`), `notes` (`db.Text`), `created_by` (FK→`users.id`), `created_at`. Quan hệ `history`, `pet`, `service`.
  Ghi docstring giải thích vì sao lưu `ends_at` thay vì tính lúc đọc (sai khác ②).
- `AppointmentHistory`: `id`, `appointment_id` (FK), `old_time`, `new_time` (`db.DateTime`), `reason` (`db.String(255)`, bắt buộc), `changed_by` (FK), `changed_at`.
- `CareRecord`: `id`, `pet_id` (FK, bắt buộc), `appointment_id` (FK, cho phép rỗng), `staff_id` (FK, bắt buộc), `record_date` (`db.Date`, **bắt buộc**), `weight_at_visit` (`db.Numeric(6, 2)`, **bắt buộc**), `condition_notes`, `treatment_notes`, `next_recommendation` (`db.Text`), `created_at`.
- `VaccinationSchedule`: `id`, `pet_id` (FK), `vaccine_name` (`db.String(64)`, bắt buộc), `last_date` (`db.Date`), `next_due_date` (`db.Date`, bắt buộc), `is_done` (`db.Boolean`, mặc định `False`), `created_at`. **Không có cột `status`.**

Cập nhật `models/__init__.py`.

- [ ] **Step 4: Chạy test, xác nhận XANH**

```powershell
pytest
```
Kỳ vọng: 20 passed.

- [ ] **Step 5: Commit**

Message: thêm model lịch hẹn với `ends_at` lưu sẵn và enum 4 trạng thái không có `rescheduled`; hồ sơ chăm sóc bắt buộc ngày và cân nặng; lịch tiêm chỉ lưu `is_done`.

---

### Task 5: Model tài chính

**Files:**
- Create: `backend/app/models/billing.py`, `backend/tests/test_models_tai_chinh.py`
- Modify: `backend/app/models/__init__.py`

**Interfaces:**
- Produces: `Invoice`, `PaymentStatus` (enum: `CHUA_THANH_TOAN='chua_thanh_toan'`, `MOT_PHAN='mot_phan'`, `DA_THANH_TOAN='da_thanh_toan'`), `InvoiceItem`, `Payment`.

- [ ] **Step 1: Viết test đỏ**

`backend/tests/test_models_tai_chinh.py`:

```python
"""Kiểm thử model hóa đơn, dòng hóa đơn, thanh toán."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.app.models import (Appointment, Invoice, InvoiceItem, Owner, Payment,
                                PaymentStatus, Pet, Service, ServiceCategory,
                                User, UserRole)


def test_invoice_khong_co_cot_appointment_id(session):
    """Sai khác ⑦: appointment_id nằm ở invoice_items, không ở invoices."""
    assert not hasattr(Invoice, 'appointment_id')
    assert hasattr(InvoiceItem, 'appointment_id')


def test_mot_hoa_don_gop_nhieu_lich_hen(session):
    """Yêu cầu mục 3.7: lập hóa đơn từ 1 hoặc nhiều lịch hẹn."""
    chu = Owner(full_name='A', phone='0900000001')
    lt = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    dv = Service(name='Tắm', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add_all([chu, lt, dv])
    session.flush()
    pet = Pet(owner_id=chu.id, name='Mực', species='chó')
    session.add(pet)
    session.flush()

    t = datetime(2026, 9, 1, 9, 0)
    lh1 = Appointment(pet_id=pet.id, service_id=dv.id, scheduled_at=t,
                      ends_at=t + timedelta(minutes=45), created_by=lt.id)
    lh2 = Appointment(pet_id=pet.id, service_id=dv.id, scheduled_at=t + timedelta(days=7),
                      ends_at=t + timedelta(days=7, minutes=45), created_by=lt.id)
    session.add_all([lh1, lh2])
    session.flush()

    hd = Invoice(owner_id=chu.id, invoice_number='HD-0001', issue_date=date(2026, 9, 10),
                 discount_amount=Decimal('0'), total_amount=Decimal('300000'),
                 created_by=lt.id)
    session.add(hd)
    session.flush()
    session.add_all([
        InvoiceItem(invoice_id=hd.id, service_id=dv.id, appointment_id=lh1.id,
                    quantity=1, unit_price=Decimal('150000'), line_total=Decimal('150000')),
        InvoiceItem(invoice_id=hd.id, service_id=dv.id, appointment_id=lh2.id,
                    quantity=1, unit_price=Decimal('150000'), line_total=Decimal('150000')),
    ])
    session.flush()

    assert len(hd.items) == 2
    assert {i.appointment_id for i in hd.items} == {lh1.id, lh2.id}


def test_hoa_don_mac_dinh_chua_thanh_toan(session):
    chu = Owner(full_name='B', phone='0900000002')
    lt = User(username='lt2', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add_all([chu, lt])
    session.flush()
    hd = Invoice(owner_id=chu.id, invoice_number='HD-0002', issue_date=date(2026, 9, 10),
                 discount_amount=Decimal('0'), total_amount=Decimal('100000'),
                 created_by=lt.id)
    session.add(hd)
    session.flush()
    assert hd.payment_status == PaymentStatus.CHUA_THANH_TOAN


def test_nhieu_dong_thanh_toan_cho_mot_hoa_don(session):
    """Thanh toán từng phần: nhiều dòng payments trên một hóa đơn."""
    chu = Owner(full_name='C', phone='0900000003')
    lt = User(username='lt3', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add_all([chu, lt])
    session.flush()
    hd = Invoice(owner_id=chu.id, invoice_number='HD-0003', issue_date=date(2026, 9, 10),
                 discount_amount=Decimal('0'), total_amount=Decimal('300000'),
                 created_by=lt.id)
    session.add(hd)
    session.flush()
    session.add_all([
        Payment(invoice_id=hd.id, amount=Decimal('100000'), payment_date=date(2026, 9, 10),
                method='tien_mat', received_by=lt.id),
        Payment(invoice_id=hd.id, amount=Decimal('150000'), payment_date=date(2026, 9, 12),
                method='chuyen_khoan', received_by=lt.id),
    ])
    session.flush()

    assert sum(p.amount for p in hd.payments) == Decimal('250000')
    assert sum(p.amount for p in hd.payments) < hd.total_amount  # còn thiếu -> một phần
```

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

```powershell
pytest backend/tests/test_models_tai_chinh.py
```

- [ ] **Step 3: Viết `backend/app/models/billing.py`**

Theo thiết kế mục 5.1 hàng 12–14:

- `PaymentStatus(enum.Enum)`: 3 giá trị như trên.
- `Invoice`: `id`, `owner_id` (FK, bắt buộc), `invoice_number` (`db.String(32)`, duy nhất, bắt buộc), `issue_date` (`db.Date`, bắt buộc), `discount_amount` (`db.Numeric(12, 2)`, mặc định 0), `total_amount` (`db.Numeric(12, 2)`, bắt buộc), `payment_status` (enum, mặc định `CHUA_THANH_TOAN`), `created_by` (FK), `created_at`. Quan hệ `items`, `payments`, `owner`.
  **Không có cột `appointment_id`** — docstring ghi rõ lý do (sai khác ⑦).
- `InvoiceItem`: `id`, `invoice_id` (FK, bắt buộc), `service_id` (FK, bắt buộc), `appointment_id` (FK→`appointments.id`, cho phép rỗng), `package_id` (FK→`service_packages.id`, cho phép rỗng), `quantity` (`db.Integer`, mặc định 1), `unit_price` (`db.Numeric(12, 2)`, bắt buộc), `line_total` (`db.Numeric(12, 2)`, bắt buộc).
  Docstring ghi rõ: `unit_price` và `line_total` **chép cứng lúc lập**, không tính lúc đọc.
- `Payment`: `id`, `invoice_id` (FK, bắt buộc), `amount` (`db.Numeric(12, 2)`, bắt buộc), `payment_date` (`db.Date`, bắt buộc), `method` (`db.String(32)`, bắt buộc), `received_by` (FK), `created_at`.

- [ ] **Step 4: Chạy test, xác nhận XANH**

```powershell
pytest
```
Kỳ vọng: 24 passed.

- [ ] **Step 5: Commit**

Message: thêm model tài chính; `appointment_id` nằm ở `invoice_items` để một hóa đơn gộp nhiều lịch hẹn theo yêu cầu mục 3.7.

---

### Task 6: Model hệ thống và AI

**Files:**
- Create: `backend/app/models/system.py`, `backend/tests/test_models_he_thong.py`
- Modify: `backend/app/models/__init__.py`

**Interfaces:**
- Produces: `AiInteractionLog`, `ActivityLog`, `AppSetting`, `Notification`.

- [ ] **Step 1: Viết test đỏ**

`backend/tests/test_models_he_thong.py`:

```python
"""Kiểm thử 4 bảng hệ thống: log AI, log thao tác, cấu hình, thông báo."""
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models import (ActivityLog, AiInteractionLog, AppSetting,
                                Notification, Owner, Pet, User, UserRole)


def test_log_ai_co_cot_latency_va_was_flagged(session):
    """Hai cột phục vụ xử lý lỗi AI mục 8.4 và số liệu báo cáo KT3."""
    u = User(username='u', password_hash='h', role=UserRole.STAFF)
    session.add(u)
    session.flush()
    log = AiInteractionLog(feature_type='qa', user_id=u.id, prompt_input='hỏi',
                           ai_response='{}', model_used='gemini-1.5-flash',
                           latency_ms=820, was_flagged=True)
    session.add(log)
    session.flush()
    assert log.latency_ms == 820
    assert log.was_flagged is True


def test_log_thao_tac_ghi_nguoi_thuc_hien(session):
    """Yêu cầu mục 4: log thao tác quan trọng kèm người thực hiện và thời gian."""
    u = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add(u)
    session.flush()
    log = ActivityLog(actor_user_id=u.id, action='tao_lich_hen',
                      entity_type='appointments', entity_id=1,
                      detail='Đặt lịch tắm cho Mực')
    session.add(log)
    session.flush()
    assert log.actor.username == 'lt'
    assert log.created_at is not None


def test_app_setting_dung_key_lam_khoa_chinh(session):
    """Cấu hình AI sửa được lúc chạy; khóa API KHÔNG bao giờ lưu ở đây."""
    u = User(username='ad', password_hash='h', role=UserRole.ADMIN)
    session.add(u)
    session.flush()
    session.add(AppSetting(key='ai_enabled', value='true', updated_by=u.id))
    session.flush()
    assert session.get(AppSetting, 'ai_enabled').value == 'true'


def test_khong_the_nhac_trung_cung_mot_lich(session):
    """Khóa duy nhất (pet_id, reminder_type, due_date) chặn job gửi trùng mỗi ngày."""
    chu = Owner(full_name='A', phone='0900000001')
    session.add(chu)
    session.flush()
    pet = Pet(owner_id=chu.id, name='Mực', species='chó')
    session.add(pet)
    session.flush()

    chung = dict(pet_id=pet.id, owner_id=chu.id, reminder_type='tiem_phong',
                 due_date=date(2027, 1, 10), channel='sms', message='Nhắc tiêm',
                 urgency='soon')
    session.add(Notification(**chung))
    session.flush()

    session.add(Notification(**chung))
    with pytest.raises(IntegrityError):
        session.flush()
```

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

- [ ] **Step 3: Viết `backend/app/models/system.py`**

Theo thiết kế mục 5.1 hàng 15–18:

- `AiInteractionLog`: `id`, `feature_type` (`db.String(32)`, bắt buộc), `user_id` (FK, rỗng được), `pet_id` (FK, rỗng được), `prompt_input` (`db.Text`), `ai_response` (`db.Text`), `model_used` (`db.String(64)`), `latency_ms` (`db.Integer`), `was_flagged` (`db.Boolean`, mặc định `False`), `created_at`.
- `ActivityLog`: `id`, `actor_user_id` (FK, bắt buộc), `action` (`db.String(64)`, bắt buộc), `entity_type` (`db.String(32)`), `entity_id` (`db.Integer`), `detail` (`db.Text`), `created_at` (mặc định `datetime.now`). Quan hệ `actor`.
- `AppSetting`: `key` (`db.String(64)`, **khóa chính**), `value` (`db.String(255)`), `updated_by` (FK), `updated_at`.
- `Notification`: `id`, `pet_id` (FK), `owner_id` (FK), `reminder_type` (`db.String(32)`), `due_date` (`db.Date`), `channel` (`db.String(16)`), `message` (`db.Text`), `urgency` (`db.String(16)`), `status` (`db.String(16)`, mặc định `'da_tao'`), `created_at`.
  Thêm ràng buộc bảng:
  ```python
  __table_args__ = (
      db.UniqueConstraint('pet_id', 'reminder_type', 'due_date',
                          name='uq_nhac_lich_khong_trung'),
  )
  ```

- [ ] **Step 4: Chạy test, xác nhận XANH — và kiểm tra đủ 18 bảng**

```powershell
pytest
```
Kỳ vọng: 28 passed.

Thêm test đếm bảng vào `backend/tests/test_models_he_thong.py`:
```python
def test_du_18_bang(app):
    """Thiết kế chốt đúng 18 bảng — không thêm, không bớt."""
    from backend.app.extensions import db
    assert len(db.metadata.tables) == 18
```
Chạy lại: 29 passed.

- [ ] **Step 5: Commit**

Message: thêm 4 bảng hệ thống, khóa duy nhất chống nhắc trùng; kiểm chứng đủ 18 bảng.

---

### Task 7: Xác thực — hash mật khẩu, đăng nhập, đăng xuất

**Files:**
- Create: `backend/app/auth/__init__.py`, `backend/app/auth/password.py`, `backend/app/auth/routes.py`
- Create: `frontend/templates/base.html`, `frontend/templates/auth/login.html`
- Create: `backend/tests/test_auth.py`
- Modify: `backend/app/main.py` (đăng ký blueprint)
- Delete: `backend/app/auth/.gitkeep`

**Interfaces:**
- Produces: `hash_password(plain: str) -> str`; `verify_password(plain: str, hashed: str) -> bool`; blueprint `auth_bp` với route `GET/POST /dang-nhap` và `POST /dang-xuat`. Sau khi đăng nhập, `session['user_id']` chứa id người dùng.

- [ ] **Step 1: Viết test đỏ**

`backend/tests/test_auth.py`:

```python
"""Kiểm thử hash mật khẩu và luồng đăng nhập, đăng xuất."""
from backend.app.auth.password import hash_password, verify_password
from backend.app.extensions import db
from backend.app.models import User, UserRole


def test_hash_khong_luu_mat_khau_dang_thuong():
    h = hash_password('matkhau123')
    assert h != 'matkhau123'
    assert 'matkhau123' not in h


def test_hai_lan_hash_cung_mat_khau_cho_ket_qua_khac_nhau():
    """bcrypt tự sinh salt ngẫu nhiên -> chống tấn công rainbow table."""
    assert hash_password('matkhau123') != hash_password('matkhau123')


def test_verify_dung_mat_khau():
    assert verify_password('matkhau123', hash_password('matkhau123')) is True


def test_verify_sai_mat_khau():
    assert verify_password('sai', hash_password('matkhau123')) is False


def test_dang_nhap_thanh_cong_tao_phien(client, app):
    with app.app_context():
        db.session.add(User(username='letan', password_hash=hash_password('mk'),
                            role=UserRole.RECEPTIONIST))
        db.session.commit()

    r = client.post('/dang-nhap', data={'username': 'letan', 'password': 'mk'})

    assert r.status_code == 302
    with client.session_transaction() as s:
        assert 'user_id' in s


def test_dang_nhap_sai_mat_khau_bao_loi_tieng_viet(client, app):
    with app.app_context():
        db.session.add(User(username='letan', password_hash=hash_password('mk'),
                            role=UserRole.RECEPTIONIST))
        db.session.commit()

    r = client.post('/dang-nhap', data={'username': 'letan', 'password': 'sai'})

    assert r.status_code == 200
    assert 'Tên đăng nhập hoặc mật khẩu không đúng' in r.get_data(as_text=True)
    with client.session_transaction() as s:
        assert 'user_id' not in s


def test_tai_khoan_bi_khoa_khong_dang_nhap_duoc(client, app):
    with app.app_context():
        db.session.add(User(username='nghi', password_hash=hash_password('mk'),
                            role=UserRole.STAFF, is_active=False))
        db.session.commit()

    r = client.post('/dang-nhap', data={'username': 'nghi', 'password': 'mk'})

    assert r.status_code == 200
    with client.session_transaction() as s:
        assert 'user_id' not in s


def test_dang_xuat_xoa_phien(client, app):
    with app.app_context():
        db.session.add(User(username='letan', password_hash=hash_password('mk'),
                            role=UserRole.RECEPTIONIST))
        db.session.commit()
    client.post('/dang-nhap', data={'username': 'letan', 'password': 'mk'})

    client.post('/dang-xuat')

    with client.session_transaction() as s:
        assert 'user_id' not in s
```

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

```powershell
pytest backend/tests/test_auth.py
```
Kỳ vọng: `ModuleNotFoundError: No module named 'backend.app.auth.password'`.

- [ ] **Step 3: Viết `backend/app/auth/password.py`**

```python
"""Hash và kiểm tra mật khẩu bằng bcrypt.

bcrypt tự sinh salt ngẫu nhiên cho mỗi lần hash, nên hai người dùng đặt
cùng mật khẩu vẫn cho hai chuỗi hash khác nhau.
"""
import bcrypt


def hash_password(plain: str) -> str:
    """Băm mật khẩu dạng thường thành chuỗi lưu được vào CSDL."""
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Kiểm tra mật khẩu người dùng nhập có khớp chuỗi đã băm không."""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
```

- [ ] **Step 4: Viết `backend/app/auth/routes.py`**

Blueprint `auth_bp` (không đặt `url_prefix`). **Tên hàm view phải đúng như dưới đây** — Task 8 gọi `url_for('auth.trang_dang_nhap')`:

| Hàm view | Route | Hành vi |
|---|---|---|
| `trang_dang_nhap()` | `GET, POST /dang-nhap` | `GET` → render `auth/login.html`. `POST` → tìm `User` theo `username`; nếu không thấy, hoặc `is_active` là `False`, hoặc `verify_password` trả `False` thì render lại kèm biến `error = 'Tên đăng nhập hoặc mật khẩu không đúng'` với mã **200**. Nếu hợp lệ thì `session.clear()`, `session['user_id'] = user.id`, `session.permanent = True`, rồi `redirect('/')` (mã 302) |
| `dang_xuat()` | `POST /dang-xuat` | `session.clear()`, `redirect(url_for('auth.trang_dang_nhap'))` |

Blueprint khai báo là `auth_bp = Blueprint('auth', __name__, ...)` — tên `'auth'` là phần trước dấu chấm trong `url_for('auth.trang_dang_nhap')`.

Truy vấn người dùng dùng `db.session.execute(db.select(User).filter_by(username=...)).scalar_one_or_none()`, **không dùng** `User.query.filter_by(...).first()` — API cũ sinh cảnh báo trên SQLAlchemy 2.x, mà skill TDD yêu cầu đầu ra sạch, không cảnh báo.

Route `/` chưa tồn tại ở mốc này nên `redirect('/')` sẽ trả 302 rồi 404 khi đi theo. Test chỉ kiểm tra mã 302 và nội dung session nên không ảnh hưởng; KT2-B sẽ thêm trang chủ.

**Lưu ý bảo mật:** thông báo lỗi phải **giống nhau** cho cả ba trường hợp (sai tên, sai mật khẩu, tài khoản bị khóa). Nếu phân biệt, kẻ tấn công dò được tên đăng nhập nào tồn tại.

- [ ] **Step 5: Viết template tối thiểu**

`frontend/templates/base.html`: khung HTML5, `lang="vi"`, nạp Bootstrap từ `url_for('static', ...)`, có khối `{% block content %}`.

`frontend/templates/auth/login.html`: kế thừa `base.html`, form POST tới `/dang-nhap` với hai ô `username`, `password`, và vùng hiển thị `error` nếu có.

Tải Bootstrap về `frontend/static/css/bootstrap.min.css` — **không dùng CDN**, để demo được khi không có mạng.

- [ ] **Step 6: Đăng ký blueprint trong `main.py`**

```python
    from backend.app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
```

Xóa `backend/app/auth/.gitkeep`.

- [ ] **Step 7: Chạy test, xác nhận XANH**

```powershell
pytest
```
Kỳ vọng: 37 passed.

- [ ] **Step 8: Commit**

Message: thêm xác thực bcrypt và luồng đăng nhập/đăng xuất bằng session; thông báo lỗi không tiết lộ tên đăng nhập nào tồn tại.

---

### Task 8: Phân quyền lớp 1 — decorator theo vai trò

**Files:**
- Create: `backend/app/auth/decorators.py`, `backend/tests/test_phan_quyen_vai_tro.py`
- Modify: `backend/app/main.py` (thêm route thử nghiệm cho test)

**Interfaces:**
- Produces: `current_user() -> User | None`; `require_role(*roles)` — decorator. Chưa đăng nhập → chuyển hướng 302 về `/dang-nhap`. Đã đăng nhập nhưng sai vai trò → 403.

**Ghi chú phạm vi:** đây mới là **lớp 1**. Lớp 2 (lọc theo quyền sở hữu dữ liệu) làm ở KT2-B, khi đã có tầng `services/` để đặt bộ lọc vào. Thiết kế mục 4.1 nêu rõ lớp 1 một mình không đủ.

- [ ] **Step 1: Viết test đỏ**

`backend/tests/test_phan_quyen_vai_tro.py`:

```python
"""Kiểm thử decorator phân quyền theo vai trò (lớp 1)."""
import pytest

from backend.app.auth.password import hash_password
from backend.app.extensions import db
from backend.app.models import User, UserRole


@pytest.fixture
def tao_nguoi_dung(app):
    """Tạo sẵn 4 tài khoản, mỗi vai trò một cái."""
    def _tao():
        with app.app_context():
            for role in UserRole:
                db.session.add(User(username=role.value,
                                    password_hash=hash_password('mk'), role=role))
            db.session.commit()
    return _tao


def dang_nhap(client, username):
    return client.post('/dang-nhap', data={'username': username, 'password': 'mk'})


def test_chua_dang_nhap_bi_chuyen_ve_trang_dang_nhap(client):
    r = client.get('/_thu-nghiem/chi-admin')
    assert r.status_code == 302
    assert '/dang-nhap' in r.headers['Location']


def test_admin_vao_duoc_route_chi_danh_cho_admin(client, tao_nguoi_dung):
    tao_nguoi_dung()
    dang_nhap(client, 'admin')
    r = client.get('/_thu-nghiem/chi-admin')
    assert r.status_code == 200


def test_nhan_vien_goi_route_bao_cao_doanh_thu_bi_403(client, tao_nguoi_dung):
    """Ca kiểm thử bắt buộc ở mục 10 đặc tả."""
    tao_nguoi_dung()
    dang_nhap(client, 'staff')
    r = client.get('/_thu-nghiem/chi-admin')
    assert r.status_code == 403


def test_le_tan_bi_chan_khoi_cau_hinh_ai(client, tao_nguoi_dung):
    """Mục 9 đặc tả: lễ tân không được cấu hình AI."""
    tao_nguoi_dung()
    dang_nhap(client, 'receptionist')
    r = client.get('/_thu-nghiem/chi-admin')
    assert r.status_code == 403


def test_route_cho_nhieu_vai_tro_chap_nhan_ca_hai(client, tao_nguoi_dung):
    tao_nguoi_dung()
    dang_nhap(client, 'receptionist')
    assert client.get('/_thu-nghiem/admin-va-le-tan').status_code == 200
    client.post('/dang-xuat')
    dang_nhap(client, 'admin')
    assert client.get('/_thu-nghiem/admin-va-le-tan').status_code == 200


def test_chu_nuoi_khong_vao_duoc_route_noi_bo(client, tao_nguoi_dung):
    tao_nguoi_dung()
    dang_nhap(client, 'owner')
    assert client.get('/_thu-nghiem/admin-va-le-tan').status_code == 403
```

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

Kỳ vọng: 404 trên route thử nghiệm hoặc `ModuleNotFoundError` — chưa có decorator lẫn route.

- [ ] **Step 3: Viết `backend/app/auth/decorators.py`**

```python
"""Phân quyền lớp 1: chặn theo vai trò.

Đây MỚI LÀ LỚP MỘT. Vai trò đúng chưa đủ: chủ nuôi A có vai trò 'owner' hợp
lệ nhưng không được xem thú cưng của chủ nuôi B. Việc lọc theo quyền sở hữu
dữ liệu nằm ở tầng services/ (KT2-B), không làm được bằng decorator vì
decorator chỉ biết vai trò, không biết bản ghi đang truy cập thuộc về ai.
"""
from functools import wraps

from flask import abort, redirect, session, url_for

from backend.app.extensions import db
from backend.app.models import User


def current_user():
    """Trả người dùng của phiên hiện tại, hoặc None nếu chưa đăng nhập."""
    user_id = session.get('user_id')
    if user_id is None:
        return None
    # db.session.get() thay cho Query.get() — API cũ sinh cảnh báo trên SQLAlchemy 2.x.
    return db.session.get(User, user_id)


def require_role(*roles):
    """Chỉ cho phép các vai trò được liệt kê truy cập route."""
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                return redirect(url_for('auth.trang_dang_nhap'))
            if user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorator
```

- [ ] **Step 4: Thêm route thử nghiệm — chỉ đăng ký ở chế độ test**

Trong `create_app()`, sau khi đăng ký blueprint:

```python
    if app.config.get('TESTING'):
        _dang_ky_route_thu_nghiem(app)
```

Hàm `_dang_ky_route_thu_nghiem(app)` đặt cuối `main.py`, đăng ký hai route `/_thu-nghiem/chi-admin` (chỉ `ADMIN`) và `/_thu-nghiem/admin-va-le-tan` (`ADMIN`, `RECEPTIONIST`), mỗi route trả chuỗi `'ok'`.

Đặt sau cờ `TESTING` để route thử nghiệm **không tồn tại khi chạy thật** — tránh mở thêm bề mặt tấn công.

- [ ] **Step 5: Chạy test, xác nhận XANH**

```powershell
pytest
```
Kỳ vọng: 43 passed.

- [ ] **Step 6: Commit**

Message: thêm decorator phân quyền theo vai trò; route thử nghiệm chỉ đăng ký ở chế độ test; ghi rõ đây mới là lớp 1, lớp 2 làm ở KT2-B.

---

### Task 9: Dữ liệu mẫu và lệnh khởi tạo CSDL

**Files:**
- Create: `backend/app/cli.py`, `database/seed_data.sql`, `backend/tests/test_seed.py`
- Modify: `backend/app/main.py` (đăng ký lệnh CLI)
- Delete: `database/.gitkeep`

**Interfaces:**
- Produces: lệnh `flask --app backend.app.main init-db` và `flask --app backend.app.main seed-db`.

- [ ] **Step 1: Viết test đỏ**

`backend/tests/test_seed.py`:

```python
"""Kiểm thử dữ liệu mẫu dùng cho demo."""
from pathlib import Path

from sqlalchemy import text

from backend.app.extensions import db
from backend.app.models import CareRecord, Owner, Pet, Service

SEED = Path(__file__).resolve().parents[2] / 'database' / 'seed_data.sql'


def _nap_seed():
    """Nạp toàn bộ câu lệnh trong seed_data.sql vào CSDL đang mở."""
    for cau in SEED.read_text(encoding='utf-8').split(';'):
        if cau.strip():
            db.session.execute(text(cau))
    db.session.commit()


def test_seed_du_so_luong_toi_thieu(app):
    """Mục 15 đặc tả: tối thiểu 5 chủ nuôi, 8 thú cưng."""
    with app.app_context():
        _nap_seed()
        assert Owner.query.count() >= 5
        assert Pet.query.count() >= 8
        assert Service.query.count() >= 5


def test_co_thu_cung_sut_can_lien_tuc(app):
    """Cần ít nhất 1 con có xu hướng sụt cân để chức năng tóm tắt AI ở KT3
    thực sự bật cờ cảnh báo khi demo, thay vì tóm tắt hồ sơ nhạt nhòa."""
    with app.app_context():
        _nap_seed()
        for pet in Pet.query.all():
            ho_so = (CareRecord.query
                     .filter_by(pet_id=pet.id)
                     .order_by(CareRecord.record_date)
                     .all())
            if len(ho_so) >= 3:
                can_nang = [r.weight_at_visit for r in ho_so]
                if all(b < a for a, b in zip(can_nang, can_nang[1:])):
                    return
        assert False, 'Không có thú cưng nào sụt cân liên tục qua 3 lần khám trở lên'


def test_moi_vai_tro_deu_co_it_nhat_mot_tai_khoan(app):
    from backend.app.models import User, UserRole
    with app.app_context():
        _nap_seed()
        for role in UserRole:
            assert User.query.filter_by(role=role).count() >= 1, f'Thiếu tài khoản {role.value}'
```

- [ ] **Step 2: Chạy test, xác nhận ĐỎ**

Kỳ vọng: `FileNotFoundError` vì chưa có `database/seed_data.sql`.

- [ ] **Step 3: Viết `database/seed_data.sql`**

Nội dung tối thiểu:
- **6 tài khoản:** 1 `admin`, 1 `receptionist`, 2 `staff`, 2 `owner` (hai tài khoản `owner` có `owner_id` trỏ về hai chủ nuôi khác nhau — cần cho ca kiểm thử truy cập chéo ở KT2-B). Mật khẩu hash bcrypt của chuỗi `demo1234`; sinh hash bằng `python -c "from backend.app.auth.password import hash_password; print(hash_password('demo1234'))"` rồi dán vào file.
- **6 chủ nuôi**, mỗi người 1–3 thú cưng, tổng **9 thú cưng**.
- **6 dịch vụ** trải đủ 4 danh mục, **2 gói dịch vụ** với `package_items` tương ứng.
- **Hồ sơ chăm sóc trải 4 tháng**: mỗi thú cưng 2–5 bản ghi. Riêng thú cưng `id = 3` có **4 bản ghi cân nặng giảm dần** (ví dụ 8.5 → 8.1 → 7.6 → 7.0 kg) — đây là dữ liệu để chức năng tóm tắt AI bật cờ.
- **Lịch tiêm**: vài mũi đã quá hạn, vài mũi sắp đến hạn, vài mũi đã tiêm.
- **Lịch hẹn** trải đủ 4 trạng thái.

Mọi câu lệnh dùng `INSERT INTO ... VALUES ...;`, mỗi câu một dòng logic, kết thúc bằng `;`. Thêm chú thích `--` tiếng Việt cho từng khối.

**Ràng buộc bắt buộc:** hàm nạp trong test tách câu lệnh bằng cách cắt theo dấu `;`, nên **không được dùng dấu `;` bên trong chuỗi** (ghi chú, tên, địa chỉ). Nếu cần ngăn cách trong ghi chú thì dùng dấu phẩy hoặc gạch ngang.

- [ ] **Step 4: Viết `backend/app/cli.py`**

Hai lệnh Flask CLI:
- `init-db`: gọi `db.create_all()`, in ra số bảng đã tạo.
- `seed-db`: đọc `database/seed_data.sql`, thực thi từng câu, in số bản ghi từng bảng chính. **Từ chối chạy nếu bảng `owners` đã có dữ liệu**, trừ khi truyền cờ `--force` — tránh nạp chồng dữ liệu thành trùng lặp.

Đăng ký trong `create_app()`: `from backend.app.cli import dang_ky_lenh; dang_ky_lenh(app)`.

- [ ] **Step 5: Chạy test, xác nhận XANH**

```powershell
pytest
```
Kỳ vọng: 46 passed.

- [ ] **Step 6: Kiểm chứng thủ công đầu-cuối**

```powershell
copy backend\.env.example backend\.env
flask --app backend.app.main init-db
flask --app backend.app.main seed-db
flask --app backend.app.main run
```

Mở `http://127.0.0.1:5000/dang-nhap`, đăng nhập bằng `admin` / `demo1234`, xác nhận vào được. Đăng xuất, đăng nhập bằng tài khoản `staff`, xác nhận vẫn vào được trang chính.

Sau khi kiểm tra xong: **xóa `backend/.env` và `pet_care.db`** — cả hai đã bị `.gitignore` loại trừ, nhưng xóa để chắc chắn không lẫn vào commit.

- [ ] **Step 7: Commit**

Message: thêm dữ liệu mẫu 6 chủ nuôi/9 thú cưng/hồ sơ 4 tháng và hai lệnh CLI khởi tạo CSDL; dữ liệu có sẵn ca sụt cân liên tục cho chức năng tóm tắt AI ở KT3.

---

## Kết quả mong đợi sau 9 task

| Hạng mục | Số lượng |
|---|---|
| Commit | 9 |
| Bảng CSDL | 18 |
| Test | 46, tất cả xanh |
| Chạy được | Đăng nhập 4 vai trò, phân quyền lớp 1 hoạt động, CSDL có dữ liệu mẫu |
| Chưa làm (để KT2-B) | Phân quyền lớp 2, toàn bộ CRUD nghiệp vụ, chống trùng lịch |

## Tự rà soát trước khi kết thúc KT2-A

```powershell
# Không có mã nào trong services/ import ai/ — ràng buộc kiến trúc xuyên suốt
Select-String -Path backend\app\services\*.py -Pattern "from backend.app.ai|import ai"

# Không có .env hay file CSDL lọt vào git
git ls-files | Select-String -Pattern "\.env$|\.db$"

# Không có mật khẩu dạng thường trong mã nguồn
Select-String -Path backend\app\*.py,backend\app\**\*.py -Pattern "password\s*=\s*['\"][^'\"]+['\"]"
```

Cả ba lệnh phải **không trả về kết quả nào**.

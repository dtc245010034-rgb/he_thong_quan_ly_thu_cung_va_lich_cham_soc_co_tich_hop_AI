"""Nghiệp vụ quản lý chủ nuôi.

PHÂN QUYỀN LỚP 2 nằm ở đây. Decorator require_role ở tầng route chỉ biết vai
trò, không biết bản ghi đang truy cập thuộc về ai — nên chủ nuôi A có vai trò
'owner' hợp lệ vẫn có thể đổi tham số id trên URL để xem hồ sơ nhà B. Việc
chặn chuyện đó là trách nhiệm của tầng này.
"""
from datetime import datetime

from backend.app.extensions import db
from backend.app.models import Appointment, Invoice, Owner, Pet, UserRole
from backend.app.services import activity_log_service
from backend.app.services.errors import DuLieuKhongHopLe, QuyenTruyCapBiTuChoi

# Vai trò được phép thêm, sửa, xóa hồ sơ chủ nuôi (mục 3.1 đặc tả).
_VAI_TRO_QUAN_LY_HO_SO = (UserRole.ADMIN, UserRole.RECEPTIONIST)


def _bat_buoc_vai_tro_quan_ly(current_user):
    """Chặn mọi vai trò không được phép sửa hồ sơ chủ nuôi."""
    if current_user.role not in _VAI_TRO_QUAN_LY_HO_SO:
        raise QuyenTruyCapBiTuChoi(
            'Bạn không có quyền thay đổi hồ sơ chủ nuôi'
        )


def _bat_buoc_quyen_tren_chu_nuoi(owner_id, current_user):
    """Chủ nuôi chỉ được thao tác trên hồ sơ của chính mình."""
    if (current_user.role == UserRole.OWNER
            and current_user.owner_id != owner_id):
        raise QuyenTruyCapBiTuChoi(
            'Bạn không có quyền xem hồ sơ của chủ nuôi khác'
        )


def danh_sach(current_user, tu_khoa=None):
    """Danh sách chủ nuôi chưa bị xóa mềm, đã lọc theo quyền của người dùng."""
    truy_van = db.select(Owner).where(Owner.is_deleted.is_(False))

    # Lớp 2: tài khoản chủ nuôi chỉ thấy đúng hồ sơ của mình.
    if current_user.role == UserRole.OWNER:
        truy_van = truy_van.where(Owner.id == current_user.owner_id)

    if tu_khoa:
        mau = f'%{tu_khoa}%'
        truy_van = truy_van.where(
            db.or_(Owner.full_name.like(mau), Owner.phone.like(mau))
        )

    return list(db.session.execute(truy_van.order_by(Owner.full_name))
                .scalars().all())


def lay_theo_id(owner_id, current_user):
    """Lấy một chủ nuôi, kiểm tra quyền trước khi trả về."""
    _bat_buoc_quyen_tren_chu_nuoi(owner_id, current_user)

    chu = db.session.get(Owner, owner_id)
    if chu is None or chu.is_deleted:
        raise DuLieuKhongHopLe('Không tìm thấy chủ nuôi này')
    return chu


def tao(du_lieu, current_user):
    """Tạo hồ sơ chủ nuôi mới."""
    _bat_buoc_vai_tro_quan_ly(current_user)
    _kiem_tra_du_lieu(du_lieu, bat_buoc_day_du=True)

    chu = Owner(
        full_name=du_lieu['full_name'].strip(),
        phone=du_lieu['phone'].strip(),
        email=(du_lieu.get('email') or None),
        address=(du_lieu.get('address') or None),
    )
    db.session.add(chu)
    db.session.flush()  # cần id để ghi nhật ký

    activity_log_service.ghi(current_user, 'tao_chu_nuoi', 'owners', chu.id,
                             f'Tạo hồ sơ chủ nuôi {chu.full_name}')
    return chu


def cap_nhat(owner_id, du_lieu, current_user):
    """Cập nhật hồ sơ chủ nuôi."""
    _bat_buoc_vai_tro_quan_ly(current_user)
    chu = lay_theo_id(owner_id, current_user)
    _kiem_tra_du_lieu(du_lieu, bat_buoc_day_du=False)

    for truong in ('full_name', 'phone', 'email', 'address'):
        if truong in du_lieu:
            gia_tri = du_lieu[truong]
            setattr(chu, truong, gia_tri.strip() if gia_tri else None)

    activity_log_service.ghi(current_user, 'sua_chu_nuoi', 'owners', chu.id,
                             f'Cập nhật hồ sơ chủ nuôi {chu.full_name}')
    return chu


def xoa_mem(owner_id, current_user):
    """Xóa mềm hồ sơ chủ nuôi.

    Trả về số bản ghi liên quan để giao diện cảnh báo trước khi xác nhận
    (mục 3.2 đặc tả). Không xóa cứng vì các hóa đơn cũ vẫn trỏ về chủ nuôi.
    """
    _bat_buoc_vai_tro_quan_ly(current_user)
    chu = lay_theo_id(owner_id, current_user)

    so_thu_cung = db.session.execute(
        db.select(db.func.count(Pet.id))
        .where(Pet.owner_id == owner_id, Pet.is_deleted.is_(False))
    ).scalar_one()
    so_lich_hen = db.session.execute(
        db.select(db.func.count(Appointment.id))
        .join(Pet, Appointment.pet_id == Pet.id)
        .where(Pet.owner_id == owner_id)
    ).scalar_one()
    so_hoa_don = db.session.execute(
        db.select(db.func.count(Invoice.id)).where(Invoice.owner_id == owner_id)
    ).scalar_one()

    chu.is_deleted = True
    chu.deleted_at = datetime.now()

    activity_log_service.ghi(current_user, 'xoa_chu_nuoi', 'owners', chu.id,
                             f'Xóa mềm hồ sơ chủ nuôi {chu.full_name}')

    return {
        'so_thu_cung': so_thu_cung,
        'so_lich_hen': so_lich_hen,
        'so_hoa_don': so_hoa_don,
    }


def _kiem_tra_du_lieu(du_lieu, bat_buoc_day_du):
    """Kiểm tra dữ liệu đầu vào, báo lỗi bằng tiếng Việt nêu rõ trường nào sai."""
    if bat_buoc_day_du or 'full_name' in du_lieu:
        if not (du_lieu.get('full_name') or '').strip():
            raise DuLieuKhongHopLe('Họ tên chủ nuôi không được để trống')
    if bat_buoc_day_du or 'phone' in du_lieu:
        if not (du_lieu.get('phone') or '').strip():
            raise DuLieuKhongHopLe('Số điện thoại không được để trống')

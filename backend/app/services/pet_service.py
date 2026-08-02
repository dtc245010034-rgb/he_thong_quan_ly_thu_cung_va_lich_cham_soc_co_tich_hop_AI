"""Nghiệp vụ quản lý thú cưng.

Cùng nguyên tắc phân quyền lớp 2 như owner_service, nhưng quyền được xét
qua pet.owner_id thay vì owner.id.
"""
from datetime import datetime

from backend.app.extensions import db
from backend.app.models import Owner, Pet, UserRole
from backend.app.services import activity_log_service
from backend.app.services.errors import DuLieuKhongHopLe, QuyenTruyCapBiTuChoi

_VAI_TRO_QUAN_LY_HO_SO = (UserRole.ADMIN, UserRole.RECEPTIONIST)


def _bat_buoc_vai_tro_quan_ly(current_user):
    if current_user.role not in _VAI_TRO_QUAN_LY_HO_SO:
        raise QuyenTruyCapBiTuChoi(
            'Bạn không có quyền thay đổi hồ sơ thú cưng'
        )


def _bat_buoc_quyen_tren_thu_cung(pet, current_user):
    """Chủ nuôi chỉ xem được thú cưng nhà mình.

    Nhân viên chăm sóc xem được mọi thú cưng vì cần nắm hồ sơ trước khi
    phục vụ (mục 3.1 đặc tả).
    """
    if (current_user.role == UserRole.OWNER
            and pet.owner_id != current_user.owner_id):
        raise QuyenTruyCapBiTuChoi(
            'Bạn không có quyền xem thú cưng của chủ nuôi khác'
        )


def danh_sach(current_user, owner_id=None, tu_khoa=None):
    """Danh sách thú cưng chưa bị xóa mềm, đã lọc theo quyền."""
    truy_van = db.select(Pet).where(Pet.is_deleted.is_(False))

    # Lớp 2: tài khoản chủ nuôi chỉ thấy thú cưng của mình.
    if current_user.role == UserRole.OWNER:
        truy_van = truy_van.where(Pet.owner_id == current_user.owner_id)
    elif owner_id is not None:
        truy_van = truy_van.where(Pet.owner_id == owner_id)

    if tu_khoa:
        mau = f'%{tu_khoa}%'
        truy_van = (truy_van.join(Owner, Pet.owner_id == Owner.id)
                    .where(db.or_(Pet.name.like(mau), Owner.full_name.like(mau))))

    return list(db.session.execute(truy_van.order_by(Pet.name)).scalars().all())


def lay_theo_id(pet_id, current_user):
    """Lấy một thú cưng, kiểm tra quyền trước khi trả về."""
    pet = db.session.get(Pet, pet_id)
    if pet is None or pet.is_deleted:
        raise DuLieuKhongHopLe('Không tìm thấy thú cưng này')

    _bat_buoc_quyen_tren_thu_cung(pet, current_user)
    return pet


def tao(du_lieu, current_user):
    """Tạo hồ sơ thú cưng mới, gắn với đúng một chủ nuôi."""
    _bat_buoc_vai_tro_quan_ly(current_user)
    _kiem_tra_du_lieu(du_lieu, bat_buoc_day_du=True)

    chu = db.session.get(Owner, du_lieu['owner_id'])
    if chu is None or chu.is_deleted:
        raise DuLieuKhongHopLe('Chủ nuôi không tồn tại hoặc đã bị xóa')

    pet = Pet(
        owner_id=chu.id,
        name=du_lieu['name'].strip(),
        species=du_lieu['species'].strip(),
        breed=(du_lieu.get('breed') or None),
        gender=(du_lieu.get('gender') or None),
        birth_date=du_lieu.get('birth_date'),
        weight=du_lieu.get('weight'),
        color=(du_lieu.get('color') or None),
        notes=(du_lieu.get('notes') or None),
    )
    db.session.add(pet)
    db.session.flush()

    activity_log_service.ghi(current_user, 'tao_thu_cung', 'pets', pet.id,
                             f'Tạo hồ sơ thú cưng {pet.name}')
    return pet


def cap_nhat(pet_id, du_lieu, current_user):
    """Cập nhật hồ sơ thú cưng."""
    _bat_buoc_vai_tro_quan_ly(current_user)
    pet = lay_theo_id(pet_id, current_user)
    _kiem_tra_du_lieu(du_lieu, bat_buoc_day_du=False)

    for truong in ('name', 'species', 'breed', 'gender', 'color', 'notes'):
        if truong in du_lieu:
            gia_tri = du_lieu[truong]
            setattr(pet, truong, gia_tri.strip() if gia_tri else None)
    for truong in ('birth_date', 'weight'):
        if truong in du_lieu:
            setattr(pet, truong, du_lieu[truong])

    activity_log_service.ghi(current_user, 'sua_thu_cung', 'pets', pet.id,
                             f'Cập nhật hồ sơ thú cưng {pet.name}')
    return pet


def xoa_mem(pet_id, current_user):
    """Xóa mềm hồ sơ thú cưng — không xóa cứng vì lịch hẹn cũ vẫn trỏ về nó."""
    _bat_buoc_vai_tro_quan_ly(current_user)
    pet = lay_theo_id(pet_id, current_user)

    pet.is_deleted = True
    pet.deleted_at = datetime.now()

    activity_log_service.ghi(current_user, 'xoa_thu_cung', 'pets', pet.id,
                             f'Xóa mềm hồ sơ thú cưng {pet.name}')
    return pet


def _kiem_tra_du_lieu(du_lieu, bat_buoc_day_du):
    """Kiểm tra dữ liệu đầu vào, báo lỗi bằng tiếng Việt nêu rõ trường nào sai."""
    if bat_buoc_day_du and du_lieu.get('owner_id') is None:
        raise DuLieuKhongHopLe('Phải chọn chủ nuôi cho thú cưng')
    if bat_buoc_day_du or 'name' in du_lieu:
        if not (du_lieu.get('name') or '').strip():
            raise DuLieuKhongHopLe('Tên thú cưng không được để trống')
    if bat_buoc_day_du or 'species' in du_lieu:
        if not (du_lieu.get('species') or '').strip():
            raise DuLieuKhongHopLe('Loài thú cưng không được để trống')

"""Nghiệp vụ nhắc lịch tiêm phòng.

CHỈ Ở MỨC NHẮC LỊCH (mục 3.6 đặc tả). Việc tiêm thực tế do phòng khám thú y
bên ngoài thực hiện, hệ thống này không quản lý hồ sơ y tế.

Bảng vaccination_schedules KHÔNG có cột status (sai khác ④). Hai trạng thái
"sắp đến hạn" và "quá hạn" phụ thuộc ngày hiện tại nên được tính lúc truy
vấn; lưu cứng thì hôm sau đã sai, trừ khi thêm một job chỉ để cập nhật cột
đó — một điểm hỏng không cần thiết.
"""
from datetime import timedelta

from flask import current_app

from backend.app.extensions import db
from backend.app.models import Pet, UserRole, VaccinationSchedule
from backend.app.services import activity_log_service
from backend.app.services.errors import (DuLieuKhongHopLe,
                                         QuyenTruyCapBiTuChoi)

# Chu kỳ mặc định giữa hai lần tiêm. Phần lớn vắc-xin cho chó mèo tiêm nhắc
# lại hằng năm.
CHU_KY_MAC_DINH_NGAY = 365

_VAI_TRO_QUAN_LY = (UserRole.ADMIN, UserRole.RECEPTIONIST)


def _nguong_sap_den_han():
    """Số ngày trước hạn thì coi là sắp đến hạn, đọc từ cấu hình."""
    return current_app.config.get('VACCINE_DUE_SOON_DAYS', 7)


def tinh_trang_thai(lich, hom_nay):
    """Tính trạng thái hiển thị của một mũi tiêm.

    Nhận hom_nay làm THAM SỐ thay vì gọi date.today() bên trong. Nếu tự lấy
    ngày hiện tại thì test sẽ phụ thuộc ngày chạy máy và đỏ vào một ngày nào
    đó trong tương lai — loại lỗi rất khó truy khi xảy ra.
    """
    if lich.is_done:
        return 'da_tiem'
    if lich.next_due_date < hom_nay:
        return 'qua_han'
    if lich.next_due_date <= hom_nay + timedelta(days=_nguong_sap_den_han()):
        return 'sap_den_han'
    return 'binh_thuong'


def danh_sach_theo_thu_cung(pet_id, current_user):
    """Toàn bộ lịch tiêm của một thú cưng."""
    from backend.app.services import pet_service
    pet_service.lay_theo_id(pet_id, current_user)

    return list(db.session.execute(
        db.select(VaccinationSchedule)
        .where(VaccinationSchedule.pet_id == pet_id)
        .order_by(VaccinationSchedule.next_due_date)
    ).scalars().all())


def danh_sach_sap_den_han(current_user, hom_nay, so_ngay=None):
    """Các mũi tiêm sắp đến hạn HOẶC đã quá hạn, chưa tiêm.

    Gộp cả quá hạn vào đây vì màn hình nhắc tiêm mà bỏ sót mũi đã quá hạn
    thì mất luôn ý nghĩa nhắc nhở.
    """
    nguong = hom_nay + timedelta(days=so_ngay if so_ngay is not None
                                 else _nguong_sap_den_han())

    truy_van = (db.select(VaccinationSchedule)
                .join(Pet, VaccinationSchedule.pet_id == Pet.id)
                .where(VaccinationSchedule.is_done.is_(False),
                       VaccinationSchedule.next_due_date <= nguong,
                       Pet.is_deleted.is_(False)))

    # Phân quyền lớp 2: chủ nuôi chỉ thấy lịch tiêm của thú cưng nhà mình.
    if current_user.role == UserRole.OWNER:
        truy_van = truy_van.where(Pet.owner_id == current_user.owner_id)

    return list(db.session.execute(
        truy_van.order_by(VaccinationSchedule.next_due_date)).scalars().all())


def tao(du_lieu, current_user):
    """Thêm một mũi tiêm cần theo dõi."""
    if current_user.role not in _VAI_TRO_QUAN_LY:
        raise QuyenTruyCapBiTuChoi('Bạn không có quyền thêm lịch tiêm phòng')

    from backend.app.services import pet_service
    pet = pet_service.lay_theo_id(du_lieu.get('pet_id'), current_user)

    if not (du_lieu.get('vaccine_name') or '').strip():
        raise DuLieuKhongHopLe('Phải nhập tên vắc-xin')
    if du_lieu.get('next_due_date') is None:
        raise DuLieuKhongHopLe('Phải nhập ngày đến hạn tiêm tiếp theo')

    lich = VaccinationSchedule(
        pet_id=pet.id,
        vaccine_name=du_lieu['vaccine_name'].strip(),
        last_date=du_lieu.get('last_date'),
        next_due_date=du_lieu['next_due_date'],
    )
    db.session.add(lich)
    db.session.flush()

    activity_log_service.ghi(
        current_user, 'tao_lich_tiem', 'vaccination_schedules', lich.id,
        f'Thêm lịch tiêm {lich.vaccine_name} cho {pet.name}')
    return lich


def danh_dau_da_tiem(vaccination_id, current_user, ngay_tiem,
                     chu_ky_ngay=CHU_KY_MAC_DINH_NGAY):
    """Đánh dấu đã tiêm và sinh lịch cho kỳ tiếp theo.

    Sinh luôn kỳ kế tiếp thay vì bắt lễ tân nhập tay, vì bỏ sót bước đó là
    cách phổ biến nhất khiến thú cưng lỡ mũi nhắc lại.
    """
    if current_user.role not in _VAI_TRO_QUAN_LY:
        raise QuyenTruyCapBiTuChoi('Bạn không có quyền cập nhật lịch tiêm')

    lich = db.session.get(VaccinationSchedule, vaccination_id)
    if lich is None:
        raise DuLieuKhongHopLe('Không tìm thấy lịch tiêm này')
    if lich.is_done:
        raise DuLieuKhongHopLe('Mũi tiêm này đã được đánh dấu hoàn thành')

    lich.is_done = True
    lich.last_date = ngay_tiem

    ke_tiep = VaccinationSchedule(
        pet_id=lich.pet_id,
        vaccine_name=lich.vaccine_name,
        last_date=ngay_tiem,
        next_due_date=ngay_tiem + timedelta(days=chu_ky_ngay),
    )
    db.session.add(ke_tiep)
    db.session.flush()

    activity_log_service.ghi(
        current_user, 'danh_dau_da_tiem', 'vaccination_schedules', lich.id,
        f'Đánh dấu đã tiêm {lich.vaccine_name}, hẹn lại '
        f'{ke_tiep.next_due_date}')
    return lich

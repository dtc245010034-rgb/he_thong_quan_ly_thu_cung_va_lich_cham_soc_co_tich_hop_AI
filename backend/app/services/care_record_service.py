"""Nghiệp vụ hồ sơ chăm sóc.

Hồ sơ này là đầu vào chính của chức năng tóm tắt AI ở KT3, nên hai trường
có cấu trúc record_date và weight_at_visit là bắt buộc: chúng cho phép AI so
sánh xu hướng cân nặng qua các lần khám thay vì chỉ đọc ghi chú rời rạc.
"""
from decimal import Decimal

from backend.app.extensions import db
from backend.app.models import (Appointment, AppointmentStatus, CareRecord,
                                UserRole)
from backend.app.services import activity_log_service, pet_service
from backend.app.services.errors import (DuLieuKhongHopLe,
                                         QuyenTruyCapBiTuChoi)

_VAI_TRO_GHI_HO_SO = (UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.STAFF)


def ghi_ho_so(du_lieu, current_user):
    """Ghi hồ sơ chăm sóc sau một buổi hẹn đã hoàn thành."""
    if current_user.role not in _VAI_TRO_GHI_HO_SO:
        raise QuyenTruyCapBiTuChoi('Bạn không có quyền ghi hồ sơ chăm sóc')

    _kiem_tra_du_lieu(du_lieu)

    # lay_theo_id đã kiểm tra quyền sở hữu, dùng lại thay vì tự truy vấn.
    pet = pet_service.lay_theo_id(du_lieu['pet_id'], current_user)

    lich = None
    if du_lieu.get('appointment_id'):
        lich = db.session.get(Appointment, du_lieu['appointment_id'])
        if lich is None:
            raise DuLieuKhongHopLe('Không tìm thấy lịch hẹn này')
        if lich.status != AppointmentStatus.COMPLETED:
            raise DuLieuKhongHopLe(
                'Chỉ ghi hồ sơ cho buổi hẹn đã hoàn thành. '
                'Hãy đánh dấu hoàn thành trước.'
            )
        # Nhân viên chỉ ghi hồ sơ cho lịch do mình phụ trách (mục 4.2).
        if (current_user.role == UserRole.STAFF
                and lich.staff_id != current_user.id):
            raise QuyenTruyCapBiTuChoi(
                'Bạn chỉ ghi được hồ sơ cho buổi hẹn do mình phụ trách'
            )

    ho_so = CareRecord(
        pet_id=pet.id,
        appointment_id=lich.id if lich else None,
        staff_id=current_user.id,
        record_date=du_lieu['record_date'],
        weight_at_visit=du_lieu['weight_at_visit'],
        condition_notes=(du_lieu.get('condition_notes') or None),
        treatment_notes=(du_lieu.get('treatment_notes') or None),
        next_recommendation=(du_lieu.get('next_recommendation') or None),
    )
    db.session.add(ho_so)

    # Hồ sơ mới làm bản tóm tắt AI cũ lỗi thời. Không xóa cache ở đây thì ở
    # KT3 nhân viên sẽ đọc bản tóm tắt không còn phản ánh lần khám mới nhất.
    pet.ai_summary_cache = None
    pet.ai_summary_cached_at = None

    db.session.flush()
    activity_log_service.ghi(
        current_user, 'ghi_ho_so_cham_soc', 'care_records', ho_so.id,
        f'Ghi hồ sơ chăm sóc cho {pet.name} ngày {ho_so.record_date}')
    return ho_so


def danh_sach_theo_thu_cung(pet_id, current_user):
    """Hồ sơ chăm sóc của một thú cưng, sắp xếp theo ngày tăng dần.

    Sắp xếp tăng dần để so sánh được xu hướng cân nặng qua các lần khám —
    đây cũng là thứ tự mà chức năng tóm tắt AI ở KT3 cần.
    """
    # Kiểm tra quyền xem thú cưng trước, rồi mới lấy hồ sơ của nó.
    pet_service.lay_theo_id(pet_id, current_user)

    return list(db.session.execute(
        db.select(CareRecord)
        .where(CareRecord.pet_id == pet_id)
        .order_by(CareRecord.record_date)
    ).scalars().all())


def _kiem_tra_du_lieu(du_lieu):
    """Kiểm tra dữ liệu bắt buộc, báo lỗi nêu rõ trường nào thiếu."""
    if du_lieu.get('record_date') is None:
        raise DuLieuKhongHopLe('Phải nhập ngày ghi hồ sơ')

    can_nang = du_lieu.get('weight_at_visit')
    if can_nang is None:
        raise DuLieuKhongHopLe('Phải nhập cân nặng tại thời điểm khám')
    if Decimal(can_nang) <= 0:
        raise DuLieuKhongHopLe('Cân nặng phải lớn hơn 0')

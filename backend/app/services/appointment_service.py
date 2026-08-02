"""Nghiệp vụ lịch hẹn: đặt lịch, chống trùng, xác nhận, hoàn thành.

Chống trùng lịch là quy tắc nghiệp vụ dễ sai nhất của dự án. Xem docstring
của _tim_lich_trung để hiểu vì sao điều kiện phải dùng dấu nhỏ hơn thay vì
nhỏ hơn hoặc bằng.
"""
from datetime import datetime, timedelta

from backend.app.extensions import db
from backend.app.models import (Appointment, AppointmentStatus, Pet, Service,
                                UserRole)
from backend.app.services import activity_log_service
from backend.app.services.errors import (DuLieuKhongHopLe,
                                         QuyenTruyCapBiTuChoi, TrungLichHen)

# Chỉ hai trạng thái này mới chiếm chỗ của nhân viên. Lịch đã hoàn thành
# hoặc đã hủy thì không chặn lịch mới.
_TRANG_THAI_CHIEM_CHO = (AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED)

_VAI_TRO_DAT_LICH = (UserRole.ADMIN, UserRole.RECEPTIONIST)


def _bat_buoc_vai_tro_dat_lich(current_user):
    """Mục 3.4: đặt lịch là việc của lễ tân, chủ nuôi chỉ xem."""
    if current_user.role not in _VAI_TRO_DAT_LICH:
        raise QuyenTruyCapBiTuChoi(
            'Bạn không có quyền đặt hoặc thay đổi lịch hẹn'
        )


def _tim_lich_trung(staff_id, bat_dau, ket_thuc, bo_qua_id=None):
    """Tìm lịch hẹn chồng khung giờ của cùng một nhân viên.

    Điều kiện chồng lấn: bat_dau < old_end AND old_start < ket_thuc.

    Dùng dấu NHỎ HƠN chứ không phải nhỏ hơn hoặc bằng. Nếu dùng <= thì hai
    lịch kề sát nhau — lịch cũ kết thúc đúng lúc lịch mới bắt đầu — sẽ bị
    coi là trùng, và nhân viên mất một chỗ trống hoàn toàn hợp lệ.

    bo_qua_id dùng khi đổi lịch: bản ghi đang sửa không được tự chặn chính nó.
    """
    if staff_id is None:
        return None

    dieu_kien = [
        Appointment.staff_id == staff_id,
        Appointment.status.in_(_TRANG_THAI_CHIEM_CHO),
        Appointment.scheduled_at < ket_thuc,
        bat_dau < Appointment.ends_at,
    ]
    if bo_qua_id is not None:
        dieu_kien.append(Appointment.id != bo_qua_id)

    return db.session.execute(
        db.select(Appointment).where(*dieu_kien)
    ).scalars().first()


def _bao_trung_lich(lich_trung):
    """Ném lỗi trùng lịch kèm thông tin cụ thể, không báo chung chung.

    Yêu cầu trải nghiệm mục 4: thông báo lỗi phải nêu rõ nguyên nhân để lễ
    tân biết chọn khung giờ nào khác, thay vì chỉ nói "trùng lịch".
    """
    ten_nv = (lich_trung.staff.full_name or lich_trung.staff.username)
    raise TrungLichHen(
        f'Nhân viên {ten_nv} đã có lịch khác từ '
        f'{lich_trung.scheduled_at:%H:%M %d/%m/%Y} đến '
        f'{lich_trung.ends_at:%H:%M}. Vui lòng chọn khung giờ khác '
        f'hoặc nhân viên khác.'
    )


def dat_lich(du_lieu, current_user):
    """Đặt lịch hẹn mới.

    ends_at được tính và LƯU tại đây, không tính lại lúc đọc. Nhờ vậy nếu
    quản lý sửa duration_minutes của dịch vụ sau này thì các lịch đã đặt
    không bị dịch chuyển ngầm.
    """
    _bat_buoc_vai_tro_dat_lich(current_user)

    bat_dau = du_lieu.get('scheduled_at')
    if not isinstance(bat_dau, datetime):
        raise DuLieuKhongHopLe('Phải chọn thời gian bắt đầu hợp lệ')
    if bat_dau < datetime.now():
        raise DuLieuKhongHopLe('Không thể đặt lịch ở thời điểm đã qua')

    pet = db.session.get(Pet, du_lieu.get('pet_id'))
    if pet is None or pet.is_deleted:
        raise DuLieuKhongHopLe('Thú cưng không tồn tại hoặc đã bị xóa')

    dich_vu = db.session.get(Service, du_lieu.get('service_id'))
    if dich_vu is None or not dich_vu.is_active:
        raise DuLieuKhongHopLe('Dịch vụ không tồn tại hoặc đã ngừng bán')

    ket_thuc = bat_dau + timedelta(minutes=dich_vu.duration_minutes)
    staff_id = du_lieu.get('staff_id')

    lich_trung = _tim_lich_trung(staff_id, bat_dau, ket_thuc)
    if lich_trung is not None:
        _bao_trung_lich(lich_trung)

    lich = Appointment(
        pet_id=pet.id,
        service_id=dich_vu.id,
        staff_id=staff_id,
        scheduled_at=bat_dau,
        ends_at=ket_thuc,
        status=AppointmentStatus.PENDING,
        notes=(du_lieu.get('notes') or None),
        created_by=current_user.id,
    )
    db.session.add(lich)
    db.session.flush()

    activity_log_service.ghi(
        current_user, 'tao_lich_hen', 'appointments', lich.id,
        f'Đặt lịch {dich_vu.name} cho {pet.name} lúc {bat_dau:%H:%M %d/%m/%Y}')
    return lich


def danh_sach(current_user, tu_ngay=None, den_ngay=None, trang_thai=None,
              staff_id=None):
    """Danh sách lịch hẹn, đã lọc theo quyền của người đang đăng nhập.

    Nhân viên chỉ thấy lịch của mình; chủ nuôi chỉ thấy lịch của thú cưng
    nhà mình (ma trận quyền mục 4.2).
    """
    truy_van = db.select(Appointment)

    if current_user.role == UserRole.STAFF:
        truy_van = truy_van.where(Appointment.staff_id == current_user.id)
    elif current_user.role == UserRole.OWNER:
        truy_van = (truy_van.join(Pet, Appointment.pet_id == Pet.id)
                    .where(Pet.owner_id == current_user.owner_id))
    elif staff_id is not None:
        truy_van = truy_van.where(Appointment.staff_id == staff_id)

    if tu_ngay is not None:
        truy_van = truy_van.where(Appointment.scheduled_at >= tu_ngay)
    if den_ngay is not None:
        truy_van = truy_van.where(Appointment.scheduled_at <= den_ngay)
    if trang_thai is not None:
        truy_van = truy_van.where(Appointment.status == trang_thai)

    return list(db.session.execute(
        truy_van.order_by(Appointment.scheduled_at)).scalars().all())


def lay_theo_id(appointment_id, current_user):
    """Lấy một lịch hẹn, kiểm tra quyền trước khi trả về."""
    lich = db.session.get(Appointment, appointment_id)
    if lich is None:
        raise DuLieuKhongHopLe('Không tìm thấy lịch hẹn này')

    if (current_user.role == UserRole.OWNER
            and lich.pet.owner_id != current_user.owner_id):
        raise QuyenTruyCapBiTuChoi(
            'Bạn không có quyền xem lịch hẹn của thú cưng nhà khác'
        )
    if (current_user.role == UserRole.STAFF
            and lich.staff_id != current_user.id):
        raise QuyenTruyCapBiTuChoi(
            'Bạn chỉ xem được lịch hẹn do mình phụ trách'
        )
    return lich


def xac_nhan(appointment_id, current_user):
    """Chuyển lịch từ chờ xác nhận sang đã xác nhận."""
    _bat_buoc_vai_tro_dat_lich(current_user)
    lich = lay_theo_id(appointment_id, current_user)

    if lich.status != AppointmentStatus.PENDING:
        raise DuLieuKhongHopLe(
            'Chỉ xác nhận được lịch hẹn đang ở trạng thái chờ xác nhận'
        )

    lich.status = AppointmentStatus.CONFIRMED
    activity_log_service.ghi(current_user, 'xac_nhan_lich_hen', 'appointments',
                             lich.id, 'Xác nhận lịch hẹn')
    return lich


def hoan_thanh(appointment_id, current_user):
    """Đánh dấu buổi hẹn đã hoàn thành.

    Nhân viên phụ trách cũng đánh dấu được, vì họ là người thực hiện dịch vụ.
    """
    if current_user.role not in _VAI_TRO_DAT_LICH + (UserRole.STAFF,):
        raise QuyenTruyCapBiTuChoi('Bạn không có quyền hoàn thành lịch hẹn')

    lich = lay_theo_id(appointment_id, current_user)

    if lich.status not in (AppointmentStatus.PENDING,
                           AppointmentStatus.CONFIRMED):
        raise DuLieuKhongHopLe(
            'Chỉ hoàn thành được lịch hẹn chưa bị hủy và chưa hoàn thành'
        )

    lich.status = AppointmentStatus.COMPLETED
    activity_log_service.ghi(current_user, 'hoan_thanh_lich_hen',
                             'appointments', lich.id, 'Hoàn thành lịch hẹn')
    return lich

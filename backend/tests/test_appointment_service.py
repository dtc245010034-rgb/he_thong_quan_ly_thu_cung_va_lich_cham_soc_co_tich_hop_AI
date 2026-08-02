"""Kiểm thử đặt lịch và chống trùng lịch.

Chống trùng lịch là ca kiểm thử bắt buộc ở mục 10 đặc tả, và là logic
nghiệp vụ dễ sai nhất của dự án.
"""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from backend.app.models import (Appointment, AppointmentStatus, Owner, Pet,
                                Service, ServiceCategory, User, UserRole)
from backend.app.services import appointment_service
from backend.app.services.errors import (DuLieuKhongHopLe,
                                         QuyenTruyCapBiTuChoi, TrungLichHen)

# Mốc thời gian trong tương lai để test không phụ thuộc ngày chạy máy.
GIO_9H = datetime(2027, 9, 1, 9, 0)


@pytest.fixture
def du_lieu(session):
    """Hai thú cưng, hai nhân viên, một dịch vụ 45 phút."""
    chu = Owner(full_name='Chủ A', phone='0900000001')
    session.add(chu)
    session.flush()

    nv1 = User(username='nv1', password_hash='h', role=UserRole.STAFF)
    nv2 = User(username='nv2', password_hash='h', role=UserRole.STAFF)
    le_tan = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    tk_chu = User(username='chu', password_hash='h', role=UserRole.OWNER,
                  owner_id=chu.id)
    session.add_all([nv1, nv2, le_tan, tk_chu])
    session.flush()

    dv = Service(name='Tắm', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add(dv)
    session.flush()

    pet1 = Pet(owner_id=chu.id, name='Mực', species='chó')
    pet2 = Pet(owner_id=chu.id, name='Vàng', species='mèo')
    session.add_all([pet1, pet2])
    session.flush()

    return {'nv1': nv1, 'nv2': nv2, 'le_tan': le_tan, 'tk_chu': tk_chu,
            'dv': dv, 'pet1': pet1, 'pet2': pet2}


def _dat(du_lieu, gio, staff=None, pet=None):
    """Rút gọn lời gọi đặt lịch trong test."""
    return appointment_service.dat_lich({
        'pet_id': (pet or du_lieu['pet1']).id,
        'service_id': du_lieu['dv'].id,
        'staff_id': (staff or du_lieu['nv1']).id if staff is not False else None,
        'scheduled_at': gio,
    }, du_lieu['le_tan'])


def test_dat_lich_hop_le_tinh_dung_gio_ket_thuc(session, du_lieu):
    """ends_at = scheduled_at + duration_minutes của dịch vụ."""
    lh = _dat(du_lieu, GIO_9H)
    session.flush()

    assert lh.ends_at == GIO_9H + timedelta(minutes=45)
    assert lh.status == AppointmentStatus.PENDING


def test_dat_trung_khung_gio_nhan_vien_bi_chan(session, du_lieu):
    """CA KIỂM THỬ BẮT BUỘC mục 10: trùng lịch nhân viên phải bị chặn."""
    _dat(du_lieu, GIO_9H)
    session.flush()

    # Lịch mới bắt đầu 9:30, chồng lên lịch cũ 9:00-9:45.
    with pytest.raises(TrungLichHen):
        _dat(du_lieu, GIO_9H + timedelta(minutes=30), pet=du_lieu['pet2'])


def test_lich_ke_sat_nhau_khong_bi_coi_la_trung(session, du_lieu):
    """Lịch cũ 9:00-9:45, lịch mới bắt đầu ĐÚNG 9:45 — hợp lệ.

    Ca biên dễ làm sai nhất: nếu điều kiện chồng lấn dùng <= thay vì < thì
    hai lịch kề sát nhau bị chặn oan, nhân viên mất chỗ trống hợp lệ.
    """
    _dat(du_lieu, GIO_9H)
    session.flush()

    lh2 = _dat(du_lieu, GIO_9H + timedelta(minutes=45), pet=du_lieu['pet2'])
    session.flush()
    assert lh2.id is not None


def test_lich_da_huy_khong_chan_lich_moi(session, du_lieu):
    """Chỉ lịch pending/confirmed mới chặn. Lịch cancelled thì không."""
    lh = _dat(du_lieu, GIO_9H)
    session.flush()
    lh.status = AppointmentStatus.CANCELLED
    session.flush()

    lh2 = _dat(du_lieu, GIO_9H, pet=du_lieu['pet2'])
    session.flush()
    assert lh2.id is not None


def test_lich_khong_gan_nhan_vien_khong_kiem_tra_trung(session, du_lieu):
    """staff_id rỗng thì bỏ qua kiểm tra trùng (mục 3.4 đặc tả)."""
    _dat(du_lieu, GIO_9H, staff=False)
    session.flush()
    lh2 = _dat(du_lieu, GIO_9H, staff=False, pet=du_lieu['pet2'])
    session.flush()
    assert lh2.id is not None


def test_trung_gio_nhung_khac_nhan_vien_van_dat_duoc(session, du_lieu):
    """Hai nhân viên khác nhau phục vụ cùng khung giờ là bình thường."""
    _dat(du_lieu, GIO_9H, staff=du_lieu['nv1'])
    session.flush()

    lh2 = _dat(du_lieu, GIO_9H, staff=du_lieu['nv2'], pet=du_lieu['pet2'])
    session.flush()
    assert lh2.id is not None


def test_dat_lich_o_qua_khu_bi_chan(session, du_lieu):
    with pytest.raises(DuLieuKhongHopLe):
        _dat(du_lieu, datetime(2020, 1, 1, 9, 0))


def test_chu_nuoi_khong_duoc_dat_lich(session, du_lieu):
    """Mục 3.4: đặt lịch là việc của lễ tân, không phải chủ nuôi."""
    with pytest.raises(QuyenTruyCapBiTuChoi):
        appointment_service.dat_lich({
            'pet_id': du_lieu['pet1'].id,
            'service_id': du_lieu['dv'].id,
            'staff_id': du_lieu['nv1'].id,
            'scheduled_at': GIO_9H,
        }, du_lieu['tk_chu'])


def test_thong_bao_trung_lich_neu_ro_nhan_vien_va_khung_gio(session, du_lieu):
    """Thông báo lỗi phải nêu rõ ai bận lúc nào, không báo chung chung.

    Yêu cầu trải nghiệm mục 4: thông báo lỗi rõ ràng bằng tiếng Việt.
    """
    _dat(du_lieu, GIO_9H)
    session.flush()

    with pytest.raises(TrungLichHen) as loi:
        _dat(du_lieu, GIO_9H + timedelta(minutes=30), pet=du_lieu['pet2'])

    thong_diep = str(loi.value)
    assert 'nv1' in thong_diep
    assert '09:00' in thong_diep


def test_danh_sach_loc_theo_nhan_vien_cua_minh(session, du_lieu):
    """Nhân viên chỉ thấy lịch của mình (ma trận quyền mục 4.2)."""
    _dat(du_lieu, GIO_9H, staff=du_lieu['nv1'])
    _dat(du_lieu, GIO_9H, staff=du_lieu['nv2'], pet=du_lieu['pet2'])
    session.flush()

    ds_nv1 = appointment_service.danh_sach(du_lieu['nv1'])
    assert len(ds_nv1) == 1
    assert ds_nv1[0].staff_id == du_lieu['nv1'].id

    ds_le_tan = appointment_service.danh_sach(du_lieu['le_tan'])
    assert len(ds_le_tan) == 2

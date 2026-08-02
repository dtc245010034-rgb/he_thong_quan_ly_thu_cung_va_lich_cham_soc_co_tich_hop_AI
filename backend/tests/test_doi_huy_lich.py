"""Kiểm thử đổi lịch và hủy lịch hẹn.

Hủy lịch không nhập lý do phải bị chặn — ca kiểm thử bắt buộc ở mục 10.
"""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from backend.app.models import (ActivityLog, AppointmentHistory,
                                AppointmentStatus, Owner, Pet, Service,
                                ServiceCategory, User, UserRole)
from backend.app.services import appointment_service
from backend.app.services.errors import DuLieuKhongHopLe, TrungLichHen

GIO_9H = datetime(2027, 9, 1, 9, 0)


@pytest.fixture
def du_lieu(session):
    chu = Owner(full_name='Chủ A', phone='0900000001')
    session.add(chu)
    session.flush()

    nv = User(username='nv1', password_hash='h', role=UserRole.STAFF)
    le_tan = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add_all([nv, le_tan])
    session.flush()

    dv = Service(name='Tắm', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add(dv)
    session.flush()

    pet1 = Pet(owner_id=chu.id, name='Mực', species='chó')
    pet2 = Pet(owner_id=chu.id, name='Vàng', species='mèo')
    session.add_all([pet1, pet2])
    session.flush()
    return {'nv': nv, 'le_tan': le_tan, 'dv': dv, 'pet1': pet1, 'pet2': pet2}


def _dat(du_lieu, gio, pet=None):
    return appointment_service.dat_lich({
        'pet_id': (pet or du_lieu['pet1']).id,
        'service_id': du_lieu['dv'].id,
        'staff_id': du_lieu['nv'].id,
        'scheduled_at': gio,
    }, du_lieu['le_tan'])


# ----- Đổi lịch -----

def test_doi_lich_cap_nhat_tai_cho_va_ghi_lich_su(session, du_lieu):
    """Đổi tại chỗ: cùng id, ghi đúng một dòng lịch sử (sai khác ⑥)."""
    lich = _dat(du_lieu, GIO_9H)
    session.flush()
    id_cu = lich.id
    gio_moi = GIO_9H + timedelta(days=1)

    appointment_service.doi_lich(lich.id, gio_moi, 'khach_yeu_cau',
                                 du_lieu['le_tan'])
    session.flush()

    assert lich.id == id_cu
    assert lich.scheduled_at == gio_moi
    ls = session.query(AppointmentHistory).filter_by(appointment_id=id_cu).all()
    assert len(ls) == 1
    assert ls[0].old_time == GIO_9H
    assert ls[0].new_time == gio_moi
    assert ls[0].reason == 'khach_yeu_cau'


def test_doi_lich_dua_trang_thai_ve_pending(session, du_lieu):
    """Giờ mới phải được xác nhận lại, không kế thừa xác nhận của giờ cũ."""
    lich = _dat(du_lieu, GIO_9H)
    session.flush()
    appointment_service.xac_nhan(lich.id, du_lieu['le_tan'])
    session.flush()
    assert lich.status == AppointmentStatus.CONFIRMED

    appointment_service.doi_lich(lich.id, GIO_9H + timedelta(days=1),
                                 'khach_yeu_cau', du_lieu['le_tan'])
    session.flush()
    assert lich.status == AppointmentStatus.PENDING


def test_doi_lich_tinh_lai_gio_ket_thuc(session, du_lieu):
    lich = _dat(du_lieu, GIO_9H)
    session.flush()
    gio_moi = GIO_9H + timedelta(days=2)

    appointment_service.doi_lich(lich.id, gio_moi, 'khach_yeu_cau',
                                 du_lieu['le_tan'])
    session.flush()
    assert lich.ends_at == gio_moi + timedelta(minutes=45)


def test_doi_lich_sang_gio_da_bi_chiem_bi_chan(session, du_lieu):
    """Giờ mới trùng lịch khác thì từ chối, lịch cũ giữ nguyên."""
    lich1 = _dat(du_lieu, GIO_9H)
    lich2 = _dat(du_lieu, GIO_9H + timedelta(days=1), pet=du_lieu['pet2'])
    session.flush()
    gio_cu_cua_lich2 = lich2.scheduled_at

    with pytest.raises(TrungLichHen):
        appointment_service.doi_lich(lich2.id, GIO_9H, 'khach_yeu_cau',
                                     du_lieu['le_tan'])

    assert lich2.scheduled_at == gio_cu_cua_lich2


def test_doi_lich_khong_tu_chan_chinh_no(session, du_lieu):
    """Đổi sang giờ chồng chính nó phải được, nhờ tham số bo_qua_id.

    Không có bo_qua_id thì mọi lần dời lịch một chút đều bị chính bản ghi
    đang sửa chặn lại — lỗi rất khó hiểu với người dùng.
    """
    lich = _dat(du_lieu, GIO_9H)
    session.flush()

    # Dời 15 phút, khung giờ mới chồng lên khung giờ cũ của chính nó.
    appointment_service.doi_lich(lich.id, GIO_9H + timedelta(minutes=15),
                                 'nhan_vien_ban', du_lieu['le_tan'])
    session.flush()
    assert lich.scheduled_at == GIO_9H + timedelta(minutes=15)


def test_lich_da_hoan_thanh_khong_doi_duoc(session, du_lieu):
    lich = _dat(du_lieu, GIO_9H)
    session.flush()
    lich.status = AppointmentStatus.COMPLETED
    session.flush()

    with pytest.raises(DuLieuKhongHopLe):
        appointment_service.doi_lich(lich.id, GIO_9H + timedelta(days=1),
                                     'khach_yeu_cau', du_lieu['le_tan'])


def test_doi_lich_khong_ly_do_bi_chan(session, du_lieu):
    """Mục 3.4: đổi lịch phải lưu lý do."""
    lich = _dat(du_lieu, GIO_9H)
    session.flush()

    with pytest.raises(DuLieuKhongHopLe):
        appointment_service.doi_lich(lich.id, GIO_9H + timedelta(days=1),
                                     '', du_lieu['le_tan'])


# ----- Hủy lịch -----

def test_huy_lich_khong_ly_do_bi_chan(session, du_lieu):
    """CA KIỂM THỬ BẮT BUỘC mục 10: hủy lịch không nhập lý do → validate chặn."""
    lich = _dat(du_lieu, GIO_9H)
    session.flush()

    with pytest.raises(DuLieuKhongHopLe):
        appointment_service.huy_lich(lich.id, '', None, du_lieu['le_tan'])

    assert lich.status == AppointmentStatus.PENDING


def test_huy_ly_do_khong_hop_le_bi_chan(session, du_lieu):
    """Lý do phải nằm trong danh sách 4 giá trị của mục 3.4."""
    lich = _dat(du_lieu, GIO_9H)
    session.flush()

    with pytest.raises(DuLieuKhongHopLe):
        appointment_service.huy_lich(lich.id, 'ly_do_bia_dat', None,
                                     du_lieu['le_tan'])


def test_huy_ly_do_khac_bat_buoc_nhap_mo_ta(session, du_lieu):
    """Chọn 'khác' mà không mô tả thì lý do trở nên vô nghĩa khi tra cứu."""
    lich = _dat(du_lieu, GIO_9H)
    session.flush()

    with pytest.raises(DuLieuKhongHopLe):
        appointment_service.huy_lich(lich.id, 'khac', '', du_lieu['le_tan'])

    appointment_service.huy_lich(lich.id, 'khac', 'Cửa hàng mất điện',
                                 du_lieu['le_tan'])
    session.flush()
    assert lich.status == AppointmentStatus.CANCELLED


def test_lich_da_hoan_thanh_khong_huy_duoc(session, du_lieu):
    lich = _dat(du_lieu, GIO_9H)
    session.flush()
    lich.status = AppointmentStatus.COMPLETED
    session.flush()

    with pytest.raises(DuLieuKhongHopLe):
        appointment_service.huy_lich(lich.id, 'khach_yeu_cau', None,
                                     du_lieu['le_tan'])


def test_huy_lich_ghi_nhat_ky(session, du_lieu):
    lich = _dat(du_lieu, GIO_9H)
    session.flush()

    appointment_service.huy_lich(lich.id, 'thu_cung_om', None,
                                 du_lieu['le_tan'])
    session.flush()

    log = session.query(ActivityLog).filter_by(
        action='huy_lich_hen', entity_id=lich.id).one()
    assert log.actor_user_id == du_lieu['le_tan'].id
    assert 'thu_cung_om' in log.detail


def test_lich_da_huy_khong_chan_lich_moi_cung_gio(session, du_lieu):
    """Hủy xong thì khung giờ đó phải được giải phóng ngay."""
    lich = _dat(du_lieu, GIO_9H)
    session.flush()
    appointment_service.huy_lich(lich.id, 'khach_yeu_cau', None,
                                 du_lieu['le_tan'])
    session.flush()

    lich_moi = _dat(du_lieu, GIO_9H, pet=du_lieu['pet2'])
    session.flush()
    assert lich_moi.id is not None

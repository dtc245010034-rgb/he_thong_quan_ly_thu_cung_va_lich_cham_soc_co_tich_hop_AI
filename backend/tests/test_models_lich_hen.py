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

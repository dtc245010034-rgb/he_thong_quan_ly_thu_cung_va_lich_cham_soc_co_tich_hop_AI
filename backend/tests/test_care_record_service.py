"""Kiểm thử service hồ sơ chăm sóc.

Hồ sơ thiếu cân nặng hoặc ngày phải báo lỗi rõ ràng — ca kiểm thử bắt buộc
ở mục 10 đặc tả.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from backend.app.models import (AppointmentStatus, CareRecord, Owner, Pet,
                                Service, ServiceCategory, User, UserRole)
from backend.app.services import appointment_service, care_record_service
from backend.app.services.errors import (DuLieuKhongHopLe,
                                         QuyenTruyCapBiTuChoi)

GIO_9H = datetime(2027, 9, 1, 9, 0)


@pytest.fixture
def du_lieu(session):
    """Một buổi hẹn đã hoàn thành do nv1 phụ trách."""
    chu = Owner(full_name='Chủ A', phone='0900000001')
    session.add(chu)
    session.flush()

    nv1 = User(username='nv1', password_hash='h', role=UserRole.STAFF)
    nv2 = User(username='nv2', password_hash='h', role=UserRole.STAFF)
    le_tan = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add_all([nv1, nv2, le_tan])
    session.flush()

    dv = Service(name='Tắm', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add(dv)
    session.flush()

    pet = Pet(owner_id=chu.id, name='Mực', species='chó')
    session.add(pet)
    session.flush()

    lich = appointment_service.dat_lich({
        'pet_id': pet.id, 'service_id': dv.id, 'staff_id': nv1.id,
        'scheduled_at': GIO_9H,
    }, le_tan)
    session.flush()

    return {'nv1': nv1, 'nv2': nv2, 'le_tan': le_tan, 'pet': pet, 'lich': lich}


def _hoan_thanh(du_lieu):
    appointment_service.hoan_thanh(du_lieu['lich'].id, du_lieu['nv1'])


def _du_lieu_ho_so(du_lieu, **ghi_de):
    goc = {
        'pet_id': du_lieu['pet'].id,
        'appointment_id': du_lieu['lich'].id,
        'record_date': date(2027, 9, 1),
        'weight_at_visit': Decimal('18.5'),
        'condition_notes': 'Da lông bình thường',
        'treatment_notes': 'Tắm, sấy, vệ sinh tai',
        'next_recommendation': 'Duy trì lịch tắm hàng tháng',
    }
    goc.update(ghi_de)
    return goc


def test_ghi_ho_so_day_du_truong(session, du_lieu):
    _hoan_thanh(du_lieu)
    session.flush()

    hs = care_record_service.ghi_ho_so(_du_lieu_ho_so(du_lieu), du_lieu['nv1'])
    session.flush()

    assert hs.id is not None
    assert hs.weight_at_visit == Decimal('18.5')
    assert hs.staff_id == du_lieu['nv1'].id


def test_thieu_can_nang_bao_loi_ro_rang(session, du_lieu):
    """CA BẮT BUỘC mục 10: thiếu cân nặng phải báo lỗi nêu rõ trường nào."""
    _hoan_thanh(du_lieu)
    session.flush()

    with pytest.raises(DuLieuKhongHopLe) as loi:
        care_record_service.ghi_ho_so(
            _du_lieu_ho_so(du_lieu, weight_at_visit=None), du_lieu['nv1'])

    assert 'cân nặng' in str(loi.value).lower()


def test_thieu_ngay_bao_loi_ro_rang(session, du_lieu):
    _hoan_thanh(du_lieu)
    session.flush()

    with pytest.raises(DuLieuKhongHopLe) as loi:
        care_record_service.ghi_ho_so(
            _du_lieu_ho_so(du_lieu, record_date=None), du_lieu['nv1'])

    assert 'ngày' in str(loi.value).lower()


def test_can_nang_am_bi_chan(session, du_lieu):
    _hoan_thanh(du_lieu)
    session.flush()

    with pytest.raises(DuLieuKhongHopLe):
        care_record_service.ghi_ho_so(
            _du_lieu_ho_so(du_lieu, weight_at_visit=Decimal('-1')),
            du_lieu['nv1'])


def test_nhan_vien_chi_ghi_ho_so_cho_lich_cua_minh(session, du_lieu):
    """Nhân viên khác không được ghi hồ sơ hộ (ma trận quyền mục 4.2)."""
    _hoan_thanh(du_lieu)
    session.flush()

    with pytest.raises(QuyenTruyCapBiTuChoi):
        care_record_service.ghi_ho_so(_du_lieu_ho_so(du_lieu), du_lieu['nv2'])


def test_chi_ghi_ho_so_cho_lich_da_hoan_thanh(session, du_lieu):
    """Lịch chưa hoàn thành thì chưa có gì để ghi hồ sơ."""
    assert du_lieu['lich'].status == AppointmentStatus.PENDING

    with pytest.raises(DuLieuKhongHopLe):
        care_record_service.ghi_ho_so(_du_lieu_ho_so(du_lieu), du_lieu['nv1'])


def test_ghi_ho_so_xoa_cache_tom_tat_ai(session, du_lieu):
    """Cache tóm tắt AI phải bị xóa khi có hồ sơ mới.

    Thiếu bước này thì ở KT3 màn hình hiển thị bản tóm tắt cũ sau khi thú
    cưng đã có lần khám mới — sai lệch đúng chỗ chức năng AI cần chính xác.
    """
    _hoan_thanh(du_lieu)
    pet = du_lieu['pet']
    pet.ai_summary_cache = '{"summary_vi": "tóm tắt cũ"}'
    pet.ai_summary_cached_at = datetime(2027, 8, 1, 10, 0)
    session.flush()

    care_record_service.ghi_ho_so(_du_lieu_ho_so(du_lieu), du_lieu['nv1'])
    session.flush()

    assert pet.ai_summary_cache is None
    assert pet.ai_summary_cached_at is None


def test_danh_sach_theo_thu_cung_sap_xep_theo_ngay(session, du_lieu):
    """Hồ sơ trả về theo thứ tự thời gian để so sánh xu hướng cân nặng."""
    _hoan_thanh(du_lieu)
    session.flush()
    for ngay, can in [(date(2027, 7, 1), '19.0'), (date(2027, 8, 1), '18.7'),
                      (date(2027, 9, 1), '18.5')]:
        session.add(CareRecord(pet_id=du_lieu['pet'].id,
                               staff_id=du_lieu['nv1'].id,
                               record_date=ngay,
                               weight_at_visit=Decimal(can)))
    session.flush()

    ds = care_record_service.danh_sach_theo_thu_cung(du_lieu['pet'].id,
                                                     du_lieu['le_tan'])
    ngay_thang = [r.record_date for r in ds]
    assert ngay_thang == sorted(ngay_thang)

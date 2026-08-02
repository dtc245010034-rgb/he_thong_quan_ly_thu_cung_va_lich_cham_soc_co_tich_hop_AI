"""Kiểm thử service lịch tiêm phòng.

Trạng thái sắp đến hạn và quá hạn được TÍNH lúc truy vấn, không lưu vào
CSDL (sai khác ④). Hàm tính nhận ngày hiện tại làm tham số để test không
phụ thuộc ngày chạy máy.
"""
from datetime import date, timedelta

import pytest

from backend.app.models import Owner, Pet, User, UserRole, VaccinationSchedule
from backend.app.services import vaccination_service
from backend.app.services.errors import (DuLieuKhongHopLe,
                                         QuyenTruyCapBiTuChoi)

HOM_NAY = date(2027, 6, 15)


@pytest.fixture
def du_lieu(session):
    chu = Owner(full_name='Chủ A', phone='0900000001')
    session.add(chu)
    session.flush()

    le_tan = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    tk_chu = User(username='chu', password_hash='h', role=UserRole.OWNER,
                  owner_id=chu.id)
    session.add_all([le_tan, tk_chu])
    session.flush()

    pet = Pet(owner_id=chu.id, name='Mực', species='chó')
    session.add(pet)
    session.flush()
    return {'chu': chu, 'le_tan': le_tan, 'tk_chu': tk_chu, 'pet': pet}


def _lich(pet, ngay_den_han, da_tiem=False):
    return VaccinationSchedule(pet_id=pet.id, vaccine_name='Dại',
                               last_date=date(2026, 6, 15),
                               next_due_date=ngay_den_han, is_done=da_tiem)


def test_da_tiem_thi_tra_da_tiem(session, du_lieu):
    """is_done=True thì luôn là 'da_tiem', BẤT KỂ ngày đến hạn đã qua hay chưa."""
    lich = _lich(du_lieu['pet'], HOM_NAY - timedelta(days=100), da_tiem=True)
    assert vaccination_service.tinh_trang_thai(lich, HOM_NAY) == 'da_tiem'


def test_qua_han_khi_ngay_den_han_da_qua(session, du_lieu):
    lich = _lich(du_lieu['pet'], HOM_NAY - timedelta(days=1))
    assert vaccination_service.tinh_trang_thai(lich, HOM_NAY) == 'qua_han'


def test_sap_den_han_trong_nguong_cau_hinh(session, du_lieu):
    """Ngưỡng mặc định VACCINE_DUE_SOON_DAYS là 7 ngày."""
    lich = _lich(du_lieu['pet'], HOM_NAY + timedelta(days=3))
    assert vaccination_service.tinh_trang_thai(lich, HOM_NAY) == 'sap_den_han'


def test_dung_ngay_den_han_van_la_sap_den_han(session, du_lieu):
    """Ca biên: đến hạn đúng hôm nay thì chưa quá hạn."""
    lich = _lich(du_lieu['pet'], HOM_NAY)
    assert vaccination_service.tinh_trang_thai(lich, HOM_NAY) == 'sap_den_han'


def test_ngoai_nguong_thi_binh_thuong(session, du_lieu):
    lich = _lich(du_lieu['pet'], HOM_NAY + timedelta(days=60))
    assert vaccination_service.tinh_trang_thai(lich, HOM_NAY) == 'binh_thuong'


def test_trang_thai_khong_luu_vao_csdl(session, du_lieu):
    """Giữ ràng buộc sai khác ④: bảng không có cột status."""
    lich = _lich(du_lieu['pet'], HOM_NAY)
    assert not hasattr(lich, 'status')


def test_danh_dau_da_tiem_tao_lich_ke_tiep(session, du_lieu):
    """Đánh dấu đã tiêm thì cập nhật last_date và sinh kỳ tiếp theo."""
    lich = _lich(du_lieu['pet'], HOM_NAY)
    session.add(lich)
    session.flush()

    vaccination_service.danh_dau_da_tiem(lich.id, du_lieu['le_tan'],
                                         ngay_tiem=HOM_NAY)
    session.flush()

    assert lich.is_done is True
    assert lich.last_date == HOM_NAY
    ke_tiep = session.query(VaccinationSchedule).filter(
        VaccinationSchedule.pet_id == du_lieu['pet'].id,
        VaccinationSchedule.id != lich.id).one()
    assert ke_tiep.next_due_date == HOM_NAY + timedelta(days=365)
    assert ke_tiep.is_done is False


def test_danh_sach_sap_den_han_gom_ca_qua_han(session, du_lieu):
    """Màn hình nhắc tiêm phải hiện cả mũi đã quá hạn, không chỉ sắp đến."""
    session.add_all([
        _lich(du_lieu['pet'], HOM_NAY - timedelta(days=10)),   # quá hạn
        _lich(du_lieu['pet'], HOM_NAY + timedelta(days=3)),    # sắp đến hạn
        _lich(du_lieu['pet'], HOM_NAY + timedelta(days=90)),   # bình thường
        _lich(du_lieu['pet'], HOM_NAY, da_tiem=True),          # đã tiêm
    ])
    session.flush()

    ds = vaccination_service.danh_sach_sap_den_han(du_lieu['le_tan'],
                                                   hom_nay=HOM_NAY)
    assert len(ds) == 2


def test_chu_nuoi_chi_thay_lich_tiem_thu_cung_minh(session, du_lieu):
    """Phân quyền lớp 2 áp dụng cả cho lịch tiêm."""
    chu_b = Owner(full_name='Chủ B', phone='0900000002')
    session.add(chu_b)
    session.flush()
    pet_b = Pet(owner_id=chu_b.id, name='Vàng', species='mèo')
    session.add(pet_b)
    session.flush()

    session.add_all([
        _lich(du_lieu['pet'], HOM_NAY),
        _lich(pet_b, HOM_NAY),
    ])
    session.flush()

    ds = vaccination_service.danh_sach_sap_den_han(du_lieu['tk_chu'],
                                                   hom_nay=HOM_NAY)
    assert len(ds) == 1
    assert ds[0].pet_id == du_lieu['pet'].id


def test_chu_nuoi_khong_duoc_tao_lich_tiem(session, du_lieu):
    with pytest.raises(QuyenTruyCapBiTuChoi):
        vaccination_service.tao({
            'pet_id': du_lieu['pet'].id, 'vaccine_name': 'Dại',
            'next_due_date': HOM_NAY,
        }, du_lieu['tk_chu'])


def test_thieu_ten_vac_xin_bi_chan(session, du_lieu):
    with pytest.raises(DuLieuKhongHopLe):
        vaccination_service.tao({
            'pet_id': du_lieu['pet'].id, 'vaccine_name': '',
            'next_due_date': HOM_NAY,
        }, du_lieu['le_tan'])

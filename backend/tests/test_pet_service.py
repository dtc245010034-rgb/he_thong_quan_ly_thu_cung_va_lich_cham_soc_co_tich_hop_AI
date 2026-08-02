"""Kiểm thử service thú cưng và phân quyền lớp 2."""
import pytest

from backend.app.models import Owner, Pet, User, UserRole
from backend.app.services import pet_service
from backend.app.services.errors import QuyenTruyCapBiTuChoi


@pytest.fixture
def du_lieu(session):
    """Hai chủ nuôi, mỗi người một thú cưng và một tài khoản riêng."""
    chu_a = Owner(full_name='Chủ A', phone='0900000001')
    chu_b = Owner(full_name='Chủ B', phone='0900000002')
    session.add_all([chu_a, chu_b])
    session.flush()

    tk_a = User(username='a', password_hash='h', role=UserRole.OWNER,
                owner_id=chu_a.id)
    le_tan = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    nhan_vien = User(username='nv', password_hash='h', role=UserRole.STAFF)
    session.add_all([tk_a, le_tan, nhan_vien])
    session.flush()

    pet_a = Pet(owner_id=chu_a.id, name='Mực', species='chó')
    pet_b = Pet(owner_id=chu_b.id, name='Vàng', species='mèo')
    session.add_all([pet_a, pet_b])
    session.flush()
    return {'chu_a': chu_a, 'chu_b': chu_b, 'tk_a': tk_a, 'le_tan': le_tan,
            'nhan_vien': nhan_vien, 'pet_a': pet_a, 'pet_b': pet_b}


def test_le_tan_xem_duoc_tat_ca_thu_cung(session, du_lieu):
    ds = pet_service.danh_sach(du_lieu['le_tan'])
    assert len(ds) == 2


def test_chu_nuoi_chi_xem_duoc_thu_cung_cua_minh(session, du_lieu):
    ds = pet_service.danh_sach(du_lieu['tk_a'])
    assert [p.name for p in ds] == ['Mực']


def test_chu_nuoi_a_truy_cap_thu_cung_nha_b_bi_tu_choi(session, du_lieu):
    """LỖ HỔNG PHẢI CHẶN: đổi ?pet_id= sang thú cưng nhà khác."""
    with pytest.raises(QuyenTruyCapBiTuChoi):
        pet_service.lay_theo_id(du_lieu['pet_b'].id, du_lieu['tk_a'])


def test_nhan_vien_xem_duoc_thu_cung_de_phuc_vu(session, du_lieu):
    """Nhân viên cần xem hồ sơ thú cưng trước khi phục vụ (mục 3.1)."""
    p = pet_service.lay_theo_id(du_lieu['pet_b'].id, du_lieu['nhan_vien'])
    assert p.name == 'Vàng'


def test_loc_thu_cung_theo_chu_nuoi(session, du_lieu):
    ds = pet_service.danh_sach(du_lieu['le_tan'], owner_id=du_lieu['chu_b'].id)
    assert [p.name for p in ds] == ['Vàng']


def test_thu_cung_da_xoa_mem_khong_hien_trong_danh_sach(session, du_lieu):
    pet_service.xoa_mem(du_lieu['pet_a'].id, du_lieu['le_tan'])
    session.flush()

    ds = pet_service.danh_sach(du_lieu['le_tan'])
    assert [p.name for p in ds] == ['Vàng']
    assert session.query(Pet).count() == 2  # vẫn còn trong CSDL

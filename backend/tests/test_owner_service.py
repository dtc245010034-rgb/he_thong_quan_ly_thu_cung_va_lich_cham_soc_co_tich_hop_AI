"""Kiểm thử service chủ nuôi, đặc biệt là phân quyền lớp 2.

Lớp 1 (decorator require_role) chỉ biết vai trò. Lớp 2 ở đây biết bản ghi
đang truy cập thuộc về ai — đó là thứ chặn lỗ hổng đổi tham số id trên URL
để xem hồ sơ nhà khác.
"""
import pytest

from backend.app.models import ActivityLog, Owner, Pet, User, UserRole
from backend.app.services import owner_service
from backend.app.services.errors import QuyenTruyCapBiTuChoi


@pytest.fixture
def du_lieu(session):
    """Hai chủ nuôi, mỗi người một tài khoản owner riêng, cộng một lễ tân."""
    chu_a = Owner(full_name='Chủ A', phone='0900000001')
    chu_b = Owner(full_name='Chủ B', phone='0900000002')
    session.add_all([chu_a, chu_b])
    session.flush()

    tk_a = User(username='a', password_hash='h', role=UserRole.OWNER,
                owner_id=chu_a.id)
    tk_b = User(username='b', password_hash='h', role=UserRole.OWNER,
                owner_id=chu_b.id)
    le_tan = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add_all([tk_a, tk_b, le_tan])
    session.flush()

    pet_a = Pet(owner_id=chu_a.id, name='Mực', species='chó')
    session.add(pet_a)
    session.flush()
    return {'chu_a': chu_a, 'chu_b': chu_b, 'tk_a': tk_a, 'tk_b': tk_b,
            'le_tan': le_tan, 'pet_a': pet_a}


def test_le_tan_xem_duoc_tat_ca_chu_nuoi(session, du_lieu):
    ds = owner_service.danh_sach(du_lieu['le_tan'])
    assert len(ds) == 2


def test_chu_nuoi_chi_xem_duoc_ho_so_cua_minh(session, du_lieu):
    """Lớp 2: vai trò owner hợp lệ nhưng chỉ thấy dữ liệu của mình."""
    ds = owner_service.danh_sach(du_lieu['tk_a'])
    assert [o.full_name for o in ds] == ['Chủ A']


def test_chu_nuoi_a_truy_cap_ho_so_chu_b_bi_tu_choi(session, du_lieu):
    """LỖ HỔNG PHẢI CHẶN: đổi tham số id để xem hồ sơ nhà khác."""
    with pytest.raises(QuyenTruyCapBiTuChoi):
        owner_service.lay_theo_id(du_lieu['chu_b'].id, du_lieu['tk_a'])


def test_chu_nuoi_khong_duoc_tao_chu_nuoi_moi(session, du_lieu):
    with pytest.raises(QuyenTruyCapBiTuChoi):
        owner_service.tao({'full_name': 'X', 'phone': '0900000009'},
                          du_lieu['tk_a'])


def test_le_tan_tao_chu_nuoi_va_ghi_nhat_ky(session, du_lieu):
    chu = owner_service.tao({'full_name': 'Chủ C', 'phone': '0900000003'},
                            du_lieu['le_tan'])
    session.flush()
    assert chu.id is not None
    log = session.query(ActivityLog).filter_by(entity_type='owners',
                                               entity_id=chu.id).one()
    assert log.action == 'tao_chu_nuoi'
    assert log.actor_user_id == du_lieu['le_tan'].id


def test_tim_kiem_theo_so_dien_thoai(session, du_lieu):
    ds = owner_service.danh_sach(du_lieu['le_tan'], tu_khoa='0900000002')
    assert [o.full_name for o in ds] == ['Chủ B']


def test_xoa_mem_canh_bao_so_ban_ghi_lien_quan(session, du_lieu):
    """Mục 3.2: xóa chủ nuôi còn thú cưng phải cảnh báo, không xóa cứng."""
    kq = owner_service.xoa_mem(du_lieu['chu_a'].id, du_lieu['le_tan'])
    session.flush()

    assert kq['so_thu_cung'] == 1
    assert du_lieu['chu_a'].is_deleted is True
    assert session.query(Owner).count() == 2  # vẫn còn trong CSDL
    assert len(owner_service.danh_sach(du_lieu['le_tan'])) == 1

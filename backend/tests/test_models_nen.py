"""Kiểm thử ba model nền: users, owners, pets."""
import pytest
from sqlalchemy.exc import StatementError

from backend.app.models import Owner, Pet, User, UserRole


def test_tao_owner_va_pet_lien_ket_dung(session):
    """Thú cưng gắn với đúng một chủ nuôi."""
    chu = Owner(full_name='Nguyễn Văn A', phone='0900000001')
    session.add(chu)
    session.flush()

    cun = Pet(owner_id=chu.id, name='Mực', species='chó')
    session.add(cun)
    session.flush()

    assert cun.owner.full_name == 'Nguyễn Văn A'
    assert chu.pets[0].name == 'Mực'


def test_role_khong_hop_le_bi_chan(session):
    """role phải là enum kiểm soát, không nhận text tự do (ràng buộc mục 5.3)."""
    u = User(username='x', password_hash='h', role='giam_doc')
    session.add(u)
    with pytest.raises(StatementError):
        session.flush()


def test_bon_vai_tro_deu_hop_le(session):
    """Đủ 4 vai trò theo thiết kế."""
    for i, role in enumerate(UserRole):
        session.add(User(username=f'u{i}', password_hash='h', role=role))
    session.flush()
    assert session.query(User).count() == 4


def test_nhan_vien_khong_gan_owner_id(session):
    """Tài khoản nhân viên có owner_id rỗng; tài khoản chủ nuôi thì trỏ về hồ sơ."""
    chu = Owner(full_name='Trần Thị B', phone='0900000002')
    session.add(chu)
    session.flush()

    le_tan = User(username='letan', password_hash='h', role=UserRole.RECEPTIONIST)
    tk_chu = User(username='chub', password_hash='h', role=UserRole.OWNER,
                  owner_id=chu.id)
    session.add_all([le_tan, tk_chu])
    session.flush()

    assert le_tan.owner_id is None
    assert tk_chu.owner.full_name == 'Trần Thị B'


def test_query_active_loai_bo_ban_ghi_da_xoa_mem(session):
    """Xóa mềm: bản ghi đã xóa không xuất hiện trong truy vấn mặc định."""
    con_dung = Owner(full_name='Còn dùng', phone='0900000003')
    da_xoa = Owner(full_name='Đã xóa', phone='0900000004', is_deleted=True)
    session.add_all([con_dung, da_xoa])
    session.flush()

    ten = [o.full_name for o in Owner.query_active().all()]
    assert ten == ['Còn dùng']
    assert session.query(Owner).count() == 2  # vẫn còn trong CSDL, chỉ bị ẩn


def test_pet_co_hai_cot_cache_tom_tat_ai(session):
    """Hai cột cache tóm tắt AI tồn tại và mặc định rỗng (thiết kế mục 5.1)."""
    chu = Owner(full_name='C', phone='0900000005')
    session.add(chu)
    session.flush()
    p = Pet(owner_id=chu.id, name='Vàng', species='mèo')
    session.add(p)
    session.flush()

    assert p.ai_summary_cache is None
    assert p.ai_summary_cached_at is None

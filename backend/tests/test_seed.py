"""Kiểm thử dữ liệu mẫu dùng cho demo."""
from pathlib import Path

from sqlalchemy import text

from backend.app.extensions import db
from backend.app.models import CareRecord, Owner, Pet, Service, User, UserRole

SEED = Path(__file__).resolve().parents[2] / 'database' / 'seed_data.sql'


def _nap_seed():
    """Nạp toàn bộ câu lệnh trong seed_data.sql vào CSDL đang mở.

    Tách câu theo dấu chấm phẩy, nên seed_data.sql không được chứa dấu này
    bên trong chuỗi.
    """
    for cau in SEED.read_text(encoding='utf-8').split(';'):
        if cau.strip():
            db.session.execute(text(cau))
    db.session.commit()


def test_seed_du_so_luong_toi_thieu(app):
    """Mục 15 đặc tả: tối thiểu 5 chủ nuôi, 8 thú cưng."""
    with app.app_context():
        _nap_seed()
        assert Owner.query.count() >= 5
        assert Pet.query.count() >= 8
        assert Service.query.count() >= 5


def test_co_thu_cung_sut_can_lien_tuc(app):
    """Cần ít nhất 1 con có xu hướng sụt cân để chức năng tóm tắt AI ở KT3
    thực sự bật cờ cảnh báo khi demo, thay vì tóm tắt hồ sơ nhạt nhòa."""
    with app.app_context():
        _nap_seed()
        for pet in Pet.query.all():
            ho_so = (CareRecord.query
                     .filter_by(pet_id=pet.id)
                     .order_by(CareRecord.record_date)
                     .all())
            if len(ho_so) >= 3:
                can_nang = [r.weight_at_visit for r in ho_so]
                if all(b < a for a, b in zip(can_nang, can_nang[1:])):
                    return
        assert False, 'Không có thú cưng nào sụt cân liên tục qua 3 lần khám trở lên'


def test_moi_vai_tro_deu_co_it_nhat_mot_tai_khoan(app):
    with app.app_context():
        _nap_seed()
        for role in UserRole:
            assert User.query.filter_by(role=role).count() >= 1, \
                f'Thiếu tài khoản {role.value}'

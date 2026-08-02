"""Lệnh dòng lệnh để khởi tạo và nạp dữ liệu cho CSDL."""
import os

import click
from sqlalchemy import text

from backend.app.extensions import db

_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
_SEED_FILE = os.path.join(_PROJECT_ROOT, 'database', 'seed_data.sql')


def dang_ky_lenh(app):
    """Gắn các lệnh CLI vào ứng dụng."""

    @app.cli.command('init-db')
    def init_db():
        """Tạo toàn bộ bảng trong CSDL."""
        db.create_all()
        click.echo(f'Đã tạo {len(db.metadata.tables)} bảng.')

    @app.cli.command('seed-db')
    @click.option('--force', is_flag=True,
                  help='Nạp đè kể cả khi CSDL đã có dữ liệu.')
    def seed_db(force):
        """Nạp dữ liệu mẫu từ database/seed_data.sql."""
        from backend.app.models import Owner, Pet, Service, User

        # Từ chối nạp chồng, tránh dữ liệu bị nhân đôi khi lỡ chạy hai lần.
        da_co = db.session.execute(
            text('SELECT COUNT(*) FROM owners')
        ).scalar()
        if da_co and not force:
            click.echo(
                f'CSDL đã có {da_co} chủ nuôi. Dùng --force nếu vẫn muốn nạp.'
            )
            return

        with open(_SEED_FILE, encoding='utf-8') as f:
            noi_dung = f.read()

        # Tách câu lệnh theo dấu chấm phẩy — xem cảnh báo ở đầu seed_data.sql.
        for cau in noi_dung.split(';'):
            if cau.strip():
                db.session.execute(text(cau))
        db.session.commit()

        click.echo('Đã nạp dữ liệu mẫu:')
        for ten, model in [('Chủ nuôi', Owner), ('Thú cưng', Pet),
                           ('Dịch vụ', Service), ('Tài khoản', User)]:
            click.echo(f'  {ten}: {db.session.query(model).count()}')

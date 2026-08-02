"""Route đăng nhập và đăng xuất."""
from flask import Blueprint, redirect, render_template, request, session, url_for

from backend.app.auth.password import verify_password
from backend.app.extensions import db
from backend.app.models import User

auth_bp = Blueprint('auth', __name__)

# Dùng CHUNG cho cả ba trường hợp: sai tên, sai mật khẩu, tài khoản bị khóa.
# Nếu tách thông báo riêng cho từng trường hợp thì kẻ tấn công dò được tài
# khoản nào có tồn tại trong hệ thống.
_LOI_DANG_NHAP = 'Tên đăng nhập hoặc mật khẩu không đúng'


@auth_bp.route('/dang-nhap', methods=['GET', 'POST'])
def trang_dang_nhap():
    """Hiển thị form đăng nhập và xử lý việc đăng nhập."""
    if request.method == 'GET':
        return render_template('auth/login.html')

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    user = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar_one_or_none()

    if user is None or not user.is_active or not verify_password(password,
                                                                 user.password_hash):
        return render_template('auth/login.html', error=_LOI_DANG_NHAP), 200

    # Xóa sạch phiên cũ trước khi ghi danh tính mới, tránh session fixation.
    session.clear()
    session['user_id'] = user.id
    session.permanent = True
    return redirect('/')


@auth_bp.route('/dang-xuat', methods=['POST'])
def dang_xuat():
    """Xóa phiên và quay về trang đăng nhập."""
    session.clear()
    return redirect(url_for('auth.trang_dang_nhap'))

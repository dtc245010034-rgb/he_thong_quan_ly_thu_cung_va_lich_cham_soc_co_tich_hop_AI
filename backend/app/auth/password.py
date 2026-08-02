"""Hash và kiểm tra mật khẩu bằng bcrypt.

bcrypt tự sinh salt ngẫu nhiên cho mỗi lần hash, nên hai người dùng đặt
cùng một mật khẩu vẫn cho hai chuỗi hash khác nhau. Nhờ vậy kẻ tấn công
lấy được CSDL cũng không dùng lại được bảng tra sẵn (rainbow table).
"""
import bcrypt


def hash_password(plain: str) -> str:
    """Băm mật khẩu dạng thường thành chuỗi lưu được vào CSDL."""
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Kiểm tra mật khẩu người dùng nhập có khớp chuỗi đã băm không."""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

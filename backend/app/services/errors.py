"""Ngoại lệ nghiệp vụ.

Tầng service không import Flask, nên không gọi abort() được. Thay vào đó nó
ném các ngoại lệ dưới đây và route dịch sang mã HTTP tương ứng. Nhờ vậy
service gọi được cả từ route lẫn từ scheduler (chạy ngoài ngữ cảnh request).
"""


class QuyenTruyCapBiTuChoi(Exception):
    """Người dùng không có quyền trên bản ghi này. Route dịch thành 403."""


class DuLieuKhongHopLe(Exception):
    """Dữ liệu đầu vào sai. Route hiển thị lại biểu mẫu kèm thông báo."""


class TrungLichHen(Exception):
    """Khung giờ đã có lịch khác của cùng nhân viên. Route hiển thị xung đột."""

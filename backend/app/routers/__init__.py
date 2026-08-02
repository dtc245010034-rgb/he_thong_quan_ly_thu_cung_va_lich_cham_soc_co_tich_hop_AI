"""Tầng route.

Route chỉ làm ba việc: nhận dữ liệu từ biểu mẫu, gọi tầng services/, và
render kết quả. Không chứa quy tắc nghiệp vụ — quy tắc nằm hết ở services/
để scheduler ở KT3 gọi lại được.
"""

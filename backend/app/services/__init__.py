"""Tầng nghiệp vụ.

Toàn bộ quy tắc nghiệp vụ nằm ở đây, không nằm trong route. Hai lý do:

1. Scheduler nhắc lịch ở KT3 chạy NGOÀI ngữ cảnh HTTP request — không có
   request, không có session — nên không gọi lại được logic đặt trong route.
2. Kiểm thử gọi thẳng hàm Python nhanh và rõ hơn nhiều so với đi qua HTTP.

Tầng này TUYỆT ĐỐI KHÔNG import gì từ backend.app.ai. Đó là cách biến yêu
cầu "AI sập thì hệ thống vẫn chạy" thành ràng buộc kiểm chứng được.
"""

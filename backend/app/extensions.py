"""Các đối tượng mở rộng dùng chung.

Tách riêng ra file này để models/ và main.py cùng import được mà không tạo
vòng lặp import: nếu đặt db trong main.py thì models/ phải import main.py,
mà main.py lại import models/.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

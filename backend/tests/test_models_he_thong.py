"""Kiểm thử 4 bảng hệ thống: log AI, log thao tác, cấu hình, thông báo."""
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models import (ActivityLog, AiInteractionLog, AppSetting,
                                Notification, Owner, Pet, User, UserRole)


def test_log_ai_co_cot_latency_va_was_flagged(session):
    """Hai cột phục vụ xử lý lỗi AI mục 8.4 và số liệu báo cáo KT3."""
    u = User(username='u', password_hash='h', role=UserRole.STAFF)
    session.add(u)
    session.flush()
    log = AiInteractionLog(feature_type='qa', user_id=u.id, prompt_input='hỏi',
                           ai_response='{}', model_used='gemini-1.5-flash',
                           latency_ms=820, was_flagged=True)
    session.add(log)
    session.flush()
    assert log.latency_ms == 820
    assert log.was_flagged is True


def test_log_thao_tac_ghi_nguoi_thuc_hien(session):
    """Yêu cầu mục 4: log thao tác quan trọng kèm người thực hiện và thời gian."""
    u = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add(u)
    session.flush()
    log = ActivityLog(actor_user_id=u.id, action='tao_lich_hen',
                      entity_type='appointments', entity_id=1,
                      detail='Đặt lịch tắm cho Mực')
    session.add(log)
    session.flush()
    assert log.actor.username == 'lt'
    assert log.created_at is not None


def test_app_setting_dung_key_lam_khoa_chinh(session):
    """Cấu hình AI sửa được lúc chạy; khóa API KHÔNG bao giờ lưu ở đây."""
    u = User(username='ad', password_hash='h', role=UserRole.ADMIN)
    session.add(u)
    session.flush()
    session.add(AppSetting(key='ai_enabled', value='true', updated_by=u.id))
    session.flush()
    assert session.get(AppSetting, 'ai_enabled').value == 'true'


def test_khong_the_nhac_trung_cung_mot_lich(session):
    """Khóa duy nhất (pet_id, reminder_type, due_date) chặn job gửi trùng mỗi ngày."""
    chu = Owner(full_name='A', phone='0900000001')
    session.add(chu)
    session.flush()
    pet = Pet(owner_id=chu.id, name='Mực', species='chó')
    session.add(pet)
    session.flush()

    chung = dict(pet_id=pet.id, owner_id=chu.id, reminder_type='tiem_phong',
                 due_date=date(2027, 1, 10), channel='sms', message='Nhắc tiêm',
                 urgency='soon')
    session.add(Notification(**chung))
    session.flush()

    session.add(Notification(**chung))
    with pytest.raises(IntegrityError):
        session.flush()


def test_du_18_bang(app):
    """Thiết kế chốt đúng 18 bảng — không thêm, không bớt."""
    from backend.app.extensions import db
    assert len(db.metadata.tables) == 18

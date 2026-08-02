"""Ghi nhật ký thao tác nghiệp vụ.

Mục 4 đặc tả yêu cầu log các thao tác quan trọng kèm người thực hiện và
thời gian, phục vụ kiểm toán.
"""
from backend.app.extensions import db
from backend.app.models import ActivityLog


def ghi(current_user, action, entity_type, entity_id, detail=None):
    """Thêm một dòng nhật ký thao tác.

    Cố ý KHÔNG commit — hàm gọi quyết định ranh giới giao dịch, để nhật ký
    và thay đổi dữ liệu cùng thành công hoặc cùng thất bại.
    """
    log = ActivityLog(
        actor_user_id=current_user.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=detail,
    )
    db.session.add(log)
    return log

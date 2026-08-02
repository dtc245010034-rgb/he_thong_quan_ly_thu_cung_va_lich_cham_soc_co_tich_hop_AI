"""Kiểm thử model hóa đơn, dòng hóa đơn, thanh toán."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.app.models import (Appointment, Invoice, InvoiceItem, Owner, Payment,
                                PaymentStatus, Pet, Service, ServiceCategory,
                                User, UserRole)


def test_invoice_khong_co_cot_appointment_id(session):
    """Sai khác ⑦: appointment_id nằm ở invoice_items, không ở invoices."""
    assert not hasattr(Invoice, 'appointment_id')
    assert hasattr(InvoiceItem, 'appointment_id')


def test_mot_hoa_don_gop_nhieu_lich_hen(session):
    """Yêu cầu mục 3.7: lập hóa đơn từ 1 hoặc nhiều lịch hẹn."""
    chu = Owner(full_name='A', phone='0900000001')
    lt = User(username='lt', password_hash='h', role=UserRole.RECEPTIONIST)
    dv = Service(name='Tắm', category=ServiceCategory.TAM,
                 price=Decimal('150000'), duration_minutes=45)
    session.add_all([chu, lt, dv])
    session.flush()
    pet = Pet(owner_id=chu.id, name='Mực', species='chó')
    session.add(pet)
    session.flush()

    t = datetime(2026, 9, 1, 9, 0)
    lh1 = Appointment(pet_id=pet.id, service_id=dv.id, scheduled_at=t,
                      ends_at=t + timedelta(minutes=45), created_by=lt.id)
    lh2 = Appointment(pet_id=pet.id, service_id=dv.id,
                      scheduled_at=t + timedelta(days=7),
                      ends_at=t + timedelta(days=7, minutes=45), created_by=lt.id)
    session.add_all([lh1, lh2])
    session.flush()

    hd = Invoice(owner_id=chu.id, invoice_number='HD-0001',
                 issue_date=date(2026, 9, 10), discount_amount=Decimal('0'),
                 total_amount=Decimal('300000'), created_by=lt.id)
    session.add(hd)
    session.flush()
    session.add_all([
        InvoiceItem(invoice_id=hd.id, service_id=dv.id, appointment_id=lh1.id,
                    quantity=1, unit_price=Decimal('150000'),
                    line_total=Decimal('150000')),
        InvoiceItem(invoice_id=hd.id, service_id=dv.id, appointment_id=lh2.id,
                    quantity=1, unit_price=Decimal('150000'),
                    line_total=Decimal('150000')),
    ])
    session.flush()

    assert len(hd.items) == 2
    assert {i.appointment_id for i in hd.items} == {lh1.id, lh2.id}


def test_hoa_don_mac_dinh_chua_thanh_toan(session):
    chu = Owner(full_name='B', phone='0900000002')
    lt = User(username='lt2', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add_all([chu, lt])
    session.flush()
    hd = Invoice(owner_id=chu.id, invoice_number='HD-0002',
                 issue_date=date(2026, 9, 10), discount_amount=Decimal('0'),
                 total_amount=Decimal('100000'), created_by=lt.id)
    session.add(hd)
    session.flush()
    assert hd.payment_status == PaymentStatus.CHUA_THANH_TOAN


def test_nhieu_dong_thanh_toan_cho_mot_hoa_don(session):
    """Thanh toán từng phần: nhiều dòng payments trên một hóa đơn."""
    chu = Owner(full_name='C', phone='0900000003')
    lt = User(username='lt3', password_hash='h', role=UserRole.RECEPTIONIST)
    session.add_all([chu, lt])
    session.flush()
    hd = Invoice(owner_id=chu.id, invoice_number='HD-0003',
                 issue_date=date(2026, 9, 10), discount_amount=Decimal('0'),
                 total_amount=Decimal('300000'), created_by=lt.id)
    session.add(hd)
    session.flush()
    session.add_all([
        Payment(invoice_id=hd.id, amount=Decimal('100000'),
                payment_date=date(2026, 9, 10), method='tien_mat', received_by=lt.id),
        Payment(invoice_id=hd.id, amount=Decimal('150000'),
                payment_date=date(2026, 9, 12), method='chuyen_khoan',
                received_by=lt.id),
    ])
    session.flush()

    assert sum(p.amount for p in hd.payments) == Decimal('250000')
    assert sum(p.amount for p in hd.payments) < hd.total_amount

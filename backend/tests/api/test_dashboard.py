from datetime import date
from uuid import uuid4

from app.db.session import SessionLocal
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.partner import Partner
from app.models.stock_movement import StockMovement
from app.models.sales_invoice import SalesInvoice
from app.services.ar_service import on_invoice_issued


def _setup_data():
    db = SessionLocal()
    prod = Product(id=uuid4(), name="P1", sku="SKU1", price=1, restock_level=5)
    wh = Warehouse(id=uuid4(), name="Main", code="MAIN")
    partner = Partner(id=uuid4(), name="Cust", type="customer")
    db.add_all([prod, wh, partner])
    db.commit()
    move = StockMovement(
        id=uuid4(),
        product_id=prod.id,
        warehouse_id=wh.id,
        direction="IN",
        quantity=2,
    )
    db.add(move)
    inv = SalesInvoice(
        id=uuid4(),
        number="I-1",
        partner_id=partner.id,
        currency="TRY",
        status="ISSUED",
        issue_date=date.today(),
        subtotal=100,
        tax_total=0,
        grand_total=100,
    )
    db.add(inv)
    db.commit()
    on_invoice_issued(db, inv)
    db.close()
    return partner.id


def test_dashboard_requires_auth(client):
    res = client.get("/dashboard/summary")
    assert res.status_code == 401


def test_dashboard_summary(client, user_token):
    partner_id = _setup_data()
    res = client.get(
        "/dashboard/summary",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert float(data["sales"]["today"]) == 100
    assert float(data["sales"]["month"]) == 100
    assert float(data["ar"]["open_total"]) == 100
    assert float(data["ar"]["aging"]["0_30"]) == 100
    assert data["stock"]["low"][0]["sku"] == "SKU1"
    assert len(data["top_customers"]) == 1
    assert data["top_customers"][0]["partner_id"] == str(partner_id)

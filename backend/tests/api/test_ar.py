from decimal import Decimal

from app.db.session import SessionLocal
from app.models.ar import AREntry


def create_partner(client, admin_token):
    res = client.post(
        "/partners",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Cust", "type": "customer", "tax_number": "TN1"},
    )
    assert res.status_code == 201
    return res.json()["id"]


def create_product(client, admin_token):
    res = client.post(
        "/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Prod", "sku": "SKU1", "price": 100},
    )
    assert res.status_code == 201
    return res.json()["id"]


def create_invoice(client, admin_token, partner_id, product_id):
    payload = {
        "partner_id": partner_id,
        "items": [{"product_id": product_id, "quantity": 1, "unit_price": 100}],
    }
    res = client.post(
        "/sales/invoices",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res.status_code == 201
    return res.json()


def test_ar_flow_issue_payment_balance_paid(client, admin_token, user_token):
    partner_id = create_partner(client, admin_token)
    product_id = create_product(client, admin_token)
    invoice = create_invoice(client, admin_token, partner_id, product_id)
    inv_id = invoice["id"]
    grand_total = Decimal(str(invoice["grand_total"]))

    # issue invoice
    res_issue = client.post(
        f"/sales/invoices/{inv_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "ISSUED"},
    )
    assert res_issue.status_code == 200

    # ar entry exists once
    db = SessionLocal()
    entries = (
        db.query(AREntry)
        .filter(AREntry.invoice_id == inv_id, AREntry.type == "INVOICE")
        .all()
    )
    assert len(entries) == 1
    db.close()

    # balance after issue
    res_bal = client.get(
        f"/finance/ar/balances/{partner_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res_bal.status_code == 200
    bal = res_bal.json()
    assert float(bal["total_due"]) == float(grand_total)

    # attempt to pay status before payment -> 409
    res_paid_fail = client.post(
        f"/sales/invoices/{inv_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "PAID"},
    )
    assert res_paid_fail.status_code == 409

    # post payment
    res_pay = client.post(
        "/finance/ar/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"partner_id": partner_id, "amount": str(grand_total)},
    )
    assert res_pay.status_code == 201
    pay_data = res_pay.json()
    assert pay_data["applied"][0]["invoice_id"] == inv_id

    # balance after payment
    res_bal2 = client.get(
        f"/finance/ar/balances/{partner_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert float(res_bal2.json()["total_due"]) == 0.0

    # now set to PAID
    res_paid = client.post(
        f"/sales/invoices/{inv_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "PAID"},
    )
    assert res_paid.status_code == 200

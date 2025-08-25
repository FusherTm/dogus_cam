from uuid import uuid4

from app.db.session import SessionLocal
from app.models.partner import Partner
from app.models.product import Product


def seed_partner_and_product():
    db = SessionLocal()
    partner = Partner(id=uuid4(), name="Cust", type="customer")
    product = Product(id=uuid4(), name="Widget", sku=str(uuid4())[:8], price=100)
    db.add_all([partner, product])
    db.commit()
    db.refresh(partner)
    db.refresh(product)
    db.close()
    return partner, product


def test_admin_create_quote_and_totals(client, admin_token, user_token):
    partner, product = seed_partner_and_product()
    payload = {
        "partner_id": str(partner.id),
        "items": [
            {
                "product_id": str(product.id),
                "quantity": 2,
                "unit_price": 100,
                "line_discount_rate": 10,
                "tax_rate": 20,
            }
        ],
    }
    res = client.post(
        "/sales/quotes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "DRAFT"
    assert float(data["grand_total"]) == 216.0

    res_forbidden = client.post(
        "/sales/quotes",
        headers={"Authorization": f"Bearer {user_token}"},
        json=payload,
    )
    assert res_forbidden.status_code == 403


def test_status_transitions(client, admin_token):
    partner, product = seed_partner_and_product()
    payload = {
        "partner_id": str(partner.id),
        "items": [
            {
                "product_id": str(product.id),
                "quantity": 1,
                "unit_price": 50,
            }
        ],
    }
    res = client.post(
        "/sales/quotes",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    quote_id = res.json()["id"]

    bad = client.post(
        f"/sales/quotes/{quote_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "EXPIRED"},
    )
    assert bad.status_code == 409

    sent = client.post(
        f"/sales/quotes/{quote_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "SENT"},
    )
    assert sent.status_code == 200
    assert sent.json()["status"] == "SENT"

    approved = client.post(
        f"/sales/quotes/{quote_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "APPROVED"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"

    again = client.post(
        f"/sales/quotes/{quote_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "REJECTED"},
    )
    assert again.status_code == 409


def test_list_search_status_filters(client, admin_token, user_token):
    partner1, product = seed_partner_and_product()
    db = SessionLocal()
    partner2 = Partner(id=uuid4(), name="Beta", type="customer")
    db.add(partner2)
    db.commit()
    db.refresh(partner2)
    db.close()

    def create_quote(p_id):
        res = client.post(
            "/sales/quotes",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "partner_id": str(p_id),
                "items": [{"product_id": str(product.id), "quantity": 1, "unit_price": 10}],
            },
        )
        return res.json()

    q1 = create_quote(partner1.id)
    q2 = create_quote(partner1.id)
    client.post(
        f"/sales/quotes/{q2['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "SENT"},
    )
    q3 = create_quote(partner2.id)
    client.post(
        f"/sales/quotes/{q3['id']}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "APPROVED"},
    )

    res_all = client.get(
        "/sales/quotes",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res_all.status_code == 200
    assert res_all.json()["total"] == 3

    res_status = client.get(
        "/sales/quotes",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"status": "APPROVED"},
    )
    assert res_status.status_code == 200
    assert res_status.json()["total"] == 1

    res_partner = client.get(
        "/sales/quotes",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"partner_id": str(partner1.id)},
    )
    assert res_partner.status_code == 200
    assert res_partner.json()["total"] == 2

    res_search = client.get(
        "/sales/quotes",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"search": q1["number"]},
    )
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1

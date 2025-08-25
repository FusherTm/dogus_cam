from app.db.session import SessionLocal
from app.models.partner import Partner

def seed_partners():
    db = SessionLocal()
    partners = [
        Partner(name="Alpha Co", type="customer", tax_number="TN1"),
        Partner(name="Beta LLC", type="supplier", tax_number="TN2"),
        Partner(name="Gamma Ltd", type="both", tax_number="TN3"),
    ]
    db.add_all(partners)
    db.commit()
    db.close()


def test_admin_can_create_and_get_partner(client, admin_token):
    payload = {"name": "Acme", "type": "customer", "tax_number": "UNQ1"}
    res = client.post(
        "/partners",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res.status_code == 201
    data = res.json()
    part_id = data["id"]
    assert data["tax_number"] == "UNQ1"

    res_get = client.get(
        f"/partners/{part_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_get.status_code == 200
    assert res_get.json()["id"] == part_id


def test_list_partners_pagination_search_type(client, user_token):
    seed_partners()
    res = client.get(
        "/partners",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"page": 1, "page_size": 2},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2

    res_search = client.get(
        "/partners",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"search": "beta"},
    )
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1

    res_type = client.get(
        "/partners",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"type": "supplier"},
    )
    assert res_type.status_code == 200
    body_type = res_type.json()
    assert body_type["total"] == 1
    assert body_type["items"][0]["type"] == "supplier"


def test_user_cannot_modify_partner(client, user_token, admin_token):
    res_create = client.post(
        "/partners",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Tmp", "type": "customer"},
    )
    part_id = res_create.json()["id"]

    res_post = client.post(
        "/partners",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "X", "type": "customer"},
    )
    assert res_post.status_code == 403

    res_put = client.put(
        f"/partners/{part_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"phone": "123"},
    )
    assert res_put.status_code == 403

    res_delete = client.delete(
        f"/partners/{part_id}", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res_delete.status_code == 403


def test_tax_number_conflict(client, admin_token):
    payload = {"name": "DupCo", "type": "customer", "tax_number": "DUP1"}
    res1 = client.post(
        "/partners",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res1.status_code == 201
    res2 = client.post(
        "/partners",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res2.status_code == 409

from app.db.session import SessionLocal
from app.models.product import Product
from app.models.organization import Organization


def seed_products():
    db = SessionLocal()
    org = db.query(Organization).filter_by(slug="default").first()
    from uuid import uuid4
    products = [
        Product(id=uuid4(), name="Alpha", sku="ALPHA", price=1, org_id=org.id),
        Product(id=uuid4(), name="Beta", sku="BETA", price=2, org_id=org.id),
        Product(id=uuid4(), name="Gamma", sku="GAMMA", price=3, org_id=org.id),
    ]
    db.add_all(products)
    db.commit()
    db.close()


def test_admin_can_create_and_get_product(client, admin_token):
    payload = {"name": "Widget", "sku": "WID123", "price": 10}
    res = client.post(
        "/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res.status_code == 201
    data = res.json()
    prod_id = data["id"]
    assert data["sku"] == "WID123"

    res_get = client.get(
        f"/products/{prod_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_get.status_code == 200
    assert res_get.json()["id"] == prod_id


def test_list_products_pagination_search(client, user_token):
    seed_products()
    res = client.get(
        "/products",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"page": 1, "page_size": 2},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2

    res_search = client.get(
        "/products",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"search": "beta"},
    )
    assert res_search.status_code == 200
    body_search = res_search.json()
    assert body_search["total"] == 1
    assert body_search["items"][0]["sku"] == "BETA"


def test_duplicate_sku_conflict(client, admin_token):
    payload = {"name": "Item", "sku": "DUP1", "price": 5}
    res1 = client.post(
        "/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res1.status_code == 201
    res2 = client.post(
        "/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res2.status_code == 409


def test_user_cannot_crud_product(client, user_token, admin_token):
    payload = {"name": "UserProd", "sku": "USR1", "price": 1}
    res = client.post(
        "/products",
        headers={"Authorization": f"Bearer {user_token}"},
        json=payload,
    )
    assert res.status_code == 403

    # create as admin for further tests
    admin_res = client.post(
        "/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    prod_id = admin_res.json()["id"]

    res_put = client.put(
        f"/products/{prod_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"price": 2},
    )
    assert res_put.status_code == 403

    res_del = client.delete(
        f"/products/{prod_id}", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res_del.status_code == 403


def test_admin_update_and_delete_product(client, admin_token):
    payload = {"name": "ToUpdate", "sku": "UPD1", "price": 3}
    res = client.post(
        "/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    prod_id = res.json()["id"]

    res_put = client.put(
        f"/products/{prod_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"price": 4},
    )
    assert res_put.status_code == 204

    res_get = client.get(
        f"/products/{prod_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert float(res_get.json()["price"]) == 4

    res_del = client.delete(
        f"/products/{prod_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_del.status_code == 204

    res_get2 = client.get(
        f"/products/{prod_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_get2.status_code == 404

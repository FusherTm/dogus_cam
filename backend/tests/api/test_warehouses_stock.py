from app.db.session import SessionLocal
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.organization import Organization


def seed_product_and_warehouse():
    db = SessionLocal()
    org = db.query(Organization).filter_by(slug="default").first()
    from uuid import uuid4
    product = Product(id=uuid4(), name="Widget", sku="WIDG1", price=1, org_id=org.id)
    warehouse = Warehouse(name="Main", code="MAIN")
    db.add_all([product, warehouse])
    db.commit()
    db.refresh(product)
    db.refresh(warehouse)
    db.close()
    return product, warehouse


def test_warehouse_crud_and_rbac(client, admin_token, user_token):
    # admin create
    res = client.post(
        "/warehouses",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Main", "code": "MAIN"},
    )
    assert res.status_code == 201
    wid = res.json()["id"]

    # user list
    res_list = client.get(
        "/warehouses", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res_list.status_code == 200
    assert res_list.json()["total"] == 1

    # user cannot create
    res_user_create = client.post(
        "/warehouses",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "X", "code": "X"},
    )
    assert res_user_create.status_code == 403

    # admin update
    res_put = client.put(
        f"/warehouses/{wid}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Main2"},
    )
    assert res_put.status_code == 204

    # admin delete
    res_del = client.delete(
        f"/warehouses/{wid}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_del.status_code == 204

    res_get = client.get(
        f"/warehouses/{wid}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_get.status_code == 404


def test_stock_movements_and_stock_endpoint(client, admin_token, user_token):
    product, warehouse = seed_product_and_warehouse()

    payload_in = {
        "product_id": str(product.id),
        "warehouse_id": str(warehouse.id),
        "direction": "IN",
        "quantity": 5,
    }
    res_in = client.post(
        "/stock-movements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload_in,
    )
    assert res_in.status_code == 201

    # stock check
    res_stock = client.get(
        f"/stock/product/{product.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res_stock.status_code == 200
    body = res_stock.json()
    assert body["total"] == 5
    assert body["by_warehouse"][0]["qty"] == 5

    # out movement success
    payload_out = payload_in | {"direction": "OUT", "quantity": 2}
    res_out = client.post(
        "/stock-movements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload_out,
    )
    assert res_out.status_code == 201

    # out movement exceeding stock -> 409
    payload_out_bad = payload_in | {"direction": "OUT", "quantity": 99}
    res_out_bad = client.post(
        "/stock-movements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload_out_bad,
    )
    assert res_out_bad.status_code == 409
    assert res_out_bad.json()["detail"] == "insufficient_stock"

    # user cannot create movement
    res_user = client.post(
        "/stock-movements",
        headers={"Authorization": f"Bearer {user_token}"},
        json=payload_in,
    )
    assert res_user.status_code == 403

    # user can list movements
    res_list = client.get(
        "/stock-movements",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"product_id": str(product.id)},
    )
    assert res_list.status_code == 200
    assert res_list.json()["total"] >= 2

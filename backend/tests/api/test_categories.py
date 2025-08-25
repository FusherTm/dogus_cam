from app.db.session import SessionLocal
from app.models.category import Category


def seed_categories():
    db = SessionLocal()
    categories = [
        Category(name="Alpha", code="ALPHA"),
        Category(name="Beta", code="BETA"),
        Category(name="Gamma", code="GAMMA"),
    ]
    db.add_all(categories)
    db.commit()
    db.close()


def test_admin_can_create_and_get_category(client, admin_token):
    payload = {"name": "Electronics", "code": "ELEC"}
    res = client.post(
        "/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res.status_code == 201
    data = res.json()
    cat_id = data["id"]
    assert data["code"] == "ELEC"

    res_get = client.get(
        f"/categories/{cat_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_get.status_code == 200
    assert res_get.json()["id"] == cat_id


def test_list_categories_pagination_search(client, user_token):
    seed_categories()
    res = client.get(
        "/categories",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"page": 1, "page_size": 2},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2

    res_search = client.get(
        "/categories",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"search": "beta"},
    )
    assert res_search.status_code == 200
    body_search = res_search.json()
    assert body_search["total"] == 1
    assert body_search["items"][0]["code"] == "BETA"


def test_user_cannot_create_category(client, user_token):
    payload = {"name": "UserCat", "code": "USRC"}
    res = client.post(
        "/categories",
        headers={"Authorization": f"Bearer {user_token}"},
        json=payload,
    )
    assert res.status_code == 403


def test_duplicate_category_conflict(client, admin_token):
    payload = {"name": "Dup", "code": "DUP1"}
    res1 = client.post(
        "/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res1.status_code == 201
    res2 = client.post(
        "/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res2.status_code == 409

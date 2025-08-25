from uuid import uuid4


def test_admin_get_user_by_id(client, admin_token, seed_users):
    target = seed_users["alice"]
    response = client.get(
        f"/users/{target.id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(target.id)


def test_admin_get_user_not_found(client, admin_token):
    response = client.get(
        f"/users/{uuid4()}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404

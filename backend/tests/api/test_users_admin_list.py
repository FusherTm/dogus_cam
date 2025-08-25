def test_admin_can_list_users(client, admin_token, seed_users):
    response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) == 3


def test_user_forbidden(client, user_token):
    response = client.get("/users", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403


def test_search_filters(client, admin_token, seed_users):
    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"search": "ali"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == "alice@example.com"

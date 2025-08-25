from app.db.session import SessionLocal
from app.models.employee import Employee


def seed_employee():
    db = SessionLocal()
    emp = Employee(code="E001", first_name="John", last_name="Doe")
    db.add(emp)
    db.commit()
    db.close()


def test_admin_can_create_and_get_employee(client, admin_token):
    payload = {"code": "EMP1", "first_name": "Alice", "last_name": "Smith"}
    res = client.post(
        "/hr/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res.status_code == 201
    emp_id = res.json()["id"]
    res_get = client.get(
        f"/hr/employees/{emp_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_get.status_code == 200
    assert res_get.json()["id"] == emp_id


def test_list_employees(client, admin_token):
    seed_employee()
    res = client.get(
        "/hr/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1


def test_user_cannot_create_employee(client, user_token):
    payload = {"code": "USR1", "first_name": "Bob", "last_name": "Jones"}
    res = client.post(
        "/hr/employees",
        headers={"Authorization": f"Bearer {user_token}"},
        json=payload,
    )
    assert res.status_code == 403


def test_duplicate_code_conflict(client, admin_token):
    payload = {"code": "DUP1", "first_name": "Ann", "last_name": "Brown"}
    res1 = client.post(
        "/hr/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res1.status_code == 201
    res2 = client.post(
        "/hr/employees",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert res2.status_code == 409

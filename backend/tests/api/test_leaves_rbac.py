import uuid
from uuid import uuid4

from app.db.session import SessionLocal
from app.models.leave_type import LeaveType
from app.models.employee import Employee

def test_user_cannot_create_leave_request(client, user_token):
    payload = {
        "employee_id": str(uuid.uuid4()),
        "type_id": str(uuid.uuid4()),
        "start_date": "2025-08-28",
        "end_date": "2025-08-30",
    }
    res = client.post(
        "/hr/leaves/requests",
        headers={
            "Authorization": f"Bearer {user_token}",
            "X-Org-Slug": "default",
        },
        json=payload,
    )
    assert res.status_code == 403
    assert res.json()["detail"] == "admin_only"


def test_admin_can_create_leave_request(client, admin_token):
    db = SessionLocal()
    lt = LeaveType(id=uuid4(), code="YILLIK", name="Yıllık İzin", is_annual=True)
    emp = Employee(id=uuid4(), code="EMP1", first_name="John", last_name="Doe")
    db.add_all([lt, emp])
    db.commit()
    db.refresh(lt)
    db.refresh(emp)
    payload = {
        "employee_id": str(emp.id),
        "type_id": str(lt.id),
        "start_date": "2025-08-28",
        "end_date": "2025-08-30",
    }
    res = client.post(
        "/hr/leaves/requests",
        headers={
            "Authorization": f"Bearer {admin_token}",
            "X-Org-Slug": "default",
        },
        json=payload,
    )
    assert res.status_code == 201
    body = res.json()
    assert body["employee_id"] == str(emp.id)
    db.close()

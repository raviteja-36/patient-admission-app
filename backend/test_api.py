import os
os.environ["DATABASE_URL"] = "sqlite:///./test_patients.db"
os.environ["STATIC_DIR"] = "/nonexistent"
from datetime import timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import today_ist

c = TestClient(app)
good = dict(name="Ravi Kumar", age=54, gender="Male", ward="ICU", department="Cardiology",
            doctor="Dr. Anita Sharma", admission_date=str(today_ist()), status="Admitted")


def test_flow():
    r = c.post("/api/patients", json=good); assert r.status_code == 201
    pid = r.json()["id"]
    assert len(c.get("/api/patients").json()) >= 1
    assert c.get("/api/patients?search=ravi").json()
    assert c.get("/api/patients?ward=Maternity&search=ravi").json() == []
    r = c.put(f"/api/patients/{pid}", json={**good, "age": 55}); assert r.json()["age"] == 55
    r = c.patch(f"/api/patients/{pid}/discharge"); assert r.json()["status"] == "Discharged"
    assert c.patch(f"/api/patients/{pid}/discharge").status_code == 400
    assert c.delete(f"/api/patients/{pid}").status_code == 204
    assert c.get(f"/api/patients/{pid}").status_code == 404


def bad(**over):
    r = c.post("/api/patients", json={**good, **over}); assert r.status_code == 422, over
    return r.json()


def test_validation():
    assert "letters" in bad(name="R4vi")["errors"]["name"]
    assert "required" in bad(name="  ")["errors"]["name"]
    assert "between 0 and 120" in bad(age=121)["errors"]["age"]
    assert "between 0 and 120" in bad(age=-1)["errors"]["age"]
    assert "number" in bad(age="abc")["errors"]["age"]
    assert "required" in bad(gender="")["errors"]["gender"]
    assert "must be one of" in bad(ward="Mars")["errors"]["ward"]
    assert "future" in bad(admission_date=str(today_ist() + timedelta(days=3)))["errors"]["admission_date"]
    assert "valid date" in bad(admission_date="nope")["errors"]["admission_date"]
    r = c.post("/api/patients", json={}); assert r.status_code == 422 and len(r.json()["errors"]) == 7
    assert c.post("/api/patients", json={**good, "age": 0}).status_code == 201
    assert c.post("/api/patients", json={**good, "age": 120}).status_code == 201

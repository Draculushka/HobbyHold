from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.security import create_access_token
from models import Hobby, Notification, Persona, User


def auth_headers(email: str):
    token = create_access_token(data={"sub": email})
    return {"Authorization": f"Bearer {token}"}

def test_comment_reply_and_notifications(client: TestClient, db: Session):
    # Setup: 2 users, each with a persona
    u1 = User(email="u1@test.com", hashed_password="pw", is_active=True)
    db.add(u1)
    db.flush()
    p1 = Persona(user_id=u1.id, username="persona1", is_default=True)
    db.add(p1)
    db.flush()
    u1.active_persona_id = p1.id

    u2 = User(email="u2@test.com", hashed_password="pw", is_active=True)
    db.add(u2)
    db.flush()
    p2 = Persona(user_id=u2.id, username="persona2", is_default=True)
    db.add(p2)
    db.flush()
    u2.active_persona_id = p2.id

    # User 2 creates a hobby
    h = Hobby(title="Hobby 2", description="Desc", persona_id=p2.id)
    db.add(h)
    db.commit()

    # 1. User 1 comments on User 2's hobby
    resp = client.post(
        f"/api/v1/hobbies/{h.id}/comments",
        json={"text": "Nice hobby!"},
        headers=auth_headers(u1.email)
    )
    assert resp.status_code == 200
    root_comment_id = resp.json()["id"]

    # Check notification for User 2
    db.expire_all()
    n1 = db.query(Notification).filter(Notification.user_id == u2.id, Notification.type == "comment").first()
    assert n1 is not None
    assert "Hobby 2" in n1.message

    # 2. User 2 replies to User 1's comment
    resp = client.post(
        f"/api/v1/hobbies/{h.id}/comments",
        json={"text": "Thanks!", "parent_id": root_comment_id},
        headers=auth_headers(u2.email)
    )
    assert resp.status_code == 200
    assert resp.json()["parent_id"] == root_comment_id

    # Check notification for User 1 (reply notification)
    n2 = db.query(Notification).filter(Notification.user_id == u1.id, Notification.type == "reply").first()
    assert n2 is not None
    assert "Ответ" in n2.message

def test_reaction_notifications(client: TestClient, db: Session):
    u1 = User(email="liker@test.com", hashed_password="pw", is_active=True)
    u2 = User(email="owner@test.com", hashed_password="pw", is_active=True)
    db.add_all([u1, u2])
    db.flush()
    p1 = Persona(user_id=u1.id, username="liker_p", is_default=True)
    p2 = Persona(user_id=u2.id, username="owner_p", is_default=True)
    db.add_all([p1, p2])
    db.flush()
    u1.active_persona_id = p1.id
    u2.active_persona_id = p2.id
    h = Hobby(title="Like Me", description="Desc", persona_id=p2.id)
    db.add(h)
    db.commit()

    # User 1 likes User 2's hobby
    client.post(
        f"/api/v1/hobbies/{h.id}/reactions",
        json={"emoji_type": "heart"},
        headers=auth_headers(u1.email)
    )

    # Check notification
    db.expire_all()
    n = db.query(Notification).filter(Notification.user_id == u2.id, Notification.type == "like").first()
    assert n is not None
    assert "❤️" in n.message

def test_api_get_notifications(client: TestClient, db: Session):
    u = User(email="notif@test.com", hashed_password="pw", is_active=True)
    db.add(u)
    db.flush()
    n = Notification(user_id=u.id, type="test", message="Test alert")
    db.add(n)
    db.commit()

    # Fixed path
    resp = client.get("/api/v1/notifications", headers=auth_headers(u.email))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
    assert resp.json()[0]["message"] == "Test alert"

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


from database.sql_database import get_db
from sqlalchemy.orm import Session

from models.employee import Employee
from models.user import User

from utils.jwt import verify_access_token
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user_id = int(payload["sub"])
    user_type = payload["user_type"]

    if user_type == "employee":

        user = (
            db.query(Employee)
            .filter(Employee.id == user_id)
            .first()
        )
    else:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return {
        "id": user.id,
        "role": payload["role"],
        "user_type": user_type,
        "team_id": payload.get("team_id")
    }
def get_current_admin(
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    return current_user
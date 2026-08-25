# Third-Party Imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Local Application Imports
from database.sql_database import get_db
from models.employee import Employee
from models.user import User
from schemas.User import UserRegister
from schemas.employee import EmployeeLogin
from utils.jwt import create_access_token
from utils.logger import logger
from utils.password import (
    hash_password,
    verify_password,
)

# Admin Router Configuration
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login")
def login(
    request: EmployeeLogin,
    db: Session = Depends(get_db)
):
    """
            Authenticate an employee or customer.

            Verifies the provided email and password. If the credentials belong
            to an active employee, employee details are returned. Otherwise,
            the system checks the customer table and returns customer details
            upon successful authentication.

            Args:
                request (EmployeeLogin): User login credentials containing
                    email and password.
                db (Session): Database session.

            Returns:
                dict: Login status along with user details including
                    user type, role, and identifiers.

            Raises:
                JSONResponse: Returns a 500 Internal Server Error if an
                unexpected exception occurs during authentication.
            """
    try:

        logger.info("Login post page arrived")
        # ------------------------
        # Check if its is  Support agent (employee table) admin in employee table
        # ------------------------

        employee = db.query(Employee).filter(
            Employee.email == request.email
        ).first()

        if employee:

            if not verify_password(
                request.password,
                str(employee.password_hash)
            ):
                return {"message": "Invalid Credentials"}
            if not employee.is_active:
                raise HTTPException(
                    status_code=403,
                    detail="Employee account is inactive."
                )

            token = create_access_token(
                data={
                    "sub": str(employee.id),
                    "role": employee.role,
                    "user_type": "employee",
                    "team_id": employee.team_id
                }
            )

            return {
                "message": "Login Successful",
                "access_token": token,
                "token_type": "bearer",
                "name": employee.name,
                "email": employee.email,
                "role": employee.role,
                "user_type": "employee",
                "employee_id": employee.id,
                "team_id": employee.team_id
            }

        # ------------------------
        # Check if it is Customers (users table)
        # ------------------------

        user = db.query(User).filter(
            User.email == request.email
        ).first()

        if user:

            if not verify_password(
                request.password,
                str(user.password)
            ):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password."
                )

            token = create_access_token(
                data={
                    "sub": str(user.id),
                    "role": "customer",
                    "user_type": "customer"
                }
            )

            return {
                "message": "Login Successful",
                "access_token": token,
                "token_type": "bearer",
                "user_type": "customer",
                "name": user.username,
                "email": user.email,
                "role": "customer",
                "customer_id": user.id
            }

        return {
            "message": "Invalid Credentials"
        }
    except HTTPException:
        logger.error(f"login post page request failed")
        raise
    except Exception as e:
        logger.error(f"login post page request failed")
        return JSONResponse( status_code=500,content={"message": f"Login page post page failed with exception{e}"})

@router.post("/register")
def register(
    request: UserRegister,
    db: Session = Depends(get_db)
):
    """
            Register a new customer account.

            Creates a new customer after validating that the email does not
            belong to an employee and that both the email and username are
            unique among existing customers. A unique customer code is also
            generated for every new registration.

            Args:
                request (UserRegister): Customer registration details
                    including username, email, and password.
                db (Session): Database session.

            Returns:
                dict: A confirmation message indicating successful
                    customer registration.

            Raises:
                JSONResponse: Returns a 500 Internal Server Error if an
                unexpected exception occurs during registration.
            """
    try:

        logger.info("Register post page arrived")
        # Check if email belongs to an employee
        employee = db.query(Employee).filter(
            Employee.email == request.email
        ).first()

        if employee:
            return {
                "message": "This email belongs to an employee. Employees cannot register themselves. Please contact the administrator."
            }

        # Check if customer already exists
        existing_user = db.query(User).filter(
            User.email == request.email
        ).first()

        if existing_user:
            return {
                "message": "Email already exists."
            }

        # Optional: Prevent duplicate usernames
        existing_username = db.query(User).filter(
            User.username == request.username
        ).first()

        if existing_username:
            return {
                "message": "Username already exists."
            }


        count = db.query(User).count()
        customer_code = f"CUS-{1001 + count}"

        new_user = User(
            customer_code=customer_code,
            username=request.username,
            email=request.email,
            password=hash_password(request.password),
            role="customer"
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "Registration Successful"
        }
    except Exception as e:
        logger.error("register post page request failed")
        return JSONResponse(f"Register post page request failed with exception{e}")




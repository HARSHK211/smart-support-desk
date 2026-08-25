# Third-Party Imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

# Local Application Imports
from crud.employee_crud import EmployeeCRUD
from database.sql_database import get_db
from models.team import Team
from models.user import User
from schemas.User import UserUpdate
from utils.logger import logger

# Admin Router Configuration
customer_router = APIRouter(
    prefix="/customer",
    tags=["Customer"]
)
@customer_router.put("/profile/{customer_id}")
def update_customer_profile(
    customer_id: int,
    customer: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a customer's profile.

    Updates the customer's username and email after verifying that
    the customer exists in the system.

    Args:
        customer_id (int): Unique identifier of the customer.
        customer (UserUpdate): Updated customer details including
            name and email.
        db (Session): Database session.

    Returns:
        dict: Confirmation message indicating the profile was
        updated successfully.

    Raises:
        HTTPException:
            - 404: If the customer does not exist.
        JSONResponse:
            Returns a 500 Internal Server Error if an unexpected
            exception occurs while updating the customer profile.
    """
    try:
        logger.info("update customer profile arrived")
        existing_customer = (
            db.query(User)
            .filter(User.id == customer_id)
            .first()
        )

        if existing_customer is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        existing_customer.username = customer.name
        existing_customer.email = customer.email

        db.commit()
        db.refresh(existing_customer)
        logger.info(f"update customer {customer.name}")

        return {
            "message": "Profile updated successfully"
        }
    except Exception as e:
        logger.error(f"update customer failed ")
        return JSONResponse(status_code=500,content={"message": f"Update customer failed with exception: {e}"})

@customer_router.get("/count")
def get_customer_count(
        db: Session = Depends(get_db)
):
    """
    Retrieve the total number of customers.

    Fetches the total count of registered customers from the
    database.

    Args:
        db (Session): Database session.

    Returns:
        dict: Total number of registered customers.

    Raises:
        JSONResponse:
            Returns a 500 Internal Server Error if an unexpected
            exception occurs while retrieving the customer count.
    """
    try:
        logger.info(f"get customer count")
        return {"customers": EmployeeCRUD.get_total_customers(db)}
    except Exception as e:
        logger.error(f"get customer count failed ")
        return JSONResponse(status_code=500,content={"message": f"Get customer count failed with exception: {e}"})


@customer_router.get("/teams")
def get_all_teams(
    db: Session = Depends(get_db),
):
    """
        Retrieve all available support teams.

        Fetches the complete list of support teams that customers can
        choose from while creating a support ticket.

        Args:
            db (Session): Database session.

        Returns:
            list[Team]: A list of all support teams.

        Raises:
            JSONResponse: Returns a 500 Internal Server Error if an
            unexpected exception occurs while retrieving the teams.
    """
    try:
        logger.info("customer get all teams page arrived")
        return db.query(Team).all()

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("customer get all teams failed")
        return JSONResponse(
            status_code=500,
            content={
                "message": f"customer all teams get page failed: {e}"
            }
        )



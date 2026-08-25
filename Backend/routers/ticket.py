# Third-Party Imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Local Application Imports
from crud.ticket_crud import TicketCRUD
from database.sql_database import get_db
from dependencies.auth import get_current_user
from models.ticket import Ticket
from schemas.ticket_schemas import CreateTicket
from utils.logger import logger

# Admin Router Configuration
ticket_router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)

@ticket_router.get("/assigned/{employee_id}")
def get_assigned_tickets(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve all tickets assigned to a support agent.

    Fetches every ticket currently assigned to the specified support
    agent regardless of its status.

    Args:
        employee_id (int): Database ID of the support agent.
        db (Session): Database session.

    Returns:
        list[Ticket]: A list of tickets assigned to the employee.

    Raises:
        JSONResponse: Returns a 500 Internal Server Error if an
        unexpected exception occurs while retrieving tickets.
    """
    try:
        logger.info("Admin get assigned tickets page arrived")
        tickets = db.query(Ticket).filter(
            Ticket.assigned_to == employee_id
        ).all()

        return tickets
    except Exception as e:
        logger.error("Admin get assigned tickets page failed")
        return JSONResponse(status_code=500,content=f"Admin get assigned tickets page failed with exception {e}")

@ticket_router.get("/team/{team_id}")
def get_team_open_tickets(
    team_id:int,
    db:Session=Depends(get_db)
):
    """
    Retrieve all open tickets for a support team.

    Returns all tickets that belong to the specified team and are
    currently unassigned with an "Open" status.

    Args:
        team_id (int): Database ID of the support team.
        db (Session): Database session.

    Returns:
        list[Ticket]: A list of open and unassigned tickets for
        the specified team.

    Raises:
        JSONResponse: Returns a 500 Internal Server Error if an
        unexpected exception occurs while retrieving tickets.
    """
    try:
        logger.info("Admin get team open tickets page arrived")
        tickets = db.query(Ticket).filter(
            Ticket.team_id == team_id,
            Ticket.assigned_to == None,
            Ticket.status == "Open"
        ).all()
        return tickets
    except Exception as e:
        logger.error("Admin open ticket page failed")
        return JSONResponse(status_code=500,content=f"Admin open ticket page failed with exception {e}")

@ticket_router.get("/customer/{customer_id}")
def get_customer_tickets(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve all tickets raised by a customer.

    Fetches every ticket submitted by the specified customer,
    including open, in-progress, and closed tickets.

    Args:
        customer_id (int): Database ID of the customer.
        db (Session): Database session.

    Returns:
        list[Ticket]: A list of tickets raised by the customer.

    Raises:
        JSONResponse: Returns a 500 Internal Server Error if an
        unexpected exception occurs while retrieving tickets.
    """
    try:
        logger.info("Admin get customer tickets page arrived")
        tickets = db.query(Ticket).filter(
            Ticket.customer_id == customer_id
        ).all()

        return tickets
    except Exception as e:
        logger.error("Admin get customer tickets page failed")
        return JSONResponse(status_code=500,content=f"Admin get customer tickets page failed with exception {e}")

@ticket_router.post("/")
def create_ticket(
    request: CreateTicket,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Create a new support ticket.

    Allows an authenticated customer to create a new support ticket.
    A unique ticket number is generated automatically, and the ticket
    is initially created with an "Open" status.

    Args:
        request (CreateTicket): Ticket details including title,
            description, team ID, and priority.
        db (Session): Database session.
        current_user (dict): Authenticated user information obtained
            from the JWT access token.

    Returns:
        dict: Confirmation message along with the ID of the newly
        created ticket.

    Raises:
        HTTPException:
            - 403 Forbidden: If the authenticated user is not
              authorized to create tickets.
            - 500 Internal Server Error: If an unexpected error
              occurs while creating the ticket.
    """
    try:
        allowed_roles = ["customer", "support_agent"]

        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to create tickets."
            )

        customer_id = current_user["id"]
        count = db.query(Ticket).count()
        ticket_number = f"TKT-{1001 + count}"

        ticket = Ticket(
            ticket_number=ticket_number,
            customer_id=customer_id,
            title=request.title,
            description=request.description,
            team_id=request.team_id,
            priority=request.priority,
            status="Open"
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return {
            "message": "Ticket created successfully",
            "ticket_id": ticket.id
        }


    except Exception as e:

        db.rollback()  # Undo any pending database changes

        logger.exception(

            f"Failed to create ticket for customer_id={request.customer_id}: {e}"

        )

        raise HTTPException(

            status_code=500,

            detail="Unable to create ticket. Please try again later."

        )

@ticket_router.put("/{ticket_id}/accept")
def accept_ticket(
    ticket_id: int,
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Assign a ticket to a support agent.

    Assigns the specified ticket to the provided support agent and
    updates the ticket status to "In Progress".

    Args:
        ticket_id (int): Database ID of the ticket.
        employee_id (int): Database ID of the support agent.
        db (Session): Database session.

    Returns:
        dict: Confirmation message indicating that the ticket has
        been assigned successfully.

    Raises:
        JSONResponse: Returns a 500 Internal Server Error if an
        unexpected exception occurs while assigning the ticket.
    """
    try:
        logger.info("Support agent accept ticket page arrived")
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id
        ).first()

        if ticket is None:

            return {
                "message": "Ticket not found"
            }

        ticket.assigned_to = employee_id

        ticket.status = "In Progress"

        db.commit()

        return {
            "message": "Ticket Assigned"
        }
    except Exception as e:
        logger.error("Admin accept ticket page failed")
        return JSONResponse(status_code=500,content=f"Admin accept ticket page failed with exception {e}")

@ticket_router.put("/{ticket_id}/close")
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Close a support ticket.

    Updates the specified ticket's status to "Closed", indicating
    that the support request has been completed.

    Args:
        ticket_id (int): Database ID of the ticket.
        db (Session): Database session.

    Returns:
        dict: Confirmation message indicating that the ticket has
        been closed successfully.

    Raises:
        JSONResponse: Returns a 500 Internal Server Error if an
        unexpected exception occurs while closing the ticket.
    """
    try:
        logger.info("Support agent  close ticket page arrived")
        ticket = db.query(Ticket).filter(
                Ticket.id == ticket_id
            ).first()

        if ticket is None:

            return {
                    "message": "Ticket not found"
            }

        ticket.status = "Closed"

        db.commit()

        return {
                "message": "Ticket Closed"
            }
    except Exception as e:
        logger.error("Admin close ticket page failed")
        return JSONResponse(status_code=500,content=f"Admin close ticket page failed with exception {e}")

@ticket_router.get("/open/count")
def get_open_ticket_count(
        db: Session = Depends(get_db)
):
    """
    Retrieve the total number of open tickets.

    Fetches the total count of tickets whose status is marked as
    'open' in the system.

    Args:
        db (Session): Database session.

    Returns:
        dict: Total number of open tickets.

    Raises:
        JSONResponse:
            Returns a 500 Internal Server Error if an unexpected
            exception occurs while retrieving the open ticket count.
    """
    try:
        logger.info("Get open ticket count")
        count = TicketCRUD.get_total_open_tickets(db)
        return {"open_tickets": count}
    except Exception as e:
        logger.error("Admin open ticket count page failed")
        return JSONResponse(status_code=500,content=f"Admin open ticket count page failed with exception {e}")

@ticket_router.get("/priority/stats")
def priority_stats(
    db: Session = Depends(get_db)
):
    """
    Retrieve ticket statistics grouped by priority.

    Fetches the total number of support tickets for each priority
    level (e.g., Low, Medium, High, Critical). This data is
    primarily used for dashboard charts and reporting.

    Args:
        db (Session): Database session.

    Returns:
        list[dict]: A list containing each priority level and its
        corresponding ticket count.

    Raises:
        JSONResponse: Returns a 500 Internal Server Error if an
        unexpected exception occurs while retrieving the statistics.
    """
    try:
        return TicketCRUD.get_ticket_priority_stats(db)

    except Exception as e:
        logger.exception("Failed to retrieve ticket priority statistics")

        return JSONResponse(
            status_code=500,
            content={
                "message": f"Failed to retrieve ticket priority statistics: {e}"
            }
        )

@ticket_router.get("/customers/top")
def top_customers(
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Retrieve the top customers by ticket count.

    Fetches the customers who have raised the highest number of
    support tickets. The number of customers returned can be
    controlled using the `limit` query parameter.

    Args:
        limit (int): Maximum number of customers to return.
            Defaults to 5.
        db (Session): Database session.

    Returns:
        list[dict]: A list of customers along with the total number
        of tickets they have raised.

    Raises:
        JSONResponse: Returns a 500 Internal Server Error if an
        unexpected exception occurs while retrieving the data.
    """
    try:
        return TicketCRUD.get_top_customers(db, limit)

    except Exception as e:
        logger.exception("Failed to retrieve top customers")

        return JSONResponse(
            status_code=500,
            content={
                "message": f"Failed to retrieve top customers: {e}"
            }
        )

@ticket_router.get("/all")
def get_all_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Retrieve all support tickets.

    Fetches every support ticket in the system. This endpoint is
    restricted to administrators and is typically used for ticket
    management and monitoring.

    Args:
        db (Session): Database session.
        current_user (dict): Authenticated user information obtained
            from the JWT access token.

    Returns:
        list[Ticket]: A list of all support tickets.

    Raises:
        HTTPException:
            - 403 Forbidden: If the authenticated user is not an
              administrator.
        JSONResponse:
            Returns a 500 Internal Server Error if an unexpected
            exception occurs while retrieving the tickets.
    """
    try:
        if current_user["role"] != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required."
            )

        tickets = db.query(Ticket).all()

        return tickets

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Admin get all tickets failed")

        return JSONResponse(
            status_code=500,
            content={
                "message": f"Failed to retrieve tickets: {e}"
            }
        )



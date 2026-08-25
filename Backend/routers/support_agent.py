# Third-Party Imports
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime

# Local / Project Imports
from database.sql_database import get_db
from models.agent_support_ticket import AgentSupportTicket
from schemas.agent_support_ticket import AgentSupportCreate
from utils.logger import logger
from models.team import Team
from dependencies.auth import get_current_user


support_agent_router = APIRouter(
    prefix="/agent-support",
    tags=["Agent Support"]
)

@support_agent_router.get("/teams")
def get_teams(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """

    Retrieve all available support teams.

    Fetches the complete list of support teams that support agents can choose from while creating a support ticket.

    Args: db (Session): Database session. current_user: Currently authenticated user.

    Returns: list[Team]: A list of all available support teams.

    Raises: JSONResponse: Returns a 500 Internal Server Error if an unexpected exception occurs while retrieving the teams.

     """
    try:
        logger.info("All teams get pages arrived")
        return db.query(Team).all()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(" get all teams failed")
        return JSONResponse(
            status_code=500,
            content={
                "message": f" all teams get page failed: {e}"
            }
        )

@support_agent_router.post("/tickets/{employee_id}")
def create_support_ticket(
    employee_id: int,
    request: AgentSupportCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket for an employee.

    Creates a support ticket containing the selected team, title, description, and priority.

    Args: employee_id (int): Database ID of the employee creating the support ticket.

    request (AgentSupportCreate): Support ticket details including team ID, title, description, and priority. db (Session): Database session.

    Returns: dict: A success message after the support ticket is created.

    Raises: JSONResponse: Returns a 500 Internal Server Error if an unexpected exception occurs while creating the ticket.

    """
    try:

        count = db.query(
            AgentSupportTicket
        ).count()

        ticket = AgentSupportTicket(
            ticket_number=f"AST-{1001+count}",
            employee_id=employee_id,
            team_id=request.team_id,
            title=request.title,
            description=request.description,
            priority=request.priority
        )

        db.add(ticket)

        db.commit()

        db.refresh(ticket)

        return {
            "message": "Support ticket created."
        }

    except Exception as e:

        logger.exception("Support agent ticket create page arrived ",e)

        return JSONResponse(
            status_code=500,
            content={
                "message": f" Support agent ticket create page failed: {e}"
            }
        )

@support_agent_router.put("/{ticket_id}/accept")
def accept_ticket(
    ticket_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept a support ticket.

    Allows an administrator to accept an open support ticket and assign the ticket to the currently authenticated admin.

    Args: ticket_id (int): Database ID of the support ticket. current_user: Currently authenticated user. db (Session): Database session.

    Returns: dict: A success message containing the ticket ID, assigned admin ID, and updated ticket status.

    Raises: HTTPException: If the current user is not an admin, the ticket does not exist, or the ticket has already been accepted.

    """
    try:
        # Only admins can accept support tickets
        if current_user["role"] != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required."
            )

        ticket = (
            db.query(AgentSupportTicket)
            .filter(AgentSupportTicket.id == ticket_id)
            .first()
        )

        if ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found."
            )

        if ticket.status != "Open":
            raise HTTPException(
                status_code=400,
                detail="Ticket has already been accepted."
            )

        ticket.assigned_admin = current_user["id"]
        ticket.status = "Resolved..Done"

        db.commit()
        db.refresh(ticket)

        return {
            "message": "Support ticket accepted successfully.",
            "ticket_id": ticket.id,
            "assigned_admin": ticket.assigned_admin,
            "status": ticket.status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Support agent ticket create page arrived " , e)

        return JSONResponse(
            status_code=500,
            content={
                "message": f" Support agent ticket create page failed: {e}"
            }
        )

@support_agent_router.put("/my-tickets/{ticket_id}/resolve")
def resolve_my_ticket(
    ticket_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """

    Resolve a support ticket created by the current user.

    Allows the employee who created a support ticket to resolve their own ticket when the ticket is currently in progress.

    Args: ticket_id (int): Database ID of the support ticket. current_user: Currently authenticated user. db (Session): Database session.

    Returns: dict: A success message after the support ticket is resolved.

    Raises: HTTPException: If the ticket does not exist, the current user is not the ticket owner, or the ticket is not currently in progress.

    """
    try:
        logger.info("Resolve a support ticket page arrived")
        ticket = (
            db.query(AgentSupportTicket)
            .filter(AgentSupportTicket.id == ticket_id)
            .first()
        )

        if ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found."
            )

        if ticket.employee_id != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="You can only resolve your own tickets."
            )

        if ticket.status != "In Progress":
            raise HTTPException(
                status_code=400,
                detail="Ticket is not in progress."
            )

        ticket.status = "Resolved"
        ticket.resolved_at = datetime.now()

        db.commit()

        return {
            "message": "Support ticket resolved successfully."
        }
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f" Resolve a support ticket page failed: {e}"
            }
        )
@support_agent_router.get("/my-tickets/{employee_id}")
def my_support_tickets(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """

    Retrieve all support tickets created by an employee.

    Fetches the complete list of support tickets created by the specified employee.

    Args: employee_id (int): Database ID of the employee. db (Session): Database session.

    Returns: list[AgentSupportTicket]: A list of all support tickets created by the employee.

     """
    try:
        logger.info("GET all support tickets page arrived")
        return (
            db.query(AgentSupportTicket)
            .filter(AgentSupportTicket.employee_id == employee_id)
            .all()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Retrieve all support tickets page failed",e)
        return JSONResponse(
            status_code=500,
            content={
                "message": f" GET all support tickets  page failed: {e}"
            }
        )

@support_agent_router.get("/all")
def all_tickets(
    db: Session = Depends(get_db)
):
    """

    Retrieve all support tickets.

    Fetches the complete list of support tickets available in the system.

    Args: db (Session): Database session.

    Returns: list[AgentSupportTicket]: A list of all support tickets.

    Raises: JSONResponse: Returns a 500 Internal Server Error if an unexpected exception occurs while retrieving the tickets.

     """
    try:
        logger.info("GET all support tickets page arrived")
        tickets = db.query(
            AgentSupportTicket
        ).all()

        return tickets

    except Exception as e:
        logger.error("Retrieve all support ticket page failed",e)
        return JSONResponse(
            status_code=500,
            content={
                "message": f"Retrieve all support ticket page failed {e}"
            }
        )



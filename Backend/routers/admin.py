# Third-Party Imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Local Application Imports
from crud.employee_crud import EmployeeCRUD
from database.sql_database import get_db
from dependencies.auth import get_current_admin
from models.employee import Employee
from models.team import Team
from models.ticket import Ticket
from schemas.employee import CreateEmployee
from schemas.team_schema import TeamCreate
from utils.logger import logger
from utils.password import hash_password


# Admin Router Configuration
admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin)]
)

@admin_router.get("/employees")
def get_all_employees(
    db: Session = Depends(get_db)
):
    """
    Retrieve all support employees.

    Returns:
        list: Employee details including assigned team name.
    """
    try:

        logger.info("Admin get all employees page arrived")

        employees = (
            db.query(Employee, Team)
            .outerjoin(
                Team,
                Employee.team_id == Team.id
            )
            .filter(
                Employee.role == "support_agent"
            )
            .all()
        )

        result = []

        for employee, team in employees:

            result.append({
                "id": employee.id,
                "employee_id": employee.employee_id,
                "name": employee.name,
                "email": employee.email,
                "role": employee.role,
                "is_active": employee.is_active,
                "team_id": employee.team_id,
                "team_name": team.team_name if team else None
            })

        return result

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            "Admin all employees get page failed"
        )

        return JSONResponse(
            status_code=500,
            content={
                "message": (
                    f"Admin all employees get page failed "
                    f"with exception: {e}"
                )
            }
        )

@admin_router.get("/teams")
def get_all_teams(
    db: Session = Depends(get_db),
):
    """
        Retrieve all teams from the database.

        Args: db (Session): Database session used to query the Team table.

        Returns: list: A list containing all teams available in the system.

        Raises: HTTPException: If an HTTP-related error occurs.

        Exception: If an unexpected database or server error occurs.

    """
    try:
        logger.info("Admin get all teams page arrived")
        return db.query(Team).all()

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Admin get all teams failed")
        return JSONResponse(
            status_code=500,
            content={
                "message": f"Admin all teams get page failed: {e}"
            }
        )
@admin_router.post("/employees")
def create_employee(
    request: CreateEmployee,
    db: Session = Depends(get_db)
):
    """
    Create a new support agent.

    Args:
        request (CreateEmployee): Employee details including employee ID,
            name, email, and password.
        db (Session): Database session.

    Returns:
        dict: A success message after the employee is created.

    Raises:
        HTTPException: If the employee ID or email already exists.
    """
    try:
        logger.info("Admin create employee page arrived")
        existing_email = db.query(Employee).filter(
            Employee.email == request.email
        ).first()

        if existing_email:
            return {"message": "Email already exists."}

        last_employee = (
            db.query(Employee)
            .order_by(Employee.id.desc())
            .first()
        )

        if last_employee:
            next_no = last_employee.id + 1
        else:
            next_no = 1

        emp_id = f"EMP_{next_no:02d}"

        employee = Employee(
            employee_id=emp_id,
            name=request.name,
            email=request.email,
            password_hash=hash_password(request.password),
            role="support_agent",
            is_active=True
        )

        db.add(employee)
        db.commit()
        db.refresh(employee)

        return {
            "message": "Support Agent created successfully."
        }
    except Exception as e:
        logger.error("Admin create employee page failed")
        return JSONResponse(status_code=500,content={"message": f"Admin create employee page failed with exception as {e}"})

@admin_router.post("/teams", status_code=201)
def add_team(
    team: TeamCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new support team.

    Args:
        team (TeamCreate): Team details containing the team name.
        db (Session): Database session.

    Returns:
        dict: A success message along with the newly created team.

    Raises:
        HTTPException: If a team with the same name already exists.
    """
    try:
        logger.info("Admin add team page arrived")
        existing_team = (
            db.query(Team)
            .filter(Team.team_name == team.team_name)
            .first()
        )

        if existing_team:
            raise HTTPException(
                status_code=400,
                detail="Team already exists."
            )

        new_team = Team(
            team_name=team.team_name,
        )

        db.add(new_team)
        db.commit()
        db.refresh(new_team)

        return {
            "message": "Team added successfully.",
            "team": new_team
        }
    except Exception as e:
        logger.error("Admin add team page failed")
        return JSONResponse(status_code=500,content={"message": f"Admin add team page failed with exception as {e}"})

@admin_router.put("/employees/{employee_id}/team")
def assign_team(
    employee_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """
        Assign a support employee to a specific team.

        Args:
            employee_id (int): Database ID of the employee.
            data (dict): Request data containing the team ID.
            db (Session): Database session used to query and update records.

        Returns:
            dict: Success message containing employee ID, team ID,
                and team name.

        Raises:
            HTTPException:
                - 404: If the employee does not exist.
                - 400: If team_id is not provided.
                - 404: If the specified team does not exist.
            JSONResponse:
                - 500: If an unexpected error occurs while assigning
                  the employee to the team.
        """
    try:

        logger.info(
            f"Assign team requested for employee ID: {employee_id}"
        )

        # ==========================
        # Find employee
        # ==========================

        employee = (
            db.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )

        if not employee:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

        # ==========================
        # Get team ID
        # ==========================

        team_id = data.get("team_id")

        if team_id is None:
            raise HTTPException(
                status_code=400,
                detail="team_id is required."
            )

        # ==========================
        # Verify team exists
        # ==========================

        team = (
            db.query(Team)
            .filter(Team.id == team_id)
            .first()
        )

        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found."
            )

        # ==========================
        # Assign team
        # ==========================

        employee.team_id = team.id

        db.commit()
        db.refresh(employee)

        logger.info(
            f"Employee {employee.id} assigned to team {team.id}"
        )

        return {
            "message": "Team assigned successfully.",
            "employee_id": employee.id,
            "team_id": employee.team_id,
            "team_name": team.team_name
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        logger.exception(
            "Failed to assign team"
        )

        return JSONResponse(
            status_code=500,
            content={
                "message": f"Failed to assign team: {e}"
            }
        )

@admin_router.delete("/employees/{employee_id}/delete")
def remove_agents(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a support employee.

    Removes an employee from the system after validating that the
    employee exists, is not an administrator, and has no assigned
    tickets. Employees with assigned tickets must be deactivated
    instead of being deleted.

    Args:
        employee_id (int): Unique identifier of the employee.
        db (Session): Database session.

    Returns:
        dict: Confirmation message indicating successful deletion.

    Raises:
        HTTPException:
            - 404: If the employee does not exist.
            - 400: If the employee is an administrator.
            - 400: If the employee has assigned tickets.
        JSONResponse:
            Returns a 500 Internal Server Error if an unexpected
            exception occurs during deletion.
    """
    try:
        logger.info("Admin Delete employee page arrived")
        employee = (
            db.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )

        if employee is None:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

        # Optional: Don't allow deleting admin accounts
        if employee.role == "admin":
            raise HTTPException(
                status_code=400,
                detail="Admin account cannot be deleted."
            )
        #ASSIGNED TICKETS USERS CANNOT BE DELETED
        assigned_ticket = (
            db.query(Ticket)
            .filter(Ticket.assigned_to == employee_id)
            .first()
        )

        if assigned_ticket:
            raise HTTPException(
                status_code=400,
                detail="Employee has assigned tickets. Deactivate instead."
            )

        db.delete(employee)
        db.commit()

        return {
            "message": "Employee removed successfully"
        }
    except Exception as e:
        logger.error("Admin Delete employee page failed")
        return JSONResponse(status_code=500,content={"message": f"Admin delete employee page failed with exception as {e}"})

@admin_router.put("/employees/{employee_id}/status")
def change_employee_status(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """
    Toggle the active status of an employee.

    Changes an employee's account status between active and inactive.
    Inactive employees cannot log in until their account is activated
    again.

    Args:
        employee_id (int): Unique identifier of the employee.
        db (Session): Database session.

    Returns:
        dict: Confirmation message along with the employee's updated
        active status.

    Raises:
        HTTPException:
            - 404: If the employee does not exist.
        JSONResponse:
            Returns a 500 Internal Server Error if an unexpected
            exception occurs while updating the employee status.
    """
    try:
        logger.info(
            f"Admin change employee status requested for ID: {employee_id}"
        )

        employee = EmployeeCRUD.toggle_employee_status(
            db,
            employee_id
        )

        if employee is None:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

        logger.info(
            f"Employee {employee_id} status changed to {employee.is_active}"
        )

        return {
            "message": "Status updated successfully",
            "is_active": employee.is_active
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            "Admin change employee status page failed"
        )

        return JSONResponse(
            status_code=500,
            content={
                "message": (
                    "Admin change employee status page failed "
                    f"with exception: {e}"
                )
            }
        )



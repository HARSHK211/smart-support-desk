from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.user import User
from models.employee import Employee
from schemas.User import UserUpdate


class EmployeeCRUD:

    # ==========================
    # Update Customer
    # ==========================

    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        customer: UserUpdate
    ):

        try:

            existing_customer = (
                db.query(User)
                .filter(User.id == customer_id)
                .first()
            )

            if existing_customer is None:
                return None

            existing_customer.username = customer.name
            existing_customer.email = customer.email

            db.commit()
            db.refresh(existing_customer)

            return existing_customer

        except SQLAlchemyError:

            db.rollback()

            raise

    # ==========================
    # Get Total Customers
    # ==========================

    @staticmethod
    def get_total_customers(
        db: Session
    ):

        try:

            return db.query(User).count()

        except SQLAlchemyError:

            db.rollback()

            raise

    # ==========================
    # Toggle Employee Status
    # ==========================

    @staticmethod
    def toggle_employee_status(
        db: Session,
        employee_id: int
    ):

        try:

            employee = (
                db.query(Employee)
                .filter(Employee.id == employee_id)
                .first()
            )

            if employee is None:
                return None

            employee.is_active = not employee.is_active

            db.commit()
            db.refresh(employee)

            return employee

        except SQLAlchemyError:

            db.rollback()

            raise
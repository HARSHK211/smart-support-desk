from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.ticket import Ticket
from models.user import User


class TicketCRUD:

    # ==========================
    # Get Ticket Priority Stats
    # ==========================

    @staticmethod
    def get_ticket_priority_stats(
        db: Session
    ):

        try:

            result = (
                db.query(
                    Ticket.priority,
                    func.count(Ticket.id).label("count")
                )
                .group_by(Ticket.priority)
                .all()
            )

            return [
                {
                    "priority": row.priority,
                    "count": row.count
                }
                for row in result
            ]

        except SQLAlchemyError:

            db.rollback()

            raise

    # ==========================
    # Get Top Customers
    # ==========================

    @staticmethod
    def get_top_customers(
        db: Session,
        limit: int = 5
    ):

        try:

            result = (
                db.query(
                    User.username,
                    func.count(Ticket.id).label("tickets")
                )
                .join(
                    Ticket,
                    Ticket.customer_id == User.id
                )
                .group_by(
                    User.id,
                    User.username
                )
                .order_by(
                    func.count(Ticket.id).desc()
                )
                .limit(limit)
                .all()
            )

            return [
                {
                    "customer": row.username,
                    "tickets": row.tickets
                }
                for row in result
            ]

        except SQLAlchemyError:

            db.rollback()

            raise

    # ==========================
    # Get Total Open Tickets
    # ==========================

    @staticmethod
    def get_total_open_tickets(
        db: Session
    ):

        try:

            return (
                db.query(Ticket)
                .filter(Ticket.status == "open")
                .count()
            )

        except SQLAlchemyError:

            db.rollback()

            raise
# Standard Library Imports
import uvicorn

# Third-Party Imports
from fastapi import FastAPI
from fastapi.responses import (
    RedirectResponse,
    JSONResponse
)

# Local / Project Imports
from database.sql_database import Base, engine
from routers.auth import router
from routers.admin import admin_router
from routers.ticket import ticket_router
from routers.customer import customer_router
from routers.support_agent import support_agent_router
from utils.logger import logger

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Smart Support Desk API",
    version="1.0.0"
)

@app.get("/")
def home():
    """
    Redirect users to the Smart Support Desk Streamlit application.
    """
    try:
        logger.info("Home page arrived")

        return RedirectResponse(
            url="http://localhost:8501"
        )

    except Exception as e:
        logger.exception("Home page request failed")

        return JSONResponse(
            status_code=500,
            content={
                "message": f"Home page request failed. Exception: {str(e)}"
            }
        )

# Register routers
app.include_router(router)
app.include_router(admin_router)
app.include_router(ticket_router)
app.include_router(customer_router)
app.include_router(support_agent_router)


# ============================
# Application Entry Point
# ============================
if __name__ == "__main__":
    logger.info("Starting Smart Support Desk API...")

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
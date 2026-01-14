from fastapi import APIRouter
from app.api.v1.endpoints import integrations, agent

# Create the main v1 router
api_router = APIRouter()

# Include the Integrations Router (The one with Composio logic)
api_router.include_router(
    integrations.router, 
    prefix="/integrations", 
    tags=["Integrations"]
)

api_router.include_router(
    agent.router,
    prefix="/agent",
    tags=["Agent"]
)
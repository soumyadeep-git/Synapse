from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.core.celery_app import celery_app

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Synapse Autonomous Ops Agent API",
    version="1.0.0",
)

# Set all CORS enabled origins
# In production, replace ["*"] with [settings.FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health Check Endpoint
@app.get("/health")
def health_check():
    """
    Simple health check to ensure the container is running.
    """
    return {
        "status": "healthy", 
        "service": settings.PROJECT_NAME,
        "database": "connected" # You can add actual DB check logic here later
    }

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Synapse API. Go to /docs for Swagger UI."}
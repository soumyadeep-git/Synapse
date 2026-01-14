from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging
from pydantic import BaseModel

from app.core.database import get_db
from app.core.cache import get_cache, set_cache
from app.core.config import settings
from app.models.integration import IntegrationMetadata
from composio import Composio

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Composio
composio_client = Composio(api_key=settings.COMPOSIO_API_KEY)

# Define relevant tools for the Ops Agent
OPS_TOOLS = [
    "github", "jira", "slack", "pagerduty", 
    "linear", "notion", "gmail", "googlecalendar"
]

async def get_current_user():
    # TODO: Replace with real JWT Auth later
    return {"sub": "default_admin_user"}

@router.get("/available", response_model=List[dict])
async def get_available_integrations(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns all available ops tools with user connection status"""
    user_id = user.get('sub')
    if not user_id:
        raise HTTPException(status_code=403, detail="User ID not found")
    
    try:
        composio_cache_key = f"ops_agent:{user_id}:mcp:composio_apps"
        metadata_cache_key = f"ops_agent:{user_id}:mcp:integration_metadata"
        
        # 1. Fetch Composio Toolkits (Cached)
        composio_apps = get_cache(composio_cache_key)
        
        if not composio_apps:
            logger.info(f"Cache miss: Fetching apps from Composio for {user_id}")
            # Get integrations from Composio
            toolkits_response = composio_client.integrations.get()
            
            composio_apps = {}
            TARGET_TOOLS_LOWER = [t.lower() for t in OPS_TOOLS]
            
            # Iterate through the response list
            for app in toolkits_response:
                # Handle potential Pydantic model or Dict access
                slug = getattr(app, "slug", "").lower() if hasattr(app, "slug") else app.get("slug", "").lower()
                
                if not slug or slug not in TARGET_TOOLS_LOWER:
                    continue
                    
                meta = getattr(app, "meta", {}) if hasattr(app, "meta") else app.get("meta", {})
                categories = meta.get("categories", [])
                
                composio_apps[slug] = {
                    "integration_id": slug,
                    "name": getattr(app, "name", slug.title()) if hasattr(app, "name") else app.get("name", slug.title()),
                    "description": meta.get("description", ""),
                    "logo": meta.get("logo", None),
                    "categories": categories
                }
            
            set_cache(composio_cache_key, composio_apps, ttl=3600)
        
        # 2. Fetch Metadata from Postgres (Cached)
        metadata_map = get_cache(metadata_cache_key)
        
        if not metadata_map:
            logger.info(f"Metadata miss: Querying Postgres for {user_id}")
            result = await db.execute(
                select(IntegrationMetadata).where(IntegrationMetadata.user_id == user_id)
            )
            user_metadata = result.scalars().all()
            
            metadata_map = {
                m.integration_id: {
                    "status": m.status,
                    "connected_account_id": m.connected_account_id
                } for m in user_metadata
            }
            set_cache(metadata_cache_key, metadata_map, ttl=600)
            
        # 3. Combine Data
        available_integrations = []
        for app_slug, app_info in composio_apps.items():
            db_status = metadata_map.get(app_slug, {})
            
            integration_obj = {
                "integration_id": app_info.get("integration_id"),
                "name": app_info.get("name"),
                "description": app_info.get("description"),
                "category": app_info.get("categories"),
                "logo": app_info.get("logo"),
                "status": db_status.get("status", "disconnected"),
                "connected_account_id": db_status.get("connected_account_id"),
                "auth_config_id": None
            }
            available_integrations.append(integration_obj)
        
        return available_integrations

    except Exception as e:
        logger.error(f"Error fetching integrations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class ConnectionRequest(BaseModel):
    integration_id: str # e.g., "jira", "slack"

@router.post("/connect")
async def initiate_connection(
    request: ConnectionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Creates a connection request to Composio and returns the Redirect URL.
    The Frontend will open this URL so the user can log in to Jira/Slack.
    """
    user_id = user.get('sub')
    try:
        # 1. Ask Composio for a connection object
        # We use the user_id as the "entity_id" so Composio knows who this belongs to.
        entity = composio_client.get_entity(id=user_id)
        
        connection = entity.initiate_connection(
            app_name=request.integration_id,
            redirect_url="http://localhost:3000/settings" # Where to go after login (Frontend URL)
        )
        
        logger.info(f"Initiated connection for {request.integration_id}: {connection.redirectUrl}")
        
        return {
            "redirectUrl": connection.redirectUrl,
            "connectionId": connection.connectedAccountId
        }

    except Exception as e:
        logger.error(f"Failed to create connection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class ConnectionRequest(BaseModel):
    integration_id: str # e.g., "jira", "slack"

@router.post("/connect")
async def initiate_connection(
    request: ConnectionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Creates a connection request to Composio and returns the Redirect URL.
    The Frontend will open this URL so the user can log in to Jira/Slack.
    """
    user_id = user.get('sub')
    try:
        # 1. Ask Composio for a connection object
        # We use the user_id as the "entity_id" so Composio knows who this belongs to.
        entity = composio_client.get_entity(id=user_id)
        
        connection = entity.initiate_connection(
            app_name=request.integration_id,
            redirect_url="http://localhost:3000/settings" # Where to go after login (Frontend URL)
        )
        
        logger.info(f"Initiated connection for {request.integration_id}: {connection.redirectUrl}")
        
        return {
            "redirectUrl": connection.redirectUrl,
            "connectionId": connection.connectedAccountId
        }

    except Exception as e:
        logger.error(f"Failed to create connection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
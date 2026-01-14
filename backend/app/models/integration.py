from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class IntegrationMetadata(Base):
    __tablename__ = "integration_metadata"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) # The "sub" from your code
    integration_id = Column(String, index=True) # e.g., "jira", "slack"
    status = Column(String, default="disconnected") # "connected" | "disconnected"
    connected_account_id = Column(String, nullable=True)
    connection_details = Column(JSON, default={}) # Stores extra metadata
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
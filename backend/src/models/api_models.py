from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import datetime


class APIResponse(BaseModel):
    """
    Standard response structure returned by API endpoints
    """
    status: str = Field(..., description="Response status (success, error)", pattern="^(success|error)$")
    data: Optional[Union[Dict, List]] = Field(default=None, description="The main response data")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata about the response")
    errors: Optional[List[Dict]] = Field(default=[], description="List of errors if status is error")


class QueryRequest(BaseModel):
    """
    Represents a user query request to the system
    """
    query: str = Field(..., description="The natural language query from the user", min_length=1, max_length=1000)
    query_type: Optional[str] = Field(default="text_search", description="Type of query (text_search, url_search, module_search, section_search)")
    parameters: Optional[Dict] = Field(default={}, description="Additional parameters for the query")
    context: Optional[Dict] = Field(default={}, description="Additional context for the agent")


class VectorResponse(BaseModel):
    """
    Response structure for vector retrieval operations
    """
    id: str = Field(..., description="Unique identifier for the vector record")
    embedding: List[float] = Field(..., description="The vector embedding representation of the content")
    metadata: Dict = Field(..., description="Key-value pairs containing contextual information")
    similarity_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Similarity score if retrieved via semantic search")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="When the vector was created/updated")


class VectorListResponse(BaseModel):
    """
    Response structure for multiple vector retrieval operations
    """
    vectors: List[VectorResponse] = Field(..., description="List of retrieved vector embeddings")
    total_count: int = Field(..., description="Total number of vectors found")
    limit: Optional[int] = Field(default=100, description="Maximum number of vectors returned")
    offset: Optional[int] = Field(default=0, description="Offset for pagination")
    query_text: Optional[str] = Field(default=None, description="Original query text for semantic search")
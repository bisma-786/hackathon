from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from datetime import datetime


class AgentRequest(BaseModel):
    """
    Request structure for the OpenAI agent
    """
    query: str = Field(..., description="The original user query", min_length=1, max_length=1000)
    context: Optional[List[str]] = Field(default=[], description="Retrieved context to provide to the agent")
    instructions: Optional[str] = Field(default="You are an AI assistant for the AI-Driven Robotics Textbook. Answer questions based on the provided context.",
                                      description="Instructions for how the agent should respond")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0, description="Temperature setting for response creativity")
    max_tokens: Optional[int] = Field(default=500, ge=1, description="Maximum tokens in the response")
    parameters: Optional[Dict] = Field(default={}, description="Additional parameters for the query")


class AgentResponse(BaseModel):
    """
    Response from the OpenAI agent with context-aware answers
    """
    answer: str = Field(..., description="The agent's answer to the user's query", min_length=1)
    sources: List[str] = Field(default=[], description="List of source identifiers used to generate the answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the answer (0.0 to 1.0)")
    retrieved_context: List[Dict] = Field(default=[], description="Context used to generate the answer")
    followup_questions: List[str] = Field(default=[], description="Suggested follow-up questions")


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
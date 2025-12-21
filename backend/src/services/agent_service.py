"""
Agent service to handle OpenAI agent query processing with RAG functionality
"""

from typing import List, Dict, Optional
from src.lib.config import get_openai_client, get_qdrant_client, get_collection_name, AgentException
from src.services.qdrant_service import QdrantService
from src.models.agent_models import AgentRequest, AgentResponse
from openai import OpenAI
import logging


class AgentService:
    """
    Service class to handle OpenAI agent query processing with RAG functionality
    """

    def __init__(self):
        self.qdrant_service = QdrantService()
        self.logger = logging.getLogger(__name__)
        self._openai_client = None
        self._openai_available = False
        self._initialize_openai_client()

    def _initialize_openai_client(self):
        """Initialize the OpenAI client with connection validation"""
        try:
            self._openai_client = get_openai_client()
            # Test the connection with a simple call
            self._openai_available = self._validate_openai_connection()
            if not self._openai_available:
                self.logger.warning("OpenAI connection validation failed during initialization")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self._openai_available = False
            self._openai_client = None

    def _validate_openai_connection(self) -> bool:
        """Validate that the OpenAI connection is working"""
        try:
            if not self._openai_client:
                return False
            # Test with a simple model listing call
            models = self._openai_client.models.list()
            return len(models.data) > 0
        except Exception as e:
            self.logger.warning(f"OpenAI connection validation failed: {str(e)}")
            return False

    @property
    def openai_client(self):
        """Property to access the OpenAI client with automatic reconnection if needed"""
        if not self._openai_client or not self._openai_available:
            self.logger.info("Reinitializing OpenAI client due to connection issues")
            self._initialize_openai_client()
        return self._openai_client

    def process_agent_query(self, agent_request: AgentRequest) -> AgentResponse:
        """
        Process an agent query by retrieving relevant context and generating a response
        """
        try:
            self.logger.info(f"Processing agent query: {agent_request.query[:100]}...")

            # Retrieve relevant context based on the query
            context_chunks = self._retrieve_context(agent_request.query)

            # Format context for the agent
            formatted_context = self._format_context_for_agent(context_chunks)

            # Generate response using OpenAI
            response_text = self._generate_response(agent_request, formatted_context)

            # Calculate confidence score based on context quality
            confidence_score = self._calculate_confidence(context_chunks)

            # Extract sources from context
            sources = self._extract_sources(context_chunks)

            # Generate follow-up questions
            followup_questions = self._generate_followup_questions(agent_request.query, response_text)

            # Create and return the agent response
            agent_response = AgentResponse(
                answer=response_text,
                sources=sources,
                confidence=confidence_score,
                retrieved_context=context_chunks,
                followup_questions=followup_questions
            )

            self.logger.info(f"Successfully processed agent query, response length: {len(response_text)}")
            return agent_response

        except AgentException:
            # Re-raise custom agent exceptions
            raise
        except Exception as e:
            self.logger.error(f"Error processing agent query: {str(e)}")
            raise AgentException(f"Error processing agent query: {str(e)}")

    def _retrieve_context(self, query: str) -> List[Dict]:
        """
        Retrieve relevant context chunks based on the query
        """
        # For now, we'll use semantic search to retrieve relevant chunks
        # In a more sophisticated implementation, we might use multiple retrieval strategies
        try:
            # Use the Qdrant service to perform semantic search
            # For now, we'll return an empty list since we need to implement semantic search properly
            # This will be enhanced when we implement proper embedding generation
            search_results = self.qdrant_service.semantic_search(query, limit=5)

            context_chunks = []
            for vector_resp in search_results.vectors:
                chunk = {
                    'id': vector_resp.id,
                    'content': vector_resp.metadata.get('content', ''),
                    'url': vector_resp.metadata.get('url', ''),
                    'module': vector_resp.metadata.get('module', ''),
                    'section': vector_resp.metadata.get('section', ''),
                    'similarity_score': vector_resp.similarity_score
                }
                context_chunks.append(chunk)

            return context_chunks
        except Exception as e:
            self.logger.error(f"Error retrieving context: {str(e)}")
            return []

    def _format_context_for_agent(self, context_chunks: List[Dict]) -> str:
        """
        Format the retrieved context chunks for the agent
        """
        if not context_chunks:
            return "No relevant context found in the textbook."

        formatted_context = "Relevant context from the AI-Driven Robotics Textbook:\n\n"
        for i, chunk in enumerate(context_chunks, 1):
            content = chunk.get('content', '')[:500]  # Limit content length
            url = chunk.get('url', '')
            module = chunk.get('module', '')
            section = chunk.get('section', '')

            formatted_context += f"Source {i}:\n"
            formatted_context += f"Content: {content}\n"
            if module:
                formatted_context += f"Module: {module}\n"
            if section:
                formatted_context += f"Section: {section}\n"
            if url:
                formatted_context += f"URL: {url}\n"
            formatted_context += "\n"

        return formatted_context

    def _generate_response(self, agent_request: AgentRequest, formatted_context: str) -> str:
        """
        Generate a response using OpenAI based on the query and context
        """
        try:
            # Construct the system message with instructions
            system_message = agent_request.instructions or "You are an AI assistant for the AI-Driven Robotics Textbook. Answer questions based on the provided context."

            # Construct the user message with context and query
            user_message = f"{formatted_context}\n\nUser Query: {agent_request.query}\n\nPlease provide a helpful answer based on the context above. If the context doesn't contain relevant information, please state that clearly."

            # Make the OpenAI API call
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Could be configurable
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=agent_request.temperature,
                max_tokens=agent_request.max_tokens
            )

            # Extract the response text
            response_text = response.choices[0].message.content
            return response_text if response_text else "I couldn't generate a response based on the provided context."

        except Exception as e:
            # Handle specific OpenAI errors
            error_msg = str(e)
            self.logger.error(f"Error generating response from OpenAI: {error_msg}")

            # Check for specific OpenAI error types and handle accordingly
            if "authentication_error" in error_msg.lower() or "api key" in error_msg.lower():
                self.logger.warning("Authentication error with OpenAI API, returning default response")
                return "I'm having trouble accessing the AI service. Please check the API key configuration."
            elif "rate_limit" in error_msg.lower():
                self.logger.warning("Rate limit exceeded for OpenAI API, returning default response")
                return "I've reached the rate limit for AI queries. Please try again later."
            elif "invalid_request_error" in error_msg.lower():
                self.logger.warning(f"Invalid request to OpenAI: {error_msg}")
                return "I couldn't process your request. Please try rephrasing your question."
            elif "server_error" in error_msg.lower() or "500" in error_msg:
                self.logger.warning("OpenAI server error, returning default response")
                return "The AI service is temporarily unavailable. Please try again later."
            else:
                # For other errors, return a default response for graceful degradation
                self.logger.warning(f"Error communicating with OpenAI: {error_msg}, returning default response")
                return "I'm currently unable to process your request. The AI service may be temporarily unavailable."

    def _calculate_confidence(self, context_chunks: List[Dict]) -> float:
        """
        Calculate a confidence score based on the quality of retrieved context
        """
        if not context_chunks:
            return 0.1  # Low confidence if no context found

        # Calculate multiple factors for confidence scoring
        total_similarity = 0
        valid_scores = 0
        total_content_length = 0

        for chunk in context_chunks:
            # Factor 1: Similarity score (if available)
            score = chunk.get('similarity_score')
            if score is not None:
                total_similarity += score
                valid_scores += 1

            # Factor 2: Content length (longer relevant content might be better)
            content = chunk.get('content', '')
            total_content_length += len(content)

        # Calculate average similarity if scores are available
        avg_similarity = total_similarity / valid_scores if valid_scores > 0 else 0

        # Calculate average content length per chunk
        avg_content_length = total_content_length / len(context_chunks) if len(context_chunks) > 0 else 0

        # Weighted confidence calculation
        confidence = 0.0

        # Similarity score contributes 70% to confidence if available
        if valid_scores > 0:
            confidence += avg_similarity * 0.7

        # Content length contributes 30% to confidence (normalized)
        # Normalize content length: 0-500 chars = 0-0.3 confidence
        normalized_length = min(1.0, avg_content_length / 500.0) * 0.3
        confidence += normalized_length

        # Ensure confidence is between 0.1 and 0.95
        confidence = max(0.1, min(0.95, confidence))

        return confidence

    def _extract_sources(self, context_chunks: List[Dict]) -> List[str]:
        """
        Extract unique sources from context chunks
        """
        sources = set()
        for chunk in context_chunks:
            url = chunk.get('url')
            if url:
                sources.add(url)

        return list(sources)

    def _generate_followup_questions(self, original_query: str, response: str) -> List[str]:
        """
        Generate potential follow-up questions based on the original query and response
        """
        # For now, return an empty list
        # In a more sophisticated implementation, we could use the LLM to generate follow-up questions
        return []
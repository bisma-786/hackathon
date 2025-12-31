---
sidebar_position: 999
title: AI Assistant Integration
---

# AI Assistant Integration

This textbook includes an AI-powered assistant that can answer questions about the book content using Retrieval-Augmented Generation (RAG).

## How It Works

The AI assistant uses a RAG system that:
- Retrieves relevant content from the book's knowledge base
- Generates contextually appropriate answers based on the retrieved information
- Maintains conversation history to support follow-up questions

## Using the Assistant

You can access the AI assistant in two ways:

1. **Dedicated Page**: Visit the [AI Assistant page](/chatbot-demo) for a focused experience
2. **Integrated Experience**: Look for the chatbot icon on relevant documentation pages (coming soon)

## Features

- **Contextual Understanding**: The assistant understands the context of your questions
- **Citation**: Responses include references to relevant book sections
- **Conversation History**: Maintains context across multiple questions
- **Real-time Responses**: Get answers to your questions quickly

## Best Practices

- Ask specific questions about the book content
- Use follow-up questions to dive deeper into topics
- If you get a "no relevant content found" response, try rephrasing your question

## Technical Details

The assistant is powered by:
- OpenAI GPT models for natural language understanding
- Qdrant vector database for content retrieval
- FastAPI backend for processing requests
- React frontend for the user interface

For developers interested in the implementation, see the backend API documentation.
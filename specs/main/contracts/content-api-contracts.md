# Content Management API Contracts

## Overview
API contracts for managing textbook content, including modules, chapters, sections, and related entities.

## Content Structure API

### Module Operations

#### GET /api/modules
- **Description**: Retrieve all textbook modules
- **Request**: No parameters required
- **Response**:
  ```json
  {
    "modules": [
      {
        "id": "string",
        "title": "string",
        "description": "string",
        "learning_objectives": ["string"],
        "prerequisites": ["string"],
        "estimated_duration": "string",
        "order": "integer",
        "status": "draft|review|published|archived"
      }
    ]
  }
  ```
- **Error Codes**:
  - 200: Success
  - 500: Server error

#### GET /api/modules/{moduleId}
- **Description**: Retrieve specific module details
- **Parameters**:
  - moduleId (path): Unique identifier for the module
- **Response**: Single module object as above
- **Error Codes**:
  - 200: Success
  - 404: Module not found
  - 500: Server error

#### GET /api/modules/{moduleId}/chapters
- **Description**: Retrieve all chapters in a specific module
- **Parameters**:
  - moduleId (path): Unique identifier for the module
- **Response**:
  ```json
  {
    "chapters": [
      {
        "id": "string",
        "title": "string",
        "description": "string",
        "learning_objectives": ["string"],
        "prerequisites": ["string"],
        "estimated_duration": "string",
        "order": "integer",
        "status": "draft|review|published|archived"
      }
    ]
  }
  ```

### Chapter Operations

#### GET /api/chapters/{chapterId}
- **Description**: Retrieve specific chapter details
- **Parameters**:
  - chapterId (path): Unique identifier for the chapter
- **Response**:
  ```json
  {
    "id": "string",
    "module_id": "string",
    "title": "string",
    "content": "string (Markdown)",
    "learning_objectives": ["string"],
    "prerequisites": ["string"],
    "next_chapter_id": "string",
    "estimated_duration": "string",
    "order": "integer",
    "status": "draft|review|published|archived"
  }
  ```

#### GET /api/chapters/{chapterId}/sections
- **Description**: Retrieve all sections in a specific chapter
- **Parameters**:
  - chapterId (path): Unique identifier for the chapter
- **Response**:
  ```json
  {
    "sections": [
      {
        "id": "string",
        "title": "string",
        "content": "string (Markdown)",
        "type": "text|code|diagram|exercise",
        "order_in_chapter": "integer",
        "status": "draft|review|published|archived"
      }
    ]
  }
  ```

### Section Operations

#### GET /api/sections/{sectionId}
- **Description**: Retrieve specific section details
- **Parameters**:
  - sectionId (path): Unique identifier for the section
- **Response**:
  ```json
  {
    "id": "string",
    "chapter_id": "string",
    "title": "string",
    "content": "string (Markdown)",
    "type": "text|code|diagram|exercise",
    "order_in_chapter": "integer",
    "content_elements": [
      {
        "id": "string",
        "type": "text|code|image|video|equation",
        "content": "string",
        "caption": "string",
        "source": "string"
      }
    ],
    "status": "draft|review|published|archived"
  }
  ```

## Search and Navigation API

### GET /api/search
- **Description**: Search across all textbook content
- **Parameters**:
  - query (query): Search term
  - limit (query, optional): Number of results (default: 10)
  - offset (query, optional): Offset for pagination (default: 0)
- **Response**:
  ```json
  {
    "results": [
      {
        "id": "string",
        "type": "module|chapter|section",
        "title": "string",
        "snippet": "string",
        "url": "string",
        "relevance_score": "number"
      }
    ],
    "total_results": "integer"
  }
  ```

### GET /api/navigation
- **Description**: Retrieve the complete navigation structure
- **Request**: No parameters required
- **Response**:
  ```json
  {
    "navigation": {
      "modules": [
        {
          "id": "string",
          "title": "string",
          "path": "string",
          "chapters": [
            {
              "id": "string",
              "title": "string",
              "path": "string",
              "sections": [
                {
                  "id": "string",
                  "title": "string",
                  "path": "string"
                }
              ]
            }
          ]
        }
      ]
    }
  }
  ```

## Reference and Citation API

### GET /api/references
- **Description**: Retrieve all references used in the textbook
- **Parameters**:
  - type (query, optional): Filter by reference type (book|paper|website|documentation)
  - limit (query, optional): Number of results (default: 50)
  - offset (query, optional): Offset for pagination
- **Response**:
  ```json
  {
    "references": [
      {
        "id": "string",
        "type": "book|paper|website|documentation",
        "title": "string",
        "authors": ["string"],
        "publication_date": "string",
        "url": "string",
        "doi": "string",
        "citation_text": "string",
        "accessed_date": "string"
      }
    ]
  }
  ```

### GET /api/references/{referenceId}
- **Description**: Retrieve specific reference details
- **Parameters**:
  - referenceId (path): Unique identifier for the reference
- **Response**: Single reference object as above

## Learning Objectives API

### GET /api/learning-objectives
- **Description**: Retrieve all learning objectives in the textbook
- **Parameters**:
  - parent_type (query, optional): Filter by parent type (module|chapter|section)
  - parent_id (query, optional): Filter by specific parent entity
- **Response**:
  ```json
  {
    "objectives": [
      {
        "id": "string",
        "parent_id": "string",
        "parent_type": "module|chapter|section",
        "description": "string",
        "assessment_method": "string"
      }
    ]
  }
  ```

## Exercise and Assessment API

### GET /api/exercises
- **Description**: Retrieve exercises filtered by various criteria
- **Parameters**:
  - section_id (query, optional): Filter by section
  - difficulty_level (query, optional): Filter by difficulty (beginner|intermediate|advanced)
  - limit (query, optional): Number of results (default: 20)
- **Response**:
  ```json
  {
    "exercises": [
      {
        "id": "string",
        "section_id": "string",
        "title": "string",
        "problem_statement": "string",
        "solution": "string",
        "difficulty_level": "beginner|intermediate|advanced",
        "tags": ["string"],
        "learning_objective_ids": ["string"]
      }
    ]
  }
  ```

## Error Response Format

All error responses follow this format:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "string (optional)"
  }
}
```

## Authentication
All API endpoints are public and do not require authentication for reading operations.
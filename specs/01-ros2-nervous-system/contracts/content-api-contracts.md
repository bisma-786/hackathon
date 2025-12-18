# Content Management API Contracts: Module 1

## Overview
API contracts for managing Module 1 content: The Robotic Nervous System (ROS 2).

## Module-Specific API

### Module Operations

#### GET /api/modules/01-ros2-nervous-system
- **Description**: Retrieve Module 1 details
- **Request**: No parameters required
- **Response**:
  ```json
  {
    "id": "01-ros2-nervous-system",
    "title": "The Robotic Nervous System (ROS 2)",
    "description": "ROS 2 as middleware for embodied intelligence applications",
    "chapters_count": 3,
    "learning_objectives": ["understand ROS 2 as middleware", "master communication primitives", "create robot representations"],
    "prerequisites": ["basic robotics concepts", "distributed systems", "Python programming"],
    "estimated_duration": "8-10 hours",
    "status": "published"
  }
  ```
- **Error Codes**:
  - 200: Success
  - 404: Module not found
  - 500: Server error

#### GET /api/modules/01-ros2-nervous-system/chapters
- **Description**: Retrieve all chapters in Module 1
- **Request**: No parameters required
- **Response**:
  ```json
  {
    "chapters": [
      {
        "id": "chapter-1-ros2-nervous-system",
        "module_id": "01-ros2-nervous-system",
        "title": "ROS 2 as the Nervous System of Physical AI",
        "description": "Middleware concepts, DDS, real-time constraints, fault tolerance",
        "chapter_number": 1,
        "learning_objectives": ["understand ROS 2 middleware role", "explain DDS architecture", "compare ROS 1 vs ROS 2"],
        "estimated_duration": "3-4 hours",
        "status": "published"
      },
      {
        "id": "chapter-2-communication-primitives",
        "module_id": "01-ros2-nervous-system",
        "title": "Communication Primitives in ROS 2",
        "description": "Nodes, topics, services, actions, QoS policies, rclpy",
        "chapter_number": 2,
        "learning_objectives": ["master communication primitives", "understand QoS tradeoffs", "connect Python AI agents"],
        "estimated_duration": "3-4 hours",
        "status": "published"
      },
      {
        "id": "chapter-3-robot-body-representation",
        "module_id": "01-ros2-nervous-system",
        "title": "Robot Body Representation",
        "description": "URDF, kinematic chains, sensors, actuators, sim-to-real preparation",
        "chapter_number": 3,
        "learning_objectives": ["create URDF models", "understand kinematic chains", "prepare for sim-to-real"],
        "estimated_duration": "2-3 hours",
        "status": "published"
      }
    ]
  }
  ```

### Chapter-Specific Operations

#### GET /api/chapters/{chapterId}/learning-objectives
- **Description**: Retrieve learning objectives for a specific chapter
- **Parameters**:
  - chapterId (path): Unique identifier for the chapter
- **Response**:
  ```json
  {
    "learning_objectives": [
      {
        "id": "lo-01-01-01",
        "chapter_id": "chapter-1-ros2-nervous-system",
        "description": "Understand the role of ROS 2 as middleware in embodied intelligence applications",
        "bloom_level": "understand",
        "assessment_method": "comprehension exercises"
      }
    ]
  }
  ```

#### GET /api/chapters/{chapterId}/exercises
- **Description**: Retrieve exercises for a specific chapter
- **Parameters**:
  - chapterId (path): Unique identifier for the chapter
- **Response**:
  ```json
  {
    "exercises": [
      {
        "id": "ex-01-01-01",
        "chapter_id": "chapter-1-ros2-nervous-system",
        "title": "DDS Architecture Comparison",
        "problem_statement": "Compare the DDS architecture in ROS 2 with traditional client-server models",
        "solution": "Solution details...",
        "difficulty_level": "intermediate",
        "tags": ["dds", "architecture", "comparison"],
        "learning_objective_ids": ["lo-01-01-01"]
      }
    ]
  }
  ```

## Content Validation API

### POST /api/validate/ros2-concept
- **Description**: Validate ROS 2 concepts against official documentation
- **Request**:
  ```json
  {
    "concept_name": "Quality of Service policies",
    "definition": "Mechanisms to ensure communication reliability and performance",
    "examples": ["reliability", "durability", "deadline"],
    "use_case": "Controlling communication behavior in robotics applications"
  }
  ```
- **Response**:
  ```json
  {
    "valid": true,
    "feedback": "Concept aligns with official ROS 2 documentation",
    "suggestions": [],
    "references": ["https://docs.ros.org/en/rolling/Concepts/About-Quality-of-Service-Settings.html"]
  }
  ```

### POST /api/validate/urdf-model
- **Description**: Validate URDF model against ROS 2 standards
- **Request**:
  ```json
  {
    "urdf_content": "<robot name='example_robot'>...</robot>",
    "robot_name": "example_robot",
    "validation_level": "basic|full"
  }
  ```
- **Response**:
  ```json
  {
    "valid": true,
    "errors": [],
    "warnings": [],
    "compatibility": {
      "gazebo": "compatible",
      "isaac": "compatible",
      "real_hardware": "compatible"
    }
  }
  ```

## Module Progress API

### GET /api/modules/01-ros2-nervous-system/progress
- **Description**: Retrieve progress tracking for Module 1
- **Response**:
  ```json
  {
    "module_id": "01-ros2-nervous-system",
    "total_chapters": 3,
    "completed_chapters": 0,
    "current_chapter": null,
    "completion_percentage": 0,
    "time_spent": "0 hours",
    "exercises_completed": 0,
    "exercises_total": 15
  }
  ```

## Search and Navigation API

### GET /api/search/modules/01-ros2-nervous-system
- **Description**: Search within Module 1 content
- **Parameters**:
  - query (query): Search term
  - limit (query, optional): Number of results (default: 10)
- **Response**:
  ```json
  {
    "results": [
      {
        "id": "section-01-01-01",
        "type": "section",
        "title": "DDS Architecture in ROS 2",
        "chapter_id": "chapter-1-ros2-nervous-system",
        "snippet": "Data Distribution Service (DDS) serves as the middleware layer in ROS 2...",
        "url": "/modules/01-ros2-nervous-system/chapter-1/dds-architecture",
        "relevance_score": 0.95
      }
    ],
    "total_results": 1
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
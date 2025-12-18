# ADR 006: rclpy Focus Scope (Module 1)

## Status
Proposed

## Context
When teaching ROS 2 communication primitives in Module 1, we need to decide the scope of Python integration coverage, specifically whether to focus primarily on rclpy or include multiple client libraries.

## Decision
We will focus primarily on rclpy (Python ROS Client Library) for Python integration in Module 1.

## Alternatives Considered
1. Multiple language bindings: Broader coverage but分散s focus across languages
2. rclcpp only: C++ focus but less AI integration capability
3. Third-party libraries: Less official support and updates
4. rclpy focus (selected): Official Python interface with full feature parity

## Rationale
Python is the dominant language in AI development, and rclpy provides the official Python interface to ROS 2 with full feature parity. This provides the best integration between AI tools and robotics systems for the textbook's audience.

## Consequences
- Positive: Strong integration between AI tools and robotics systems
- Positive: Alignment with industry AI development practices
- Negative: Less multi-language coverage
- Neutral: Students will need additional learning for other languages

## Links
- Related to: Module 1 - Communication Primitives chapter
- Tracked in: specs/01-ros2-nervous-system/plan.md
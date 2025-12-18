# ADR 005: ROS 2 vs Alternative Middleware (Module 1)

## Status
Proposed

## Context
For Module 1 of the Physical AI & Humanoid Robotics textbook, we need to decide whether to focus on ROS 2 as the primary middleware framework or consider alternative middleware solutions for robotics applications.

## Decision
We will focus on ROS 2 as the primary middleware framework in Module 1.

## Alternatives Considered
1. ROS 1: Legacy system with limited real-time support and maintenance
2. Custom middleware: Potential for optimization but high development overhead
3. Other robotics frameworks: Different feature sets but less community support
4. ROS 2 (selected): Industry standard with strong real-time capabilities and community

## Rationale
ROS 2 provides the most mature and industry-adopted middleware for robotics applications with strong support for real-time constraints and fault tolerance required for physical AI systems. It offers the best balance of features, community support, and industry relevance for the textbook's objectives.

## Consequences
- Positive: Access to extensive documentation, tools, and community support
- Positive: Industry-relevant skills for students
- Negative: Complexity compared to simpler alternatives
- Neutral: Need to address ROS 2's learning curve in the textbook

## Links
- Related to: Module 1 - The Robotic Nervous System
- Tracked in: specs/01-ros2-nervous-system/plan.md
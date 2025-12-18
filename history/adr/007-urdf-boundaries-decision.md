# ADR 007: URDF Boundaries and Extensions (Module 1)

## Status
Proposed

## Context
For the Robot Body Representation chapter in Module 1, we need to decide the scope of URDF (Unified Robot Description Format) coverage, specifically whether to limit to basic URDF or include extensions like XACRO.

## Decision
We will focus on basic URDF in Module 1, with potential extensions covered in later modules.

## Alternatives Considered
1. XACRO inclusion: More advanced features but adds complexity to learning
2. Custom formats: More flexibility but reduces compatibility
3. Basic URDF only (selected): Simplicity and broad compatibility across tools
4. Extended URDF: More features but potentially overwhelming for beginners

## Rationale
Basic URDF provides sufficient foundation for robot representation while maintaining compatibility with all major simulation environments. This approach ensures universal compatibility while keeping the learning curve manageable for the foundational module.

## Consequences
- Positive: Universal compatibility with simulation tools (Gazebo, Isaac)
- Positive: Simpler learning curve for foundational concepts
- Negative: Less advanced modeling capabilities initially
- Neutral: Students will need additional learning for advanced features

## Links
- Related to: Module 1 - Robot Body Representation chapter
- Tracked in: specs/01-ros2-nervous-system/plan.md
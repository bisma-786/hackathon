# ADR 004: Simulation-First Pedagogy

## Status
Accepted

## Context
When designing the learning progression for the Physical AI & Humanoid Robotics textbook, we needed to decide whether to start with hardware-based learning (hardware-first) or simulation-based learning (simulation-first). This pedagogical decision would significantly impact the accessibility, cost, and learning effectiveness of the textbook.

## Decision
We will use a simulation-first pedagogy approach for the Physical AI & Humanoid Robotics textbook.

## Alternatives Considered
1. Hardware-first approach: Begin with physical hardware and real-world robotics platforms
   - Pros: More tangible and authentic learning experience, immediate real-world application
   - Cons: Higher barrier to entry, expensive equipment requirements, safety considerations, limited accessibility

2. Parallel simulation/hardware development: Develop both simulation and hardware content simultaneously
   - Pros: Comprehensive coverage, clear connections between simulation and reality
   - Cons: Complex to coordinate, higher resource requirements, potentially overwhelming for learners

3. Simulation-first approach (selected): Begin with simulation environments before transitioning to hardware
   - Pros: Accessible to all students regardless of hardware access, safe experimentation, cost-effective, enables complex scenario exploration
   - Cons: Potential disconnect between simulation and reality, less tangible initial experience

## Rationale
The simulation-first approach allows students to experiment without hardware access requirements, reduces barriers to entry, enables safe exploration of complex concepts, and aligns with industry practices where simulation is extensively used. This approach makes the textbook accessible to a broader audience while still providing comprehensive learning outcomes.

## Consequences
- Positive: Accessible learning path that scales to multiple students without hardware constraints
- Positive: Safe environment for experimentation with complex robotics concepts
- Positive: Cost-effective for students and institutions
- Negative: Potential disconnect between simulation and real-world hardware behavior
- Neutral: Requires careful attention to sim-to-real transfer concepts

## Links
- Related to: Physical AI & Humanoid Robotics textbook project
- Tracked in: specs/main/research.md, specs/main/plan.md
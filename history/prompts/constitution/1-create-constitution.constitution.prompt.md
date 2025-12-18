---
id: 1
title: Create Constitution
stage: constitution
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: Bisma Gondal
command: /sp.constitution
labels: ["constitution","governance","principles"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
---

## Prompt

```text
/sp.constitution

Project: Physical AI & Humanoid Robotics — AI-Driven Textbook

Purpose:
Create a modular, production-grade technical textbook on Physical AI and Humanoid Robotics, focused on embodied intelligence and real-world AI systems. The book must bridge digital AI models with physical robotic bodies using ROS 2, Gazebo, Unity, NVIDIA Isaac, and Vision-Language-Action (VLA) systems.

Audience:
Advanced undergraduate and graduate students in AI, Robotics, and Computer Science with prior programming experience.

Core Principles:
- Technical accuracy aligned with industry and research standards
- Clarity for engineering and AI practitioners
- Systems thinking (brain–body–environment integration)
- Reproducibility and traceability of all technical claims
- Progressive learning from simulation to physical deployment

Authoring & here applicable
- Zero plagiarism tolerance

Constraints:
- Markdown source only (no PDFs, no notebooks)
- No copy-paste from instructor or reference repositories
- No implementation code unless explicitly required later
- Focus on explanation, architecture, and system design over tutorials

Success Criteria:
- Readers can explain and design a full Physical AI stack
- Clear understanding of sim-to-real transfer challenges
- Cohesive narrative from ROS 2 fundamentals to autonomous humanoid capstone
- Clean Docusaurus structure with navigable sidebar
- Ready for extension with RAG chatbot in later phases
```

## Response snapshot

Created a comprehensive constitution for the Physical AI & Humanoid Robotics textbook project. The constitution establishes six core principles: Technical Accuracy and Industry Standards, Clarity for Engineering and AI Practitioners, Systems Thinking Approach, Reproducibility and Traceability, Progressive Learning from Simulation to Reality, and Zero Plagiarism Tolerance. Additionally, it defines constraints and requirements, development workflow standards, and governance procedures.

## Outcome

- ✅ Impact: Created foundational governance document establishing project principles
- 🧪 Tests: N/A (documentation task)
- 📁 Files: Updated .specify/memory/constitution.md with complete constitution
- 🔁 Next prompts: Proceed with feature specification using /sp.specify
- 🧠 Reflection: Constitution provides clear guidelines for maintaining technical accuracy and academic integrity throughout the textbook development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - Constitution aligns with project requirements
- Prompt variant (if applicable): Standard constitution creation
- Next experiment (smallest change to try): Begin feature specification based on established principles
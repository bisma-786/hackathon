# ADR 003: Markdown-Only Content Format

## Status
Accepted

## Context
The Physical AI & Humanoid Robotics textbook project constitution mandates that all content must be authored in Markdown format only, with no PDFs, Jupyter notebooks, or other document formats. This constraint was established to ensure consistency, version control compatibility, and ease of collaboration. However, we needed to formally document this decision and its implications.

## Decision
We will strictly adhere to Markdown-only content format for the Physical AI & Humanoid Robotics textbook, as required by the project constitution.

## Alternatives Considered
1. Mixed formats (Markdown + Jupyter notebooks): Would allow interactive code examples and richer content
   - Pros: More interactive content, executable examples, rich output formats
   - Cons: Violates project constitution, complicates version control, harder collaboration

2. Pure HTML: Would provide maximum control over presentation and interactivity
   - Pros: Maximum flexibility in presentation, full control over output
   - Cons: Harder to maintain and collaborate, not web-friendly for content authors

3. LaTeX: Would provide superior academic document formatting and mathematical expressions
   - Pros: Excellent for academic content, superior mathematical notation
   - Cons: Less web-friendly, steeper learning curve, harder to maintain

4. Markdown-only (selected): Strict adherence to project constitution requirements
   - Pros: Consistent, maintainable, collaborative content creation; version control friendly; integrates well with Docusaurus
   - Cons: Limited interactivity vs. richer content formats

## Rationale
The Markdown-only approach aligns with the project constitution requirement for consistency, version control compatibility, and ease of collaboration. It ensures that all content follows the same format and can be easily managed through version control systems. This approach supports the project's goal of maintaining academic integrity while enabling collaborative development.

## Consequences
- Positive: Consistent, maintainable, and collaborative content creation process
- Positive: Excellent version control compatibility
- Positive: Simplified toolchain and workflow
- Negative: Limited interactivity compared to richer content formats
- Neutral: Requires external files for complex diagrams and visual elements

## Links
- Related to: Physical AI & Humanoid Robotics textbook project
- Tracked in: .specify/memory/constitution.md, specs/main/research.md
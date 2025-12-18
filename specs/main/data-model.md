# Data Model: Physical AI & Humanoid Robotics Textbook

## Content Entities

### Module
- **Fields**: id, title, description, learning_objectives, prerequisites, estimated_duration
- **Relationships**: Contains multiple Chapters; Links to other Modules
- **Validation**: Title required, learning_objectives required, estimated_duration positive
- **State transitions**: Draft → Review → Published → Archived

### Chapter
- **Fields**: id, module_id, title, content, learning_objectives, prerequisites, next_chapter_id
- **Relationships**: Belongs to Module; Contains multiple Sections; Links to other Chapters
- **Validation**: Title required, content required, belongs to valid Module
- **State transitions**: Draft → Review → Published → Archived

### Section
- **Fields**: id, chapter_id, title, content, type (text, code, diagram, exercise), order_in_chapter
- **Relationships**: Belongs to Chapter; Contains multiple Content Elements
- **Validation**: Title required, content required, belongs to valid Chapter
- **State transitions**: Draft → Review → Published → Archived

### Content Element
- **Fields**: id, section_id, type (text, code, image, video, equation), content, caption, source
- **Relationships**: Belongs to Section; References external resources
- **Validation**: Type required, content required, valid format for type
- **State transitions**: Draft → Review → Published → Archived

### Learning Objective
- **Fields**: id, parent_id, parent_type (module, chapter, section), description, assessment_method
- **Relationships**: Belongs to Module/Chapter/Section; Connected to Exercises
- **Validation**: Description required, valid parent reference
- **State transitions**: Draft → Approved → Archived

### Exercise
- **Fields**: id, section_id, title, problem_statement, solution, difficulty_level, tags
- **Relationships**: Belongs to Section; Connected to Learning Objectives
- **Validation**: Problem statement required, difficulty level in range
- **State transitions**: Draft → Review → Published → Archived

### Reference
- **Fields**: id, type (book, paper, website, documentation), title, authors, publication_date, url, doi, citation_text
- **Relationships**: Referenced by multiple Content Elements; Cross-references
- **Validation**: Type required, citation_text required, valid URL if provided
- **State transitions**: Draft → Verified → Archived

### Author
- **Fields**: id, name, affiliation, expertise_areas, bio, contact_info
- **Relationships**: Creates multiple Modules/Chapters/Sections; Reviews content
- **Validation**: Name required, expertise_areas required
- **State transitions**: Active → Inactive

### Reviewer
- **Fields**: id, name, expertise_areas, affiliation, review_history
- **Relationships**: Reviews multiple Modules/Chapters/Sections; Comments on content
- **Validation**: Name required, expertise_areas required
- **State transitions**: Active → Inactive

## System Configuration Entities

### Site Configuration
- **Fields**: site_title, tagline, favicon, theme, default_language, version
- **Relationships**: Applies to entire site; Contains navigation structure
- **Validation**: Site title required, valid theme options
- **State transitions**: Active → Inactive (for versioning)

### Navigation Structure
- **Fields**: id, parent_id, title, path, order, is_external, children_order
- **Relationships**: Hierarchical structure; Points to content entities
- **Validation**: Title required, valid path format
- **State transitions**: Draft → Published → Archived

### Search Index
- **Fields**: id, content_id, content_type, title, body_snippet, tags, last_updated
- **Relationships**: Mirrors content structure; Enables search functionality
- **Validation**: Content_id required, content_type valid
- **State transitions**: Active → Needs Update → Updated

## Content Relationships

### Module Relationships
- **Prerequisite Modules**: Directed graph showing dependencies between modules
- **Related Modules**: Undirected graph showing conceptual connections
- **Sequential Path**: Linear ordering for progressive learning

### Cross-Reference Mapping
- **Internal Links**: Connections between content elements within the textbook
- **External References**: Links to authoritative sources and documentation
- **Citation Network**: Academic citation relationships between concepts

## Validation Rules

### Content Integrity
- Each Module must have at least one Chapter
- Each Chapter must have at least one Section
- All Learning Objectives must be assessable through Exercises
- All external references must be verifiable

### Navigation Consistency
- All content must be accessible through navigation structure
- No orphaned content elements
- Consistent terminology across all modules
- Proper cross-referencing between related concepts

### Educational Standards
- Each module must align with target audience requirements
- Content complexity must progress appropriately
- All technical claims must be verifiable
- Learning objectives must be measurable

## State Management

### Content States
- **Draft**: Initial creation state, editable by authors
- **Review**: Under review by domain experts
- **Published**: Live and visible to readers
- **Archived**: No longer active but preserved for history

### Workflow States
- Content moves through states based on review and approval process
- State transitions require specific validations
- Multiple reviewers may be involved in state transitions
- Version history is maintained for all state changes
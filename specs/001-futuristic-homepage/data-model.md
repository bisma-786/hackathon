# Data Model: Futuristic Homepage for AI DRIVEN BOOK

**Feature**: 001-futuristic-homepage
**Date**: 2025-12-19
**Status**: Design

## Overview

This document describes the data structures and entities for the futuristic homepage redesign. Since this is primarily a UI/visual redesign with minimal data requirements, the data model is lightweight and focused on configuration and presentation data.

## Key Entities

### 1. ModuleCard

**Description**: Represents a single module card displayed on the homepage

**Fields**:
- `id`: String - Unique identifier for the module (e.g., "module-1", "module-2")
- `title`: String - Display title of the module (e.g., "Module 1: ROS 2 Fundamentals")
- `description`: String - Brief description of the module content
- `imageUrl`: String - Path to the futuristic/robotics-themed image for this module
- `linkPath`: String - URL path to navigate to when card is clicked
- `order`: Number - Display order in the grid (1-4)

**Validation Rules**:
- `id` must be unique across all module cards
- `title` must not exceed 50 characters
- `description` must not exceed 150 characters
- `imageUrl` must be a valid path in static/img directory
- `order` must be between 1 and 4

### 2. HeroSection

**Description**: Configuration for the homepage hero section

**Fields**:
- `title`: String - Main headline text (e.g., "AI DRIVEN BOOK")
- `subtitle`: String - Supporting text below the title
- `ctaText`: String - Text for the primary call-to-action button (e.g., "Start Learning")
- `ctaLink`: String - URL path for the CTA button
- `backgroundImageUrl`: String - Path to the background image for the hero section

**Validation Rules**:
- `title` must not exceed 50 characters
- `ctaText` must not exceed 20 characters
- `ctaLink` must be a valid internal path
- `backgroundImageUrl` must be a valid path in static/img directory

### 3. PageConfiguration

**Description**: Overall configuration for the homepage layout

**Fields**:
- `pageTitle`: String - HTML title for the page
- `metaDescription`: String - SEO meta description
- `showModuleCards`: Boolean - Whether to display the module cards section
- `showHeroSection`: Boolean - Whether to display the hero section
- `theme`: String - CSS theme identifier (e.g., "futuristic", "metaverse")

**Validation Rules**:
- `pageTitle` must not exceed 70 characters
- `metaDescription` must not exceed 160 characters

## State Transitions

### ModuleCard State
- **Initial**: Card is rendered in static state
- **Hover**: Card receives CSS hover effects when mouse enters
- **Click**: Card triggers navigation to specified link path

### HeroSection State
- **Initial**: Hero section renders with background image and text
- **CTA Hover**: CTA button receives hover effects
- **CTA Click**: Navigation to specified module path

## Relationships

```
PageConfiguration (1) -> HeroSection (1)
PageConfiguration (1) -> ModuleCard (4)
```

The PageConfiguration contains one HeroSection and four ModuleCard entities, forming the complete homepage structure.

## UI Components Mapping

The data model maps to the following UI components:
- `HeroSection` → Hero section component with background and CTA
- `ModuleCard[]` → Grid of 4 module cards
- `PageConfiguration` → Overall page wrapper and layout settings
# Lesson 010: Organizing Project Insights into Logical Categories

## Context

As a project evolves, the volume and diversity of "insights" (learnings, patterns, best practices) grow. Effectively organizing these insights is crucial for discoverability, maintaining clarity, and ensuring they remain valuable resources for both human developers and AI agents. This lesson outlines a strategy for categorizing insights using a folder structure complemented by `README.md` files as sources of truth.

## Insight

Organize project insights into logical categories using dedicated folders, with each folder containing a `README.md` file that serves as its index and source of truth. The number and type of categories should evolve organically with the project, avoiding premature over-fragmentation.

## Key Principles

1.  **Logical Categorization**: Group insights into folders based on their primary subject matter. Common initial categories include:
    *   **`/architecture`**: Insights related to fundamental system design, core patterns, and high-level principles.
    *   **`/development`**: Insights covering technical implementation patterns, coding best practices, and specific engineering solutions.
    *   **`/workflow`**: Insights focused on development processes, documentation management, team collaboration, and effective utilization of tools (including AI agents).
2.  **`README.md` as Source of Truth**: Each category folder (`/architecture`, `/development`, `/workflow`) should contain a `README.md` file. This `README.md` serves as:
    *   An index for all insights within that folder, listing them with their numbers and titles.
    *   The authoritative source for determining the next available sequential number when creating new insights within that category.
    *   A brief description of the category's purpose.
3.  **Organic Evolution of Categories**:
    *   **Start Simple**: Initially, there is no need for an exhaustive set of categories. Begin with a minimal, broad set (e.g., `/architecture` and `/development`).
    *   **Categories Reveal Themselves**: New categories should emerge organically as the project progresses and new types of insights accumulate. For instance, in the Cornjacket platform, while `/architecture` and `/development` were initially sufficient, it soon became evident that many process-related learnings were being added, necessitating the creation of a dedicated `/workflow` category.
    *   **Avoid Over-fragmentation**: Resist the urge to create excessive categories (e.g., `/testing`, `/tooling`, `/operations`) until the volume and specificity of insights truly warrant them. Over-fragmentation makes insights harder to find and categories harder to maintain.
4.  **Sequential Numbering within Categories**: Insights within each category folder should be sequentially numbered (e.g., `001-insight-name.md`, `002-another-insight.md`). This numbering is independent across categories.

## Benefits

*   **Improved Discoverability**: Insights are easier to find when grouped by relevant topics.
*   **Clearer Structure**: Provides a navigable and understandable knowledge base.
*   **Reduced Clutter**: Keeps a large volume of insights organized and prevents a single flat list from becoming overwhelming.
*   **Consistent Practice**: Establishes a clear process for adding new insights for both human and AI contributors.
*   **Adapts to Project Needs**: The structure can grow and adapt without requiring a complete overhaul.

## Practical Application Example (Excerpt from `platform-docs/insights/`)

```
platform-docs/insights/
  ├── architecture/
  │   ├── 001-time-separation-of-concerns.md
  │   └── README.md
  ├── development/
  │   ├── 001-per-service-migration-table-isolation.md
  │   └── README.md
  └── workflow/
      ├── 001-single-source-of-truth-for-tasks.md
      ├── 002-task-documents-as-design-specs.md
      └── README.md
```

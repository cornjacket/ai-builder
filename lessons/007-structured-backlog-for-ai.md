# Lesson 007: Structured Backlog Management for AI Agents

## Context

When working with AI agents, it's crucial to provide clear, unambiguous information about the state of a project, especially regarding tasks and future work. Conflating actively committed tasks with potential, unprioritized tasks can lead to confusion, inefficiency, and misdirection for AI agents. This lesson outlines a strategy for organizing such information using a structured backlog system that is easily interpretable by both humans and AI.

## Problem

Initially, all tasks (whether committed or merely identified as potential work) were intended to reside in a single `tasks/` directory, numbered sequentially. This approach, while simple, made it difficult to distinguish between "in-progress/committed" work and "future/potential" work. For an AI agent, this could lead to:
- Attempting to implement tasks that are not yet prioritized.
- Difficulty in understanding the current project focus.
- Unnecessary "noise" in the primary task list.

## Solution: Separated Backlog

To address this, a "backlog" strategy was implemented, leveraging the file system and dedicated documentation to create a clear separation.

### Organization

1.  **Committed Tasks (`platform-services/tasks/`)**:
    *   This directory now exclusively holds tasks that are actively committed to and are part of the current development plan.
    *   Tasks are sequentially numbered (e.g., `001-feature.md`, `002-bugfix.md`).
    *   These tasks are typically associated with an "In Progress" or "Complete" status as they move through the development lifecycle.

2.  **Potential/Future Tasks (`platform-services/tasks/backlog/`)**:
    *   A new subdirectory `backlog/` was created within `platform-services/tasks/`.
    *   This directory stores tasks that have been identified but are *not* yet prioritized, scheduled, or committed for immediate implementation.
    *   Tasks within the backlog are prefixed with numbers (e.g., `000_dlq-implementation.md`), but their numbering is independent of the main `tasks/` sequence. This allows for flexible ordering and does not consume "real" task numbers until the item is promoted.
    *   When a backlog item is committed for development, it is moved from `backlog/` to the parent `tasks/` directory and assigned the *next available sequential number* from the main `tasks/` sequence.

3.  **Backlog Index (`platform-services/tasks/BACKLOG.md`)**:
    *   A dedicated `BACKLOG.md` file was created in `platform-services/tasks/`.
    *   This file serves as an index and summary of all items currently residing in the `platform-services/tasks/backlog/` directory.
    *   It provides a human-readable and AI-parseable overview of potential future work.

4.  **Project-wide Documentation (`platform-docs/README.md`)**:
    *   The top-level `platform-docs/README.md` was updated to include a section describing the new backlog management strategy.
    *   This ensures that any AI agent starting in the root of the project can quickly understand how tasks are organized, distinguishing between active and potential work.

5.  **Feature Status (`platform-docs/design-spec.md`)**:
    *   For features that are partially implemented or have identified gaps, the `platform-docs/design-spec.md` can directly reference the relevant backlog item.
    *   This provides a direct link from design specifications to the current status of implementation or identified future work, offering a comprehensive view for the AI. For example: `For current status and future work, refer to the backlog task: [`platform-services/tasks/BACKLOG.md`](../platform-services/tasks/BACKLOG.md#000_dlq-implementationmd---dlq-implementation-status-event-handler-service)`.

6.  **`PROJECT.md` Update Reminder**: Every task or backlog item that impacts the overall project status tracked in `PROJECT.md` should explicitly include a reminder within its own acceptance criteria or verification section to update `PROJECT.md` upon completion. This serves as a critical self-correction mechanism to ensure high-level progress tracking remains accurate.

## Benefits for AI Agents

This structured approach significantly benefits AI agents by:
-   **Clear Scope Definition**: AI can easily differentiate between tasks that are actively in scope versus those that are merely candidates for future work.
-   **Reduced Ambiguity**: The explicit separation and indexing reduce ambiguity when an AI is trying to understand what needs to be done.
-   **Improved Task Prioritization**: By consulting `BACKLOG.md` and the main `tasks/` directory, an AI can better understand the project's priorities.
-   **Efficient Information Retrieval**: AI can quickly locate relevant task information without sifting through unrelated documents or unprioritized items.
-   **Enhanced Decision Making**: When analyzing feature gaps or proposing solutions, the AI has direct access to acknowledged future work items.

By leveraging the inherent structure of the file system and providing clear, consistent documentation, AI agents can operate more effectively within the project, aligning their efforts with the project's actual development roadmap.

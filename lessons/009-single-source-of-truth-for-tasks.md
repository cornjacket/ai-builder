# Lesson 009: Single Source of Truth for Task Numbering

## Context

In collaborative development environments, especially those involving multiple agents (human or AI), managing sequential task numbering and indexing can become a source of inconsistency and conflict. Relying on ad-hoc methods or incomplete listings leads to errors, duplicate numbers, and costly re-synchronization overhead, undermining project traceability and efficiency.

## Insight

It is critically important to establish and strictly adhere to a **single, explicitly defined source of truth for sequential numbering and indexing in task management systems.** This ensures consistency, prevents numbering discrepancies, and provides a clear, shared understanding of the task landscape for all contributors, human and AI alike.

For the Cornjacket platform, `platform-services/tasks/README.md` serves as this authoritative index for all `platform-services` tasks.

## Key Principles for Maintaining a Single Source of Truth

1.  **Centralized Index**: Designate a specific document (e.g., `tasks/README.md`) as the authoritative index for all tasks. This document becomes the single point of reference.
2.  **Numbering Authority**: This index is the *only* place to determine the next available sequential number for new tasks or specs. Direct inspection of file system contents is unreliable due to potential deletions or reordering.
3.  **Strict Process for New Tasks**:
    *   **Consult First**: Before creating any new task file, developers (or AI agents) *must* consult the central index to find the highest sequential number.
    *   **Reserve Number**: Assign the next available number (`Highest + 1`).
    *   **Update Index Immediately**: Add the new task to the central index *before* creating the actual task file content. This reserves the number and keeps the index perpetually up-to-date and consistent.
    *   **File Name Match**: Task file names (`NNN-description.md`) *must* exactly match the number and description in the central index.
4.  **Backlog Integration**: Integrate backlog management (e.g., `tasks/backlog/` indexed by `tasks/BACKLOG.md`) into this system, with clear rules for promoting backlog items to active tasks (which would then follow the above numbering process).
5.  **Automation Potential**: Where feasible, automate the process of assigning numbers and updating the index (e.g., via scripts or AI tools) to minimize human error and ensure strict adherence.

## Benefits

*   **Prevents Numbering Conflicts**: Eliminates duplicate task numbers across the project.
*   **Ensures Consistency**: All participants (human and AI) operate from the same understanding of task sequencing and status.
*   **Reduces Re-synchronization Efforts**: Avoids time-consuming corrections due to out-of-sync documentation or file system states.
*   **Improves Traceability**: Every task has a clear, unique identifier, enhancing project history.
*   **Enhances AI Collaboration**: AI agents can reliably interpret task status, generate new tasks, and manage project plans without creating conflicts.

## Origin of this Insight

This lesson was directly derived from a real-world experience during the development of the Cornjacket platform, where a lack of strict adherence to a central task index led to conflicting task numbers and required significant re-synchronization efforts. It underscores the importance of well-defined processes even for seemingly simple administrative tasks.

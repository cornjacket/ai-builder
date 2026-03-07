# Lesson 016: Commit the Task Doc Before Implementation

## Context

AI agents can fail mid-implementation — context window limits, crashes, wrong approaches, or user intervention. When the task doc and implementation are committed together, a failed implementation means the task doc is also lost.

## Problem

If an AI agent writes a task doc, implements code, and something goes wrong, the user must re-explain the entire task from scratch. The planning work is thrown away with the failed code.

## Solution

Commit the task document as a separate commit before starting implementation. This creates a checkpoint: if implementation fails, the task doc survives. The next AI session can read the committed task doc and pick up where the previous session left off.

Workflow:
1. Create task document
2. **Commit task document** (checkpoint)
3. Implement
4. Test
5. Commit implementation

## Decision Guidance

Always commit planning artifacts before execution artifacts. The cost is one extra commit. The benefit is a recoverable starting point for any failed implementation.

# Lesson 001 — Separate Meta-Learning from Project Repos

**Category:** repo-structure
**Source project:** cornjacket-platform
**Date:** 2026-02-09

## Context

While building a multi-repo platform with AI agent assistance, lessons about the *process of building with AI* began emerging alongside the platform code itself. These insights (workflow patterns, prompt strategies, architectural decisions shaped by AI collaboration) were project-agnostic but had no natural home — the project repos captured *what* was built, not *how the building process works*.

The question arose: where should these meta-lessons live?

## Lesson

Keep a dedicated, project-agnostic repo for AI-assisted development lessons, separate from the project's own documentation and code repos. This creates a clean separation of concerns:

- **Project repos** capture *what* was built and *why* (ADRs, task docs, code).
- **Meta-learning repo** captures *how the building process itself works* — the patterns, anti-patterns, and decision frameworks discovered through AI collaboration.

This separation ensures lessons are reusable across future projects without being buried in project-specific context. It also establishes a meta-feedback loop: the act of building improves not just the product, but the process template for all future products.

## Decision Guidance

When starting a new AI-assisted project, create a separate meta-learning repo from day one. As lessons accumulate, they naturally cluster into decision points (e.g., "When starting a new project, should you scaffold first or write ADRs first?" -> "If using AI agents, scaffold first because..."). This tree structure can eventually become a runbook or even a starter-template generator for new projects.

## Related Lessons

- [002 — Project Insights Folder Complements ADRs](002-project-insights-folder-complements-adrs.md): While this lesson covers the cross-project meta-learning repo, lesson 002 covers repo-level insights folders. Together they form a two-tier knowledge capture system.

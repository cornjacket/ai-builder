
ORCHESTRATOR FLOW
=================

Two modes:

  Non-TM mode (--job):    starts at ARCHITECT, pipeline runs once for a
                          single pre-defined job document.

  TM mode (--target-repo): the Oracle starts each pipeline run at ARCHITECT
                            with a pre-built job document. TASK_MANAGER runs
                            only at the end to update the task system. The
                            Oracle drives the outer loop — it reads TM output
                            and decides whether to start another pipeline run.


TM MODE FLOW
============

  Each pipeline run handles one job (planning or implementation of a single
  subtask). The Oracle is external — it prepares the job document and invokes
  the orchestrator. The orchestrator always starts at ARCHITECT in TM mode.

  [Oracle] -- prepares job doc --> orchestrator
                                        |
                                        v
                                  +-----------+
                      .---------->| ARCHITECT |<-----------.
                      |           |  (claude) |            |
                      |           +-----------+            |
                      |                 |                  |
                      |           OUTCOME: DONE            |
                      |                 |                  |
                      |           [DOCUMENTER hook]        |
                      |                 |                  |
                      |                 v                  |
                      |           +-------------+          |
                      |           | IMPLEMENTOR |          |
                      |           |  (gemini)   |          |
                      |           +-------------+          |
                      |            |           |           |
                      |   NEEDS_ARCHITECT      DONE        |
                      |            |           |           |
                      |            '-----------'     [DOCUMENTER hook]
                      |                               |
                      |                               v
                      |                         +-----------+
                      |                         |  TESTER   |
                      |                         |  (claude) |
                      |                         +-----------+
                      |                          |         |
                      |                        DONE      FAILED
                      |                          |         |
                      |                  [DOCUMENTER hook] |
                      |                          |         '-----> IMPLEMENTOR
                      |                          v
                      |                  +--------------+
                      |                  | TASK_MANAGER |
                      |                  |   (claude)   |
                      |                  +--------------+
                      |                    |         |
                      |                DONE      NEED_HELP
                      |                    |         |
                      |                    v         v
                      |                 halt      halt
                      |
                      '-- NEEDS_ARCHITECT (from IMPLEMENTOR)

  After the pipeline halts, the Oracle reads the outcome and task system
  state to decide what to do next: start another pipeline run, pause for
  human review, or declare the project complete.


NON-TM MODE FLOW
================

  Task Document (read-only after ARCHITECT)
  templates/JOB.md  -->  cp  -->  JOB.md
                                      |
                                      | (ARCHITECT edits Design
                                      |  + Acceptance Criteria)
                                      |
                                      v
                               +-----------+
                 .------------>| ARCHITECT |<-----------.
                 |             |  (claude) |            |
                 |             +-----------+            |
                 |                   |                  |
                 |            OUTCOME: DONE             |
                 |                   |                  |
                 |                   v                  |
                 |             +-----------+            |
                 |             | IMPLEMENTOR|           |
                 |             |  (gemini)  |           |
                 |             +-----------+            |
                 |              |         |             |
           NEEDS_ARCHITECT      |        DONE           |
                 |              |         |             |
                 '------------- '         v             |
                                    +-----------+       |
                                    |  TESTER   |       |
                                    |  (claude) |       |
                                    +-----------+       |
                                     |         |        |
                                   DONE      FAILED     |
                                     |         |        |
                                     v         '--------'
                                 COMPLETE


DATA FLOWS
==========

  orchestrator.py
       |
       |-- reads --> JOB.md                (both modes: job document prepared by Oracle)
       |-- reads --> request file           (TM mode: passed to TASK_MANAGER as context)
       |-- writes -> execution.log          (append-only run history)
       |
       |-- calls --> agent_wrapper.py
                          |
                          |-- spawns --> claude / gemini   (CLI subprocess)
                          |                   |
                          |                   | stdout (stream-json)
                          |                   |
                          |-- streams to --> terminal      (real-time display)
                          |-- writes to --> logs/ROLE.log  (per-role raw events)
                          |-- writes to --> execution.log  (shared run history)
                          |
                          '-- returns --> AgentResult(exit_code, response)
                                                |
                          orchestrator parses --'
                               OUTCOME + HANDOFF + DOCS
                                    |
                                    |-- HANDOFF appended to handoff_history[]
                                    |      injected into next agent's prompt
                                    |
                                    '-- OUTCOME looked up in ROUTES table
                                             |
                                        next_role
                                             |
                                        loop back


AGENT PROMPT STRUCTURE (per turn)
==================================

  "Your role is {ROLE}.

   Task document: {path}          <-- same doc every agent reads (not TM)

   Role instructions:             <-- role-specific guidance

   Handoff Notes:                 <-- accumulated from all prior agents
     [TASK_MANAGER] ...
     [ARCHITECT] ...
     [IMPLEMENTOR] ...

   End your response with:
     OUTCOME: <valid outcomes for this role>
     HANDOFF: one paragraph summary for the next agent
     DOCS: instructions for the DOCUMENTER (omit or write 'none' if no docs needed)"


ROUTING TABLE
=============

  TM mode:
    (ARCHITECT,       DONE)            --> [DOCUMENTER hook] --> IMPLEMENTOR
    (ARCHITECT,       NEED_HELP)       --> halt
    (IMPLEMENTOR,     DONE)            --> [DOCUMENTER hook] --> TESTER
    (IMPLEMENTOR,     NEEDS_ARCHITECT) --> ARCHITECT
    (IMPLEMENTOR,     NEED_HELP)       --> halt
    (TESTER,          DONE)            --> [DOCUMENTER hook] --> TASK_MANAGER
    (TESTER,          FAILED)          --> IMPLEMENTOR
    (TESTER,          NEED_HELP)       --> halt
    (TASK_MANAGER,    DONE)            --> halt (Oracle decides next run)
    (TASK_MANAGER,    NEED_HELP)       --> halt

  Non-TM mode:
    (ARCHITECT,   DONE)             --> IMPLEMENTOR
    (ARCHITECT,   NEED_HELP)        --> halt
    (IMPLEMENTOR, DONE)             --> TESTER
    (IMPLEMENTOR, NEEDS_ARCHITECT)  --> ARCHITECT
    (IMPLEMENTOR, NEED_HELP)        --> halt
    (TESTER,      DONE)             --> halt (pipeline complete)
    (TESTER,      FAILED)           --> IMPLEMENTOR
    (TESTER,      NEED_HELP)        --> halt

  DOCUMENTER hook runs after ARCHITECT, IMPLEMENTOR, and TESTER in TM mode
  only if the role signals documentation work in its DOCS: output field.
  DOCUMENTER is not a routing node — it is a mandatory post-step managed by
  the orchestrator before routing to the next role.

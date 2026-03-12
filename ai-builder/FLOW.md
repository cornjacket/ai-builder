
ORCHESTRATOR FLOW
=================

Two modes:

  Non-TM mode (--job):    starts at ARCHITECT, pipeline runs once for a
                          single pre-defined job document.

  TM mode (--target-repo): starts at TASK_MANAGER, which decomposes a
                            project request into tasks and drives the full
                            ARCHITECT→IMPLEMENTOR→TESTER pipeline for each
                            task in sequence.


TM MODE FLOW
============

  Project request file (--request)
           |
           v
  +------------------+
  | TASK_MANAGER  |  (claude)
  |                  |<---------------------------------------------.
  | - sets up task   |                                              |
  |   system if new  |                                              |
  | - decomposes     |                                              |
  |   request into   |                                              |
  |   tasks          |                                              |
  | - writes current |                                              |
  |   task path to   |                                              |
  |   current-job   |                                              |
  +------------------+                                              |
      |          |                                                  |
  ALL_DONE   JOBS_READY                                            |
      |          |                                                  |
      v          v                                                  |
   COMPLETE  +-----------+                                          |
  .--------->| ARCHITECT |<-----------.                            |
  |          |  (claude) |            |                            |
  |          +-----------+            |                            |
  |                |                  |                            |
  |           OUTCOME: DONE           |                            |
  |                |                  |                            |
  |                v                  |                            |
  |          +-------------+          |                            |
  |          | IMPLEMENTOR |          |                            |
  |          |  (gemini)   |          |                            |
  |          +-------------+          |                            |
  |           |           |           |                            |
  |    NEEDS_ARCHITECT    DONE        |                            |
  |           |           |           |                            |
  |           '-----------.           v                            |
  |                           +-----------+                        |
  |                           |  TESTER   |                        |
  |                           |  (claude) |                        |
  |                           +-----------+                        |
  |                            |         |                         |
  |                          DONE      FAILED                      |
  |                            |         |                         |
  |                            |         '-----> IMPLEMENTOR       |
  |                            |                                   |
  |                            '-----------------------------------'
  |                            (TM marks task complete, picks next)
  |
  '-- ALL_DONE --> COMPLETE


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
       |-- reads --> request file           (TM mode: project description)
       |-- reads --> current-job.txt       (TM mode: current task path, written by TM)
       |-- reads --> JOB.md                (non-TM mode: pre-defined job document)
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
                               OUTCOME + HANDOFF
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
     HANDOFF: ..."


ROUTING TABLE
=============

  TM mode:
    (TASK_MANAGER, JOBS_READY)  --> ARCHITECT
    (TASK_MANAGER, ALL_DONE)     --> halt (pipeline complete)
    (TASK_MANAGER, NEED_HELP)    --> halt
    (ARCHITECT,       DONE)         --> IMPLEMENTOR
    (ARCHITECT,       NEED_HELP)    --> halt
    (IMPLEMENTOR,     DONE)         --> TESTER
    (IMPLEMENTOR,     NEEDS_ARCHITECT) --> ARCHITECT
    (IMPLEMENTOR,     NEED_HELP)    --> halt
    (TESTER,          DONE)         --> TASK_MANAGER
    (TESTER,          FAILED)       --> IMPLEMENTOR
    (TESTER,          NEED_HELP)    --> halt

  Non-TM mode:
    (ARCHITECT,   DONE)             --> IMPLEMENTOR
    (ARCHITECT,   NEED_HELP)        --> halt
    (IMPLEMENTOR, DONE)             --> TESTER
    (IMPLEMENTOR, NEEDS_ARCHITECT)  --> ARCHITECT
    (IMPLEMENTOR, NEED_HELP)        --> halt
    (TESTER,      DONE)             --> halt (pipeline complete)
    (TESTER,      FAILED)           --> IMPLEMENTOR
    (TESTER,      NEED_HELP)        --> halt

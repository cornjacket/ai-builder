
ORCHESTRATOR FLOW
=================

Two modes:

  Non-PM mode (--job):    starts at ARCHITECT, pipeline runs once for a
                          single pre-defined job document.

  PM mode (--target-repo): starts at PROJECT_MANAGER, which decomposes a
                           project request into tasks and drives the full
                           ARCHITECT→IMPLEMENTOR→TESTER pipeline for each
                           task in sequence.


PM MODE FLOW
============

  Project request file (--request)
           |
           v
  +------------------+
  | PROJECT_MANAGER  |  (claude)
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
  |                            (PM marks task complete, picks next)
  |
  '-- ALL_DONE --> COMPLETE


NON-PM MODE FLOW
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
       |-- reads --> request file           (PM mode: project description)
       |-- reads --> current-job.txt       (PM mode: current task path, written by PM)
       |-- reads --> JOB.md                (non-PM mode: pre-defined job document)
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

   Task document: {path}          <-- same doc every agent reads (not PM)

   Role instructions:             <-- role-specific guidance

   Handoff Notes:                 <-- accumulated from all prior agents
     [PROJECT_MANAGER] ...
     [ARCHITECT] ...
     [IMPLEMENTOR] ...

   End your response with:
     OUTCOME: <valid outcomes for this role>
     HANDOFF: ..."


ROUTING TABLE
=============

  PM mode:
    (PROJECT_MANAGER, JOBS_READY)  --> ARCHITECT
    (PROJECT_MANAGER, ALL_DONE)     --> halt (pipeline complete)
    (PROJECT_MANAGER, NEED_HELP)    --> halt
    (ARCHITECT,       DONE)         --> IMPLEMENTOR
    (ARCHITECT,       NEED_HELP)    --> halt
    (IMPLEMENTOR,     DONE)         --> TESTER
    (IMPLEMENTOR,     NEEDS_ARCHITECT) --> ARCHITECT
    (IMPLEMENTOR,     NEED_HELP)    --> halt
    (TESTER,          DONE)         --> PROJECT_MANAGER
    (TESTER,          FAILED)       --> IMPLEMENTOR
    (TESTER,          NEED_HELP)    --> halt

  Non-PM mode:
    (ARCHITECT,   DONE)             --> IMPLEMENTOR
    (ARCHITECT,   NEED_HELP)        --> halt
    (IMPLEMENTOR, DONE)             --> TESTER
    (IMPLEMENTOR, NEEDS_ARCHITECT)  --> ARCHITECT
    (IMPLEMENTOR, NEED_HELP)        --> halt
    (TESTER,      DONE)             --> halt (pipeline complete)
    (TESTER,      FAILED)           --> IMPLEMENTOR
    (TESTER,      NEED_HELP)        --> halt

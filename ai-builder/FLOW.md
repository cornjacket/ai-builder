
ORCHESTRATOR FLOW
=================

  Task Document (read-only after ARCHITECT)
  templates/TASK-fibonacci-demo.md  -->  cp  -->  TASK-fibonacci-demo.md
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
                                                        |         '--------'
                                                        v
                                                    COMPLETE


DATA FLOWS
==========

  orchestrator.py
       |
       |-- reads --> TASK-fibonacci-demo.md          (task context for all agents)
       |-- writes -> execution.log                   (append-only run history)
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

   Task document: {path}          <-- same doc every agent reads

   Role instructions:             <-- role-specific guidance

   Handoff Notes:                 <-- accumulated from all prior agents
     [ARCHITECT] ...
     [IMPLEMENTOR] ...

   End your response with:
     OUTCOME: DONE | NEEDS_ARCHITECT | FAILED | NEED_HELP | RATE_LIMIT_PAUSE
     HANDOFF: ..."


ROUTING TABLE
=============

  (ARCHITECT,   DONE)            --> IMPLEMENTOR
  (ARCHITECT,   NEED_HELP)       --> halt
  (IMPLEMENTOR, DONE)            --> TESTER
  (IMPLEMENTOR, NEEDS_ARCHITECT) --> ARCHITECT
  (IMPLEMENTOR, NEED_HELP)       --> halt
  (TESTER,      DONE)            --> halt (pipeline complete)
  (TESTER,      FAILED)          --> IMPLEMENTOR
  (TESTER,      NEED_HELP)       --> halt

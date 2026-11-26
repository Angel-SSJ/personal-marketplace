# Accepted method outputs to Notion

| Method output                         | Explicit mapping                                                       | Decision boundary                                                    |
| ------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------- |
| GTD finite committed outcome          | Projects Name/Outcome; accepted Status and dates                       | Folder or note alone does not accept commitment                      |
| GTD chosen visible action             | Tasks Name/Description with actual Project/Stage/Area                  | Preserve selected semantics; ask if the action is unknown            |
| GTD external expected result          | Tasks Waiting For, Waiting On, Expected Result, Follow-up Date         | Do not invent a person/date                                          |
| GTD incubation                        | Tasks Someday/Maybe, related useful Notes                              | Does not erase an existing promise                                   |
| GTD real due date                     | Tasks Due Date                                                         | Date-only or timezone details must match the agreement               |
| GTD future activation                 | Scheduled and Start Date                                               | No arbitrary due date                                                |
| PARA context                          | Project or Area relations and Drive links; Resource note Type          | Support remains in its actual storage home                           |
| CODE captured useful knowledge/output | Notes & References, Source/Drive/Summary and context relations         | No compulsory summary/tag/processing of all sources                  |
| CODE selected work packet             | Selected Tasks or Subtasks and concrete finish description             | JIT discovery belongs to CODE, not an automatic exhaustive breakdown |
| Inbox clarified input                 | Links to resulting Tasks/Notes and Processed after success             | Preserve partial state and pending holds                             |
| task-writing supplied attributes      | Exact live property after its vocabulary validation                    | No inferred tags or priority aliases                                 |
| MoSCoW accepted scope decision        | Preserve in relevant existing description/page support when authorized | No dedicated field exists; ask before a structured category mapping  |

The bundled local [priorities.json](../assets/priorities.json) and [tags.json](../assets/tags.json) registries own accepted task priority/tag identifiers; read them directly without requiring any companion skill. This workspace currently exposes p1, p2, p3, p4, with p1 urgent and p4 lightest as the user's stated workspace semantics. Never infer an identifier or auto-map MoSCoW categories. Schema options do not independently authorize adding registry tags. Tags are optional and the initial approved task set is empty. Ask for exact lowercase approval before extending `tags.json`. If vocabulary validation is unavailable, do independent work and hold disputed attribute changes. Project/stage/note tags have separate vocabularies; do not silently propagate them into task tags.

When an equivalence is absent, show the desired output and missing field/state meaning and ask. A field with the same name but different semantics is not a safe substitute. Read the available companion for deeper method decisions inferred from the request, without repeated method-selection prompts. MoSCoW retains its explicit choice gate. Missing companion access does not authorize reconstructing a conflicting policy or claiming it executed.

## Goal coordination

Map an accepted desired result to Goals Name and Success Criteria. The user chooses the horizon and activation; a short horizon does not force a Project. Map direct independent actions through Goals Direct Tasks / Tasks Goals, project contributions through Goals Projects / Projects Goals, responsibility context through Goals Area / Areas Goals, and supporting evidence through Goals Evidence / Notes & References Goals. See the local [Goals contract](goals.md) for transitions and review. Project Outcomes and task completion inform evidence rather than automatically satisfying a goal. Do not infer new dates, priority values or commitments from the goal target.

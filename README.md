## منهاج - minhaj
```mermaid
graph TD;
    A[Teacher Input<br/>(Raw Instructional Text)]
    B[Requirement Interpreter Agent<br/>- Extracts intent<br/>- Normalizes constraints<br/>- Outputs JSON spec]
    C[Web Search & Resource Retrieval Agent<br/>- Generates queries<br/>- Searches Web / OER<br/>- Extracts objectives<br/>- Filters relevance]
    D[Curriculum Planner Agent<br/>(Syllabus Builder)<br/>- Aligns objectives<br/>- Creates weekly plan<br/>- Maps outcomes to topics]

    E[Slide Agent<br/>(QMD)<br/>- Slides]
    F[Lab Agent<br/>(ipynb / py / java)<br/>- Labs]
    G[Exercise Agent<br/>- Problems]

    H[Exporter Agent<br/>- Organizes files<br/>- Generates README<br/>- Exports ZIP]

    A --> B
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
    E --> H
    F --> H
    G --> H

```
┌────────────────────────────┐

│        Teacher Input       │

│  (raw instructional text)  │

└─────────────┬──────────────┘

              │
              
              ▼
              
┌────────────────────────────┐
│ Requirement Interpreter    │
│ Agent                      │
│ - Extracts intent          │
│ - Normalizes constraints   │
│ - Outputs JSON spec        │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Web Search & Resource      │
│ Retrieval Agent            │
│ - Generates queries        │
│ - Searches web / OER       │
│ - Extracts objectives      │
│ - Filters relevance        │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Curriculum Planner Agent   │
│ (Syllabus Builder)         │
│ - Aligns objectives        │
│ - Creates weekly plan     │
│ - Maps outcomes → topics  │
└─────────────┬──────────────┘
              │
      ┌───────┴────────┬─────────────┐
      ▼                ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Slide Agent  │ │ Lab Agent    │ │ Exercise     │
│ (QMD)        │ │ (ipynb /     │ │ Agent        │
│              │ │  py / java) │ │              │
│ - Slides     │ │ - Labs       │ │ - Problems   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └──────────┬─────┴─────┬──────────┘
                  ▼           ▼
          ┌────────────────────────────┐
          │ Exporter Agent              │
          │ - Organizes files           │
          │ - Generates README          │
          │ - Exports ZIP               │
          └────────────────────────────┘

## منهاج - minhaj
```mermaid
graph TD;
    TeacherInput["Teacher Input\n(raw instructional text)"] --> RequirementInterpreter;
    RequirementInterpreter["Requirement Interpreter Agent\n- Extracts intent\n- Normalizes constraints\n- Outputs JSON spec"] --> WebSearchAgent;
    WebSearchAgent["Web Search & Resource Retrieval Agent\n- Generates queries\n- Searches web/OER\n- Extracts objectives\n- Filters relevance"] --> CurriculumPlanner;
    CurriculumPlanner["Curriculum Planner Agent\n(Syllabus Builder)\n- Aligns objectives\n- Creates weekly plan\n- Maps outcomes → topics"] --> SlideAgent;
    CurriculumPlanner --> LabAgent;
    CurriculumPlanner --> ExerciseAgent;
    SlideAgent["Slide Agent (QMD)\n- Slides"] --> ExporterAgent;
    LabAgent["Lab Agent (ipynb / py/java)\n- Labs"] --> ExporterAgent;
    ExerciseAgent["Exercise Agent\n- Problems"] --> ExporterAgent;
    ExporterAgent["Exporter Agent\n- Organizes files\n- Generates README\n- Exports ZIP"];
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

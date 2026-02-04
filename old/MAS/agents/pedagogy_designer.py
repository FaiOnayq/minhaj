# agents/pedagogy_designer.py
"""Agent 2: Designs learning progression using educational science"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from states import CourseState
from config import GROQ_API_KEY, PEDAGOGY_MODEL
import json


analyst_llm = ChatGroq(model=PEDAGOGY_MODEL, temperature=0.4, api_key=GROQ_API_KEY)


def pedagogy_designer_agent(state: CourseState) -> CourseState:
    """Creates scaffolded learning progression with Bloom's taxonomy"""
    print("🧠 Pedagogy Agent: Designing learning progression...")
    
    course = state["course_input"]
    resources = state["filtered_resources"]
    
    # Format top resources for context
    resource_context = "\n\n".join([
        f"[{r['source_type']}] {r['title']} (Relevance: {r['relevance_score']:.2f})\n{r['content'][:300]}"
        for r in resources[:8]
    ])
    
    prompt = f"""You are a senior curriculum designer specializing in {course['subject_domain']}. 
Design a pedagogically sound {course['duration_weeks']}-week learning progression.

PEDAGOGICAL RULES:
1. Scaffold complexity: Start concrete → abstract, simple → complex
2. Each week must include Bloom's taxonomy verbs in outcomes (remember → create)
3. Balance cognitive load: Max 3 new major concepts per week
4. Sequence dependencies properly (e.g., teach Python basics before ML libraries)
5. Include spaced repetition of key concepts

COURSE SPEC:
- Title: {course['course_title']}
- Level: {course['education_level']}
- Duration: {course['duration_weeks']} weeks
- Goals: {', '.join(course['teaching_goals'])}

TOP RESOURCES (for context):
{resource_context}

OUTPUT JSON with this structure:
{{
  "weekly_progression": [
    {{
      "week": 1,
      "theme": "Foundational concepts",
      "cognitive_focus": "remember/understand",  // Bloom's level
      "key_concepts": ["concept1", "concept2"],
      "scaffolding_notes": "Why this sequence works pedagogically"
    }}
  ],
  "prerequisite_graph": {{
    "concept_a": ["concept_b", "concept_c"],  // concept_a requires b and c first
    "concept_b": []
  }},
  "assessment_schedule": [
    {{"week": 3, "type": "formative quiz", "focus": "core concepts"}},
    {{"week": 6, "type": "midterm project", "focus": "integration"}},
    {{"week": 12, "type": "capstone", "focus": "real-world application"}}
  ]
}}
"""
    
    try:
        response = analyst_llm.invoke([
            SystemMessage(content="You are an expert curriculum designer. Output ONLY valid JSON."),
            HumanMessage(content=prompt)
        ])
        
        # Robust JSON extraction
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        progression = json.loads(content)
        print(f"✓ Designed {len(progression.get('weekly_progression', []))}-week progression")
        
        return {**state, "learning_progression": progression}
        
    except Exception as e:
        print(f"⚠ Pedagogy agent failed: {str(e)}")
        # Fallback progression (prevents workflow collapse)
        fallback = {
            "weekly_progression": [
                {
                    "week": i+1,
                    "theme": f"Week {i+1} content",
                    "cognitive_focus": "understand" if i < 3 else "apply" if i < 7 else "analyze",
                    "key_concepts": [f"concept_{i+1}_a", f"concept_{i+1}_b"],
                    "scaffolding_notes": "Fallback progression"
                }
                for i in range(course['duration_weeks'])
            ],
            "prerequisite_graph": {},
            "assessment_schedule": []
        }
        return {**state, "learning_progression": fallback}
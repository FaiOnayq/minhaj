# agents/technical_depth.py
"""Agent 3: Adds concrete technical specifications and tooling"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from states import CourseState
from config import GROQ_API_KEY, TECHNICAL_DEPTH_MODEL
import json


analyst_llm = ChatGroq(model=TECHNICAL_DEPTH_MODEL, temperature=0.3, api_key=GROQ_API_KEY)


def technical_depth_agent(state: CourseState) -> CourseState:
    """Adds concrete technical specifications to the pedagogical structure"""
    print("⚙️ Technical Depth Agent: Adding concrete specifications...")
    
    course = state["course_input"]
    progression = state["learning_progression"]
    
    # Build context from progression
    progression_context = "\n".join([
        f"Week {w['week']}: {w['theme']} (Focus: {w['cognitive_focus']}) - Concepts: {', '.join(w['key_concepts'])}"
        for w in progression.get("weekly_progression", [])[:min(8, len(progression.get('weekly_progression', [])))]
    ])
    
    prompt = f"""You are a principal engineer designing a technically rigorous curriculum for {course['subject_domain']}.
Convert pedagogical progression into concrete technical specifications.

RULES:
1. Specify EXACT tools/frameworks with versions where relevant (e.g., "PyTorch 2.1+", NOT "deep learning frameworks")
2. Map concepts to specific algorithms/models (e.g., "classification" → "Logistic Regression, Random Forest, XGBoost")
3. Include standard libraries for each domain (e.g., Pandas/Numpy for data work)
4. Ensure toolchain compatibility (don't mix TensorFlow 1.x with modern libraries)
5. Balance depth vs breadth: 2-3 frameworks max for beginners, 4-5 for advanced

COURSE LEVEL: {course['education_level']}
PEDAGOGICAL PROGRESSION:
{progression_context}

OUTPUT JSON with this structure:
{{
  "weekly_technical_specs": [
    {{
      "week": 1,
      "core_algorithms": ["algorithm1", "algorithm2"],
      "frameworks_tools": ["tool1 (vX.Y)", "tool2"],
      "libraries": ["lib1", "lib2"],
      "code_complexity": "low/medium/high",
      "environment_setup": "conda env with python=3.10, pytorch=2.1"
    }}
  ],
  "domain_toolchain": {{
    "core_frameworks": ["primary framework", "secondary framework"],
    "data_tools": ["pandas", "numpy"],
    "visualization": ["matplotlib", "seaborn"],
    "deployment": ["docker", "fastapi"]
  }},
  "version_requirements": {{
    "python": ">=3.9",
    "key_libraries": ["pytorch>=2.0", "scikit-learn>=1.3"]
  }}
}}
"""
    
    try:
        response = analyst_llm.invoke([
            SystemMessage(content="You are a principal engineer. Output ONLY valid JSON with concrete technical specs."),
            HumanMessage(content=prompt)
        ])
        
        # Robust JSON extraction
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        specs = json.loads(content)
        print(f"✓ Added technical specs for {len(specs.get('weekly_technical_specs', []))} weeks")
        
        return {**state, "technical_specifications": specs}
        
    except Exception as e:
        print(f"⚠ Technical agent failed: {str(e)}")
        # Fallback specs
        fallback = {
            "weekly_technical_specs": [
                {
                    "week": i+1,
                    "core_algorithms": [f"algorithm_{i+1}"],
                    "frameworks_tools": ["python", "jupyter"],
                    "libraries": ["numpy", "pandas"],
                    "code_complexity": "medium",
                    "environment_setup": "python=3.10"
                }
                for i in range(course['duration_weeks'])
            ],
            "domain_toolchain": {
                "core_frameworks": ["python"],
                "data_tools": ["pandas", "numpy"],
                "visualization": ["matplotlib"],
                "deployment": []
            },
            "version_requirements": {"python": ">=3.9", "key_libraries": []}
        }
        return {**state, "technical_specifications": fallback}
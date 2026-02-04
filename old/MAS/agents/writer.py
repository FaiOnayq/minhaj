# agents/writer.py
"""Final agent: Synthesizes validated curriculum into human-readable format"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from states import CourseState
from config import GROQ_API_KEY, WRITER_MODEL
import json


writer_llm = ChatGroq(model=WRITER_MODEL, temperature=0.7, api_key=GROQ_API_KEY)


def writer(state: CourseState) -> CourseState:
    """Generates final human-readable course with weekly breakdowns, resources, assessments"""
    print("✍️ Writer Agent: Generating final course...")
    
    course = state["course_input"]
    curriculum = state.get("draft_curriculum", {})
    resources = state.get("filtered_resources", [])
    validation = state.get("validation_report", {})
    
    # Format resources for inclusion
    resource_list = "\n".join([
        f"{i+1}. [{r['source_type']}] {r['title']} ({r['url']})"
        for i, r in enumerate(resources[:10])
    ])
    
    # Format weekly topics
    weekly_breakdown = ""
    for topic in curriculum.get("topics", [])[:12]:  # Show first 12 weeks
        weekly_breakdown += f"""
### Week {topic['week']}: {topic['topic_name']}
- **Difficulty**: {topic['difficulty_level'].title()}
- **Subtopics**: {', '.join(topic['subtopics'][:4])}
- **Learning Outcomes**:
  {chr(10).join(f'  - {outcome}' for outcome in topic['learning_outcomes'][:3])}
- **Tools & Frameworks**: {', '.join(topic['technical_coverage']['frameworks_tools'][:3]) or 'None'}
- **Estimated Effort**: {topic.get('estimated_hours', 10):.0f} hours
"""
    
    prompt = f"""You are a professional curriculum writer. Transform this validated curriculum structure 
into a beautiful, instructor-ready course syllabus.

COURSE METADATA:
- Title: {course['course_title']}
- Domain: {course['subject_domain']}
- Duration: {course['duration_weeks']} weeks
- Level: {course['education_level'].title()}
- Goals: {', '.join(course['teaching_goals'])}

VALIDATION QUALITY SCORE: {validation.get('quality_score', 0):.1f}/100
{'✅ Passed all validation checks' if validation.get('passed') else '⚠️ Best-effort curriculum (validation limits reached)'}

WEEKLY BREAKDOWN:
{weekly_breakdown}

CURATED RESOURCES:
{resource_list}

Generate a complete course syllabus with:
1. Engaging course description & learning philosophy
2. Week-by-week breakdown with topics, outcomes, and hands-on activities
3. Assessment strategy (quizzes, projects, capstone)
4. Required toolchain setup guide
5. Recommended resource list (prioritize high-authority sources)
6. Prerequisites and success tips

Format as clean Markdown. Be inspiring yet practical. Target audience: {course['education_level']} learners.
"""
    
    try:
        response = writer_llm.invoke([
            SystemMessage(content="You are a world-class curriculum designer. Output beautifully formatted Markdown."),
            HumanMessage(content=prompt)
        ])
        
        final_course = {
            "course_title": course['course_title'],
            "syllabus_markdown": response.content.strip(),
            "curriculum_structure": curriculum,
            "validation_report": validation,
            "resource_count": len(resources),
            "generation_timestamp": "2026-02-01"  # In production: use datetime.now()
        }
        
        print("✓ Final course generated successfully")
        return {**state, "final_course": final_course}
        
    except Exception as e:
        print(f"⚠ Writer agent failed: {str(e)}")
        # Fallback output
        fallback = {
            "course_title": course['course_title'],
            "syllabus_markdown": f"# {course['course_title']}\n\n*Auto-generated syllabus (fallback mode)*\n\n{weekly_breakdown}",
            "curriculum_structure": curriculum,
            "validation_report": validation,
            "resource_count": len(resources),
            "generation_timestamp": "2026-02-01"
        }
        return {**state, "final_course": fallback}
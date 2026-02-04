# agents/curriculum_validator.py
"""Agent 4: Validates and self-corrects curriculum drafts"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from states import CourseState, ValidationReport
from tools.Curriculum import CurriculumTools
from config import GROQ_API_KEY, CURR_VALID_MODEL
import json


validator_llm = ChatGroq(model=CURR_VALID_MODEL, temperature=0.2, api_key=GROQ_API_KEY)
tools = CurriculumTools()


def curriculum_validator_agent(state: CourseState) -> CourseState:
    """Validates curriculum draft and decides whether to accept or retry"""
    print(f"✅ Validation Agent: Attempt #{state['validation_attempts'] + 1}")
    
    course = state["course_input"]
    domain = course["subject_domain"]  # e.g., "MLOps", "Web Development", "Data Engineering"
    level = course["education_level"]
    draft = state.get("draft_curriculum", {})
    progression = state.get("learning_progression", {})
    specs = state.get("technical_specifications", {})
    
    # Build draft curriculum from components if not already merged
    if not draft or "topics" not in draft:
        topics = []
        weekly_prog = progression.get("weekly_progression", [])
        weekly_specs = specs.get("weekly_technical_specs", [])
        
        for i in range(min(len(weekly_prog), len(weekly_specs), course['duration_weeks'])):
            prog = weekly_prog[i]
            spec = weekly_specs[i] if i < len(weekly_specs) else {}
            
            estimated_hours = tools.estimate_weekly_workload(
                {
                    "topic_name": prog.get("theme", f"Week {i+1}"),
                    "subtopics": prog.get("key_concepts", []),
                    "learning_outcomes": [
                        f"{prog.get('cognitive_focus', 'understand')} {concept}" 
                        for concept in prog.get("key_concepts", [])[:2]
                    ],
                    "technical_coverage": {
                        "core_concepts": prog.get("key_concepts", []),
                        "algorithms_models": spec.get("core_algorithms", []),
                        "frameworks_tools": spec.get("frameworks_tools", [])
                    }
                },
                domain,        # ✅ REQUIRED ARGUMENT
                level       # ✅ REQUIRED ARGUMENT
            )
            
            topics.append({
                "week": i + 1,
                "topic_name": prog.get("theme", f"Week {i+1}"),
                "subtopics": prog.get("key_concepts", []),
                "learning_outcomes": [
                    f"{prog.get('cognitive_focus', 'understand')} {concept}" 
                    for concept in prog.get("key_concepts", [])[:2]
                ],
                "technical_coverage": {
                    "core_concepts": prog.get("key_concepts", []),
                    "algorithms_models": spec.get("core_algorithms", []),
                    "frameworks_tools": spec.get("frameworks_tools", [])
                },
                "difficulty_level": course['education_level'],
                "estimated_hours": estimated_hours
            })
        
        draft = {
            "topics": topics,
            "overall_structure": {
                "total_weeks": course['duration_weeks'],
                "recommended_prerequisites": ["Python basics", "High school math"],
                "assessment_pattern": "Weekly quizzes + Midterm project + Capstone",
                "lab_project_ratio": "40% theory / 60% hands-on"
            },
            "domain_technical_coverage": specs.get("domain_toolchain", {}),
            "prerequisite_graph": progression.get("prerequisite_graph", {})
        }
    
    # Run validation checks
    issues = []
    quality_score = 100.0
    
    # 1. Bloom's taxonomy check
    for topic in draft.get("topics", []):
        is_valid, blooms_issues = tools.validate_blooms_taxonomy(topic.get("learning_outcomes", []))
        if not is_valid:
            issues.extend(blooms_issues)
            quality_score -= 5.0
    
    # 2. Prerequisite gap detection
    prereq_issues = tools.detect_prerequisite_gaps(draft.get("topics", []), domain)
    issues.extend(prereq_issues)
    quality_score -= len(prereq_issues) * 3.0
    
    # 3. Workload validation
    for topic in draft.get("topics", []):
        hours = topic.get("estimated_hours", 10.0)
        if hours > 22.0:
            issues.append(f"Week {topic['week']}: Unrealistic workload ({hours:.1f}h/week)")
            quality_score -= 4.0
        elif hours < 6.0:
            issues.append(f"Week {topic['week']}: Insufficient depth ({hours:.1f}h/week)")
            quality_score -= 2.0
    
    # 4. Toolchain compatibility
    all_frameworks = []
    for topic in draft.get("topics", []):
        all_frameworks.extend(topic.get("technical_coverage", {}).get("frameworks_tools", []))
    toolchain_issues = tools.analyze_toolchain_risks(all_frameworks, domain, level)
    issues.extend(toolchain_issues)
    quality_score -= len(toolchain_issues) * 2.5
    
    # 5. Coverage completeness
    if len(draft.get("topics", [])) < course['duration_weeks'] * 0.8:
        issues.append(f"Only {len(draft['topics'])} weeks defined for {course['duration_weeks']}-week course")
        quality_score -= 10.0
    
    # Determine pass/fail
    passed = quality_score >= 85.0 and len(issues) == 0
    
    validation_report: ValidationReport = {
        "passed": passed,
        "issues": issues[:10],  # Limit to top 10 issues
        "suggested_fixes": _generate_fixes(issues, draft, course),
        "quality_score": max(0.0, quality_score)
    }
    
    print(f"{'✓ PASSED' if passed else '✗ FAILED'} validation (Score: {quality_score:.1f}/100)")
    if issues:
        print("Issues found:")
        for i, issue in enumerate(issues[:5], 1):
            print(f"  {i}. {issue}")
    
    return {
        **state,
        "draft_curriculum": draft,
        "validation_report": validation_report,
        "validation_attempts": state["validation_attempts"] + 1
    }


def _generate_fixes(issues: list, draft: dict, course: dict) -> list:
    """Generate actionable fixes for validation issues"""
    fixes = []
    
    for issue in issues[:5]:  # Limit to top 5 issues
        if "Bloom's verb" in issue:
            fixes.append("Rewrite outcomes using action verbs: 'implement CNN' not 'learn CNN'")
        elif "prerequisite" in issue.lower():
            fixes.append("Re-sequence weeks to teach foundational concepts before advanced ones")
        elif "workload" in issue.lower() and "Unrealistic" in issue:
            fixes.append("Split complex week into two weeks or reduce scope")
        elif "workload" in issue.lower() and "Insufficient" in issue:
            fixes.append("Add deeper labs/projects to increase engagement")
        elif "toolchain" in issue.lower():
            fixes.append("Standardize on one framework family per course level")
    
    if len(draft.get("topics", [])) < course['duration_weeks']:
        fixes.append(f"Expand curriculum to cover all {course['duration_weeks']} weeks with meaningful content")
    
    return fixes[:5]  # Return top 5 fixes


def should_retry_validation(state: CourseState) -> str:
    """Conditional edge: retry if failed validation AND under max attempts"""
    report = state["validation_report"]
    attempts = state["validation_attempts"]
    max_attempts = state.get("max_validation_attempts", 3)
    
    if report and report["passed"]:
        print("🎉 Validation passed! Proceeding to writer agent...")
        return "writer"
    elif attempts < max_attempts:
        print(f"↻ Validation failed ({attempts}/{max_attempts} attempts). Retrying...")
        return "pedagogy_designer"  # Loop back to redesign
    else:
        print(f"⚠ Max validation attempts reached ({max_attempts}). Proceeding with best-effort curriculum...")
        return "writer"
# agents/state.py
"""Enhanced state schema for multi-agent curriculum generation"""
from typing import TypedDict, List, Dict, Optional, Any


class CourseInput(TypedDict):
    course_title: str
    subject_domain: str
    duration_weeks: int
    education_level: str  # beginner/intermediate/advanced
    teaching_goals: List[str]
    reference_link: Optional[str]


class Resource(TypedDict):
    title: str
    url: str
    content: str
    source_type: str  # academic/blog/video/documentation
    relevance_score: float
    authority_score: float  # 0-1 based on source credibility


class WeeklyTopic(TypedDict):
    week: int
    topic_name: str
    subtopics: List[str]
    learning_outcomes: List[str]  # Must use Bloom's taxonomy verbs
    technical_coverage: Dict[str, List[str]]
    difficulty_level: str  # beginner/intermediate/advanced
    estimated_hours: float


class CurriculumStructure(TypedDict):
    topics: List[WeeklyTopic]
    overall_structure: Dict[str, Any]
    domain_technical_coverage: Dict[str, List[str]]
    prerequisite_graph: Dict[str, List[str]]  # Concept dependency map


class ValidationReport(TypedDict):
    passed: bool
    issues: List[str]
    suggested_fixes: List[str]
    quality_score: float


class CourseState(TypedDict):
    """Enhanced workflow state with validation loops"""
    course_input: CourseInput
    raw_search_results: List[Dict]  # Unfiltered results from researcher
    filtered_resources: List[Resource]  # Triage agent output
    learning_progression: Dict[str, Any]  # Pedagogy agent output
    technical_specifications: Dict[str, Any]  # Technical depth agent output
    draft_curriculum: CurriculumStructure  # Merged draft
    validation_report: Optional[ValidationReport]
    final_course: Dict[str, Any]
    validation_attempts: int  # Track retry count
    max_validation_attempts: int
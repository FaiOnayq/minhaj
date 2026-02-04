# agents/tools.py (REVISED - Domain-Agnostic)
import re
from typing import List, Dict, Tuple, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import CURR_MODEL, GROQ_API_KEY


class CurriculumTools:
    def __init__(self):
        # Lightweight validator LLM (fast + cheap)
        self.validator_llm = ChatGroq(
            model=CURR_MODEL, 
            temperature=0.1,  # Deterministic for validation
            api_key=GROQ_API_KEY
        )
        
        # Bloom's verbs (UNIVERSAL - keep this)
        self.blooms_verbs = {
            "remember": ["define", "list", "recall", "identify", "name", "recognize"],
            "understand": ["explain", "summarize", "describe", "interpret", "compare", "classify"],
            "apply": ["implement", "use", "solve", "execute", "demonstrate", "apply"],
            "analyze": ["analyze", "differentiate", "examine", "categorize", "deconstruct"],
            "evaluate": ["evaluate", "critique", "justify", "assess", "defend", "judge"],
            "create": ["design", "build", "develop", "construct", "architect", "engineer"]
        }
        
        # Authority sources (domain-agnostic credibility signals)
        self.authority_domains = [
            ".edu", ".gov", "arxiv.org", "ieee.org", "acm.org", "springer.com", 
            "nature.com", "science.org", "github.com", "official documentation"
        ]
    
    # ✅ RESTORED: Essential resource filtering (domain-agnostic)
    def filter_resources_by_relevance(self, resources: List[Dict], course_title: str, domain: str) -> List[Dict]:
        """
        Filter and score resources using LLM-powered relevance scoring.
        Works for ANY domain by providing context about the field.
        """
        if not resources:
            return []
        
        filtered = []
        # Process top 25 results to avoid token limits
        for idx, r in enumerate(resources[:25]):
            # Authority scoring (domain-agnostic)
            authority = 0.4  # baseline
            url = r.get('url', '').lower()
            title = r.get('title', '').lower()
            
            # Boost authority for educational/government/trusted sources
            if any(trusted in url for trusted in [".edu", ".gov", "arxiv.org", "ieee.org", "acm.org"]):
                authority = 0.9
            elif "github.com" in url or "official" in title:
                authority = 0.8
            elif any(blog in url for blog in ["medium.com", "towardsdatascience.com", "dev.to"]):
                authority = 0.6
            
            # Relevance scoring via LLM (domain-aware)
            snippet = (r.get('title', '') + " " + r.get('content', '')[:400]).strip()
            if not snippet or len(snippet) < 20:
                continue
            
            prompt = f"""Rate relevance of this resource to course: "{course_title}" in domain: "{domain}".
Scale: 0.0 (completely irrelevant) to 1.0 (highly relevant and authoritative)
Resource snippet: {snippet[:500]}
Respond ONLY with a number between 0.0 and 1.0:"""
            
            try:
                resp = self.validator_llm.invoke([HumanMessage(content=prompt)]).content.strip()
                # Extract first number from response
                match = re.search(r'[\d.]+', resp)
                relevance = float(match.group()) if match else 0.3
                # Clamp to 0.0-1.0 range
                relevance = max(0.0, min(1.0, relevance))
            except Exception as e:
                print(f"  ⚠ Relevance scoring failed for resource {idx}: {str(e)[:80]}")
                relevance = 0.3  # Conservative default
            
            # Only keep reasonably relevant resources
            if relevance >= 0.55:
                filtered.append({
                    **r,
                    "relevance_score": round(relevance, 2),
                    "authority_score": round(authority, 2),
                    "composite_score": round((relevance * 0.7) + (authority * 0.3), 2)
                })
        # Sort by composite score and keep top 15
        filtered = sorted(filtered, key=lambda x: x["composite_score"], reverse=True)[:15]
        print(f"  → Filtered {len(resources)} → {len(filtered)} relevant resources")
        return filtered
    
    # ✅ KEEP: Universal Bloom's taxonomy validation
    def validate_blooms_taxonomy(self, outcomes: List[str]) -> Tuple[bool, List[str]]:
        """Domain-agnostic check for proper learning outcome verbs"""
        issues = []
        valid_count = 0
        
        for outcome in outcomes:
            outcome_lower = outcome.lower().strip()
            # Skip empty/placeholder outcomes
            if not outcome_lower or outcome_lower in ["tbd", "to be determined"]:
                issues.append(f"Placeholder outcome: '{outcome}'")
                continue
                
            is_valid = any(
                any(verb in outcome_lower for verb in verbs)
                for verbs in self.blooms_verbs.values()
            )
            if not is_valid:
                issues.append(
                    f"Outcome lacks action verb (Bloom's taxonomy): '{outcome}' → "
                    f"Suggestion: 'Implement X' not 'Learn X'"
                )
            else:
                valid_count += 1
        
        pass_rate = valid_count / max(len(outcomes), 1)
        return pass_rate >= 0.85, issues  # 85% threshold
    
    def detect_prerequisite_gaps(self, topics: List[Dict], course_domain: str) -> List[str]:
        """
        Dynamically detect prerequisite gaps using LLM reasoning.
        Works for ANY domain by providing context about the field.
        """
        if not topics:
            return []
        
        # Build concise topic sequence for LLM analysis
        topic_sequence = "\n".join([
            f"Week {t['week']}: {t['topic_name']}\n"
            f"  Concepts: {', '.join(t.get('subtopics', [])[:3])}\n"
            f"  Outcomes: {', '.join(t.get('learning_outcomes', [])[:2])}"
            for t in topics[:min(12, len(topics))]  # Analyze first 12 weeks
        ])
        
        prompt = f"""You are an expert curriculum designer for {course_domain}.
Analyze this weekly topic sequence for PREREQUISITE GAPS - where Week N assumes knowledge 
that hasn't been taught in Weeks 1..N-1.

RULES:
1. Flag ONLY clear gaps (e.g., "teaches Docker containers before explaining Linux basics")
2. Ignore reasonable assumptions (e.g., "uses Python" in intermediate course)
3. Be specific: "Week 5 assumes knowledge of X taught in Week Y"
4. Return MAX 5 critical gaps

Topic Sequence:
{topic_sequence}

Respond ONLY as JSON array of strings:
["Gap 1 description", "Gap 2 description", ...]
If no gaps found, return empty array: []
"""
        
        try:
            response = self.validator_llm.invoke([
                SystemMessage(content="You are a meticulous curriculum validator. Output ONLY valid JSON."),
                HumanMessage(content=prompt)
            ])
            
            # Robust JSON extraction
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            gaps = json.loads(content)
            return [str(g) for g in gaps[:5]] if isinstance(gaps, list) else []
            
        except Exception as e:
            # Graceful degradation: never block workflow on validation failure
            print(f"⚠ Prerequisite detection failed (using safe fallback): {str(e)[:100]}")
            return []  # Return empty list → no false positives
    
    def analyze_toolchain_risks(self, frameworks: List[str], course_domain: str, education_level: str) -> List[str]:
        """
        Dynamically analyze toolchain choices for pedagogical risks.
        Adapts to domain (web dev vs ML vs embedded systems).
        """
        if not frameworks or len(frameworks) < 2:
            return []
        
        frameworks_text = ", ".join(frameworks[:8])  # Limit context length
        
        prompt = f"""You are a senior engineering educator for {course_domain} courses at {education_level} level.
Analyze this toolchain selection for PEDAGOGICAL RISKS (not technical conflicts):

Toolchain: {frameworks_text}

Consider:
1. Cognitive overload: Too many similar tools for beginners? (e.g., React + Vue + Svelte in Week 1)
2. Version mismatches: Known incompatible versions? (e.g., TensorFlow 1.x with modern libraries)
3. Domain mismatch: Tools inappropriate for field? (e.g., using Excel for big data engineering)
4. Learning curve spikes: Sudden jumps in complexity without scaffolding?

Return MAX 3 concise risk descriptions as JSON array:
["Risk 1", "Risk 2", ...]
If no significant risks, return empty array: []
"""
        
        try:
            response = self.validator_llm.invoke([
                SystemMessage(content="You are a pragmatic educator. Output ONLY valid JSON."),
                HumanMessage(content=prompt)
            ])
            
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            risks = json.loads(content)
            return [str(r) for r in risks[:3]] if isinstance(risks, list) else []
            
        except Exception as e:
            print(f"⚠ Toolchain analysis failed (safe fallback): {str(e)[:100]}")
            return []
    
    # ✅ NEW: Domain-adaptive workload estimator
    def estimate_weekly_workload(self, topic: Dict, course_domain: str, education_level: str) -> float:
        """
        Estimate hours based on domain norms (not hardcoded rules).
        Web dev labs ≠ ML model training in time requirements.
        """
        # Ask LLM for domain-aware estimate
        prompt = f"""Estimate realistic weekly hours for {education_level} learners in {course_domain} for:
Topic: {topic.get('topic_name', 'Unknown')}
Subtopics: {', '.join(topic.get('subtopics', [])[:3])}
Outcomes: {', '.join(topic.get('learning_outcomes', [])[:2])}
Tools: {', '.join(topic.get('technical_coverage', {}).get('frameworks_tools', [])[:3])}

Consider:
- Theory (lectures/reading): typically 2-4h
- Guided labs: 3-6h depending on tool complexity
- Open-ended projects: 5-10h for meaningful work
- Domain norms: Web dev labs faster than training ML models

Respond ONLY with a number (e.g., "12.5") representing total hours:
"""
        
        try:
            response = self.validator_llm.invoke([
                SystemMessage(content="You are a realistic curriculum planner. Output ONLY a number."),
                HumanMessage(content=prompt)
            ])
            hours = float(re.search(r'[\d.]+', response.content.strip()).group())
            return min(max(hours, 5.0), 25.0)  # Clamp to realistic range
        except:
            # Safe fallback based on education level
            fallbacks = {"beginner": 8.0, "intermediate": 12.0, "advanced": 15.0}
            return fallbacks.get(education_level, 10.0)
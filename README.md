

## Minhaj – AI Curriculum Builder 🎓

Minhaj is an agent-based AI system that transforms instructor inputs into a complete, structured, and exportable curriculum  including syllabus, slides, labs, and exams. in just one click.

---
## Features

- Generate a full curriculum based on:
  - Target topic
  - Learner level
  - Course duration
  - Preferred tools & technologies
  - Learning goals and constraints
  - Optional reference material support
- ⚡ Fast, clean, and user-friendly UI
- AI-assisted curriculum generation

---
## Agents Architecture

Minhaj is designed using an **agent-based AI architecture**, where each agent has a well-defined responsibility in the curriculum generation pipeline. to produce high-quality, structured educational content.

---

## Core Agents

### 1️- Interpreter Agent

**Purpose:**  
Transforms user inputs into a structured (JASON) curriculum plan.

**Inputs:**
- Target topic
- Learner level
- Course duration
- Constraints & preferences


These inputs are validated on the frontend and converted into a **JSON payload**.


---
### 2- Web Research Agent (Tavily)

**Purpose:** Ground the curriculum in real-world, up-to-date knowledge.

**Responsibilities:**
- Convert the user topic into a structured search query
- Use Tavily to search the web
- Extract:
  - Relevant subtopics
  - Industry tools and frameworks
  - Best practices and trends

**Output:**
- Clean, summarized research context passed to downstream agents
---

### 3- Curriculum Planner Agent

**Purpose:** Design the overall course structure.

**Responsibilities:**
- Analyze learner level and duration
- Split content into weekly modules
- Define learning objectives per week
- Decide progression logic (from fundamentals → advanced)

**Output:**
Structured weekly curriculum plan

---

### 4- Content Generation Agents

These agents operate **in parallel** using the curriculum plan and research context.

#### - Slides Agent
- Generates lecture slide outlines and content
- Ensures alignment with weekly objectives

#### - Labs Agent
- Creates hands-on exercises and practical tasks
- Matches tools and difficulty level

#### Exams Agent
- Generates quizzes and exams
- Includes different question types
- Aligns assessments with learning outcomes
---

### 5- Validation & Alignment Agent

**Purpose:** Ensure consistency and quality.

**Responsibilities:**
- Check alignment between:
  - Objectives
  - Slides
  - Labs
  - Examsfix 
- Enforce constraints (duration, level, goals)
- Detect missing or inconsistent content

---

##  System Data Flow

```text
User
 │
 ▼
Frontend Form
 │  (Topic, Level, Duration, Goals, Constraints)
 ▼
JSON Payload
 │
 ▼
Web Research Agent (Tavily)
 │  └─ Live web context & best practices
 ▼
Curriculum Planner Agent
 │  └─ Weekly structure & learning objectives
 ▼
Content Generation Agents (Parallel)
 │  ├─ Slides Agent
 │  ├─ Labs Agent
 │  └─ Assessment Agent
 ▼
Validation & Alignment Agent
 │  └─ Consistency + constraints enforcement
 ▼
ZIP Export

```
## Tech Stack

### Frontend
- HTML5
- Tailwind CSS
- Vanilla JavaScript

### Backend
- Python
- FastAPI
- REST API (JSON-based)


Raw, unstructured text passed to the **Interpreter Agent**.


---
### Team

Built with ♡ by:
	•	Noura Aljandol
	•	Fai AlOnayq
	•	Wajan Alqahtani


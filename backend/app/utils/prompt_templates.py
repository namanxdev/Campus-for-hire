"""
Structured prompt templates with validation.
Organizes all prompt building logic with input validation.
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class PromptType(Enum):
    """Types of prompts supported."""
    ROADMAP = "roadmap"
    INTERVIEW = "interview"
    JD_ANALYSIS = "jd_analysis"
    WEEKLY_CHECKIN = "weekly_checkin"
    SKILL_ASSESSMENT = "skill_assessment"
    CONTENT_EXPLANATION = "content_explanation"
    RESUME_TIPS = "resume_tips"
    RESOURCE_RECOMMENDATION = "resource_recommendation"


class ValidationError(Exception):
    """Raised when prompt input validation fails."""
    pass


@dataclass
class PromptTemplate:
    """Template for generating prompts with validation."""
    name: str
    system_prompt: str
    template: str
    required_params: list[str] = field(default_factory=list)
    optional_params: dict[str, Any] = field(default_factory=dict)
    validators: dict[str, Callable] = field(default_factory=dict, repr=False)
    output_format: str = "json"
    
    def validate(self, params: dict) -> tuple[bool, list[str]]:
        """
        Validate input parameters.
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check required params
        for param in self.required_params:
            if param not in params or params[param] is None:
                errors.append(f"Missing required parameter: {param}")
        
        # Run custom validators
        for param, validator in self.validators.items():
            if param in params and params[param] is not None:
                try:
                    is_valid, message = validator(params[param])
                    if not is_valid:
                        errors.append(f"Validation failed for {param}: {message}")
                except Exception as exc:
                    errors.append(f"Validator error for {param}: {exc}")
        
        return len(errors) == 0, errors
    
    def format(self, **kwargs) -> tuple[str, str]:
        """
        Format the prompt template with parameters.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Validate first
        is_valid, errors = self.validate(kwargs)
        if not is_valid:
            raise ValidationError(f"Prompt validation failed: {', '.join(errors)}")
        
        # Merge with optional params
        params = {**self.optional_params, **kwargs}
        
        # Format the template
        try:
            user_prompt = self.template.format(**params)
        except KeyError as exc:
            raise ValidationError(f"Missing template parameter: {exc}")
        
        return self.system_prompt, user_prompt


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATOR FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def validate_language(value: str) -> tuple[bool, str]:
    """Validate language code."""
    valid_languages = ["en", "hi", "ta", "te"]
    if value in valid_languages:
        return True, ""
    return False, f"Language must be one of {valid_languages}"


def validate_college_tier(value: str) -> tuple[bool, str]:
    """Validate college tier."""
    valid_tiers = ["tier1", "tier2", "tier3"]
    if value in valid_tiers:
        return True, ""
    return False, f"College tier must be one of {valid_tiers}"


def validate_user_level(value: str) -> tuple[bool, str]:
    """Validate user proficiency level."""
    valid_levels = ["beginner", "intermediate", "advanced"]
    if value in valid_levels:
        return True, ""
    return False, f"User level must be one of {valid_levels}"


def validate_hours_per_day(value: int) -> tuple[bool, str]:
    """Validate hours per day."""
    if 1 <= value <= 12:
        return True, ""
    return False, "Hours per day must be between 1 and 12"


def validate_days_per_week(value: int) -> tuple[bool, str]:
    """Validate days per week."""
    if 1 <= value <= 7:
        return True, ""
    return False, "Days per week must be between 1 and 7"


def validate_non_empty_string(value: str) -> tuple[bool, str]:
    """Validate non-empty string."""
    if value and isinstance(value, str) and value.strip():
        return True, ""
    return False, "Value must be a non-empty string"


def validate_company_list(value: list) -> tuple[bool, str]:
    """Validate list of companies."""
    if not isinstance(value, list):
        return False, "Companies must be a list"
    if len(value) > 20:
        return False, "Too many companies (max 20)"
    return True, ""


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

ROADMAP_SYSTEM_PROMPT = """You are an expert career counselor specializing in Indian campus placements. Create personalized, week-by-week learning roadmaps for college students.

You must respond ONLY with valid JSON — no markdown, no explanation, no text before or after the JSON object.

Context:
- Tier 1: IITs, NITs, BITS - focus on product companies (MAANG)
- Tier 2: State colleges, private universities - mix of service and product
- Tier 3: Local colleges - focus on service companies with off-campus prep"""


INTERVIEW_SYSTEM_PROMPT = """You are an experienced technical interviewer for Indian campus placements. Simulate real interviews from TCS, Infosys, Wipro, Amazon, Microsoft, Google, etc.

Guidelines:
- Ask one question at a time
- Progress easy → medium → hard
- Give brief feedback after each answer
- Be supportive but thorough
- Consider Tier-2/3 college contexts"""


JD_ANALYSIS_SYSTEM_PROMPT = """You are an expert at analyzing job descriptions for Indian tech companies. Map required skills against candidate profiles.

You must respond ONLY with valid JSON.

Company types:
- Service: TCS, Infosys, Wipro - aptitude, basic programming, communication
- Product: Amazon, Microsoft - DSA, system design, CS fundamentals
- Startups: Practical skills, projects, frameworks"""


WEEKLY_CHECKIN_SYSTEM_PROMPT = """You are a supportive career mentor for Indian college students. Conduct weekly progress check-ins with empathy and actionable advice.

You must respond ONLY with valid JSON.

Consider:
- Tier-2/3 students may have limited resources
- Academic pressure and time constraints
- Motivation and encouragement are key"""


SKILL_ASSESSMENT_SYSTEM_PROMPT = """You are a technical skills assessor for campus placement readiness. Evaluate students fairly based on their background.

You must respond ONLY with valid JSON.

Assessment areas:
- Programming fundamentals
- Data Structures and Algorithms
- CS fundamentals (OS, DBMS, Networks)
- Problem-solving approach
- Communication clarity"""


CONTENT_EXPLANATION_SYSTEM_PROMPT = """You are an expert technical educator for Indian college students. Explain complex CS concepts simply.

You must respond ONLY with valid JSON.

Approach:
- Use relatable analogies (Indian context)
- Adjust complexity to student level
- For regional languages: use Hinglish/Tanglish/Telgish (keep tech terms in English)"""


RESUME_TIPS_SYSTEM_PROMPT = """You are a professional resume reviewer for Indian campus placements. Know what recruiters at TCS, Infosys, Wipro, Amazon, startups look for.

You must respond ONLY with valid JSON.

Focus:
- ATS compatibility
- STAR method for projects
- Tier-2/3 student strategies
- Company-specific keywords"""


RESOURCE_RECOMMENDATION_SYSTEM_PROMPT = """You are an expert curator of learning resources for Indian students. Recommend specific, actionable resources.

You must respond ONLY with valid JSON.

Prioritize:
- Free resources
- India-specific content (CodeWithHarry, Apna College, etc.)
- Company-specific preparation materials"""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

PROMPT_TEMPLATES: dict[PromptType, PromptTemplate] = {
    PromptType.ROADMAP: PromptTemplate(
        name="roadmap",
        system_prompt=ROADMAP_SYSTEM_PROMPT,
        template="""Create a personalized weekly learning roadmap for an Indian college student.

**Student Profile:**
- College Tier: {college_tier}
- Degree: {degree}, Major: {major}
- Current Year: {current_year}
- CS Background: {is_cs_background}
- Current Skills: {skills}
- Target Role: {target_role}
- Target Companies: {target_companies}
- Available Time: {hours_per_day} hours/day, {days_per_week} days/week
- Preferred Language: {preferred_language}

**Tier-Specific Guidance:**
{college_tier_guidance}

Generate a roadmap as JSON with this structure:
{{
    "title": "...",
    "total_weeks": <number>,
    "weeks": [
        {{
            "week": 1,
            "theme": "...",
            "objectives": ["..."],
            "days": [
                {{
                    "day": 1,
                    "title": "...",
                    "tasks": [
                        {{
                            "id": "w1d1t1",
                            "title": "...",
                            "type": "video|read|practice|project",
                            "duration_minutes": 30,
                            "description": "...",
                            "resources": ["..."]
                        }}
                    ]
                }}
            ]
        }}
    ]
}}""",
        required_params=["college_tier", "target_role", "hours_per_day", "days_per_week"],
        optional_params={
            "degree": "B.Tech",
            "major": "",
            "current_year": 3,
            "is_cs_background": True,
            "skills": "beginner level",
            "target_companies": "top tech companies",
            "preferred_language": "en",
            "college_tier_guidance": ""
        },
        validators={
            "college_tier": validate_college_tier,
            "hours_per_day": validate_hours_per_day,
            "days_per_week": validate_days_per_week,
            "preferred_language": validate_language,
        },
        output_format="json"
    ),
    
    PromptType.INTERVIEW: PromptTemplate(
        name="interview",
        system_prompt=INTERVIEW_SYSTEM_PROMPT,
        template="""Start a mock interview for {role} position at {company}.

Candidate level: {user_level}
Company type: {company_type}

Begin by:
1. Introducing yourself as the interviewer
2. Asking the candidate to introduce themselves
3. Asking ONE technical/role-appropriate question

Keep it natural and conversational.""",
        required_params=["role"],
        optional_params={
            "company": "a tech company",
            "user_level": "intermediate",
            "company_type": "service"
        },
        validators={
            "user_level": validate_user_level,
        },
        output_format="text"
    ),
    
    PromptType.INTERVIEW_EVALUATE: PromptTemplate(
        name="interview_evaluate",
        system_prompt=INTERVIEW_SYSTEM_PROMPT,
        template="""Evaluate this mock interview for {role} at {company}.

**Interview Transcript:**
{conversation}

Provide evaluation as JSON:
{{
    "score": <1-10>,
    "feedback": "...",
    "strengths": ["..."],
    "improvements": ["..."],
    "technical_score": <1-10>,
    "communication_score": <1-10>,
    "problem_solving_score": <1-10>,
    "readiness_level": "not_ready|getting_ready|ready|very_ready",
    "next_steps": ["..."]
}}""",
        required_params=["role", "conversation"],
        optional_params={
            "company": "a tech company"
        },
        validators={},
        output_format="json"
    ),
    
    PromptType.JD_ANALYSIS: PromptTemplate(
        name="jd_analysis",
        system_prompt=JD_ANALYSIS_SYSTEM_PROMPT,
        template="""Analyze this job description against the candidate's skills.

**Job Description:**
{job_description}

**Candidate Skills:**
{user_skills}

Respond with JSON:
{{
    "role": "...",
    "company": "...",
    "company_type": "service|product|startup",
    "required_skills": [{{"name": "...", "level": "...", "category": "...", "importance": "..."}}],
    "gap_analysis": [{{"skill": "...", "gap": "...", "priority": "..."}}],
    "preparation_timeline": "...",
    "recommendations": ["..."],
    "resources": [{{"type": "...", "title": "...", "platform": "..."}}]
}}""",
        required_params=["job_description"],
        optional_params={
            "user_skills": "No skills provided"
        },
        validators={
            "job_description": validate_non_empty_string,
        },
        output_format="json"
    ),
    
    PromptType.WEEKLY_CHECKIN: PromptTemplate(
        name="weekly_checkin",
        system_prompt=WEEKLY_CHECKIN_SYSTEM_PROMPT,
        template="""Weekly check-in for Week {week_number}.

**Completed Tasks:**
{completed_tasks}

**Pending Tasks:**
{pending_tasks}

**Challenges:**
{challenges}

**Profile:**
- College Tier: {college_tier}
- Target Companies: {target_companies}

Respond with JSON:
{{
    "week": {week_number},
    "progress_assessment": "...",
    "completion_rate": <percentage>,
    "acknowledgment": "...",
    "blocker_analysis": [{{"blocker": "...", "solution": "..."}}],
    "adjustments": [{{"type": "...", "description": "..."}}],
    "motivation": "...",
    "next_week_priorities": ["..."]
}}""",
        required_params=["week_number"],
        optional_params={
            "completed_tasks": "None",
            "pending_tasks": "None",
            "challenges": "None",
            "college_tier": "tier2",
            "target_companies": "top companies"
        },
        validators={
            "week_number": lambda x: (isinstance(x, int) and x > 0, "Must be positive integer"),
            "college_tier": validate_college_tier,
        },
        output_format="json"
    ),
    
    PromptType.SKILL_ASSESSMENT: PromptTemplate(
        name="skill_assessment",
        system_prompt=SKILL_ASSESSMENT_SYSTEM_PROMPT,
        template="""Create skill assessment for: {skill_area}

**Context:**
- Level: {user_level}
- College Tier: {college_tier}
- Target Companies: {target_companies}

Generate assessment JSON:
{{
    "assessment_id": "...",
    "skill_area": "{skill_area}",
    "questions": [
        {{
            "id": "q1",
            "type": "conceptual|coding|scenario",
            "difficulty": "easy|medium|hard",
            "question": "...",
            "expected_answer_points": ["..."]
        }}
    ],
    "expected_duration_minutes": <number>,
    "instructions": "..."
}}""",
        required_params=["skill_area"],
        optional_params={
            "user_level": "intermediate",
            "college_tier": "tier2",
            "target_companies": "service companies"
        },
        validators={
            "user_level": validate_user_level,
            "college_tier": validate_college_tier,
        },
        output_format="json"
    ),
    
    PromptType.CONTENT_EXPLANATION: PromptTemplate(
        name="content_explanation",
        system_prompt=CONTENT_EXPLANATION_SYSTEM_PROMPT,
        template="""Explain: "{concept}"

**Level:** {user_level}
**Language:** {language}

Respond with JSON:
{{
    "concept": "{concept}",
    "explanation": {{
        "simple_definition": "...",
        "detailed_explanation": "...",
        "real_world_analogy": "...",
        "why_it_matters": "..."
    }},
    "code_examples": [{{"language": "...", "code": "..."}}],
    "key_points": ["..."],
    "common_mistakes": ["..."],
    "interview_questions": [{{"question": "...", "difficulty": "..."}}],
    "resources": [{{"title": "...", "type": "..."}}]
}}""",
        required_params=["concept"],
        optional_params={
            "user_level": "intermediate",
            "language": "en"
        },
        validators={
            "concept": validate_non_empty_string,
            "user_level": validate_user_level,
            "language": validate_language,
        },
        output_format="json"
    ),
    
    PromptType.RESUME_TIPS: PromptTemplate(
        name="resume_tips",
        system_prompt=RESUME_TIPS_SYSTEM_PROMPT,
        template="""Review resume for {target_companies}.

**Resume:**
{resume_content}

**Profile:**
- College Tier: {college_tier}
- Target: {target_role}

Analyze and provide JSON:
{{
    "overall_score": <0-100>,
    "sections": {{
        "skills": {{"score": <0-100>, "feedback": "...", "suggestions": ["..."]}},
        "projects": {{"score": <0-100>, "feedback": "...", "star_issues": ["..."]}},
        "experience": {{"score": <0-100>, "feedback": "..."}}
    }},
    "formatting_issues": ["..."],
    "action_items": [{{"priority": "...", "action": "..."}}],
    "sample_summary": "...",
    "tier_specific_advice": "..."
}}""",
        required_params=["resume_content"],
        optional_params={
            "target_companies": "campus recruiters",
            "college_tier": "tier2",
            "target_role": "Software Engineer"
        },
        validators={
            "college_tier": validate_college_tier,
        },
        output_format="json"
    ),
    
    PromptType.RESOURCE_RECOMMENDATION: PromptTemplate(
        name="resource_recommendation",
        system_prompt=RESOURCE_RECOMMENDATION_SYSTEM_PROMPT,
        template="""Recommend resources for: {topic}

**Context:**
- Level: {user_level}
- Target Company: {target_company}
- Content Type: {content_type}
- Preferred Language: {preferred_language}

Provide JSON:
{{
    "topic": "{topic}",
    "resources": [
        {{
            "title": "...",
            "platform": "...",
            "type": "...",
            "free": true|false,
            "language": "...",
            "description": "..."
        }}
    ],
    "learning_path": [{{"step": 1, "resource": "...", "focus": "..."}}],
    "pro_tips": ["..."]
}}""",
        required_params=["topic"],
        optional_params={
            "user_level": "intermediate",
            "target_company": None,
            "content_type": "all",
            "preferred_language": "en"
        },
        validators={
            "user_level": validate_user_level,
            "preferred_language": validate_language,
        },
        output_format="json"
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_template(prompt_type: PromptType) -> PromptTemplate:
    """Get a prompt template by type."""
    if prompt_type not in PROMPT_TEMPLATES:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    return PROMPT_TEMPLATES[prompt_type]


def format_prompt(prompt_type: PromptType, **kwargs) -> tuple[str, str]:
    """
    Format a prompt by type with parameters.
    
    Args:
        prompt_type: Type of prompt to format
        **kwargs: Parameters for the prompt
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    template = get_template(prompt_type)
    return template.format(**kwargs)


def validate_inputs(prompt_type: PromptType, params: dict) -> tuple[bool, list[str]]:
    """
    Validate inputs for a prompt type without formatting.
    
    Args:
        prompt_type: Type of prompt
        params: Parameters to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    template = get_template(prompt_type)
    return template.validate(params)


def get_college_tier_guidance(tier: str) -> str:
    """Get specific guidance based on college tier."""
    guidance = {
        "tier1": """Tier 1 (IITs, NITs, BITS):
- Focus: Product companies (Google, Microsoft, Amazon, Flipkart)
- Emphasize: Advanced DSA, system design, competitive programming
- Include: Complex algorithms, LLD/HLD, CS theory""",
        
        "tier2": """Tier 2 (State colleges, private universities):
- Focus: Mix of service and product companies
- Targets: TCS Digital, Infosys PP, Cognizant GenC Next, Accenture, mid-tier product
- Emphasize: Core DSA + practical projects, aptitude, communication
- Balance: Coding practice with CS fundamentals""",
        
        "tier3": """Tier 3 (Local colleges):
- Focus: Service companies + off-campus product prep
- Targets: TCS, Infosys, Wipro, Capgemini (regular), startups
- Emphasize: Aptitude, basic programming, CS fundamentals, communication
- Strategy: Clear mass recruitment first, then prepare for off-campus"""
    }
    return guidance.get(tier, guidance["tier2"])


def build_user_profile_context(user_profile: dict) -> dict:
    """
    Build a complete context dictionary from user profile.
    
    Args:
        user_profile: User profile dictionary
        
    Returns:
        Dictionary with all parameters needed for prompts
    """
    college_tier = user_profile.get("college_tier", "tier2")
    
    return {
        "college_tier": college_tier,
        "college_tier_guidance": get_college_tier_guidance(college_tier),
        "degree": user_profile.get("degree", "B.Tech"),
        "major": user_profile.get("major", ""),
        "current_year": user_profile.get("current_year", 3),
        "is_cs_background": user_profile.get("is_cs_background", True),
        "skills": user_profile.get("skills", {}),
        "target_role": user_profile.get("target_role", "Software Engineer"),
        "target_companies": user_profile.get("target_companies", []),
        "hours_per_day": user_profile.get("hours_per_day", 2),
        "days_per_week": user_profile.get("days_per_week", 5),
        "preferred_language": user_profile.get("preferred_language", "en"),
    }


class PromptBuilder:
    """Builder class for constructing prompts with validation."""
    
    def __init__(self, prompt_type: PromptType):
        self.template = get_template(prompt_type)
        self.params = {}
    
    def with_param(self, name: str, value: Any) -> "PromptBuilder":
        """Add a parameter."""
        self.params[name] = value
        return self
    
    def with_profile(self, user_profile: dict) -> "PromptBuilder":
        """Add all user profile parameters."""
        self.params.update(build_user_profile_context(user_profile))
        return self
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate current parameters."""
        return self.template.validate(self.params)
    
    def build(self) -> tuple[str, str]:
        """Build the prompt."""
        return self.template.format(**self.params)
    
    def build_safe(self, fallback: tuple[str, str] | None = None) -> tuple[str, str]:
        """Build the prompt with fallback on error."""
        try:
            return self.build()
        except ValidationError as exc:
            if fallback:
                return fallback
            raise


# Convenience functions
def create_roadmap_prompt(user_profile: dict) -> tuple[str, str]:
    """Create a roadmap prompt from user profile."""
    builder = PromptBuilder(PromptType.ROADMAP).with_profile(user_profile)
    return builder.build()


def create_interview_prompt(role: str, company: str | None = None, user_level: str = "intermediate") -> tuple[str, str]:
    """Create an interview start prompt."""
    return format_prompt(
        PromptType.INTERVIEW,
        role=role,
        company=company or "a tech company",
        user_level=user_level,
        company_type="service" if company and any(x in company.lower() for x in ["tcs", "infosys", "wipro"]) else "product"
    )


def create_jd_analysis_prompt(job_description: str, user_skills: dict | None = None) -> tuple[str, str]:
    """Create a JD analysis prompt."""
    return format_prompt(
        PromptType.JD_ANALYSIS,
        job_description=job_description,
        user_skills=user_skills or {}
    )


def create_weekly_checkin_prompt(
    week_number: int,
    completed_tasks: list,
    pending_tasks: list,
    challenges: list,
    user_profile: dict
) -> tuple[str, str]:
    """Create a weekly check-in prompt."""
    return format_prompt(
        PromptType.WEEKLY_CHECKIN,
        week_number=week_number,
        completed_tasks="\n".join(f"- {t}" for t in completed_tasks) if completed_tasks else "None",
        pending_tasks="\n".join(f"- {t}" for t in pending_tasks) if pending_tasks else "None",
        challenges="\n".join(f"- {c}" for c in challenges) if challenges else "None",
        college_tier=user_profile.get("college_tier", "tier2"),
        target_companies=user_profile.get("target_companies", [])
    )


def create_content_explanation_prompt(
    concept: str,
    language: str = "en",
    user_level: str = "intermediate"
) -> tuple[str, str]:
    """Create a content explanation prompt."""
    return format_prompt(
        PromptType.CONTENT_EXPLANATION,
        concept=concept,
        language=language,
        user_level=user_level
    )


def create_resume_tips_prompt(resume_content: dict, user_profile: dict) -> tuple[str, str]:
    """Create a resume tips prompt."""
    return format_prompt(
        PromptType.RESUME_TIPS,
        resume_content=resume_content,
        target_companies=user_profile.get("target_companies", []),
        college_tier=user_profile.get("college_tier", "tier2"),
        target_role=user_profile.get("target_role", "Software Engineer")
    )

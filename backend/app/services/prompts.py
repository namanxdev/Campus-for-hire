"""
Prompt templates for AI services.
Contains all system prompts and user prompt generators for the Campus-to-Hire platform.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

ROADMAP_SYSTEM_PROMPT = """You are an expert career counselor and learning path designer specializing in Indian campus placements and hiring. You create personalized, week-by-week learning roadmaps for college students preparing for campus placements.

You must respond ONLY with valid JSON — no markdown, no explanation, no text before or after the JSON object.

Context for Indian Students:
- Many students are from Tier-2/3 colleges with limited exposure to industry practices
- Common challenges: English communication, lack of mentorship, limited resources, internet connectivity issues
- Placement season: August-December for most colleges, some have off-campus drives year-round
- Key companies: TCS, Infosys, Wipro, Cognizant, Capgemini, Accenture, Amazon India, Microsoft India, Google India, Flipkart, startups

Tier-Specific Considerations:
- Tier 1: Focus on advanced DSA, system design, competitive programming for product companies
- Tier 2: Balance between service company prep (aptitude, basics) and product company prep (DSA)
- Tier 3: Heavy focus on fundamentals, aptitude, spoken English, and off-campus strategies"""


INTERVIEW_SYSTEM_PROMPT = """You are an experienced technical interviewer conducting mock interviews for Indian campus placements. You simulate real interview experiences from companies like Google, Amazon, Microsoft, TCS, Infosys, Wipro, Cognizant, Capgemini, Accenture, and others.

Your behavior:
- Ask one question at a time
- Start with an introduction and a warm-up question
- Progress from easy to hard
- For technical roles: mix DSA, CS fundamentals, and behavioral questions
- Give brief encouraging feedback after each answer
- Adapt difficulty based on responses
- Be conversational but professional, like a real interviewer
- Consider Tier-2/3 college contexts - be supportive but thorough

For Hindi/Regional language responses: Accept Hinglish or simple regional language responses and provide feedback accordingly.

Indian Placement Context:
- Service companies (TCS, Infosys): Focus on aptitude, basic programming, DBMS, willingness to learn
- Product companies: Focus on problem-solving approach, optimization, edge cases
- Startups: Focus on practical knowledge, frameworks, projects"""


JD_SYSTEM_PROMPT = """You are an expert at analyzing job descriptions for Indian tech companies and mapping required skills against a candidate's profile. You help students understand skill gaps for campus placement roles.

You must respond ONLY with valid JSON — no markdown, no explanation, no text before or after the JSON object.

Context for Indian Campus Placements:
- Indian service companies (TCS, Infosys, Wipro) focus on: aptitude, basic programming, communication, DBMS basics
- Service company assessments: AMCAT, Cocubes, Mettl, HackerRank (basic level)
- Product companies (Amazon, Microsoft, Google) focus on: DSA, problem-solving, CS fundamentals, system design
- Product company assessments: Online coding tests, multiple technical rounds
- Startups focus on: practical skills, projects, frameworks, quick learning ability
- Consider Tier-2/3 college students may have different exposure levels - provide realistic pathways

Gap Analysis Guidelines:
- Be honest but encouraging about skill gaps
- Provide realistic timelines (e.g., "4 weeks for basic DSA", "8 weeks for advanced")
- Suggest free resources first (YouTube, GeeksforGeeks, LeetCode free tier)
- Consider part-time preparation constraints"""


WEEKLY_CHECKIN_SYSTEM_PROMPT = """You are a supportive career mentor conducting weekly progress check-ins for Indian college students preparing for campus placements.

Your role:
- Review the student's weekly progress empathetically
- Identify blockers and provide specific, actionable solutions
- Adjust the learning plan based on their pace and circumstances
- Provide motivation and encouragement tailored to their situation
- Consider the realities of Tier-2/3 college students: limited resources, time constraints, other academic pressures, family responsibilities

Respond in a friendly, encouraging tone. Be specific and actionable in your advice.

Tier-Specific Guidance:
- Tier 1 students: Focus on optimization, advanced topics, competitive edge
- Tier 2 students: Balance improvement with confidence building
- Tier 3 students: Extra encouragement, focus on fundamentals, off-campus strategies

Common Student Challenges to Address:
- Academic exam pressure and semester conflicts
- Limited laptop/internet access
- English communication anxiety
- Lack of peer group for preparation
- Family financial concerns

You must respond ONLY with valid JSON — no markdown, no explanation, no text before or after the JSON object."""


SKILL_ASSESSMENT_SYSTEM_PROMPT = """You are a technical skills assessor specializing in evaluating Indian college students for campus placement readiness.

Your role:
- Conduct a comprehensive skill evaluation
- Ask targeted questions to gauge actual skill level (not self-reported)
- Assess technical depth, problem-solving approach, and communication
- Consider the student's college tier and background context
- Identify strengths and improvement areas
- Provide honest but encouraging feedback

Assessment areas:
- Programming fundamentals (variables, loops, functions, OOP)
- Data Structures and Algorithms (arrays, strings, linked lists, trees, graphs)
- CS fundamentals (OS, DBMS, Networks basics)
- Problem-solving approach
- Communication clarity

Tier-Specific Assessment:
- Tier 1: Include advanced DSA, system design basics, optimization questions
- Tier 2: Balanced mix of moderate DSA and CS fundamentals
- Tier 3: Focus on fundamentals, simple problem-solving, confidence building

Regional Language Consideration:
- Accept responses in Hinglish (Hindi+English), Tanglish (Tamil+English), or Telgish (Telugu+English)
- Focus on technical understanding over perfect English
- Provide feedback in their preferred language style

You must respond ONLY with valid JSON — no markdown, no explanation, no text before or after the JSON object."""


CONTENT_EXPLANATION_SYSTEM_PROMPT = """You are an expert technical educator specializing in explaining complex computer science concepts to Indian college students in simple, understandable terms.

Your approach:
- Break down complex topics into digestible, bite-sized parts
- Use relatable real-world analogies (Indian context preferred: cricket, chai, traffic, family)
- Provide code examples in the student's preferred programming language
- Include visual explanations where helpful (ASCII diagrams)
- Connect theory to practical applications relevant to placements
- Adjust complexity based on student's level (beginner, intermediate, advanced)

For regional language explanations:
- Use Hinglish (Hindi + English) or Tanglish (Tamil + English) or Telgish (Telugu + English) as appropriate
- Keep technical terms in English as they are universally understood (array, function, loop, pointer)
- Focus on clarity over perfect grammar
- Use common spoken language patterns

Examples of regional language style:
- Hinglish: "Array ek data structure hai jisme hum similar type ke items store kar sakte hain."
- Tanglish: "Array oru data structure, adhula similar type items store pannalam."
- Telgish: "Array oka data structure, dini lo similar type items store cheyavachu."

You must respond ONLY with valid JSON — no markdown, no explanation, no text before or after the JSON object."""


RESUME_TIPS_SYSTEM_PROMPT = """You are a professional resume reviewer specializing in campus placement resumes for Indian students.

Your expertise:
- Know what Indian recruiters (TCS, Infosys, Wipro, Amazon India, startups) look for
- Understand ATS (Applicant Tracking System) requirements
- Familiar with resume formats that work for Indian campus placements (1-page for freshers)
- Can suggest improvements for students with limited experience

Key focus areas:
- Format and readability (ATS-friendly)
- Skills presentation (prioritize based on target companies)
- Project descriptions (STAR method: Situation-Task-Action-Result)
- Achievements and certifications (relevance to job)
- For Tier-2/3 students: How to highlight strengths despite limited brand recognition
- Common mistakes Indian students make in resumes (photo inclusion, father's name, too personal)

Company-Specific Guidance:
- Service companies: Emphasize consistency, academics, willingness to learn
- Product companies: Emphasize problem-solving, projects, technical depth
- Startups: Emphasize versatility, practical skills, quick learning

You must respond ONLY with valid JSON — no markdown, no explanation, no text before or after the JSON object."""


# ═══════════════════════════════════════════════════════════════════════════════
# ROADMAP PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_roadmap_prompt(user_profile: dict) -> str:
    """Generate a personalized roadmap prompt based on user profile."""
    college_tier = user_profile.get("college_tier", "tier2")
    is_cs = user_profile.get("is_cs_background", False)
    target_role = user_profile.get("target_role", "Software Engineer")
    target_companies = user_profile.get("target_companies", [])
    hours_per_day = user_profile.get("hours_per_day", 2)
    days_per_week = user_profile.get("days_per_week", 5)
    skills = user_profile.get("skills", {})
    degree = user_profile.get("degree", "B.Tech")
    major = user_profile.get("major", "")
    current_year = user_profile.get("current_year", 3)
    preferred_language = user_profile.get("preferred_language", "en")

    companies_str = ", ".join(target_companies) if target_companies else "top tech companies"
    skills_str = ", ".join(skills.keys()) if isinstance(skills, dict) and skills else "beginner level"

    # College tier specific guidance
    tier_guidance = {
        "tier1": """
- Tier 1 colleges: Focus on product companies (Google, Microsoft, Amazon, Flipkart)
- Emphasize: DSA, system design, competitive programming
- Target: High-paying product roles and MAANG
- Include: Advanced algorithms, LLD/HLD preparation
- Off-campus strategy: Early preparation for internships, referral networks""",
        "tier2": """
- Tier 2 colleges: Mix of product and service companies
- Target companies: TCS Digital, Infosys Power Programmer, Cognizant GenC Next, Wipro Elite, Accenture, mid-tier product companies
- Emphasize: Balance DSA with practical projects, aptitude preparation
- Include: Core CS subjects, coding practice, communication skills
- Strategy: Clear on-campus service tests, then prepare for off-campus product roles""",
        "tier3": """
- Tier 3 colleges: Focus on service companies with upskilling for off-campus product roles
- Target companies: TCS, Infosys, Wipro, Capgemini, Cognizant (regular roles)
- Emphasize: Strong fundamentals, aptitude, communication, practical projects
- Strategy: Clear service company tests first, then prepare for off-campus product roles
- Include: Heavy focus on aptitude, basic programming, CS fundamentals, spoken English
- Special focus: Off-campus application strategies, LinkedIn networking, skill showcase"""
    }.get(college_tier, tier_guidance["tier2"])

    # Language preference note
    language_note = ""
    if preferred_language != "en":
        language_note = f"""
- Student prefers content in {preferred_language} (Hindi/Tamil/Telugu)
- Include resource links that offer regional language content:
  - Hindi: CodeWithHarry, Apna College, Anuj Bhaiya
  - Tamil: Tamil Code, Guvi (Tamil content)
  - Telugu: Telugu programming channels, local coaching resources"""

    return f"""Create a personalized weekly learning roadmap for an Indian college student preparing for campus placements.

**Student Profile:**
- College Tier: {college_tier}
- Degree: {degree}, Major: {major}
- Current Year: {current_year}
- CS Background: {"Yes" if is_cs else "No — needs fundamentals first"}
- Current Skills: {skills_str}
- Target Role: {target_role}
- Target Companies: {companies_str}
- Available Time: {hours_per_day} hours/day, {days_per_week} days/week
- Preferred Language: {preferred_language}

**Context for Indian Campus Hiring:**{tier_guidance}
- Placement season typically runs August-December for on-campus
- Off-campus drives happen year-round through company career portals, LinkedIn, referrals
- Common assessment platforms: HackerRank, Cocubes, AMCAT, Mettl, Hackerearth, TCS NQT platform
- Interview rounds: Online test (aptitude + coding), technical interview, HR interview
- Service companies often have mass recruitment drives
- Many Tier-2/3 students need to apply off-campus for better opportunities{language_note}

{"- Since the student is NOT from a CS background, include foundational CS topics (programming basics, data structures intro) in early weeks." if not is_cs else ""}

**Generate a roadmap as JSON with this exact structure:**
{{
    "title": "Personalized Roadmap for [role] at [companies]",
    "total_weeks": <8-12 based on available time>,
    "weeks": [
        {{
            "week": 1,
            "theme": "Week theme",
            "objectives": ["objective 1", "objective 2"],
            "days": [
                {{
                    "day": 1,
                    "title": "Day title",
                    "tasks": [
                        {{
                            "id": "w1d1t1",
                            "title": "Task title",
                            "type": "video|read|practice|project",
                            "duration_minutes": 30,
                            "description": "What to do",
                            "resources": ["resource link or name"]
                        }}
                    ]
                }}
            ]
        }}
    ]
}}

Important:
- Each day should have 2-4 tasks fitting within {hours_per_day} hours
- Only include {days_per_week} days per week
- Mix task types: video lectures, reading, coding practice, mini-projects
- Progressively increase difficulty
- Include specific resource suggestions:
  - YouTube: CodeWithHarry, Apna College, Striver, NeetCode, Anuj Bhaiya, Love Babbar
  - Websites: GeeksforGeeks, LeetCode, Coding Ninjas, HackerRank, InterviewBit
  - Practice: LeetCode (free problems), HackerRank, CodeChef, Codeforces
- For non-CS students, start with programming fundamentals before DSA
- Include India-specific resources and platforms
- Add tips for company-specific preparation (TCS NQT, Infosys SP, etc.)
- Consider adding spoken English practice for Tier-2/3 students
- Include off-campus preparation strategies for Tier-3 students"""


# ═══════════════════════════════════════════════════════════════════════════════
# INTERVIEW PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_interview_start_prompt(role: str, company: str | None, user_level: str = "intermediate") -> str:
    """Generate the initial prompt for starting a mock interview."""
    company_str = company if company else "a top tech company"
    
    company_specific = ""
    if company:
        company_lower = company.lower()
        if any(x in company_lower for x in ["tcs", "infosys", "wipro", "cognizant", "capgemini"]):
            company_specific = """
- Focus on: Basic DSA, DBMS, SQL, aptitude-style problems
- Interview style: Structured, process-oriented
- May ask about: willingness to relocate, bond period, service agreement
- Common questions: "Why IT?", "Willing to work night shifts?", "Comfortable with any location?"
- They value consistency and attitude over exceptional skills"""
        elif any(x in company_lower for x in ["amazon", "microsoft", "google", "flipkart", "adobe"]):
            company_specific = """
- Focus on: Advanced DSA, system design (for experienced), problem-solving approach
- Interview style: Bar raiser rounds, leadership principles (Amazon)
- Expect: Coding on shared editors, follow-up questions, edge cases
- They value: Optimal solutions, clean code, communication of thought process
- Amazon specifically asks about Leadership Principles - prepare 2-3 stories using STAR method"""
        elif "startup" in company_lower:
            company_specific = """
- Focus on: Practical skills, projects, frameworks, system design basics
- Interview style: Conversational, might include take-home assignments
- They value: Quick learning, versatility, passion for technology"""

    return f"""You are starting a mock interview for a {role} position at {company_str} for an Indian campus placement.

Candidate level: {user_level}

Begin by:
1. Briefly introducing yourself as the interviewer
2. Asking the candidate to introduce themselves (name, college, year, why this role)
3. Then ask your first technical/role-appropriate question

Company-specific context:{company_specific if company_specific else "\n- Standard tech interview format"}

Keep it natural and conversational. Ask only ONE question to start.

For Tier-2/3 college students: Be encouraging but maintain professional standards. Help them feel comfortable."""


def get_interview_evaluate_prompt(role: str, company: str | None, messages: list) -> str:
    """Generate prompt for evaluating a completed mock interview."""
    company_str = company if company else "a top tech company"
    conversation = "\n".join(
        f"{'Interviewer' if m['role'] == 'assistant' else 'Candidate'}: {m['content']}"
        for m in messages
    )
    
    company_criteria = ""
    if company:
        company_lower = company.lower()
        if any(x in company_lower for x in ["tcs", "infosys", "wipro", "cognizant", "capgemini"]):
            company_criteria = """
Service Company Criteria:
- Basic programming knowledge is sufficient
- Communication clarity is important
- Attitude and willingness to learn matter greatly
- Consistency in answers
- Professional demeanor"""
        elif any(x in company_lower for x in ["amazon", "microsoft", "google", "flipkart"]):
            company_criteria = """
Product Company Criteria:
- Problem-solving approach and optimization
- Code quality and edge case handling
- Communication of thought process
- Handling of follow-up questions
- System design knowledge (for experienced roles)"""

    return f"""Evaluate this mock interview for a {role} position at {company_str}.

**Interview Transcript:**
{conversation}

**Provide your evaluation as JSON only (no other text):**
{{
    "score": <1-10>,
    "feedback": "Overall feedback paragraph - be honest but encouraging, especially for Tier-2/3 students",
    "strengths": ["strength 1", "strength 2"],
    "improvements": ["area 1", "area 2"],
    "technical_score": <1-10>,
    "communication_score": <1-10>,
    "problem_solving_score": <1-10>,
    "readiness_level": "not_ready|getting_ready|ready|very_ready",
    "next_steps": ["specific action 1", "specific action 2"],
    "company_fit": "How well the candidate fits {company_str} specifically"
}}

Evaluation criteria:
- Technical accuracy and depth of answers
- Communication clarity (especially important for Indian students from Tier-2/3 colleges)
- Problem-solving approach and thought process
- Confidence and professionalism
- Code quality (if coding was involved)
- Response structure and organization
- Relevance to {role} role at {company_str}
{company_criteria}

Consider the candidate's background and be fair in assessment. Tier-2/3 students may have less exposure but can be equally capable with proper guidance."""


def get_interview_followup_prompt(role: str, company: str | None, last_answer: str, context: list) -> str:
    """Generate prompt for continuing an interview based on the last answer."""
    company_str = company if company else "a top tech company"
    
    return f"""Continue the mock interview for {role} at {company_str}.

**Context so far:**
{"\n".join(f"{'Interviewer' if m['role'] == 'assistant' else 'Candidate'}: {m['content']}" for m in context[-4:])}

**Candidate's last answer:**
{last_answer}

**Your response should:**
1. Provide brief, constructive feedback on their answer (1-2 sentences) - be encouraging for Tier-2/3 students
2. Ask the next question OR follow up for clarification
3. Keep the conversation natural and professional
4. Progress difficulty gradually based on their performance

If they struggled: Ask a simpler question or ask them to clarify, help them think through
If they did well: Increase difficulty slightly or ask about edge cases
If coding question: Ask about time/space complexity optimization

For non-native English speakers: Focus on technical understanding over perfect English.

Respond as the interviewer in a conversational manner."""


# ═══════════════════════════════════════════════════════════════════════════════
# JD ANALYSIS PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_jd_analysis_prompt(job_description: str, user_skills: dict | None) -> str:
    """Generate prompt for analyzing a job description against user skills."""
    skills_str = ""
    if user_skills and isinstance(user_skills, dict):
        skills_str = "\n".join(f"- {k}: {v}" for k, v in user_skills.items())
    else:
        skills_str = "No skills data provided"

    return f"""Analyze this job description and compare it against the candidate's current skills.

**Job Description:**
{job_description}

**Candidate's Current Skills:**
{skills_str}

**Respond with this exact JSON structure:**
{{
    "role": "extracted role title",
    "company": "extracted company name or null",
    "company_type": "service|product|startup|consulting",
    "experience_level": "fresher|0-2 years|2-5 years",
    "required_skills": [
        {{
            "name": "skill name",
            "level": "beginner|intermediate|advanced",
            "category": "technical|soft|domain",
            "importance": "must_have|good_to_have"
        }}
    ],
    "gap_analysis": [
        {{
            "skill": "skill name",
            "user_level": "none|beginner|intermediate|advanced",
            "required_level": "beginner|intermediate|advanced",
            "gap": "none|small|medium|large",
            "priority": "high|medium|low"
        }}
    ],
    "preparation_timeline": "estimated weeks to prepare",
    "preparation_timeline_weeks": <number>,
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2"
    ],
    "resources": [
        {{
            "type": "course|video|article|practice",
            "title": "resource name",
            "platform": "YouTube|Coursera|GeeksforGeeks|etc",
            "free": true|false,
            "language": "en|hi|ta|te"
        }}
    ],
    "indian_context": {{
        "relevant_for_tier2_3": true|false,
        "off-campus_feasible": true|false,
        "application_tips": "tips for Indian context"
    }}
}}

Focus on:
- Skills relevant to Indian campus placements: DSA, programming languages, CS fundamentals, aptitude, communication
- Company-specific requirements (TCS, Infosys have different expectations than Google, Amazon)
- Realistic assessment for Tier-2/3 college students
- Actionable next steps with time estimates
- Free resources first (YouTube, GeeksforGeeks, LeetCode free)
- Consider if the role is feasible for off-campus applications from Tier-2/3 colleges"""


# ═══════════════════════════════════════════════════════════════════════════════
# WEEKLY CHECKIN PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_weekly_checkin_prompt(
    week_number: int,
    completed_tasks: list,
    pending_tasks: list,
    challenges: list,
    user_profile: dict,
    previous_feedback: list | None = None
) -> str:
    """Generate prompt for weekly progress check-in."""
    college_tier = user_profile.get("college_tier", "tier2")
    target_companies = user_profile.get("target_companies", [])
    hours_per_day = user_profile.get("hours_per_day", 2)
    preferred_language = user_profile.get("preferred_language", "en")
    
    companies_str = ", ".join(target_companies) if target_companies else "top tech companies"
    
    completed_str = "\n".join(f"- {t}" for t in completed_tasks) if completed_tasks else "No tasks completed"
    pending_str = "\n".join(f"- {t}" for t in pending_tasks) if pending_tasks else "No pending tasks"
    challenges_str = "\n".join(f"- {c}" for c in challenges) if challenges else "No major challenges reported"
    
    previous_feedback_str = ""
    if previous_feedback:
        previous_feedback_str = f"\n**Previous Feedback:**\n" + "\n".join(f"- {f}" for f in previous_feedback[-3:])

    # Tier-specific encouragement
    tier_encouragement = {
        "tier1": "You're aiming high - keep pushing for excellence!",
        "tier2": "You're doing great! Consistency will help you compete with Tier-1 peers.",
        "tier3": "Your effort matters more than your college tag. Many successful engineers come from Tier-3 colleges!"
    }.get(college_tier, "Keep up the good work!")

    return f"""Conduct a weekly progress check-in for a student preparing for campus placements.

**Student Profile:**
- College Tier: {college_tier}
- Target Companies: {companies_str}
- Available Time: {hours_per_day} hours/day
- Preferred Language: {preferred_language}

**Week {week_number} Progress:**
**Completed Tasks:**
{completed_str}

**Pending Tasks:**
{pending_str}

**Challenges Faced:**
{challenges_str}{previous_feedback_str}

**Tier Context:** {tier_encouragement}

**Provide your check-in response as JSON only:**
{{
    "week": {week_number},
    "progress_assessment": "excellent|good|average|needs_improvement",
    "completion_rate": <percentage>,
    "acknowledgment": "Encouraging message about their progress - personalize based on tier and language preference",
    "blocker_analysis": [
        {{
            "blocker": "description",
            "severity": "high|medium|low",
            "suggested_solution": "specific solution - consider Indian student context",
            "resources": ["specific resources to help"]
        }}
    ],
    "adjustments": [
        {{
            "type": "pace|content|schedule",
            "description": "what to adjust",
            "reason": "why this adjustment"
        }}
    ],
    "motivation": "Personalized encouragement message - be culturally sensitive",
    "next_week_priorities": ["priority 1", "priority 2", "priority 3"],
    "resources": ["specific resource recommendations - include regional language resources if applicable"],
    "continue_next_week": true|false,
    "placement_readiness": "not_started|early_preparation|on_track|ready|very_ready"
}}

Be empathetic but honest. If they're falling behind, provide constructive guidance on how to catch up.
Consider their college tier context - Tier-3 students may need more time for fundamentals.
Address common Indian student challenges: exam pressure, limited resources, English confidence."""


# ═══════════════════════════════════════════════════════════════════════════════
# SKILL ASSESSMENT PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_skill_assessment_prompt(
    skill_area: str,
    user_level: str,
    college_tier: str,
    target_companies: list
) -> str:
    """Generate prompt for conducting skill assessment."""
    companies_str = ", ".join(target_companies) if target_companies else "service/product companies"
    
    skill_areas = {
        "programming": "programming fundamentals (variables, loops, functions, OOP)",
        "dsa": "data structures and algorithms (arrays, strings, sorting, searching, basic trees/graphs)",
        "cs_fundamentals": "CS fundamentals (OS, DBMS, Networks basics)",
        "problem_solving": "problem-solving approach and logical thinking",
        "communication": "technical communication and explanation skills",
        "system_design": "system design basics (for advanced students)",
        "aptitude": "quantitative aptitude, logical reasoning, verbal ability"
    }
    
    skill_desc = skill_areas.get(skill_area, skill_area)

    # Tier-specific question difficulty
    tier_difficulty = {
        "tier1": "Include medium to hard questions. Focus on optimization and edge cases.",
        "tier2": "Mix of easy and medium questions. Some hard questions if they perform well.",
        "tier3": "Start with easy questions to build confidence. Gradually increase to medium."
    }.get(college_tier, tier_difficulty["tier2"])

    return f"""Conduct a skill assessment for {skill_desc}.

**Assessment Context:**
- Student level: {user_level}
- College Tier: {college_tier}
- Target Companies: {companies_str}

**Difficulty Guidelines:**
{tier_difficulty}

**Generate an assessment as JSON:**
{{
    "assessment_id": "unique_id",
    "skill_area": "{skill_area}",
    "questions": [
        {{
            "id": "q1",
            "type": "conceptual|coding|scenario|explanation",
            "difficulty": "easy|medium|hard",
            "question": "The question text - can be in Hinglish/Tanglish/Telgish for better understanding",
            "expected_answer_points": ["point 1", "point 2"],
            "evaluation_criteria": "how to evaluate the answer - be lenient for Tier-3 students on communication"
        }}
    ],
    "expected_duration_minutes": <estimated time>,
    "instructions": "Instructions for the student - encourage them, mention it's okay to make mistakes",
    "tier_context": {{
        "college_tier": "{college_tier}",
        "difficulty_notes": "Notes on difficulty adjustment"
    }}
}}

Guidelines:
- Start with 1-2 easy questions to build confidence
- Include 2-3 medium difficulty questions
- Add 1 harder question if they seem ready
- For Tier-3 colleges, focus more on fundamentals and be encouraging
- For product companies, include more challenging problems
- Make questions relevant to actual interview questions asked by {companies_str}
- Consider language barriers - allow explanations in Hinglish/Tanglish/Telgish
- Coding questions should have clear problem statements with examples"""


def get_skill_assessment_evaluation_prompt(
    skill_area: str,
    questions: list,
    answers: list,
    college_tier: str
) -> str:
    """Generate prompt for evaluating skill assessment responses."""
    qa_pairs = "\n\n".join(
        f"Q: {q['question']}\nExpected: {', '.join(q.get('expected_answer_points', []))}\nA: {a['answer']}"
        for q, a in zip(questions, answers)
    )

    # Tier-specific evaluation notes
    tier_notes = {
        "tier1": "Evaluate strictly. Look for optimal solutions and clear communication.",
        "tier2": "Evaluate fairly. Consider effort and approach, not just final answer.",
        "tier3": "Evaluate with encouragement. Focus on understanding, not perfection. Consider communication challenges."
    }.get(college_tier, tier_notes["tier2"])

    return f"""Evaluate the following skill assessment responses for {skill_area}.

**Student Background:** College Tier {college_tier}

**Tier Evaluation Notes:** {tier_notes}

**Questions and Answers:**
{qa_pairs}

**Provide evaluation as JSON:**
{{
    "overall_score": <0-100>,
    "level": "beginner|intermediate|advanced",
    "skill_area": "{skill_area}",
    "question_evaluations": [
        {{
            "question_id": "q1",
            "score": <0-100>,
            "feedback": "specific feedback - encouraging tone",
            "correct": true|false,
            "partially_correct": true|false
        }}
    ],
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "learning_recommendations": [
        {{
            "topic": "topic name",
            "priority": "high|medium|low",
            "resources": ["specific free resources"]
        }}
    ],
    "estimated_preparation_time": "time needed to reach target level",
    "readiness_for_target_companies": "not_ready|partially_ready|ready",
    "encouragement_message": "Personalized message based on tier and performance"
}}

Be fair in evaluation considering the student's college tier. Tier-3 students may have gaps but show potential.
Focus on improvement areas, not just scores. Provide actionable next steps."""


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT EXPLANATION PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_content_explanation_prompt(
    concept: str,
    language: str,
    user_level: str,
    context: str | None = None,
    examples_requested: bool = True
) -> str:
    """Generate prompt for explaining a technical concept."""
    
    language_instructions = {
        "hi": """Explain in Hinglish (mix of Hindi and English):
- Use simple Hindi for explanations
- Keep technical terms in English (e.g., "variable", "function", "array")
- Use Devanagari script for Hindi parts
- Style: Conversational, like a friend explaining
- Example: "Array ek data structure hai jisme hum similar type ke items store kar sakte hain."
- Use relatable Indian analogies (cricket, Bollywood, family, traffic)""",
        "ta": """Explain in Tanglish (mix of Tamil and English):
- Use simple Tamil for explanations
- Keep technical terms in English
- Use Roman script for Tamil parts
- Style: Friendly and approachable
- Example: "Array oru data structure, adhula similar type items store pannalam."
- Use South Indian cultural analogies when helpful""",
        "te": """Explain in Telgish (mix of Telugu and English):
- Use simple Telugu for explanations
- Keep technical terms in English
- Use Roman script for Telugu parts
- Style: Clear and encouraging
- Example: "Array oka data structure, dini lo similar type items store cheyavachu."
- Use relatable analogies for Telugu-speaking students""",
        "en": """Explain in clear, simple English with minimal jargon.
- Use analogies that Indian students can relate to
- Avoid complex English words when simple ones work
- Be concise but thorough"""
    }
    
    lang_instruction = language_instructions.get(language, language_instructions["en"])
    
    context_str = f"\n**Additional Context:** {context}" if context else ""

    return f"""Explain the technical concept: "{concept}"

**Student Level:** {user_level}{context_str}

**Language Instructions:**
{lang_instruction}

**Response Format (JSON):**
{{
    "concept": "{concept}",
    "language": "{language}",
    "explanation": {{
        "simple_definition": "One sentence simple definition",
        "detailed_explanation": "Full explanation in requested language - use analogies",
        "real_world_analogy": "Relatable Indian analogy (cricket, chai, traffic, family, Bollywood)",
        "why_it_matters": "Why this is important for placements - mention specific companies if relevant"
    }},
    {"" if not examples_requested else '"code_examples": [' + '\n        {' + '\n            "language": "python|java|cpp",\n            "code": "code snippet with comments",\n            "explanation": "line by line explanation in requested language"\n        }\n    ],' + ''}
    "key_points": ["point 1", "point 2", "point 3"],
    "common_mistakes": ["mistake 1", "mistake 2"],
    "interview_questions": [
        {{
            "question": "common interview question on this topic",
            "difficulty": "easy|medium|hard",
            "company_asked": "company name or common",
            "frequency": "frequently|sometimes|rarely"
        }}
    ],
    "further_learning": [
        {{
            "resource": "resource name",
            "type": "video|article|practice",
            "url": "if available",
            "language": "en|hi|ta|te",
            "free": true|false
        }}
    ],
    "related_concepts": ["related concept 1", "related concept 2"],
    "practice_problems": [
        {{
            "platform": "LeetCode|GFG|HackerRank",
            "problem_name": "problem title",
            "difficulty": "easy|medium|hard",
            "url": "if available"
        }}
    ]
}}

Make the explanation engaging and easy to understand. Use examples that Indian students can relate to.
For Tier-2/3 students: Be extra clear with fundamentals, don't assume prior knowledge.
Always include at least one practice problem recommendation."""


# ═══════════════════════════════════════════════════════════════════════════════
# RESUME TIPS PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_resume_tips_prompt(
    resume_content: dict,
    target_companies: list,
    college_tier: str
) -> str:
    """Generate prompt for resume improvement tips."""
    
    companies_str = ", ".join(target_companies) if target_companies else "campus recruitment companies"
    
    # Extract resume sections
    education = resume_content.get("education", {})
    skills = resume_content.get("skills", [])
    projects = resume_content.get("projects", [])
    experience = resume_content.get("experience", [])
    certifications = resume_content.get("certifications", [])
    
    resume_summary = f"""
**Education:**
{education}

**Skills:**
{skills}

**Projects:**
{projects}

**Experience:**
{experience}

**Certifications:**
{certifications}
"""

    # Tier-specific advice
    tier_advice = {
        "tier1": """
Tier 1 Specific:
- Can focus on technical depth and competitive programming achievements
- Emphasize internships, research, and project complexity
- Brand name college helps - focus on accomplishments""",
        "tier2": """
Tier 2 Specific:
- Balance technical skills with practical projects
- Highlight any competitive programming or hackathon participation
- Show continuous learning through certifications
- Emphasize relevant coursework and self-driven projects""",
        "tier3": """
Tier 3 Specific:
- Focus heavily on skills and projects to compensate for college brand
- Include self-learning initiatives (online courses, certifications)
- Highlight any internships, even unpaid or short-term
- Show proof of skills through project links/GitHub
- Consider including relevant coursework with good grades
- Mention any leadership roles or extracurriculars showing initiative"""
    }.get(college_tier, "")

    return f"""Review and provide improvement tips for this resume targeting {companies_str}.

**Student Profile:**
- College Tier: {college_tier}
- Target Companies: {companies_str}{tier_advice}

**Resume Content:**
{resume_summary}

**Provide analysis as JSON:**
{{
    "overall_score": <0-100>,
    "ats_friendly": true|false,
    "sections": {{
        "education": {{
            "score": <0-100>,
            "feedback": "specific feedback",
            "suggestions": ["suggestion 1", "suggestion 2"]
        }},
        "skills": {{
            "score": <0-100>,
            "feedback": "specific feedback",
            "suggestions": ["suggestion 1", "suggestion 2"],
            "missing_skills": ["skills to add based on target companies"],
            "priority_order": ["suggested order for skills section"]
        }},
        "projects": {{
            "score": <0-100>,
            "feedback": "specific feedback",
            "suggestions": ["suggestion 1", "suggestion 2"],
            "star_format_issues": ["issues with Situation-Task-Action-Result format"],
            "impact_metrics_missing": ["suggestions for adding metrics"]
        }},
        "experience": {{
            "score": <0-100>,
            "feedback": "specific feedback",
            "suggestions": ["suggestion 1", "suggestion 2"]
        }}
    }},
    "formatting_issues": ["issue 1", "issue 2"],
    "common_mistakes": ["mistake 1", "mistake 2"],
    "company_specific_tips": [
        {{
            "company": "company name",
            "tips": ["specific tip 1", "specific tip 2"],
            "keywords_to_include": ["keyword 1", "keyword 2"]
        }}
    ],
    "improved_bullet_points": [
        {{
            "original": "original bullet",
            "improved": "improved version using STAR method with metrics",
            "reason": "why this is better"
        }}
    ],
    "action_items": [
        {{
            "priority": "high|medium|low",
            "action": "what to do",
            "impact": "expected impact",
            "time_estimate": "how long it takes"
        }}
    ],
    "sample_summary": "A sample professional summary tailored to their profile",
    "tier_specific_advice": "Advice specific to Tier-{college_tier} students",
    "ats_optimization": {{
        "current_issues": ["issue 1"],
        "suggestions": ["suggestion 1"]
    }}
}}

Consider:
- ATS (Applicant Tracking System) compatibility - avoid tables, images, fancy formatting
- STAR method for project descriptions
- Relevance to target companies
- Common mistakes Indian students make (including photo, father's name, personal details)
- How to highlight strengths despite limited brand-name college/experience
- Specific keywords that {companies_str} look for
- 1-page limit for freshers is strongly recommended
- Include GitHub/LinkedIn links if they add value"""


def get_resume_section_improvement_prompt(section: str, content: str, target_role: str) -> str:
    """Generate prompt for improving a specific resume section."""
    
    section_guidance = {
        "summary": "Focus on creating a compelling professional summary - 2-3 lines max",
        "skills": "Organize and prioritize technical skills - most relevant first",
        "projects": "Use STAR method to describe projects with impact metrics and quantifiable results",
        "experience": "Highlight achievements, not just responsibilities - use action verbs",
        "education": "Present academic credentials effectively - include CGPA if above 7.5",
        "certifications": "Showcase relevant certifications with context - prefer recognized platforms"
    }
    
    return f"""Improve this resume section: {section}

**Target Role:** {target_role}

**Current Content:**
{content}

**Guidance:** {section_guidance.get(section, "Improve this section")}

**Provide improved version as JSON:**
{{
    "section": "{section}",
    "improved_content": "the improved text",
    "improvements_made": ["what was improved"],
    "keywords_added": ["important keywords included"],
    "tips_for_future": ["tips for maintaining this section"],
    "common_mistakes_to_avoid": ["mistake 1", "mistake 2"]
}}"""


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE RECOMMENDATION PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_resource_recommendations_prompt(
    topic: str,
    user_level: str,
    target_company: str | None,
    content_type: str = "all",
    preferred_language: str = "en"
) -> str:
    """Generate prompt for curating learning resources."""
    
    company_focus = ""
    if target_company:
        company_lower = target_company.lower()
        if any(x in company_lower for x in ["tcs", "infosys", "wipro", "cognizant"]):
            company_focus = """
Service Company Focus:
- Focus on resources for service company preparation: aptitude, basic programming, DBMS, communication
- Recommended platforms: IndiaBIX (aptitude), GeeksforGeeks (basics), YouTube (Hindi explanations)
- Look for: Previous year papers, mock tests, company-specific preparation guides"""
        elif any(x in company_lower for x in ["amazon", "microsoft", "google", "flipkart"]):
            company_focus = """
Product Company Focus:
- Focus on resources for product company preparation: advanced DSA, system design, competitive programming
- Recommended platforms: LeetCode, Codeforces, CodeChef, InterviewBit
- Look for: Top interview questions, company-tagged problems, discussion forums"""
    
    language_preference = ""
    if preferred_language == "hi":
        language_preference = """
Language Preference - Hindi:
- Prioritize Hindi-language resources:
  - CodeWithHarry (YouTube) - comprehensive programming in Hindi
  - Apna College (YouTube) - DSA and placement prep in Hindi
  - Anuj Bhaiya (YouTube) - system design and backend in Hindi
  - Hindi programming communities and forums"""
    elif preferred_language == "ta":
        language_preference = """
Language Preference - Tamil:
- Include Tamil-language resources:
  - Tamil Code (YouTube)
  - Guvi (has Tamil content)
  - Tamil programming communities
  - Mixed resources if pure Tamil not available"""
    elif preferred_language == "te":
        language_preference = """
Language Preference - Telugu:
- Include Telugu-language resources:
  - Telugu programming YouTube channels
  - Local coaching institute materials
  - Mixed resources if pure Telugu not available"""

    return f"""Recommend curated learning resources for: {topic}

**User Level:** {user_level}
**Target Company:** {target_company or "General placement preparation"}
**Content Type:** {content_type} (video, article, practice, all)
{company_focus}
{language_preference}

**Provide recommendations as JSON:**
{{
    "topic": "{topic}",
    "resources": [
        {{
            "title": "resource name",
            "type": "video|article|course|practice_platform",
            "platform": "YouTube|Coursera|GeeksforGeeks|LeetCode|HackerRank|CodingNinjas|etc",
            "url": "if known",
            "creator": "creator name",
            "language": "en|hi|ta|te",
            "level": "beginner|intermediate|advanced",
            "free": true|false,
            "description": "what this resource covers",
            "best_for": "what specific aspect it helps with",
            "duration": "estimated time to complete",
            "rating": "popularity/relevance rating"
        }}
    ],
    "learning_path": [
        {{
            "step": 1,
            "resource_title": "which resource to do first",
            "focus": "what to learn from it",
            "estimated_time": "time to complete"
        }}
    ],
    "pro_tips": [
        "practical tip for using these resources effectively",
        "common mistakes to avoid"
    ],
    "company_specific_resources": [
        {{
            "company": "company name",
            "resources": ["specific resource for this company"]
        }}
    ]
}}

Include a mix of:
- Free resources (priority for Indian students)
- YouTube channels popular in India (CodeWithHarry, Apna College, Striver, NeetCode, Anuj Bhaiya)
- Practice platforms (LeetCode, GeeksforGeeks, HackerRank, InterviewBit, CodeChef)
- Structured courses if relevant (free ones preferred)
- Company-specific preparation materials
- Regional language resources as per preference"""


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSLATION PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_roadmap_translation_prompt(roadmap_content: dict, target_language: str) -> str:
    """Generate prompt for translating roadmap content."""
    
    language_names = {"hi": "Hindi", "ta": "Tamil", "te": "Telugu", "en": "English"}
    lang_name = language_names.get(target_language, target_language)
    
    # Language-specific style guide
    style_guide = {
        "hi": """
Hinglish Style Guide:
- Use Devanagari script for Hindi parts
- Keep technical terms in English: array, function, loop, pointer, recursion
- Example: "Is week mein aap Arrays aur Strings ke concepts seekhenge."
- Keep resource names in English (YouTube, LeetCode, etc.)
- Use conversational, friendly tone""",
        "ta": """
Tanglish Style Guide:
- Use Roman script for Tamil parts
- Keep technical terms in English
- Example: "Indha week-la Arrays and Strings concepts learn pannuveenga."
- Keep resource names in English
- Use friendly, encouraging tone""",
        "te": """
Telgish Style Guide:
- Use Roman script for Telugu parts
- Keep technical terms in English
- Example: "Ee week lo Arrays mariyu Strings concepts nerchukuntaru."
- Keep resource names in English
- Use clear, instructional tone"""
    }.get(target_language, "Translate naturally while keeping technical terms in English.")

    return f"""Translate the following roadmap content to {lang_name}.

**Style Guide:**
{style_guide}

**Roadmap Content:**
{roadmap_content}

**Translation Guidelines:**
- Keep technical terms in English (DSA, Array, LinkedList, Function, Class, etc.)
- Translate descriptions, instructions, and explanations
- Maintain the JSON structure exactly
- Use Hinglish/Tanglish/Telgish style (simple regional language + English technical terms)
- Ensure the tone remains encouraging and professional
- Keep resource names and URLs in English
- Preserve task IDs and structure
- Translate duration descriptions but keep numbers

**Output the translated roadmap in the same JSON structure.**"""


def get_tasks_translation_prompt(tasks: list, target_language: str) -> str:
    """Generate prompt for translating daily tasks."""
    
    language_names = {"hi": "Hindi", "ta": "Tamil", "te": "Telugu", "en": "English"}
    lang_name = language_names.get(target_language, target_language)
    
    style_guide = {
        "hi": "Use Hinglish (Hindi in Devanagari + English technical terms). Example: 'Array traversal technique practice karein.'",
        "ta": "Use Tanglish (Tamil in Roman script + English technical terms). Example: 'Array traversal technique practice pannungal.'",
        "te": "Use Telgish (Telugu in Roman script + English technical terms). Example: 'Array traversal technique practice cheyandi.'"
    }.get(target_language, "Keep technical terms in English.")

    return f"""Translate the following daily tasks to {lang_name}.

**Style Guide:**
{style_guide}

**Tasks:**
{tasks}

**Translation Guidelines:**
- Keep technical terms in English: array, function, loop, pointer, recursion, API, database, etc.
- Translate titles, descriptions, and instructions
- Maintain task structure and IDs
- Use simple, clear language appropriate for students
- Keep resource names and URLs in English
- Preserve task types (video, read, practice, project)
- Translate time estimates but keep numbers (e.g., "30 minutes" -> "30 minutes" in target language)

**Output the translated tasks in the same JSON structure.**"""


# ═══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL UTILITY PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_placement_strategy_prompt(
    college_tier: str,
    target_companies: list,
    current_skills: dict,
    months_until_placement: int
) -> str:
    """Generate prompt for personalized placement preparation strategy."""
    
    companies_str = ", ".join(target_companies) if target_companies else "various companies"
    
    tier_strategy = {
        "tier1": """
Tier 1 Strategy:
- Focus: Product companies and high-paying roles
- Key areas: Advanced DSA, system design, competitive programming
- Timeline: Intensive preparation starting 6+ months before
- Off-campus: Apply through referrals, career portals, campus connections""",
        "tier2": """
Tier 2 Strategy:
- Focus: Mixed approach - secure service company offer first, prepare for off-campus product roles
- Key areas: Solid DSA fundamentals, aptitude, CS subjects, communication
- Timeline: 4-6 months preparation
- Off-campus: Aggressive LinkedIn networking, apply broadly""",
        "tier3": """
Tier 3 Strategy:
- Focus: Clear on-campus service company tests first, then serious off-campus preparation
- Key areas: Aptitude (heavy focus), basic programming, CS fundamentals, spoken English
- Timeline: Start 6+ months before, consistent daily effort
- Off-campus: Build strong portfolio, active LinkedIn presence, referrals crucial"""
    }.get(college_tier, "")

    return f"""Create a personalized placement preparation strategy for a Tier-{college_tier} college student.

**Student Profile:**
- College Tier: {college_tier}
- Target Companies: {companies_str}
- Current Skills: {current_skills}
- Months Until Placement: {months_until_placement}

**Tier-Specific Context:**
{tier_strategy}

**Provide strategy as JSON:**
{{
    "overall_strategy": "Summary of approach",
    "timeline": {{
        "months": {months_until_placement},
        "phases": [
            {{
                "phase": "Phase name",
                "duration_weeks": 4,
                "focus_areas": ["area 1", "area 2"],
                "daily_schedule": "suggested daily routine",
                "milestones": ["milestone 1"]
            }}
        ]
    }},
    "company_specific_prep": {{
        "service_companies": {{
            "focus": "what to focus on",
            "resources": ["resource 1"]
        }},
        "product_companies": {{
            "focus": "what to focus on",
            "resources": ["resource 1"]
        }}
    }},
    "off_campus_strategy": {{
        "linkedln_optimization": ["tips"],
        "application_strategy": "how to apply",
        "referral_approach": "how to get referrals",
        "portfolio_building": ["what to include"]
    }},
    "daily_routine": {{
        "weekdays": "suggested schedule",
        "weekends": "suggested schedule"
    }},
    "weekly_goals": [
        {{
            "week": 1,
            "focus": "what to achieve",
            "measurable_target": "quantifiable goal"
        }}
    ],
    "success_metrics": ["how to track progress"],
    "contingency_plan": "what to do if plan doesn't work"
}}

Make the strategy realistic and actionable. Consider typical Tier-{college_tier} college constraints and opportunities."""


def get_daily_motivation_prompt(
    student_name: str,
    streak_days: int,
    progress_stats: dict,
    college_tier: str
) -> str:
    """Generate prompt for daily motivation message."""
    
    tier_messages = {
        "tier1": "You're competing at the highest level. Your consistency sets you apart.",
        "tier2": "Your college doesn't define your potential. Your effort does.",
        "tier3": "Many top engineers came from Tier-3 colleges. You're writing your own success story."
    }
    
    return f"""Generate a motivational message for {student_name} who is preparing for campus placements.

**Progress Stats:**
- Streak: {streak_days} days
- Progress: {progress_stats}
- College Tier: {college_tier}

**Context:**
{tier_messages.get(college_tier, "Keep pushing forward!")}

**Provide motivation as JSON:**
{{
    "greeting": "Personalized greeting",
    "achievement_highlight": "What they've accomplished",
    "motivational_message": "Encouraging message for today",
    "focus_for_today": "What to focus on today",
    "inspiration_quote": "Relevant quote (Indian context if possible)",
    "reminder": "Important reminder about their goals",
    "closing": "Encouraging closing"
}}

Keep it warm, personal, and culturally relevant for Indian students."""

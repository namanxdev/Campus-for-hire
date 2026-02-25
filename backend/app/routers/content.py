from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Roadmap
from app.schemas import (
    ExplainRequest,
    ExplainResponse,
    ResourcesRequest,
    ResourcesResponse,
    ResourceItem,
    TranslateRoadmapRequest,
    TranslateRoadmapResponse,
)
from app.services.bedrock import bedrock_service
from app.services.translate import translate_service

router = APIRouter(prefix="/api/content", tags=["content"])

# Curated resources database
CURATED_RESOURCES = {
    "python": [
        ResourceItem(
            title="Python for Beginners - Microsoft",
            type="video",
            url="https://www.youtube.com/watch?v=jFCsrlq4jTg",
            description="Comprehensive Python tutorial for beginners",
            difficulty="beginner",
            estimated_time="4 hours",
        ),
        ResourceItem(
            title="Python Official Documentation",
            type="article",
            url="https://docs.python.org/3/tutorial/",
            description="Official Python tutorial and documentation",
            difficulty="beginner",
            estimated_time="Self-paced",
        ),
        ResourceItem(
            title="Real Python Tutorials",
            type="article",
            url="https://realpython.com/",
            description="High-quality Python tutorials and articles",
            difficulty="intermediate",
            estimated_time="Varies",
        ),
    ],
    "java": [
        ResourceItem(
            title="Java Programming - Telusko",
            type="video",
            url="https://www.youtube.com/playlist?list=PLsyeobzWxl7pe_IiTFNea6wEpVDzV2D9X",
            description="Complete Java programming playlist",
            difficulty="beginner",
            estimated_time="20 hours",
        ),
        ResourceItem(
            title="Java Documentation",
            type="article",
            url="https://docs.oracle.com/en/java/",
            description="Official Oracle Java documentation",
            difficulty="intermediate",
            estimated_time="Self-paced",
        ),
    ],
    "dsa": [
        ResourceItem(
            title="Data Structures - mycodeschool",
            type="video",
            url="https://www.youtube.com/playlist?list=PL2_aWCzGMAwI3W_JlcBbtYTwiQSsOTa6P",
            description="Comprehensive DSA playlist",
            difficulty="beginner",
            estimated_time="15 hours",
        ),
        ResourceItem(
            title="GeeksforGeeks DSA",
            type="article",
            url="https://www.geeksforgeeks.org/data-structures/",
            description="Complete DSA tutorial and practice problems",
            difficulty="intermediate",
            estimated_time="Self-paced",
        ),
        ResourceItem(
            title="LeetCode Problems",
            type="practice",
            url="https://leetcode.com/problemset/all/",
            description="Practice coding problems",
            difficulty="advanced",
            estimated_time="Unlimited",
        ),
    ],
    "system design": [
        ResourceItem(
            title="System Design Primer",
            type="article",
            url="https://github.com/donnemartin/system-design-primer",
            description="Learn how to design large-scale systems",
            difficulty="advanced",
            estimated_time="40 hours",
        ),
        ResourceItem(
            title="System Design Interview",
            type="video",
            url="https://www.youtube.com/channel/UC9vLsnF6QKld-9j4fjppCCQ",
            description="System design interview preparation",
            difficulty="advanced",
            estimated_time="20 hours",
        ),
    ],
    "sql": [
        ResourceItem(
            title="SQL Tutorial - W3Schools",
            type="article",
            url="https://www.w3schools.com/sql/",
            description="Interactive SQL tutorial",
            difficulty="beginner",
            estimated_time="8 hours",
        ),
        ResourceItem(
            title="SQLZoo",
            type="practice",
            url="https://sqlzoo.net/",
            description="Interactive SQL practice",
            difficulty="beginner",
            estimated_time="6 hours",
        ),
    ],
    "react": [
        ResourceItem(
            title="React Documentation",
            type="article",
            url="https://react.dev/learn",
            description="Official React learning path",
            difficulty="intermediate",
            estimated_time="10 hours",
        ),
        ResourceItem(
            title="React Tutorial - Codevolution",
            type="video",
            url="https://www.youtube.com/playlist?list=PLC3y8-rFHvwgg3vaYJgHGnModB54rxOk3",
            description="Complete React tutorial series",
            difficulty="intermediate",
            estimated_time="12 hours",
        ),
    ],
    "javascript": [
        ResourceItem(
            title="JavaScript.info",
            type="article",
            url="https://javascript.info/",
            description="The Modern JavaScript Tutorial",
            difficulty="beginner",
            estimated_time="20 hours",
        ),
        ResourceItem(
            title="JavaScript - Traversy Media",
            type="video",
            url="https://www.youtube.com/watch?v=hdI2bqOjy3c",
            description="Crash course for beginners",
            difficulty="beginner",
            estimated_time="1 hour",
        ),
    ],
    "machine learning": [
        ResourceItem(
            title="Machine Learning - Andrew Ng",
            type="video",
            url="https://www.coursera.org/learn/machine-learning",
            description="Stanford's famous ML course",
            difficulty="intermediate",
            estimated_time="60 hours",
        ),
        ResourceItem(
            title="Fast.ai Practical Deep Learning",
            type="video",
            url="https://course.fast.ai/",
            description="Practical deep learning for coders",
            difficulty="intermediate",
            estimated_time="40 hours",
        ),
    ],
}

# AI Explanation System Prompt
EXPLAIN_SYSTEM_PROMPT = """You are an expert computer science educator specializing in explaining technical concepts to Indian college students preparing for campus placements.

Your explanations should be:
- Clear and concise
- Appropriate for the student's level
- Include practical examples relevant to placements
- Focus on what interviewers typically ask

Respond in a structured format with clear sections."""


def _get_explain_prompt(concept: str, context: str | None, difficulty_level: str) -> str:
    context_str = f"\nContext: {context}" if context else ""
    
    return f"""Explain the concept: "{concept}"{context_str}

Target audience: Indian college student preparing for campus placements
Difficulty level: {difficulty_level}

Please provide:
1. A clear, simple definition (2-3 sentences)
2. 2-3 practical examples with code snippets where applicable
3. 4-5 key points to remember
4. 3-4 related topics they should learn next
5. Common interview questions on this topic (if applicable)

Format your response as structured text with clear headings."""


@router.post("/explain", response_model=ExplainResponse)
def explain_concept(
    body: ExplainRequest,
    current_user: User = Depends(get_current_user),
):
    """Get an AI-generated explanation of a technical concept."""
    try:
        raw_response = bedrock_service.invoke_model(
            EXPLAIN_SYSTEM_PROMPT,
            _get_explain_prompt(body.concept, body.context, body.difficulty_level or "beginner"),
            max_tokens=2048,
        )
        
        # Parse the response to extract structured content
        lines = raw_response.split("\n")
        
        explanation = ""
        examples = []
        key_points = []
        related_topics = []
        
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in ["definition", "what is", "introduction"]):
                if current_section and current_content:
                    if current_section == "examples":
                        examples = current_content
                    elif current_section == "key points":
                        key_points = current_content
                    elif current_section == "related topics":
                        related_topics = current_content
                current_section = "explanation"
                current_content = []
            elif any(keyword in line_lower for keyword in ["example", "code"]):
                if current_section and current_content:
                    if current_section == "explanation":
                        explanation = "\n".join(current_content)
                current_section = "examples"
                current_content = []
            elif any(keyword in line_lower for keyword in ["key point", "remember", "important"]):
                if current_section and current_content:
                    if current_section == "examples":
                        examples = current_content
                current_section = "key_points"
                current_content = []
            elif any(keyword in line_lower for keyword in ["related topic", "learn next", "next topic"]):
                if current_section and current_content:
                    if current_section == "key_points":
                        key_points = current_content
                current_section = "related_topics"
                current_content = []
            elif line.strip():
                current_content.append(line.strip())
        
        # Handle remaining content
        if current_section == "explanation":
            explanation = "\n".join(current_content)
        elif current_section == "examples":
            examples = current_content
        elif current_section == "key_points":
            key_points = current_content
        elif current_section == "related_topics":
            related_topics = current_content
        
        # Fallback if parsing didn't work well
        if not explanation:
            explanation = raw_response[:500]
        if not examples:
            examples = ["See the detailed explanation above."]
        if not key_points:
            key_points = ["Practice this concept with coding problems."]
        if not related_topics:
            related_topics = ["Data Structures", "Algorithms"]
        
        return ExplainResponse(
            explanation=explanation,
            examples=examples[:3],
            key_points=key_points[:5],
            related_topics=related_topics[:4],
        )
        
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate explanation: {exc}",
        ) from exc


@router.get("/resources", response_model=ResourcesResponse)
def get_resources(
    topic: str,
    skill_level: str = "intermediate",
    resource_type: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """Get curated learning resources for a topic."""
    topic_lower = topic.lower()
    
    # Find matching resources
    matched_resources = []
    
    for key, resources in CURATED_RESOURCES.items():
        if key in topic_lower or topic_lower in key:
            matched_resources.extend(resources)
    
    # Filter by skill level if specified
    if skill_level != "all":
        level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        target_level = level_order.get(skill_level, 1)
        
        matched_resources = [
            r for r in matched_resources
            if abs(level_order.get(r.difficulty, 1) - target_level) <= 1
        ]
    
    # Filter by resource type if specified
    if resource_type:
        matched_resources = [
            r for r in matched_resources
            if r.type == resource_type
        ]
    
    # If no curated resources found, generate generic suggestions
    if not matched_resources:
        matched_resources = [
            ResourceItem(
                title=f"Learn {topic.title()}",
                type="article",
                url=f"https://www.google.com/search?q={topic.replace(' ', '+')}+tutorial",
                description=f"Search for {topic} tutorials and resources",
                difficulty=skill_level,
                estimated_time="Varies",
            ),
            ResourceItem(
                title=f"{topic.title()} Documentation",
                type="article",
                description=f"Official documentation for {topic}",
                difficulty="intermediate",
                estimated_time="Self-paced",
            ),
            ResourceItem(
                title=f"Practice {topic.title()}",
                type="practice",
                description=f"Hands-on exercises for {topic}",
                difficulty=skill_level,
                estimated_time="Varies",
            ),
        ]
    
    return ResourcesResponse(
        topic=topic,
        resources=matched_resources[:10],
    )


@router.post("/translate-roadmap", response_model=TranslateRoadmapResponse)
def translate_roadmap(
    body: TranslateRoadmapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Translate roadmap content to a target language."""
    # Get the roadmap
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.id == body.roadmap_id, Roadmap.user_id == current_user.id)
        .first()
    )
    
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    if not roadmap.content:
        raise HTTPException(status_code=400, detail="Roadmap has no content to translate")
    
    try:
        # Helper function to translate text fields
        def translate_text_field(text: str) -> str:
            if not text or not isinstance(text, str):
                return text
            try:
                result = translate_service.translate_text(text, body.target_language)
                return result.get("translated_text", text)
            except Exception:
                return text
        
        # Deep copy and translate content
        import copy
        translated_content = copy.deepcopy(roadmap.content)
        
        # Translate title
        if "title" in translated_content:
            translated_content["title"] = translate_text_field(translated_content["title"])
        
        # Translate weeks
        if "weeks" in translated_content:
            for week in translated_content["weeks"]:
                if "theme" in week:
                    week["theme"] = translate_text_field(week["theme"])
                
                # Translate objectives
                if "objectives" in week:
                    week["objectives"] = [
                        translate_text_field(obj) for obj in week["objectives"]
                    ]
                
                # Translate days
                if "days" in week:
                    for day in week["days"]:
                        if "title" in day:
                            day["title"] = translate_text_field(day["title"])
                        
                        # Translate tasks
                        if "tasks" in day:
                            for task in day["tasks"]:
                                if "title" in task:
                                    task["title"] = translate_text_field(task["title"])
                                if "description" in task:
                                    task["description"] = translate_text_field(task["description"])
                                if "resources" in task:
                                    task["resources"] = [
                                        translate_text_field(res) for res in task["resources"]
                                    ]
        
        return TranslateRoadmapResponse(
            roadmap_id=roadmap.id,
            translated_content=translated_content,
            target_language=body.target_language,
        )
        
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to translate roadmap: {exc}",
        ) from exc

"""
Content Service for educational content operations.
Handles concept explanations, resource recommendations, and translations.
"""

import json
import logging
from typing import AsyncGenerator

from app.services.bedrock import BedrockService, bedrock_service
from app.services.prompts import (
    get_content_explanation_prompt,
    get_resource_recommendations_prompt,
    get_roadmap_translation_prompt,
    get_tasks_translation_prompt,
    CONTENT_EXPLANATION_SYSTEM_PROMPT,
)
from app.services.translate import translate_service

logger = logging.getLogger(__name__)


class ContentService:
    """Service for handling educational content and translations."""
    
    # Language codes supported
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu"
    }
    
    # Language codes for Amazon Translate
    TRANSLATE_LANGUAGE_CODES = {
        "en": "en",
        "hi": "hi",
        "ta": "ta",
        "te": "te"
    }
    
    # Language-specific greetings and messages
    LANGUAGE_MESSAGES = {
        "en": {
            "error_explanation": "We couldn't generate an explanation at this time. Please try again or check the resources below.",
            "error_resources": "Resource recommendations are temporarily unavailable. Please try popular platforms like GeeksforGeeks or YouTube.",
            "error_translation": "Translation service is temporarily unavailable. Please try again later.",
        },
        "hi": {
            "error_explanation": "Humein abhi explanation generate nahi kar pa rahe hain. Kripya baad mein try karein ya neeche diye resources check karein.",
            "error_resources": "Resource recommendations abhi available nahi hain. Kripya GeeksforGeeks ya YouTube check karein.",
            "error_translation": "Translation service abhi available nahi hai. Kripya baad mein try karein.",
        },
        "ta": {
            "error_explanation": "Explanation generate panna mudiyala. Pozhuthu poruttu try pannunga illai keel irukka resources check pannunga.",
            "error_resources": "Resource recommendations temporary-a unavailable. GeeksforGeeks illai YouTube check pannunga.",
            "error_translation": "Translation service temporary-a unavailable. Pozhuthu poruttu try pannunga.",
        },
        "te": {
            "error_explanation": "Explanation generate cheyalekapothunnam. Tharuvatha try cheyandi leka kindi resources chudandi.",
            "error_resources": "Resource recommendations temporary ga available kavu. GeeksforGeeks leda YouTube chudandi.",
            "error_translation": "Translation service temporary ga available kadu. Tharuvatha try cheyandi.",
        }
    }
    
    def __init__(self, bedrock_service: BedrockService = None) -> None:
        self._bedrock = bedrock_service or BedrockService()
    
    def _is_language_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return language in self.SUPPORTED_LANGUAGES
    
    def _get_translate_code(self, language: str) -> str:
        """Get the Amazon Translate language code."""
        return self.TRANSLATE_LANGUAGE_CODES.get(language, "en")
    
    def _get_language_message(self, language: str, message_type: str) -> str:
        """Get a language-specific message."""
        lang_messages = self.LANGUAGE_MESSAGES.get(language, self.LANGUAGE_MESSAGES["en"])
        return lang_messages.get(message_type, self.LANGUAGE_MESSAGES["en"][message_type])
    
    async def explain_concept(
        self,
        concept: str,
        language: str = "en",
        user_level: str = "intermediate",
        context: str | None = None,
        include_examples: bool = True
    ) -> dict:
        """
        Explain a technical concept in the user's preferred language.
        
        Args:
            concept: The technical concept to explain
            language: Target language code (en, hi, ta, te)
            user_level: User's proficiency level (beginner, intermediate, advanced)
            context: Additional context about where/how the concept is used
            include_examples: Whether to include code examples
            
        Returns:
            Structured explanation with analogies, examples, and resources
        """
        # Normalize and validate language
        original_language = language
        if not self._is_language_supported(language):
            logger.warning(f"Language {language} not supported, falling back to English")
            language = "en"
        
        try:
            prompt = get_content_explanation_prompt(
                concept=concept,
                language=language,
                user_level=user_level,
                context=context,
                examples_requested=include_examples
            )
            
            response = self._bedrock.invoke_model(
                system_prompt=CONTENT_EXPLANATION_SYSTEM_PROMPT,
                user_prompt=prompt,
                max_tokens=4096,
                temperature=0.7,
                fallback_type="explanation"
            )
            
            # Parse the JSON response
            result = self._bedrock.parse_json_response(response)
            
            # Validate the response structure
            if "explanation" not in result:
                logger.warning(f"Invalid explanation response structure for {concept}")
                # Try to construct a valid response
                result = {
                    "concept": concept,
                    "language": language,
                    "explanation": {
                        "simple_definition": result.get("simple_definition", ""),
                        "detailed_explanation": result.get("detailed_explanation", ""),
                        "real_world_analogy": result.get("real_world_analogy", ""),
                        "why_it_matters": result.get("why_it_matters", "")
                    },
                    **{k: v for k, v in result.items() if k not in ["simple_definition", "detailed_explanation"]}
                }
            
            # Add metadata
            result["_meta"] = {
                "requested_language": original_language,
                "response_language": language,
                "user_level": user_level,
                "fallback_used": result.get("fallback", False)
            }
            
            logger.info(f"Successfully explained concept: {concept} in {language}")
            return result
            
        except Exception as exc:
            logger.error(f"Failed to explain concept '{concept}': {exc}")
            return self._get_fallback_explanation(concept, language)
    
    async def explain_concept_streaming(
        self,
        concept: str,
        language: str = "en",
        user_level: str = "intermediate"
    ) -> AsyncGenerator[str, None]:
        """
        Stream an explanation of a technical concept.
        
        Args:
            concept: The technical concept to explain
            language: Target language code
            user_level: User's proficiency level
            
        Yields:
            Chunks of the explanation as they're generated
        """
        result = await self.explain_concept(concept, language, user_level)
        
        # Yield sections one by one for better UX
        if "explanation" in result:
            explanation = result["explanation"]
            for key, value in explanation.items():
                yield json.dumps({key: value}) + "\n"
        
        if "key_points" in result:
            yield json.dumps({"key_points": result["key_points"]}) + "\n"
        
        if "code_examples" in result:
            yield json.dumps({"code_examples": result["code_examples"]}) + "\n"
        
        if "practice_problems" in result:
            yield json.dumps({"practice_problems": result["practice_problems"]}) + "\n"
    
    async def get_resource_recommendations(
        self,
        topic: str,
        user_level: str = "intermediate",
        target_company: str | None = None,
        content_type: str = "all",
        preferred_language: str = "en"
    ) -> dict:
        """
        Get curated learning resources for a topic.
        
        Args:
            topic: The learning topic
            user_level: User's proficiency level
            target_company: Target company for company-specific resources
            content_type: Type of content (video, article, practice, all)
            preferred_language: Preferred language for resources
            
        Returns:
            Curated list of resources with metadata
        """
        try:
            prompt = get_resource_recommendations_prompt(
                topic=topic,
                user_level=user_level,
                target_company=target_company,
                content_type=content_type,
                preferred_language=preferred_language
            )
            
            response = self._bedrock.invoke_model(
                system_prompt="You are an expert curator of learning resources for Indian students. Provide specific, actionable recommendations with real platforms and creators.",
                user_prompt=prompt,
                max_tokens=4096,
                temperature=0.7,
                fallback_type="resource_recommendations"
            )
            
            result = self._bedrock.parse_json_response(response)
            
            # Validate response
            if "resources" not in result:
                logger.warning(f"Invalid resource recommendation response for {topic}")
                result = {"resources": [], **result}
            
            # Add metadata
            result["_meta"] = {
                "topic": topic,
                "user_level": user_level,
                "target_company": target_company,
                "preferred_language": preferred_language,
                "fallback_used": result.get("fallback", False)
            }
            
            logger.info(f"Generated {len(result.get('resources', []))} resource recommendations for {topic}")
            return result
            
        except Exception as exc:
            logger.error(f"Failed to get resource recommendations for '{topic}': {exc}")
            return self._get_fallback_resources(topic, user_level, preferred_language)
    
    async def translate_roadmap(
        self,
        roadmap_content: dict,
        target_language: str
    ) -> dict:
        """
        Translate roadmap content to the target language.
        Uses AI for nuanced translation of educational content.
        
        Args:
            roadmap_content: The roadmap content to translate
            target_language: Target language code (hi, ta, te)
            
        Returns:
            Translated roadmap content
        """
        if target_language == "en":
            return {
                **roadmap_content,
                "_meta": {"translated": False, "target_language": "en"}
            }
        
        if not self._is_language_supported(target_language):
            logger.warning(f"Language {target_language} not supported for translation")
            return {
                **roadmap_content,
                "_meta": {"translated": False, "error": "Unsupported language"}
            }
        
        try:
            # For complex educational content, use AI-based translation
            prompt = get_roadmap_translation_prompt(roadmap_content, target_language)
            
            response = self._bedrock.invoke_model(
                system_prompt="You are an expert translator specializing in educational content for Indian students. Keep technical terms in English.",
                user_prompt=prompt,
                max_tokens=4096,
                temperature=0.3,  # Lower temperature for more consistent translation
                fallback_type="translation"
            )
            
            result = self._bedrock.parse_json_response(response)
            
            # Add translation metadata
            result["_meta"] = {
                "translated": True,
                "source_language": "en",
                "target_language": target_language,
                "method": "ai_translation",
                "fallback_used": result.get("fallback", False)
            }
            
            logger.info(f"Successfully translated roadmap to {target_language}")
            return result
            
        except Exception as exc:
            logger.error(f"AI translation failed, falling back to Amazon Translate: {exc}")
            # Fallback to Amazon Translate for simpler content
            translated = await self._translate_with_amazon_translate(roadmap_content, target_language)
            return {
                **translated,
                "_meta": {
                    "translated": True,
                    "source_language": "en",
                    "target_language": target_language,
                    "method": "amazon_translate",
                    "fallback": True
                }
            }
    
    async def translate_tasks(
        self,
        tasks: list,
        target_language: str
    ) -> list:
        """
        Translate daily tasks to the target language.
        
        Args:
            tasks: List of task dictionaries to translate
            target_language: Target language code (hi, ta, te)
            
        Returns:
            Translated tasks list
        """
        if target_language == "en":
            return tasks
        
        if not self._is_language_supported(target_language):
            return tasks
        
        try:
            # Try AI-based translation first for better quality
            prompt = get_tasks_translation_prompt(tasks, target_language)
            
            response = self._bedrock.invoke_model(
                system_prompt="You are a translator for educational task descriptions. Keep technical terms in English.",
                user_prompt=prompt,
                max_tokens=2048,
                temperature=0.3,
                fallback_type="translation"
            )
            
            result = self._bedrock.parse_json_response(response)
            
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "tasks" in result:
                return result["tasks"]
            else:
                raise ValueError("Invalid response format")
                
        except Exception as exc:
            logger.error(f"AI task translation failed, using Amazon Translate: {exc}")
            return await self._translate_tasks_with_amazon(tasks, target_language)
    
    async def explain_with_fallback_chain(
        self,
        concept: str,
        language: str = "en",
        user_level: str = "intermediate"
    ) -> dict:
        """
        Explain a concept with a fallback chain:
        1. Try AI explanation in requested language
        2. Try AI explanation in English if first fails
        3. Return static fallback if both fail
        
        Args:
            concept: The concept to explain
            language: Preferred language
            user_level: User's proficiency level
            
        Returns:
            Explanation dict
        """
        # Try requested language first
        result = await self.explain_concept(concept, language, user_level)
        
        if not result.get("fallback", False):
            return result
        
        # If fallback was used and language wasn't English, try English
        if language != "en":
            logger.info(f"Trying English explanation for {concept} after {language} failed")
            result_en = await self.explain_concept(concept, "en", user_level)
            
            if not result_en.get("fallback", False):
                # Add note about language fallback
                result_en["_meta"]["original_language_requested"] = language
                result_en["_meta"]["language_fallback"] = True
                return result_en
        
        # Return the original fallback
        return result
    
    async def batch_translate_tasks(
        self,
        tasks: list,
        target_language: str,
        batch_size: int = 10
    ) -> list:
        """
        Translate tasks in batches to handle large lists efficiently.
        
        Args:
            tasks: List of tasks to translate
            target_language: Target language
            batch_size: Number of tasks to translate at once
            
        Returns:
            Translated tasks
        """
        if target_language == "en" or not tasks:
            return tasks
        
        if not self._is_language_supported(target_language):
            return tasks
        
        translated_tasks = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            try:
                translated_batch = await self.translate_tasks(batch, target_language)
                translated_tasks.extend(translated_batch)
            except Exception as exc:
                logger.error(f"Failed to translate batch {i//batch_size + 1}: {exc}")
                # Keep original tasks for failed batches
                translated_tasks.extend(batch)
        
        return translated_tasks
    
    async def _translate_with_amazon_translate(
        self,
        content: dict,
        target_language: str
    ) -> dict:
        """Fallback translation using Amazon Translate."""
        target_code = self._get_translate_code(target_language)
        
        def translate_value(value):
            if isinstance(value, str):
                try:
                    result = translate_service.translate_text(
                        text=value,
                        target_language=target_code
                    )
                    return result["translated_text"]
                except Exception as exc:
                    logger.warning(f"Translation failed for text: {exc}")
                    return value
            elif isinstance(value, dict):
                return {k: translate_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [translate_value(item) for item in value]
            return value
        
        return translate_value(content)
    
    async def _translate_tasks_with_amazon(
        self,
        tasks: list,
        target_language: str
    ) -> list:
        """Translate tasks using Amazon Translate."""
        target_code = self._get_translate_code(target_language)
        
        translated_tasks = []
        for task in tasks:
            translated_task = task.copy()
            
            # Translate text fields
            for field in ["title", "description"]:
                if field in task and isinstance(task[field], str):
                    try:
                        result = translate_service.translate_text(
                            text=task[field],
                            target_language=target_code
                        )
                        translated_task[field] = result["translated_text"]
                    except Exception as exc:
                        logger.warning(f"Failed to translate task field {field}: {exc}")
            
            translated_tasks.append(translated_task)
        
        return translated_tasks
    
    def _get_fallback_explanation(self, concept: str, language: str) -> dict:
        """Generate a fallback explanation when AI service fails."""
        explanations = {
            "en": {
                "concept": concept,
                "explanation": {
                    "simple_definition": f"{concept} is an important topic in computer science.",
                    "detailed_explanation": self._get_language_message(language, "error_explanation"),
                    "real_world_analogy": "Learning this concept is like building a foundation for your programming skills.",
                    "why_it_matters": "This concept is frequently asked in technical interviews."
                },
                "key_points": [
                    "Important concept for placements",
                    "Practice with coding problems",
                    "Refer to standard resources"
                ],
                "resources": [
                    {"resource": "GeeksforGeeks", "type": "article", "url": "https://www.geeksforgeeks.org/"},
                    {"resource": "YouTube", "type": "video", "url": "https://www.youtube.com/results?search_query=" + concept.replace(" ", "+")}
                ],
                "fallback": True
            },
            "hi": {
                "concept": concept,
                "explanation": {
                    "simple_definition": f"{concept} computer science mein ek important topic hai.",
                    "detailed_explanation": self._get_language_message("hi", "error_explanation"),
                    "real_world_analogy": "Is concept ko samajhna aapki programming skills ka foundation banata hai.",
                    "why_it_matters": "Ye concept technical interviews mein frequently pucha jata hai."
                },
                "key_points": [
                    "Placements ke liye important concept",
                    "Coding problems se practice karein",
                    "Standard resources refer karein"
                ],
                "resources": [
                    {"resource": "CodeWithHarry YouTube", "type": "video", "language": "hi"},
                    {"resource": "GeeksforGeeks", "type": "article", "language": "en"}
                ],
                "fallback": True
            },
            "ta": {
                "concept": concept,
                "explanation": {
                    "simple_definition": f"{concept} computer science-la oru mukkiyamaana topic.",
                    "detailed_explanation": self._get_language_message("ta", "error_explanation"),
                    "real_world_analogy": "Itha purinjika programming skills foundation strong aagum.",
                    "why_it_matters": "Itha technical interviews-la evalo thadava ketturupanga."
                },
                "key_points": [
                    "Placements-kku mukkiyam",
                    "Coding problems practice pannungal",
                    "Nalla resources refer pannungal"
                ],
                "resources": [
                    {"resource": "YouTube Tamil", "type": "video", "language": "ta"},
                    {"resource": "GeeksforGeeks", "type": "article", "language": "en"}
                ],
                "fallback": True
            },
            "te": {
                "concept": concept,
                "explanation": {
                    "simple_definition": f"{concept} computer science-lo oka mukhyamaina topic.",
                    "detailed_explanation": self._get_language_message("te", "error_explanation"),
                    "real_world_analogy": "Ithi ardham chesukovadam mee programming skills foundation ni strong chestundi.",
                    "why_it_matters": "Ithi technical interviews-lo chala sarlu adugutharu."
                },
                "key_points": [
                    "Placements ki mukhyam",
                    "Coding problems tho practice cheyandi",
                    "Standard resources chudandi"
                ],
                "resources": [
                    {"resource": "YouTube Telugu", "type": "video", "language": "te"},
                    {"resource": "GeeksforGeeks", "type": "article", "language": "en"}
                ],
                "fallback": True
            }
        }
        
        result = explanations.get(language, explanations["en"]).copy()
        result["_meta"] = {
            "fallback": True,
            "reason": "AI service unavailable",
            "requested_language": language
        }
        return result
    
    def _get_fallback_resources(self, topic: str, user_level: str, language: str = "en") -> dict:
        """Generate fallback resource recommendations."""
        base_resources = {
            "topic": topic,
            "resources": [
                {
                    "title": f"Introduction to {topic}",
                    "platform": "GeeksforGeeks",
                    "type": "article",
                    "free": True,
                    "language": "en",
                    "url": f"https://www.geeksforgeeks.org/{topic.replace(' ', '-')}/"
                },
                {
                    "title": f"{topic} Tutorial",
                    "platform": "YouTube",
                    "type": "video",
                    "creator": "CodeWithHarry",
                    "free": True,
                    "language": "hi"
                },
                {
                    "title": f"Practice {topic}",
                    "platform": "HackerRank",
                    "type": "practice_platform",
                    "free": True,
                    "language": "en"
                }
            ],
            "pro_tips": [
                "Start with basic concepts before moving to advanced topics",
                "Practice coding problems daily",
                "Watch video tutorials if you find reading difficult"
            ],
            "fallback": True,
            "message": self._get_language_message(language, "error_resources")
        }
        
        base_resources["_meta"] = {
            "fallback": True,
            "reason": "AI service unavailable",
            "topic": topic,
            "user_level": user_level
        }
        
        return base_resources
    
    def get_supported_languages(self) -> dict:
        """
        Get list of supported languages with their details.
        
        Returns:
            Dictionary of supported languages
        """
        return {
            "languages": [
                {
                    "code": code,
                    "name": name,
                    "native_name": self._get_native_name(code)
                }
                for code, name in self.SUPPORTED_LANGUAGES.items()
            ]
        }
    
    def _get_native_name(self, language_code: str) -> str:
        """Get the native name for a language."""
        native_names = {
            "en": "English",
            "hi": "हिन्दी",
            "ta": "தமிழ்",
            "te": "తెలుగు"
        }
        return native_names.get(language_code, language_code)


# Global instance
content_service = ContentService()

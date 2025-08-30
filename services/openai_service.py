"""
OpenAI service for AI-powered evaluation features

Copyright © 2025 Utah Valley University School of Education
All Rights Reserved.

This software is proprietary and confidential property of Utah Valley University
School of Education. Licensed for educational use only.
"""

import os
from typing import Dict, List, Optional, Any
import openai
from openai import OpenAI
import json

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

class OpenAIService:
    """Service for OpenAI API integration"""
    
    def __init__(self):
        """Initialize OpenAI service"""
        self.client = None
        # Use GPT-5-mini for better JSON handling and temperature support
        self.model = os.getenv('OPENAI_MODEL', 'gpt-5-mini')
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client if API key is available"""
        api_key = self._get_api_key()
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from Streamlit secrets or environment variables"""
        # First try Streamlit secrets (preferred for Streamlit Cloud)
        if HAS_STREAMLIT:
            try:
                if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                    return st.secrets['OPENAI_API_KEY']
            except Exception:
                pass  # Fall back to environment variable
        
        # Fall back to environment variable (for local development)
        return os.getenv('OPENAI_API_KEY')
    
    def is_enabled(self) -> bool:
        """Check if OpenAI service is enabled and configured"""
        return self.client is not None
    
    def analyze_lesson_plan(self, lesson_plan_text: str) -> Dict[str, any]:
        """
        Analyze lesson plan and extract key information
        
        Args:
            lesson_plan_text: The lesson plan content as text
        
        Returns:
            Dictionary containing extracted information
        """
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")
        
        prompt = self._build_lesson_plan_analysis_prompt(lesson_plan_text)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational supervisor who analyzes lesson plans. Extract key information accurately and provide it in the specified JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=800
                # Note: Using default temperature (1) for model compatibility
            )
            
            # Parse the JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Try multiple approaches to extract JSON
            extracted_info = None
            parsing_errors = []
            
            # Method 1: Try to parse the entire response as JSON
            try:
                extracted_info = json.loads(response_text)
            except json.JSONDecodeError as e:
                parsing_errors.append(f"Method 1 (full response): {str(e)}")
                
                # Method 2: Extract JSON from response (in case there's extra text)
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_text = response_text[start_idx:end_idx]
                    try:
                        extracted_info = json.loads(json_text)
                    except json.JSONDecodeError as e:
                        parsing_errors.append(f"Method 2 (extract braces): {str(e)}")
                        
                        # Method 3: Try to find JSON between ```json blocks
                        json_start = response_text.find('```json')
                        if json_start != -1:
                            json_start += 7  # Move past '```json'
                            json_end = response_text.find('```', json_start)
                            if json_end != -1:
                                json_text = response_text[json_start:json_end].strip()
                                try:
                                    extracted_info = json.loads(json_text)
                                except json.JSONDecodeError as e:
                                    parsing_errors.append(f"Method 3 (markdown): {str(e)}")
                        
                        # Method 4: Try to find JSON between ``` blocks (without json)
                        if not extracted_info:
                            json_start = response_text.find('```')
                            if json_start != -1:
                                json_start += 3  # Move past '```'
                                # Skip any language identifier line
                                newline = response_text.find('\n', json_start)
                                if newline != -1:
                                    json_start = newline + 1
                                json_end = response_text.find('```', json_start)
                                if json_end != -1:
                                    json_text = response_text[json_start:json_end].strip()
                                    try:
                                        extracted_info = json.loads(json_text)
                                    except json.JSONDecodeError as e:
                                        parsing_errors.append(f"Method 4 (generic markdown): {str(e)}")
                        
                        # Method 5: Try to clean and fix common JSON issues
                        if not extracted_info and start_idx != -1 and end_idx != -1:
                            json_text = response_text[start_idx:end_idx]
                            # Fix common issues
                            json_text = json_text.replace('\n', ' ')  # Remove newlines
                            json_text = json_text.replace('\t', ' ')  # Remove tabs
                            json_text = ' '.join(json_text.split())   # Normalize whitespace
                            try:
                                extracted_info = json.loads(json_text)
                            except json.JSONDecodeError as e:
                                parsing_errors.append(f"Method 5 (cleaned): {str(e)}")
            
            if extracted_info:
                # Validate and clean the extracted information
                return self._validate_lesson_plan_extraction(extracted_info)
            else:
                # Create a fallback response if all parsing fails
                fallback_response = {
                    "teacher_name": None,
                    "lesson_date": None,
                    "subject_area": None,
                    "grade_levels": None,
                    "school_name": None,
                    "lesson_topic": None,
                    "class_period": None,
                    "duration": None,
                    "total_students": None,
                    "utah_core_standards": None,
                    "learning_objectives": [],
                    "materials": [],
                    "assessment_methods": [],
                    "lesson_structure": "AI parsing failed - manual review required",
                    "notes": f"JSON parsing failed. AI Response: {response_text[:200]}...",
                    "confidence_score": 0.0
                }
                
                # Log detailed error for debugging
                error_details = f"All JSON parsing methods failed. Errors: {'; '.join(parsing_errors)}. Full response: {response_text}"
                print(f"DEBUG: {error_details}")
                
                # Return fallback instead of raising exception
                return self._validate_lesson_plan_extraction(fallback_response)
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to analyze lesson plan: {str(e)}")
    
    def _build_lesson_plan_analysis_prompt(self, lesson_plan_text: str) -> str:
        """Build prompt for lesson plan analysis"""
        
        prompt = f"""Analyze the following lesson plan and extract key information. You must respond with ONLY a valid JSON object, nothing else.

LESSON PLAN TEXT:
{lesson_plan_text}

Extract the following information and return it as a JSON object:

{{
    "teacher_name": "Full name of the teacher/student teacher",
    "lesson_date": "Date of the lesson (YYYY-MM-DD format if possible, or as written)",
    "subject_area": "Subject being taught",
    "grade_levels": "Grade level(s) of students",
    "school_name": "Name of the school",
    "lesson_topic": "Main topic or title of the lesson",
    "class_period": "Class period or time if mentioned",
    "duration": "Lesson duration if mentioned",
    "total_students": "Number of students in class",
    "utah_core_standards": "Utah Core Standards referenced if mentioned",
    "learning_objectives": ["List", "of", "learning", "objectives"],
    "materials": ["List", "of", "materials", "needed"],
    "assessment_methods": ["Types", "of", "assessment", "mentioned"],
    "lesson_structure": "Brief description of lesson flow/structure",
    "notes": "Any additional notes or special considerations",
    "confidence_score": 0.95
}}

CRITICAL REQUIREMENTS:
1. If information is not found or unclear, use null for that field
2. For grade_levels, extract the specific grade(s) mentioned (e.g., "3rd Grade", "6-8", "K-5")
3. For lesson_date, convert to YYYY-MM-DD format if possible, otherwise keep as written
4. Be very careful to extract the actual teacher name, not example names
5. For total_students, look for class size information
6. confidence_score should reflect how clear and complete the information is (0.0-1.0)
7. Your response must be ONLY valid JSON - no explanations, no markdown, no additional text
8. Start your response with {{ and end with }}

Respond with the JSON object now:"""
        
        return prompt
    
    def _validate_lesson_plan_extraction(self, extracted_info: Dict) -> Dict:
        """Validate and clean extracted lesson plan information"""
        
        # Ensure required fields exist with defaults
        validated = {
            'teacher_name': extracted_info.get('teacher_name', None),
            'lesson_date': extracted_info.get('lesson_date', None),
            'subject_area': extracted_info.get('subject_area', None),
            'grade_levels': extracted_info.get('grade_levels', None),
            'school_name': extracted_info.get('school_name', None),
            'lesson_topic': extracted_info.get('lesson_topic', None),
            'class_period': extracted_info.get('class_period', None),
            'duration': extracted_info.get('duration', None),
            'total_students': extracted_info.get('total_students', None),
            'utah_core_standards': extracted_info.get('utah_core_standards', None),
            'learning_objectives': extracted_info.get('learning_objectives', []),
            'materials': extracted_info.get('materials', []),
            'assessment_methods': extracted_info.get('assessment_methods', []),
            'lesson_structure': extracted_info.get('lesson_structure', None),
            'notes': extracted_info.get('notes', None),
            'confidence_score': extracted_info.get('confidence_score', 0.8),
            'extraction_timestamp': None  # Will be set when used
        }
        
        # Clean up lists - ensure they're actually lists
        for list_field in ['learning_objectives', 'materials', 'assessment_methods']:
            if not isinstance(validated[list_field], list):
                validated[list_field] = []
        
        # Convert total_students to int if it's a string number
        if validated['total_students']:
            try:
                validated['total_students'] = int(validated['total_students'])
            except (ValueError, TypeError):
                validated['total_students'] = None
        
        return validated
    
    def generate_justification(
        self,
        item: Dict,
        score: int,
        student_name: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate AI-assisted justification for a given score
        
        Args:
            item: Assessment item dictionary
            score: Score level (0-3)
            student_name: Name of the student being evaluated
            context: Additional context (optional)
        
        Returns:
            Generated justification text
        """
        if not self.is_enabled():
            # Return generic justification if AI is not enabled
            return self._create_generic_justification(item, score)
        
        # Check if context is empty or not relevant to this competency
        if not context or not context.strip():
            return self._create_generic_justification(item, score)
        
        prompt = self._build_justification_prompt(item, score, student_name, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational evaluator specializing in student teacher assessments. Provide clear, professional, evidence-based justifications. If the provided context does not contain relevant information for the specific competency, return '[NO_CONTEXT]' as the first word of your response."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=300
                # Note: Using default temperature (1) for model compatibility
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Check if AI indicates no relevant context
            if ai_response.startswith('[NO_CONTEXT]'):
                return self._create_generic_justification(item, score)
            
            return ai_response
        
        except Exception as e:
            # Fallback to generic justification on error
            return self._create_generic_justification(item, score)
    
    def analyze_evaluation(
        self,
        scores: Dict[str, int],
        justifications: Dict[str, str],
        disposition_scores: Dict[str, int],
        rubric_type: str
    ) -> str:
        """
        Analyze complete evaluation and provide feedback
        
        Args:
            scores: Assessment item scores
            justifications: Assessment justifications
            disposition_scores: Professional disposition scores
            rubric_type: Type of rubric ("field_evaluation" or "ster")
        
        Returns:
            Analysis and feedback text
        """
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")
        
        prompt = self._build_analysis_prompt(scores, justifications, disposition_scores, rubric_type)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational supervisor providing constructive feedback on student teacher evaluations. Focus on growth and development."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=400
                # Note: Using default temperature (1) for model compatibility
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Failed to generate AI analysis: {str(e)}")
    
    def _build_justification_prompt(
        self,
        item: Dict,
        score: int,
        student_name: str,
        context: Optional[str] = None
    ) -> str:
        """Build prompt for justification generation"""
        
        score_labels = {
            0: "Does not demonstrate competency",
            1: "Is approaching competency at expected level",
            2: "Demonstrates competency at expected level",
            3: "Exceeds expected level of competency"
        }
        
        prompt = f"""You are an expert education evaluator helping write a justification for a student teaching evaluation.

Assessment Item: {item['code']} - {item['title']}
Competency Area: {item['competency_area']}
Context: {item['context']}
Score Level: {score} ({score_labels.get(score, 'Unknown')})

Score Description: {item['levels'].get(str(score), 'No description available')}

Student: {student_name}
{f'Additional Context: {context}' if context else ''}

Write a professional, specific justification (2-3 sentences) that:
1. Explains why this score was given
2. Provides specific examples of observed behaviors
3. Aligns with the score description
4. Maintains a constructive, professional tone

{f'Reference example: {item.get("example_justification", "")}' if item.get("example_justification") else ''}

Justification:"""
        
        return prompt
    
    def _build_analysis_prompt(
        self,
        scores: Dict[str, int],
        justifications: Dict[str, str],
        disposition_scores: Dict[str, int],
        rubric_type: str
    ) -> str:
        """Build prompt for evaluation analysis"""
        
        # Identify areas needing improvement (scores of 1)
        low_scoring_areas = []
        for item_id, score in scores.items():
            if score == 1:
                justification = justifications.get(item_id, "No justification provided")
                low_scoring_areas.append(f"- {item_id}: Level 1 (Justification: {justification})")
        
        # Identify disposition concerns
        disposition_concerns = []
        for disp_id, score in disposition_scores.items():
            if score < 3:
                disposition_concerns.append(f"- {disp_id}: Level {score} (Needs Level 3+)")
        
        prompt = f"""
Analyze this {rubric_type.replace('_', ' ')} evaluation focusing on specific areas needing improvement.

CRITICAL FOCUS: Students must achieve Level 2+ in ALL competency areas to pass. Average scores are misleading - identify specific areas scoring Level 1 and provide targeted improvement guidance.

COMPETENCY SCORES NEEDING ATTENTION (Level 1):
{chr(10).join(low_scoring_areas) if low_scoring_areas else "✅ No Level 1 scores - all competencies at Level 2+"}

DISPOSITION CONCERNS (Below Level 3):
{chr(10).join(disposition_concerns) if disposition_concerns else "✅ All dispositions at Level 3+"}

ANALYSIS REQUIREMENTS:
1. **Critical Areas**: For each Level 1 competency, explain WHY the score was given based on the justification
2. **Improvement Path**: Provide specific, actionable steps to move from Level 1 to Level 2
3. **Priority Focus**: Identify which Level 1 areas are most critical to address first
4. **Strengths**: Briefly note areas of strength (Level 2-3) that can support growth
5. **Conference Guidance**: Suggest specific discussion points for supervisor-student conferences

DO NOT:
- Calculate or emphasize average scores
- Provide generic feedback
- Focus primarily on strengths when Level 1 scores exist

FORMAT: Provide clear, actionable analysis that helps supervisors guide students toward meeting minimum competency requirements.
"""
        
        return prompt
    
    def generate_bulk_justifications(
        self,
        items: List[Dict],
        scores: Dict[str, int],
        observation_notes: str,
        student_name: str,
        rubric_type: str
    ) -> Dict[str, str]:
        """
        Generate justifications for all scored items using supervisor's observation notes
        
        Args:
            items: List of assessment item dictionaries
            scores: Dictionary mapping item IDs to scores
            observation_notes: Supervisor's classroom observation notes
            student_name: Name of the student being evaluated
            rubric_type: Type of rubric ("field_evaluation" or "ster")
        
        Returns:
            Dictionary mapping item IDs to generated justifications
        """
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")
        
        prompt = self._build_bulk_justification_prompt(
            items, scores, observation_notes, student_name, rubric_type
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational supervisor who writes professional, evidence-based justifications for student teacher evaluations. Use the provided observation notes to create specific, individualized justifications for each competency."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=2000  # Increased for multiple justifications
                # Note: Using default temperature (1) for model compatibility
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse the JSON response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                justifications = json.loads(json_text)
                
                # Validate that we have justifications for all scored items
                validated_justifications = {}
                for item in items:
                    item_id = item['id']
                    if item_id in scores and item_id in justifications:
                        validated_justifications[item_id] = justifications[item_id]
                    elif item_id in scores:
                        # Generate generic justification if missing
                        validated_justifications[item_id] = self._create_generic_justification(item, scores[item_id])
                
                return validated_justifications
            else:
                raise Exception("Could not parse JSON from AI response")
        
        except json.JSONDecodeError as e:
            # Fallback: Generate generic justifications
            fallback_justifications = {}
            for item in items:
                item_id = item['id']
                if item_id in scores:
                    fallback_justifications[item_id] = self._create_generic_justification(item, scores[item_id])
            return fallback_justifications
        except Exception as e:
            raise Exception(f"Failed to generate bulk justifications: {str(e)}")
    
    def _create_generic_justification(self, item: Dict, score: int) -> str:
        """
        Create a generic justification when no specific observation notes are available
        
        Args:
            item: Assessment item dictionary
            score: Score level (0-3)
            
        Returns:
            Generic justification with helpful guidance
        """
        score_labels = {
            0: "does not demonstrate competency",
            1: "is approaching competency at expected level",
            2: "demonstrates competency at expected level", 
            3: "exceeds expected level of competency"
        }
        
        score_description = item['levels'].get(str(score), 'No description available')
        score_label = score_labels.get(score, 'demonstrates competency')
        
        # Create a more helpful and less alarming generic justification
        generic_justification = (
            f"The student teacher {score_label} for {item['code']} - {item['title']}. "
            f"{score_description} "
            f"Additional specific examples from the classroom observation would strengthen this justification."
        )
        
        return generic_justification
    
    def _build_bulk_justification_prompt(
        self,
        items: List[Dict],
        scores: Dict[str, int],
        observation_notes: str,
        student_name: str,
        rubric_type: str
    ) -> str:
        """Build prompt for bulk justification generation"""
        
        score_labels = {
            0: "Does not demonstrate competency",
            1: "Is approaching competency at expected level", 
            2: "Demonstrates competency at expected level",
            3: "Exceeds expected level of competency"
        }
        
        # Build items list with scores
        items_text = ""
        for item in items:
            item_id = item['id']
            if item_id in scores:
                score = scores[item_id]
                items_text += f"\n{item['code']} - {item['title']}\n"
                items_text += f"Competency Area: {item['competency_area']}\n"
                items_text += f"Assigned Score: Level {score} ({score_labels.get(score, 'Unknown')})\n"
                items_text += f"Score Description: {item['levels'].get(str(score), 'No description available')}\n"
                items_text += "---\n"
        
        prompt = f"""You are writing professional justifications for a student teaching evaluation based on classroom observation notes.

STUDENT: {student_name}
EVALUATION TYPE: {rubric_type.replace('_', ' ').title()}

SUPERVISOR'S OBSERVATION NOTES:
{observation_notes}

ASSESSMENT ITEMS TO JUSTIFY:
{items_text}

INSTRUCTIONS:
1. Write a specific, evidence-based justification for EACH item listed above
2. Use details from the observation notes to support each score
3. Each justification should be 2-3 sentences and reference specific observed behaviors
4. Maintain a professional, constructive tone
5. Ensure justifications align with the assigned score level

IMPORTANT: If the observation notes do not contain relevant information for a specific competency area, generate a generic justification using this format:
"[GENERIC] The student teacher demonstrates competency for the assessed item. **NOTE: No specific observations were recorded for this competency area - supervisor may wish to add additional details.**"

Return your response as a JSON object with item IDs as keys and justifications as values:

{{
    "item_id_1": "Professional justification based on observation notes...",
    "item_id_2": "[GENERIC] The student teacher demonstrates for CC1 - Classroom Environment...",
    ...
}}

JSON Response:"""
        
        return prompt 

    def generate_analysis_for_competencies(
        self,
        items: List[Dict],
        observation_notes: str,
        student_name: str,
        rubric_type: str,
        lesson_plan_context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate AI analysis for competencies based on observation notes and lesson plan
        This method generates evidence-based analysis BEFORE scoring to inform supervisor decisions
        
        Args:
            items: List of assessment item dictionaries
            observation_notes: Supervisor's classroom observation notes
            student_name: Name of the student being evaluated
            rubric_type: Type of rubric ("field_evaluation" or "ster")
            lesson_plan_context: Optional lesson plan context
        
        Returns:
            Dictionary mapping item IDs to generated analysis text
        """

        
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")
        
        prompt = self._build_analysis_prompt_for_competencies(
            items, observation_notes, student_name, rubric_type, lesson_plan_context
        )
        

        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational supervisor who analyzes classroom observations to extract evidence for each competency area. Provide objective, evidence-based analysis that will help supervisors make informed scoring decisions. Focus on what was observed without assigning scores. Return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=2500  # Increased for comprehensive analysis
                # Note: Using default temperature (1) for model compatibility
            )
            
            response_text = response.choices[0].message.content.strip()
            

            
            # Use robust JSON parsing (same as lesson plan analysis)
            extracted_analyses = None
            parsing_errors = []
            
            # Method 1: Try to parse the entire response as JSON
            try:
                extracted_analyses = json.loads(response_text)
            except json.JSONDecodeError as e:
                parsing_errors.append(f"Method 1 (full response): {str(e)}")
                
                # Method 2: Extract JSON from response (in case there's extra text)
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_text = response_text[start_idx:end_idx]
                    try:
                        extracted_analyses = json.loads(json_text)
                    except json.JSONDecodeError as e:
                        parsing_errors.append(f"Method 2 (extract braces): {str(e)}")
                        
                        # Method 3: Try to find JSON between ```json blocks
                        json_start = response_text.find('```json')
                        if json_start != -1:
                            json_start += 7  # Move past '```json'
                            json_end = response_text.find('```', json_start)
                            if json_end != -1:
                                json_text = response_text[json_start:json_end].strip()
                                try:
                                    extracted_analyses = json.loads(json_text)
                                except json.JSONDecodeError as e:
                                    parsing_errors.append(f"Method 3 (markdown): {str(e)}")
                        
                        # Method 4: Try to find JSON between ``` blocks (without json)
                        if not extracted_analyses:
                            json_start = response_text.find('```')
                            if json_start != -1:
                                json_start += 3  # Move past '```'
                                # Skip any language identifier line
                                newline = response_text.find('\n', json_start)
                                if newline != -1:
                                    json_start = newline + 1
                                json_end = response_text.find('```', json_start)
                                if json_end != -1:
                                    json_text = response_text[json_start:json_end].strip()
                                    try:
                                        extracted_analyses = json.loads(json_text)
                                    except json.JSONDecodeError as e:
                                        parsing_errors.append(f"Method 4 (generic markdown): {str(e)}")
            
            if extracted_analyses:
                # Validate that we have analyses for all items
                validated_analyses = {}
                for item in items:
                    item_id = item['id']
                    if item_id in extracted_analyses and extracted_analyses[item_id].strip():
                        # Use AI-generated analysis if available and not empty
                        validated_analyses[item_id] = extracted_analyses[item_id]
                    else:
                        # Only add limited evidence warning for items that are actually missing
                        validated_analyses[item_id] = f"Based on the provided observation notes, specific evidence for {item['code']} - {item['title']} was not clearly documented. Consider adding specific observations related to {item['competency_area'].lower()} during the evaluation process."
                
                return validated_analyses
            else:

                
                # Fallback to text extraction
                return self._extract_analyses_from_text(response_text, items)
        
        except Exception as e:
            # Only in case of complete failure, provide informative fallback
            fallback_analyses = {}
            for item in items:
                item_id = item['id']
                fallback_analyses[item_id] = f"AI analysis temporarily unavailable for {item['code']} - {item['title']}. Please refer to your observation notes and professional judgment to evaluate this competency in {item['competency_area']}."
            return fallback_analyses
    
    def _extract_analyses_from_text(self, response_text: str, items: List[Dict]) -> Dict[str, str]:
        """
        Extract analyses from non-JSON AI response text as fallback
        
        Args:
            response_text: The AI response text
            items: List of assessment items
            
        Returns:
            Dictionary mapping item IDs to extracted analysis text
        """
        analyses = {}
        
        # Try to find analyses by looking for item codes in the response
        for item in items:
            item_id = item['id']
            item_code = item['code']
            
            # Look for the item code in the response
            lines = response_text.split('\n')
            analysis_lines = []
            collecting = False
            
            for line in lines:
                if item_code in line:
                    collecting = True
                    analysis_lines = [line]
                elif collecting:
                    if any(other_item['code'] in line for other_item in items if other_item['id'] != item_id):
                        # Found another item code, stop collecting
                        break
                    elif line.strip():
                        analysis_lines.append(line)
                    elif len(analysis_lines) > 1:
                        # Empty line after content, probably end of this analysis
                        break
            
            if analysis_lines:
                # Clean up the extracted analysis
                analysis = ' '.join(analysis_lines).strip()
                # Remove item code from beginning if present
                analysis = analysis.replace(f"{item_code} -", "").replace(f"{item_code}:", "").strip()
                analyses[item_id] = analysis
            else:
                # No analysis found for this item
                analyses[item_id] = f"Specific observations for {item_code} - {item['title']} were not detailed in the analysis. Consider adding targeted observations for {item['competency_area'].lower()} competencies."
        
        return analyses
    
    def _create_generic_analysis(self, item: Dict) -> str:
        """
        Create a generic analysis when no specific observation notes are available
        
        Args:
            item: Assessment item dictionary
            
        Returns:
            Generic analysis text
        """
        generic_analysis = (
            f"Analysis needed for {item['code']} - {item['title']} in the {item['competency_area']} area. "
            f"This competency focuses on: {item['context']} "
            f"**NOTE: No specific observations were available for detailed analysis - "
            f"supervisor should add specific examples and evidence based on classroom observation.**"
        )
        
        return generic_analysis
    
    def _build_analysis_prompt_for_competencies(
        self,
        items: List[Dict],
        observation_notes: str,
        student_name: str,
        rubric_type: str,
        lesson_plan_context: Optional[str] = None
    ) -> str:
        """Build prompt for competency analysis generation"""
        
        # Build items list with competency details
        items_text = ""
        for item in items:
            items_text += f"\n{item['id']}: {item['code']} - {item['title']}\n"
            items_text += f"Competency Area: {item['competency_area']}\n"
            items_text += f"Context: {item['context']}\n"
            items_text += "---\n"
        
        lesson_plan_section = ""
        if lesson_plan_context:
            lesson_plan_section = f"\nLESSON PLAN CONTEXT:\n{lesson_plan_context}\n"
        
        prompt = f"""You are analyzing classroom observation notes for teaching competencies. Return ONLY a JSON object.

OBSERVATION NOTES:
{observation_notes}

COMPETENCIES TO ANALYZE:
{items_text}

For each competency ID, provide a brief analysis based on the observation notes. If no evidence is found, state "No specific evidence found in observation notes."

Return ONLY this JSON format:
{{
    "COMPETENCY_ID": "analysis text here"
}}

JSON response:"""
        
        return prompt 

    # -------------------- Generic, rubric-agnostic grading --------------------
    def generate_feedback_for_custom_rubric(
        self,
        rubric: Dict,
        submission_text: str,
        context: Optional[str] = None,
        student_identifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate rubric-agnostic feedback for arbitrary criteria.

        Returns a dict:
        {
          "scores": {criterion_id: score or "not_applicable"},
          "feedback": {criterion_id: text},
          "overall": {"summary": str, "strengths": [...], "areas_for_improvement": [...]} 
        }
        """
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")

        # Build compact rubric specification for the model
        criteria_text = []
        for c in rubric.get('criteria', []):
            levels = c.get('levels', {})
            level_str = " | ".join([f"{k}: {v}" for k, v in levels.items()])
            criteria_text.append(
                f"{c.get('id')}: {c.get('title')} [Levels: {level_str}]"
            )

        rubric_header = f"Rubric: {rubric.get('name', 'Custom Rubric')} (v{rubric.get('version','1.0')})"
        scale = rubric.get('scale', {"min": 0, "max": 3})

        user_prompt = f"""
Evaluate the submission against the rubric.

{rubric_header}
Scale: {scale}
Criteria:
{chr(10).join(criteria_text)}

Submission:
{submission_text}

Context (optional):
{context or 'N/A'}

Instructions:
1. For each criterion ID, assign a numeric score within the scale if applicable. If truly not applicable, use "not_applicable".
2. Provide criterion-level feedback that is specific, constructive, and references evidence from the submission.
3. Provide an overall summary, strengths, and areas for improvement.
4. Return ONLY valid JSON with this structure:
{{
  "scores": {{"CRIT_ID": 0-3 or "not_applicable", ...}},
  "feedback": {{"CRIT_ID": "text", ...}},
  "overall": {{
      "summary": "text",
      "strengths": ["text", ...],
      "areas_for_improvement": ["text", ...]
  }}
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert CS teaching assistant. Be precise, fair, and evidence-based. Return JSON only."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                max_completion_tokens=1200
            )

            response_text = response.choices[0].message.content.strip()

            # Parse JSON similarly to other methods
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                result = json.loads(json_text)
                # Basic result normalization
                result.setdefault('scores', {})
                result.setdefault('feedback', {})
                result.setdefault('overall', {})
                overall = result['overall']
                overall.setdefault('summary', '')
                overall.setdefault('strengths', [])
                overall.setdefault('areas_for_improvement', [])
                return result
            else:
                raise Exception("Could not parse JSON from AI response")
        except Exception as e:
            raise Exception(f"Failed to generate rubric-agnostic feedback: {str(e)}")

    def generate_code_feedback(
        self,
        rubric: Dict,
        code_text: str,
        metrics: Optional[Dict[str, Any]] = None,
        assignment_name: Optional[str] = None,
        language: str = "Python"
    ) -> Dict[str, Any]:
        """
        Generate code-aware feedback using rubric, code, and static metrics.
        Returns same structure as generate_feedback_for_custom_rubric.
        """
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")

        # Truncate very long code to keep prompt within limits
        truncated_code = code_text
        max_len = 12000
        if len(truncated_code) > max_len:
            truncated_code = truncated_code[:9000] + "\n...\n" + truncated_code[-2500:]

        criteria_text = []
        for c in rubric.get('criteria', []):
            levels = c.get('levels', {})
            level_str = " | ".join([f"{k}: {v}" for k, v in levels.items()])
            criteria_text.append(
                f"{c.get('id')}: {c.get('title')} [Levels: {level_str}]"
            )

        rubric_header = f"Rubric: {rubric.get('name', 'Custom Rubric')} (v{rubric.get('version','1.0')})"
        scale = rubric.get('scale', {"min": 0, "max": 3})

        metrics_text = ""
        if metrics:
            pairs = []
            for k in [
                'lines','non_empty_lines','functions','classes','docstring_coverage',
                'maintainability_index','avg_cyclomatic_complexity','max_cyclomatic_complexity',
                'flake8_issues_count']:
                if k in metrics and metrics[k] is not None:
                    pairs.append(f"{k}: {metrics[k]}")
            top_issues = metrics.get('flake8_top_issues', [])
            if pairs:
                metrics_text += "\nStatic Metrics: " + ", ".join(pairs)
            if top_issues:
                metrics_text += "\nTop Lint Issues:\n- " + "\n- ".join(top_issues[:10])

        user_prompt = f"""
Evaluate the following {language} submission against the rubric. Provide criterion-level scores and feedback.

Assignment: {assignment_name or 'CS Programming Assignment'}
{rubric_header}
Scale: {scale}
Criteria:
{chr(10).join(criteria_text)}

Code:
"""
        user_prompt += "\n" + truncated_code + "\n\n"
        if metrics_text:
            user_prompt += metrics_text + "\n\n"

        user_prompt += """
Instructions:
1. For each criterion ID, assign a numeric score within the scale if applicable (or "not_applicable").
2. Provide criterion-level feedback that is specific, constructive, and references the code and metrics.
3. Provide an overall summary, strengths, and areas for improvement.
4. Return ONLY valid JSON with this structure:
{
  "scores": {"CRIT_ID": 0-3 or "not_applicable", ...},
  "feedback": {"CRIT_ID": "text", ...},
  "overall": {
      "summary": "text",
      "strengths": ["text", ...],
      "areas_for_improvement": ["text", ...]
  }
}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert computer science teaching assistant. Be precise, fair, and evidence-based. Return JSON only."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                max_completion_tokens=1500
            )

            response_text = response.choices[0].message.content.strip()
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                result = json.loads(json_text)
                result.setdefault('scores', {})
                result.setdefault('feedback', {})
                overall = result.setdefault('overall', {})
                overall.setdefault('summary', '')
                overall.setdefault('strengths', [])
                overall.setdefault('areas_for_improvement', [])
                return result
            else:
                raise Exception("Could not parse JSON from AI response")
        except Exception as e:
            raise Exception(f"Failed to generate code feedback: {str(e)}")
    
    def generate_student_email(
        self,
        student_name: str,
        assignment_name: str,
        scores: Dict[str, int],
        feedback: Dict[str, str],
        course: str = "CS 1400",
        instructor_name: str = "Professor"
    ) -> str:
        """Generate personalized email to student with feedback"""
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")
        
        total_score = sum(scores.values())
        max_score = len(scores) * 3
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Compile feedback summary
        feedback_summary = []
        for crit_id, score in scores.items():
            feedback_text = feedback.get(crit_id, "No feedback provided")
            feedback_summary.append(f"- {crit_id}: {score}/3 - {feedback_text}")
        
        prompt = f"""Write a professional, encouraging email to a computer science student about their assignment feedback.

Student: {student_name}
Course: {course}
Assignment: {assignment_name}
Score: {total_score}/{max_score} ({percentage:.1f}%)
Instructor: {instructor_name}

Detailed Feedback:
{chr(10).join(feedback_summary)}

Email should:
1. Be professional but encouraging
2. Highlight specific strengths from the feedback
3. Provide constructive guidance for areas needing improvement
4. Include next steps or suggestions for improvement
5. Maintain a supportive, educational tone
6. Be concise but comprehensive

Write the complete email with subject line."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful CS instructor writing supportive feedback emails to students. Be encouraging and specific."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate student email: {str(e)}")
    
    def detect_code_similarity(
        self,
        code1: str,
        code2: str,
        assignment_context: str = ""
    ) -> Dict[str, Any]:
        """Analyze code similarity for plagiarism detection"""
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")
        
        prompt = f"""Compare these two code submissions for similarity and potential plagiarism.

Assignment Context: {assignment_context}

Code Submission 1:
{code1}

Code Submission 2:
{code2}

Analyze:
1. Structural similarity (algorithm, logic flow)
2. Variable naming patterns
3. Comment similarity
4. Overall approach similarity
5. Likelihood of copying vs coincidental similarity

Return JSON with:
{{
  "similarity_score": 0.0-1.0,
  "likely_plagiarism": true/false,
  "analysis": "detailed explanation",
  "similar_elements": ["list of similar elements"],
  "differences": ["list of differences"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at detecting code plagiarism. Be thorough and fair in your analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=600
            )
            
            response_text = response.choices[0].message.content.strip()
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                result = json.loads(json_text)
                return result
            else:
                return {
                    "similarity_score": 0.0,
                    "likely_plagiarism": False,
                    "analysis": "Could not parse AI response",
                    "similar_elements": [],
                    "differences": []
                }
                
        except Exception as e:
            raise Exception(f"Failed to analyze code similarity: {str(e)}")
    
    def generate_improvement_suggestions(
        self,
        code: str,
        rubric_feedback: Dict[str, str],
        assignment_context: str = ""
    ) -> str:
        """Generate specific improvement suggestions for student code"""
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")
        
        feedback_text = "\n".join([f"{k}: {v}" for k, v in rubric_feedback.items()])
        
        prompt = f"""Based on the code and rubric feedback, provide specific, actionable improvement suggestions for this CS student.

Assignment: {assignment_context}

Student Code:
{code}

Rubric Feedback:
{feedback_text}

Provide 3-5 specific, actionable suggestions that would help the student improve their code. Focus on:
1. Code quality improvements
2. Best practices they should adopt
3. Specific techniques or patterns to learn
4. Resources for further learning

Be encouraging and educational."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful CS instructor providing constructive improvement suggestions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate improvement suggestions: {str(e)}")
    
    def generate_batch_grading_summary(
        self,
        assignment_results: List[Dict[str, Any]],
        course: str = "CS 1400"
    ) -> str:
        """Generate summary report for batch grading results"""
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")
        
        # Compile batch statistics
        total_submissions = len(assignment_results)
        avg_score = sum(r.get('total_score', 0) for r in assignment_results) / total_submissions if total_submissions > 0 else 0
        
        # Common issues across submissions
        all_feedback = []
        for result in assignment_results:
            feedback = result.get('final_justifications', {})
            all_feedback.extend(feedback.values())
        
        feedback_summary = "\n".join(all_feedback[:10])  # Sample feedback
        
        prompt = f"""Generate a batch grading summary report for {course} assignment results.

Total Submissions: {total_submissions}
Average Score: {avg_score:.1f}

Sample Feedback from Submissions:
{feedback_summary}

Create a summary that includes:
1. Overall class performance analysis
2. Common strengths observed across submissions
3. Common areas for improvement
4. Specific recommendations for future instruction
5. Suggestions for follow-up activities or review topics

Be constructive and focused on helping the instructor improve their teaching."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational data analyst helping instructors understand class performance patterns."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=700
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate batch summary: {str(e)}")
    
    def generate_assignment_rubric(
        self,
        assignment_prompt: str,
        learning_objectives: List[str],
        course_level: str = "introductory"
    ) -> Dict[str, Any]:
        """Generate a custom rubric for a specific assignment"""
        if not self.is_enabled():
            raise Exception("OpenAI service is not configured")
        
        objectives_text = "\n".join([f"- {obj}" for obj in learning_objectives])
        
        prompt = f"""Create a grading rubric for this CS assignment.

Course Level: {course_level}
Assignment Prompt:
{assignment_prompt}

Learning Objectives:
{objectives_text}

Generate a rubric with 4-6 criteria appropriate for this assignment. Each criterion should have:
- Clear title and description
- 4 performance levels (0-3)
- Specific descriptors for each level

Return ONLY valid JSON:
{{
  "name": "Assignment Name - Rubric",
  "version": "1.0",
  "scale": {{"min": 0, "max": 3, "labels": {{"0": "Poor", "1": "Fair", "2": "Good", "3": "Excellent"}}}},
  "criteria": [
    {{
      "id": "CRIT1",
      "code": "CRIT1", 
      "title": "Criterion Title",
      "category": "Category",
      "description": "What this measures",
      "levels": {{
        "0": "Level 0 description",
        "1": "Level 1 description", 
        "2": "Level 2 description",
        "3": "Level 3 description"
      }}
    }}
  ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert CS educator creating assessment rubrics. Generate comprehensive, fair rubrics."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=1200
            )
            
            response_text = response.choices[0].message.content.strip()
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                result = json.loads(json_text)
                return result
            else:
                raise Exception("Could not parse JSON from AI response")
                
        except Exception as e:
            raise Exception(f"Failed to generate assignment rubric: {str(e)}")
"""
Assignment grading workflow components for CS AI Grader
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from data.rubric_loader import get_sample_cs_rubric, rubric_to_items, parse_rubric_json
from data.cs_synthetic import get_sample_assignment, generate_cs_assignment_data
from services.code_analysis_service import analyze_python_code
from services.openai_service import OpenAIService
from utils.storage import save_evaluation
from utils.validation import calculate_score


def show_assignment_grading_form():
    """Streamlined assignment grading workflow"""
    st.header("📝 Grade Programming Assignment")
    
    # Initialize session state
    if 'assignment_prompt' not in st.session_state:
        st.session_state.assignment_prompt = ""
    if 'code_text' not in st.session_state:
        st.session_state.code_text = ""
    if 'scores' not in st.session_state:
        st.session_state.scores = {}
    if 'justifications' not in st.session_state:
        st.session_state.justifications = {}
    if 'ai_analyses' not in st.session_state:
        st.session_state.ai_analyses = {}
    
    # Clear button
    if st.button("🔄 Start New Assignment", help="Clear all data and start fresh"):
        for key in ['assignment_prompt', 'code_text', 'scores', 'justifications', 'ai_analyses', 'rubric_meta']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Started new assignment")
        st.rerun()
    
    # STEP 1: Assignment Context
    st.subheader("📋 Step 1: Assignment Context")
    
    # Option to use synthetic data
    col1, col2 = st.columns([3, 1])
    with col1:
        use_synthetic = st.checkbox("🧪 Use Synthetic Assignment Data", help="Load a sample CS 1400 assignment for testing")
    with col2:
        if use_synthetic and st.button("🎲 Generate Random Assignment"):
            sample = get_sample_assignment()
            st.session_state.assignment_prompt = sample['assignment_prompt']
            st.session_state.code_text = sample['student_code']
            st.session_state.extracted_info = {
                'course': sample['course'],
                'assignment_name': sample['assignment_name'],
                'grader_name': 'Test Grader',
                'topics': sample['topics'],
                'difficulty': sample['difficulty']
            }
            st.success(f"✅ Loaded: {sample['assignment_name']}")
            st.rerun()
    
    if use_synthetic and st.session_state.get('extracted_info'):
        # Show loaded synthetic data
        info = st.session_state.extracted_info
        st.info(f"**Assignment:** {info.get('assignment_name')} ({info.get('difficulty')})")
        st.caption(f"**Topics:** {', '.join(info.get('topics', []))}")
    else:
        # Manual input
        col1, col2 = st.columns([2, 1])
        with col1:
            course = st.text_input("Course", value="CS 1400", help="e.g., CS 1400, CS 2420")
            assignment_name = st.text_input("Assignment Name", help="e.g., Project 1: Calculator, Lab 3: Lists")
        with col2:
            grader_name = st.text_input("Grader Name", help="Your name or TA name")
            due_date = st.date_input("Due Date")
        
        # Store in session
        st.session_state.extracted_info = {
            'course': course,
            'assignment_name': assignment_name,
            'grader_name': grader_name,
            'due_date': due_date.isoformat()
        }
    
    # Assignment prompt/description
    prompt_text = st.text_area(
        "Assignment Prompt/Description",
        value=st.session_state.assignment_prompt,
        height=120,
        placeholder="Paste the assignment description here...\n\nExample:\nWrite a function that calculates factorial of a number.\nRequirements:\n- Handle edge cases (0, 1, negative)\n- Include docstring\n- Use appropriate variable names",
        key="assignment_prompt_input",
        help="The assignment description helps AI understand requirements"
    )
    st.session_state.assignment_prompt = prompt_text
    
    # STEP 2: Rubric Selection
    st.subheader("📊 Step 2: Select Rubric")
    
    rubric_choice = st.radio(
        "Choose rubric:",
        ["Built-in CS Rubric", "Upload Custom Rubric"],
        horizontal=True
    )
    
    custom_rubric = None
    if rubric_choice == "Built-in CS Rubric":
        custom_rubric = get_sample_cs_rubric()
        st.success("✅ Using built-in CS programming rubric")
    else:
        uploaded_rubric = st.file_uploader("Upload Rubric JSON", type=["json"])
        if uploaded_rubric:
            try:
                json_text = uploaded_rubric.read().decode("utf-8")
                custom_rubric = parse_rubric_json(json_text)
                st.success(f"✅ Loaded custom rubric: {custom_rubric.get('name')}")
            except Exception as e:
                st.error(f"❌ Failed to load rubric: {e}")
                return
        else:
            st.warning("Please upload a rubric to continue")
            return
    
    items = rubric_to_items(custom_rubric)
    
    # Store rubric metadata
    st.session_state.rubric_meta = {
        'name': custom_rubric.get('name', 'CS Programming Rubric'),
        'version': custom_rubric.get('version', '1.0'),
        'scale': custom_rubric.get('scale', {'min': 0, 'max': 3}),
        'criteria_count': len(items)
    }
    
    # STEP 3: Student Code Submission
    st.subheader("💻 Step 3: Student Code")
    
    if not use_synthetic or not st.session_state.get('code_text'):
        code_input_method = st.radio(
            "How to input code:",
            ["📤 Upload .py File", "✏️ Paste Code"],
            horizontal=True
        )
        
        code_text = ""
        if code_input_method == "📤 Upload .py File":
            code_file = st.file_uploader("Upload Python file", type=['py'])
            if code_file:
                try:
                    code_text = code_file.read().decode('utf-8')
                    st.success(f"✅ Loaded {code_file.name}")
                    st.session_state.code_text = code_text
                except Exception as e:
                    st.error(f"❌ Failed to read file: {e}")
            else:
                code_text = st.session_state.code_text
        else:
            code_text = st.text_area(
                "Paste Python code:",
                value=st.session_state.code_text,
                height=200,
                placeholder="# Paste student's Python solution here\ndef factorial(n):\n    # Student implementation\n    pass",
                key="code_input_area"
            )
            st.session_state.code_text = code_text
    else:
        # Show synthetic code
        code_text = st.session_state.code_text
        with st.expander("👀 View Synthetic Student Code", expanded=False):
            st.code(code_text, language="python")
    
    if not code_text.strip():
        st.warning("Please provide student code to continue")
        return
    
    # Show code metrics
    if code_text.strip():
        with st.expander("📊 Code Analysis", expanded=False):
            try:
                metrics = analyze_python_code(code_text)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Lines of Code", metrics.get('lines', 0))
                    st.metric("Functions", metrics.get('functions', 0))
                with col2:
                    st.metric("Classes", metrics.get('classes', 0))
                    st.metric("Doc Coverage", f"{metrics.get('docstring_coverage', 0):.1%}")
                with col3:
                    if metrics.get('maintainability_index'):
                        st.metric("Maintainability", f"{metrics.get('maintainability_index', 0):.1f}")
                    if metrics.get('avg_cyclomatic_complexity'):
                        st.metric("Avg Complexity", f"{metrics.get('avg_cyclomatic_complexity', 0):.1f}")
            except Exception as e:
                st.error(f"Code analysis failed: {e}")
    
    # STEP 4: Generate AI Feedback
    st.subheader("🤖 Step 4: Generate AI Feedback")
    
    openai_service = OpenAIService()
    
    if not openai_service.is_enabled():
        st.error("🤖 OpenAI API key not configured. Please add it in Settings.")
        return
    
    if not st.session_state.get('ai_analyses'):
        if st.button("🚀 Generate AI Feedback", type="primary"):
            info = st.session_state.get('extracted_info', {})
            assignment_name = info.get('assignment_name', 'Programming Assignment')
            course = info.get('course', 'CS 1400')
            
            if not assignment_name or not code_text.strip():
                st.error("Please provide assignment name and student code")
                return
                
            with st.spinner("Analyzing code and generating feedback..."):
                try:
                    metrics = analyze_python_code(code_text)
                    result = openai_service.generate_code_feedback(
                        rubric=custom_rubric,
                        code_text=code_text,
                        metrics=metrics,
                        assignment_name=f"{course} - {assignment_name}"
                    )
                    
                    # Store AI feedback
                    st.session_state.ai_analyses = result.get('feedback', {})
                    
                    # Initialize scores from AI suggestions
                    ai_scores = result.get('scores', {})
                    for item_id, score in ai_scores.items():
                        if isinstance(score, int):
                            st.session_state.scores[item_id] = score
                    
                    # Initialize justifications from AI feedback
                    for item_id, feedback in st.session_state.ai_analyses.items():
                        st.session_state.justifications[item_id] = feedback
                    
                    st.success(f"✅ Generated AI feedback for {len(st.session_state.ai_analyses)} criteria")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Failed to generate AI feedback: {e}")
    else:
        st.success(f"✅ AI feedback generated for {len(st.session_state.ai_analyses)} criteria")
        if st.button("🔄 Regenerate Feedback"):
            st.session_state.ai_analyses = {}
            st.session_state.scores = {}
            st.session_state.justifications = {}
            st.rerun()
    
    # STEP 5: Review and Edit Scores
    if st.session_state.get('ai_analyses'):
        st.subheader("📝 Step 5: Review & Edit Scores")
        
        for item in items:
            item_id = item['id']
            
            with st.container():
                st.markdown(f"### {item['code']}: {item['title']}")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Show AI feedback
                    ai_feedback = st.session_state.ai_analyses.get(item_id, "No AI feedback")
                    edited_feedback = st.text_area(
                        "Feedback:",
                        value=ai_feedback,
                        height=100,
                        key=f"feedback_{item_id}"
                    )
                    st.session_state.justifications[item_id] = edited_feedback
                
                with col2:
                    # Score selector
                    current_score = st.session_state.scores.get(item_id, 2)
                    score = st.selectbox(
                        "Score:",
                        options=[0, 1, 2, 3],
                        index=current_score,
                        format_func=lambda x: f"{x} - {['Does not meet', 'Approaching', 'Meets', 'Exceeds'][x]}",
                        key=f"score_{item_id}"
                    )
                    st.session_state.scores[item_id] = score
                    
                    # Show rubric level
                    level_desc = item['levels'].get(str(score), "No description")
                    st.caption(f"**Level {score}:** {level_desc}")
                
                st.divider()
        
        # STEP 6: Complete Grading
        st.subheader("✅ Step 6: Complete Grading")
        
        total_score = sum(st.session_state.scores.values())
        pass_count = sum(1 for s in st.session_state.scores.values() if s >= 2)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Score", total_score)
        with col2:
            st.metric("Criteria Passed", f"{pass_count}/{len(items)}")
        with col3:
            pass_rate = pass_count / len(items) if items else 0
            st.metric("Pass Rate", f"{pass_rate:.1%}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save as Draft"):
                save_grading_result(status="draft", items=items, custom_rubric=custom_rubric, code_text=code_text)
                st.success("Draft saved!")
        
        with col2:
            if st.button("✅ Complete Grading", type="primary"):
                info = st.session_state.get('extracted_info', {})
                save_grading_result(status="completed", items=items, custom_rubric=custom_rubric, code_text=code_text)
                st.success("🎉 Grading completed!")
                
                # Clear session for next assignment
                for key in ['assignment_prompt', 'code_text', 'scores', 'justifications', 'ai_analyses', 'extracted_info']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()


def save_grading_result(status: str, items: list, custom_rubric: Dict[str, Any], code_text: str):
    """Save grading result to storage"""
    
    info = st.session_state.get('extracted_info', {})
    
    evaluation = {
        'id': str(uuid.uuid4()),
        'student_name': 'Student Submission',  # Anonymous for now
        'grader_name': info.get('grader_name', 'Unknown Grader'),
        'course': info.get('course', 'CS 1400'),
        'assignment_name': info.get('assignment_name', 'Programming Assignment'),
        'rubric_type': 'cs_programming',
        'rubric_meta': st.session_state.get('rubric_meta'),
        'assignment_prompt': st.session_state.assignment_prompt,
        'code_text': code_text,
        'scores': st.session_state.scores,
        'justifications': st.session_state.justifications,
        'ai_analyses': st.session_state.get('ai_analyses', {}),
        'total_score': sum(st.session_state.scores.values()),
        'status': status,
        'created_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat() if status == 'completed' else None,
        'is_synthetic': info.get('topics') is not None  # Mark as synthetic if it has topics
    }
    
    save_evaluation(evaluation)

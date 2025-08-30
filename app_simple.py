#!/usr/bin/env python3
"""
CS AI Grader - Simple UX for UVU Computer Science
Clean, focused interface for AI-assisted assignment grading
"""

import streamlit as st
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Imports
from data.rubric_loader import get_sample_cs_rubric, rubric_to_items
from data.synthetic_rubric_generator import generate_assignment_package
from services.code_analysis_service import analyze_python_code
from services.openai_service import OpenAIService
from utils.storage import save_evaluation

# Page config
st.set_page_config(
    page_title="CS AI Grader",
    page_icon="💻",
    layout="wide"
)

# Initialize services
openai_service = OpenAIService()

def main():
    """Main app - simple single page"""
    
    # Header
    st.title("💻 CS AI Grader")
    st.caption("Utah Valley University - Computer Science Department")
    
    # Initialize session state
    if 'assignment_data' not in st.session_state:
        st.session_state.assignment_data = None
    if 'grading_complete' not in st.session_state:
        st.session_state.grading_complete = False
    
    # Main workflow
    if not st.session_state.assignment_data:
        show_assignment_setup()
    elif not st.session_state.grading_complete:
        show_grading_interface()
    else:
        show_results()

def show_assignment_setup():
    """Step 1: Set up assignment for grading"""
    
    st.header("🚀 Start Grading")
    
    # Quick test option
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Option 1: Quick Test with Synthetic Data")
        if st.button("🎲 Generate Test Assignment", type="primary", use_container_width=True):
            # Generate complete synthetic package
            package = generate_assignment_package("intermediate")
            
            st.session_state.assignment_data = {
                'course': 'CS 1400',
                'assignment_name': package['assignment']['name'],
                'prompt': package['assignment']['prompt'],
                'code': package['sample_solution'],
                'rubric': package['rubric'],
                'is_synthetic': True
            }
            st.rerun()
    
    with col2:
        st.markdown("### Option 2: Real Assignment")
        if st.button("📝 Manual Setup", use_container_width=True):
            st.session_state.show_manual = True
            st.rerun()
    
    # Manual setup form
    if st.session_state.get('show_manual', False):
        st.markdown("---")
        st.subheader("📋 Assignment Details")
        
        with st.form("assignment_form"):
            col1, col2 = st.columns(2)
            with col1:
                course = st.text_input("Course", value="CS 1400")
                assignment_name = st.text_input("Assignment Name")
            with col2:
                grader_name = st.text_input("Grader Name")
                student_id = st.text_input("Student ID (optional)")
            
            prompt = st.text_area("Assignment Prompt", height=100)
            code = st.text_area("Student Code", height=200, placeholder="# Paste Python code here")
            
            submitted = st.form_submit_button("✅ Start Grading", type="primary")
            
            if submitted and assignment_name and code:
                st.session_state.assignment_data = {
                    'course': course,
                    'assignment_name': assignment_name,
                    'grader_name': grader_name,
                    'student_id': student_id,
                    'prompt': prompt,
                    'code': code,
                    'rubric': get_sample_cs_rubric(),
                    'is_synthetic': False
                }
                st.session_state.show_manual = False
                st.rerun()

def show_grading_interface():
    """Step 2: AI grading and review"""
    
    data = st.session_state.assignment_data
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"📝 {data['assignment_name']}")
        st.caption(f"Course: {data['course']}")
    with col2:
        if st.button("🔄 Start Over"):
            st.session_state.assignment_data = None
            st.session_state.grading_complete = False
            st.rerun()
    
    # Show assignment and code
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("📋 Assignment")
        if data['prompt']:
            st.text_area("Prompt", data['prompt'], height=150, disabled=True)
        else:
            st.info("No prompt provided")
    
    with col2:
        st.subheader("💻 Student Code")
        st.code(data['code'], language="python")
    
    # Generate AI feedback
    st.markdown("---")
    if 'ai_feedback' not in st.session_state:
        if st.button("🤖 Generate AI Feedback", type="primary", use_container_width=True):
            if not openai_service.is_enabled():
                st.error("OpenAI API key required. Check Settings.")
                return
            
            with st.spinner("Analyzing code and generating feedback..."):
                try:
                    metrics = analyze_python_code(data['code'])
                    result = openai_service.generate_code_feedback(
                        rubric=data['rubric'],
                        code_text=data['code'],
                        metrics=metrics,
                        assignment_name=data['assignment_name']
                    )
                    
                    st.session_state.ai_feedback = result
                    st.success("✅ AI feedback generated!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"AI feedback failed: {e}")
    else:
        # Show grading interface
        st.subheader("📊 Review & Edit Scores")
        
        feedback = st.session_state.ai_feedback
        rubric = data['rubric']
        
        scores = {}
        justifications = {}
        
        for criterion in rubric['criteria']:
            crit_id = criterion['id']
            
            st.markdown(f"**{criterion['code']}: {criterion['title']}**")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                ai_text = feedback.get('feedback', {}).get(crit_id, 'No AI feedback')
                edited_feedback = st.text_area(
                    "Feedback:",
                    value=ai_text,
                    height=80,
                    key=f"feedback_{crit_id}"
                )
                justifications[crit_id] = edited_feedback
            
            with col2:
                ai_score = feedback.get('scores', {}).get(crit_id, 2)
                if isinstance(ai_score, str):
                    ai_score = 2
                
                score = st.selectbox(
                    "Score:",
                    options=[0, 1, 2, 3],
                    index=ai_score,
                    format_func=lambda x: f"{x} - {['Poor', 'Fair', 'Good', 'Excellent'][x]}",
                    key=f"score_{crit_id}"
                )
                scores[crit_id] = score
            
            st.divider()
        
        # Complete grading
        col1, col2 = st.columns([2, 1])
        with col1:
            total_score = sum(scores.values())
            pass_count = sum(1 for s in scores.values() if s >= 2)
            st.metric("Total Score", f"{total_score}/{len(scores)*3}")
            st.metric("Criteria Passed", f"{pass_count}/{len(scores)}")
        
        with col2:
            if st.button("✅ Complete Grading", type="primary", use_container_width=True):
                # Save result
                save_grading_data(data, scores, justifications, feedback)
                st.session_state.final_scores = scores
                st.session_state.final_justifications = justifications
                st.session_state.grading_complete = True
                st.rerun()

def show_results():
    """Step 3: Show results with AI-powered features"""
    
    data = st.session_state.assignment_data
    scores = st.session_state.get('final_scores', {})
    justifications = st.session_state.get('final_justifications', {})
    
    st.header("🎉 Grading Complete!")
    st.success("Assignment has been graded and saved to the research database.")
    
    # Show summary
    total_score = sum(scores.values())
    max_score = len(scores) * 3
    percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Score", f"{total_score}/{max_score}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        status = "Excellent" if percentage >= 90 else "Good" if percentage >= 80 else "Needs Work"
        st.metric("Status", status)
    
    # AI-Powered Features
    st.markdown("---")
    st.subheader("🤖 AI-Powered Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Generate Student Email", use_container_width=True):
            if openai_service.is_enabled():
                with st.spinner("Writing personalized email..."):
                    try:
                        email = openai_service.generate_student_email(
                            student_name=data.get('student_id', 'Student'),
                            assignment_name=data['assignment_name'],
                            scores=scores,
                            feedback=justifications,
                            course=data['course'],
                            instructor_name=data.get('grader_name', 'Instructor')
                        )
                        st.session_state.generated_email = email
                        st.success("✅ Email generated!")
                    except Exception as e:
                        st.error(f"Email generation failed: {e}")
            else:
                st.error("OpenAI API key required")
    
    with col2:
        if st.button("💡 Improvement Suggestions", use_container_width=True):
            if openai_service.is_enabled():
                with st.spinner("Generating improvement suggestions..."):
                    try:
                        suggestions = openai_service.generate_improvement_suggestions(
                            code=data['code'],
                            rubric_feedback=justifications,
                            assignment_context=f"{data['course']} - {data['assignment_name']}"
                        )
                        st.session_state.improvement_suggestions = suggestions
                        st.success("✅ Suggestions generated!")
                    except Exception as e:
                        st.error(f"Suggestion generation failed: {e}")
            else:
                st.error("OpenAI API key required")
    
    with col3:
        if st.button("🔍 Code Analysis Report", use_container_width=True):
            st.session_state.show_analysis = True
            st.success("✅ Analysis ready!")
    
    # Show generated content
    if st.session_state.get('generated_email'):
        st.subheader("📧 Generated Email")
        with st.expander("Student Email", expanded=True):
            st.text_area("Email Content", st.session_state.generated_email, height=300)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Download Email",
                    data=st.session_state.generated_email,
                    file_name=f"feedback_email_{data['assignment_name'].replace(' ', '_')}.txt",
                    mime="text/plain"
                )
            with col2:
                if st.button("📋 Copy to Clipboard"):
                    st.code(st.session_state.generated_email)
    
    if st.session_state.get('improvement_suggestions'):
        st.subheader("💡 Improvement Suggestions")
        with st.expander("For Student", expanded=True):
            st.markdown(st.session_state.improvement_suggestions)
    
    if st.session_state.get('show_analysis'):
        st.subheader("🔍 Code Analysis Report")
        with st.expander("Technical Analysis", expanded=True):
            try:
                metrics = analyze_python_code(data['code'])
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
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Grade Another Assignment", type="primary", use_container_width=True):
            # Clear all session state
            for key in ['assignment_data', 'grading_complete', 'ai_feedback', 'final_scores', 
                       'final_justifications', 'generated_email', 'improvement_suggestions', 'show_analysis']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("🚀 Quick Test Again", use_container_width=True):
            # Generate new test assignment
            package = generate_assignment_package("intermediate")
            st.session_state.assignment_data = {
                'course': 'CS 1400',
                'assignment_name': package['assignment']['name'],
                'prompt': package['assignment']['prompt'],
                'code': package['sample_solution'],
                'rubric': package['rubric'],
                'is_synthetic': True
            }
            st.session_state.grading_complete = False
            if 'ai_feedback' in st.session_state:
                del st.session_state.ai_feedback
            st.rerun()

def save_grading_data(assignment_data, scores, justifications, ai_feedback):
    """Save grading data securely"""
    
    evaluation = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'course': assignment_data['course'],
        'assignment_name': assignment_data['assignment_name'],
        'grader_name': assignment_data.get('grader_name', 'Anonymous'),
        'student_id_hash': hash(assignment_data.get('student_id', 'anonymous')),  # Hash for privacy
        'assignment_prompt': assignment_data['prompt'],
        'code_text': assignment_data['code'],
        'rubric_name': assignment_data['rubric']['name'],
        'ai_scores': ai_feedback.get('scores', {}),
        'ai_feedback': ai_feedback.get('feedback', {}),
        'final_scores': scores,
        'final_justifications': justifications,
        'total_score': sum(scores.values()),
        'is_synthetic': assignment_data.get('is_synthetic', False),
        'rubric_type': 'cs_programming'
    }
    
    save_evaluation(evaluation)

def show_research_summary():
    """Show research data summary"""
    st.subheader("📊 Research Data Summary")
    
    evaluations = load_evaluations()
    cs_evals = [e for e in evaluations if e.get('rubric_type') == 'cs_programming']
    
    if cs_evals:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Assignments", len(cs_evals))
        with col2:
            completed = len([e for e in cs_evals if e.get('status') == 'completed'])
            st.metric("Completed", completed)
        with col3:
            synthetic = len([e for e in cs_evals if e.get('is_synthetic', False)])
            st.metric("Synthetic", synthetic)
        
        # Show recent assignments
        st.subheader("Recent Assignments")
        for i, eval_data in enumerate(cs_evals[-5:]):  # Last 5
            with st.expander(f"{eval_data.get('assignment_name', 'Unknown')} - {eval_data.get('timestamp', '')[:10]}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Course:** {eval_data.get('course', 'N/A')}")
                    st.write(f"**Total Score:** {eval_data.get('total_score', 0)}")
                with col2:
                    st.write(f"**Grader:** {eval_data.get('grader_name', 'N/A')}")
                    st.write(f"**Status:** {eval_data.get('status', 'N/A')}")
    else:
        st.info("No grading data yet. Complete some assignments to see analytics.")

def show_settings():
    """Simple settings page"""
    st.header("⚙️ Settings")
    
    # API Key
    st.subheader("🤖 OpenAI Configuration")
    
    if openai_service.is_enabled():
        st.success("✅ AI features enabled")
        st.info(f"Model: {openai_service.model}")
    else:
        st.warning("⚠️ OpenAI API key required")
        
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        if st.button("Save API Key") and api_key:
            import os
            os.environ['OPENAI_API_KEY'] = api_key
            st.success("API key saved for this session")
            st.rerun()
    
    # Data management
    st.subheader("💾 Data Management")
    
    evaluations = load_evaluations()
    cs_evals = [e for e in evaluations if e.get('rubric_type') == 'cs_programming']
    
    if cs_evals:
        st.info(f"Currently storing {len(cs_evals)} CS assignment evaluations")
        
        if st.button("📥 Export Research Data"):
            import json
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_assignments': len(cs_evals),
                'assignments': cs_evals
            }
            
            st.download_button(
                "📥 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"cs_grading_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    # About
    st.subheader("ℹ️ About")
    st.write("""
    **CS AI Grader** helps UVU Computer Science instructors and TAs grade programming assignments 
    with AI assistance. All grading data is stored securely for research purposes.
    """)
    
    if st.button("← Back to Grading"):
        st.session_state.show_settings = False
        st.rerun()

if __name__ == "__main__":
    main()

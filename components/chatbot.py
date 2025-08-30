"""
Integrated chatbot for CS AI Grader
Provides direct GPT-5-mini access to professors/TAs with context awareness
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any
import json

from services.openai_service import OpenAIService
from services.analytics_service import analytics


def show_chatbot_sidebar():
    """Show chatbot in sidebar for professor/TA assistance"""
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 AI Assistant")
    st.sidebar.caption("Chat with GPT-5-mini")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chat_context' not in st.session_state:
        st.session_state.chat_context = {}
    
    openai_service = OpenAIService()
    
    if not openai_service.is_enabled():
        st.sidebar.error("🔑 API key required")
        return
    
    # Context awareness toggle
    use_context = st.sidebar.checkbox("🧠 Use Grading Context", value=True, 
                                     help="Include current assignment/grading data in chat")
    
    # Document upload for chatbot
    uploaded_doc = st.sidebar.file_uploader(
        "📄 Upload Document",
        type=['txt', 'pdf', 'py', 'md'],
        help="Upload document for AI to reference in chat"
    )
    
    if uploaded_doc:
        try:
            if uploaded_doc.type == "text/plain" or uploaded_doc.name.endswith('.py'):
                doc_content = uploaded_doc.read().decode('utf-8')
            elif uploaded_doc.name.endswith('.pdf'):
                # Basic PDF text extraction
                import pdfplumber
                with pdfplumber.open(uploaded_doc) as pdf:
                    doc_content = "\n".join([page.extract_text() for page in pdf.pages])
            else:
                doc_content = uploaded_doc.read().decode('utf-8')
            
            st.session_state.chat_context['uploaded_doc'] = {
                'name': uploaded_doc.name,
                'content': doc_content[:3000],  # Limit size
                'type': uploaded_doc.type
            }
            st.sidebar.success(f"✅ {uploaded_doc.name} loaded")
        except Exception as e:
            st.sidebar.error(f"Failed to load document: {e}")
    
    # Chat interface
    with st.sidebar.container():
        # Show recent chat history (last 3 messages)
        if st.session_state.chat_history:
            st.markdown("**Recent Chat:**")
            for msg in st.session_state.chat_history[-3:]:
                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                st.caption(f"{role_icon} {msg['content'][:60]}...")
        
        # Quick suggestions
        suggestions = get_chatbot_suggestions()
        selected_suggestion = st.selectbox(
            "💡 Quick Questions:",
            [""] + suggestions,
            format_func=lambda x: "Choose a suggestion..." if x == "" else x
        )
        
        # Chat input - use form to handle input clearing properly
        with st.form("chat_form", clear_on_submit=True):
            user_message = st.text_area(
                "Ask AI Assistant:",
                value=selected_suggestion if selected_suggestion else "",
                placeholder="How can I improve this rubric?\nWhat are common Python mistakes?\nHelp me write feedback...",
                height=80
            )
            
            submitted = st.form_submit_button("💬 Send", use_container_width=True)
            if submitted and user_message.strip():
                with st.spinner("🤖 AI thinking..."):
                    success = send_chat_message(user_message, use_context, openai_service)
                    if success:
                        st.rerun()
            elif submitted:
                st.sidebar.error("Please enter a message")
        
        # Clear button outside the form
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.chat_context = {}
            st.sidebar.success("Chat cleared!")
            st.rerun()
    
    # Show full chat if requested
    if st.sidebar.button("💬 Full Chat"):
        st.session_state.show_full_chat = not st.session_state.get('show_full_chat', False)
        st.rerun()


def send_chat_message(message: str, use_context: bool, openai_service: OpenAIService) -> bool:
    """Send message to AI and get response. Returns True if successful."""
    
    if not openai_service.is_enabled():
        st.sidebar.error("🔑 OpenAI API key required")
        return False
    
    # Build context
    context_parts = []
    
    if use_context:
        # Add current assignment context
        if st.session_state.get('assignment_data'):
            data = st.session_state.assignment_data
            context_parts.append(f"Current Assignment: {data.get('assignment_name', 'Unknown')}")
            context_parts.append(f"Course: {data.get('course', 'Unknown')}")
            
            if data.get('prompt'):
                context_parts.append(f"Assignment Prompt: {data['prompt'][:200]}...")
        
        # Add grading results if available
        if st.session_state.get('final_scores'):
            scores = st.session_state.final_scores
            total = sum(scores.values())
            context_parts.append(f"Recent Grading: {total}/{len(scores)*3} total score")
    
    # Add uploaded document context
    if st.session_state.chat_context.get('uploaded_doc'):
        doc = st.session_state.chat_context['uploaded_doc']
        context_parts.append(f"Document: {doc['name']}")
        context_parts.append(f"Content: {doc['content'][:500]}...")
    
    # Build system prompt
    system_prompt = """You are an AI assistant helping UVU Computer Science professors and TAs with grading and teaching tasks. 
    You have access to GPT-5-mini and can help with:
    - Assignment grading and feedback
    - Rubric creation and improvement
    - Student communication
    - Code analysis and suggestions
    - Teaching strategies
    
    Be helpful, professional, and educational."""
    
    if context_parts:
        system_prompt += f"\n\nCurrent Context:\n{chr(10).join(context_parts)}"
    
    try:
        # Get AI response
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add recent chat history for context
        for msg in st.session_state.chat_history[-4:]:  # Last 4 messages
            if msg['role'] in ['user', 'assistant']:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # Add current user message
        messages.append({
            'role': 'user',
            'content': message
        })
        
        response = openai_service.client.chat.completions.create(
            model=openai_service.model,
            messages=messages,
            max_completion_tokens=500,
            temperature=1  # Use default temperature for compatibility
        )
        
        # Extract response content
        if response and response.choices and len(response.choices) > 0:
            ai_response = response.choices[0].message.content
            if ai_response:
                ai_response = ai_response.strip()
            else:
                ai_response = "I apologize, but I couldn't generate a response. Please try again."
        else:
            ai_response = "Sorry, I received an empty response. Please try again."
        
        # Add user message to history first
        st.session_state.chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Add AI response to history
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Log chat interaction for analytics
        try:
            user = st.session_state.get('user', {})
            user_id = user.get('id', 0)
            
            # Build context for analytics
            analytics_context = {
                'user_role': user.get('role', 'unknown'),
                'course': st.session_state.get('assignment_data', {}).get('course'),
                'assignment_type': st.session_state.get('assignment_data', {}).get('assignment_type'),
                'has_document': 'uploaded_doc' in st.session_state.chat_context,
                'document_type': st.session_state.chat_context.get('uploaded_doc', {}).get('type'),
                'grading_context': use_context and bool(st.session_state.get('assignment_data'))
            }
            
            # Log to analytics
            analytics.log_chat_interaction(
                user_id=user_id,
                conversation=st.session_state.chat_history,
                context=analytics_context,
                model_used=openai_service.model
            )
        except Exception as e:
            # Don't let analytics errors affect the user experience
            print(f"Analytics logging error: {e}")
        
        st.sidebar.success("✅ AI responded!")
        return True
        
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': error_msg,
            'timestamp': datetime.now().isoformat()
        })
        st.sidebar.error(f"❌ Chat error: {str(e)}")
        return False


def show_full_chat():
    """Show full chat interface in main area"""
    
    if not st.session_state.get('show_full_chat', False):
        return
    
    st.markdown("---")
    st.subheader("💬 AI Assistant Chat")
    
    # Chat history
    if st.session_state.chat_history:
        for i, msg in enumerate(st.session_state.chat_history):
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            role_name = "You" if msg['role'] == 'user' else "AI Assistant"
            
            with st.container():
                st.markdown(f"**{role_icon} {role_name}** - {msg['timestamp'][:16]}")
                st.markdown(msg['content'])
                if i < len(st.session_state.chat_history) - 1:
                    st.markdown("---")
    else:
        st.info("No chat history yet. Use the sidebar to start chatting!")
    
    # Quick actions
    st.markdown("### 🎯 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Help with Rubric"):
            send_quick_message("How can I improve my grading rubric for this assignment?")
    
    with col2:
        if st.button("📧 Email Template"):
            send_quick_message("Create an email template for providing feedback to students.")
    
    with col3:
        if st.button("🎓 Teaching Tips"):
            send_quick_message("Give me teaching tips for common programming concepts that students struggle with.")


def send_quick_message(message: str):
    """Send a predefined quick message"""
    openai_service = OpenAIService()
    if openai_service.is_enabled():
        send_chat_message(message, use_context=True, openai_service=openai_service)
        st.rerun()


def get_chatbot_suggestions():
    """Get contextual suggestions for the chatbot based on current state"""
    suggestions = [
        "How can I improve my grading efficiency?",
        "What are common Python mistakes in CS 1400?",
        "Help me write constructive feedback for struggling students.",
        "Generate a rubric for a new assignment.",
        "How should I handle potential plagiarism?",
        "What topics should I review with my class?",
        "Create an announcement about assignment expectations.",
        "Help me design a follow-up exercise."
    ]
    
    # Add context-specific suggestions
    if st.session_state.get('assignment_data'):
        data = st.session_state.assignment_data
        suggestions.insert(0, f"How can I improve the '{data.get('assignment_name', 'current')}' assignment?")
        suggestions.insert(1, "What common issues should I look for in this type of assignment?")
    
    if st.session_state.get('final_scores'):
        suggestions.insert(0, "Help me write a class summary based on these grading results.")
        suggestions.insert(1, "What should I tell students who scored low on this assignment?")
    
    return suggestions[:6]  # Return top 6 suggestions

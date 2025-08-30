"""
Authentication components for CS AI Grader
"""

import streamlit as st
from database.db_manager import db


def show_login_form():
    """Show login form"""
    
    st.title("🔐 CS AI Grader Login")
    st.caption("Utah Valley University - Computer Science Department")
    
    tab1, tab2 = st.tabs(["🔑 Login", "👤 Register"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_clicked = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
            with col2:
                demo_clicked = st.form_submit_button("🧪 Demo Mode", use_container_width=True)
            
            if login_clicked:
                if username and password:
                    user = db.authenticate_user(username, password)
                    if user:
                        # Create session
                        session_id = db.create_session(user['id'])
                        
                        # Store in Streamlit session
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.session_id = session_id
                        
                        st.success(f"✅ Welcome back, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.error("Please enter username and password")
            
            if demo_clicked:
                # Demo mode - no authentication required
                st.session_state.authenticated = True
                st.session_state.user = {
                    'id': 0,
                    'username': 'demo_user',
                    'email': 'demo@uvu.edu',
                    'role': 'professor',
                    'department': 'Computer Science'
                }
                st.session_state.demo_mode = True
                st.success("✅ Demo mode activated!")
                st.rerun()
    
    with tab2:
        with st.form("register_form"):
            st.subheader("Register New User")
            st.caption("For UVU CS Department faculty and TAs")
            
            new_username = st.text_input("Username")
            new_email = st.text_input("Email (@uvu.edu)")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            role = st.selectbox("Role", ["professor", "ta"])
            courses = st.multiselect("Courses", ["CS 1400", "CS 1410", "CS 2420", "CS 2450", "CS 3005"])
            
            register_clicked = st.form_submit_button("👤 Register", type="primary")
            
            if register_clicked:
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                elif not new_email.endswith('@uvu.edu'):
                    st.error("Please use UVU email address")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    try:
                        user_id = db.create_user(
                            username=new_username,
                            email=new_email,
                            password=new_password,
                            role=role,
                            courses=courses
                        )
                        st.success("✅ Account created! Please login.")
                    except Exception as e:
                        st.error(f"Registration failed: {e}")


def check_authentication():
    """Check if user is authenticated"""
    
    if not st.session_state.get('authenticated', False):
        return False
    
    # Skip session validation in demo mode
    if st.session_state.get('demo_mode', False):
        return True
    
    # Validate session
    session_id = st.session_state.get('session_id')
    if session_id:
        session_data = db.validate_session(session_id)
        if session_data:
            # Update user data in session
            st.session_state.user = session_data
            return True
        else:
            # Session expired
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.session_id = None
            return False
    
    return False


def show_user_info():
    """Show user info in sidebar"""
    
    if not st.session_state.get('authenticated', False):
        return
    
    user = st.session_state.get('user', {})
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 User Info")
    
    if st.session_state.get('demo_mode', False):
        st.sidebar.info("🧪 Demo Mode")
    
    st.sidebar.write(f"**{user.get('username', 'Unknown')}**")
    st.sidebar.caption(f"{user.get('role', 'user').title()} - {user.get('department', 'CS')}")
    
    if st.sidebar.button("🚪 Logout"):
        # Invalidate session
        if st.session_state.get('session_id') and not st.session_state.get('demo_mode'):
            db.invalidate_session(st.session_state.session_id)
        
        # Clear session state
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.session_id = None
        st.session_state.demo_mode = False
        st.rerun()

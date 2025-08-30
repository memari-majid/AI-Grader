"""
Analytics Dashboard for CS AI Grader
View app usage statistics and insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from components.auth import check_authentication
from services.analytics_service import analytics
from styles.uvu_theme import apply_uvu_theme, create_uvu_header, create_uvu_footer


def main():
    """Analytics dashboard - admin only"""
    
    # Apply UVU theme
    apply_uvu_theme()
    
    # Check authentication and admin access
    if not check_authentication():
        st.error("🔒 Please login to access analytics")
        st.stop()
    
    user = st.session_state.get('user', {})
    if user.get('role') != 'admin':
        st.error("🔒 Admin access required for analytics")
        st.stop()
    
    # Header
    create_uvu_header("Analytics Dashboard", "CS AI Grader Usage Insights")
    
    # Date range selector
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        days = st.selectbox("Time Period", [7, 14, 30, 90], index=0)
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Get analytics summary
    with st.spinner("Loading analytics..."):
        summary = analytics.get_analytics_summary(days=days)
    
    # Key Metrics
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Active Users",
            summary['total_users'],
            help="Unique users in period"
        )
    
    with col2:
        st.metric(
            "Grading Sessions",
            summary['total_sessions'],
            help="Total grading sessions completed"
        )
    
    with col3:
        st.metric(
            "Chat Interactions",
            summary['total_chats'],
            help="AI Assistant conversations"
        )
    
    with col4:
        error_rate = summary.get('error_rate', 0)
        st.metric(
            "Error Rate",
            f"{error_rate:.1f}%",
            help="Percentage of sessions with errors"
        )
    
    # Grading Statistics
    st.markdown("---")
    st.markdown("### 📈 Grading Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        avg_scores = summary.get('average_scores', {})
        if avg_scores.get('sessions_count', 0) > 0:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_scores.get('average_percentage', 0),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Average Score %"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#275D38"},
                    'steps': [
                        {'range': [0, 60], 'color': "#FFE5E5"},
                        {'range': [60, 80], 'color': "#FFF5E5"},
                        {'range': [80, 100], 'color': "#E5FFE5"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No grading data available")
    
    with col2:
        # Feature usage chart
        feature_usage = summary.get('feature_usage', {})
        if feature_usage:
            df = pd.DataFrame(
                list(feature_usage.items()),
                columns=['Feature', 'Usage Count']
            )
            fig = px.bar(
                df, 
                x='Feature', 
                y='Usage Count',
                title="Feature Usage",
                color_discrete_sequence=["#275D38"]
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No feature usage data available")
    
    # Chat Analytics
    st.markdown("---")
    st.markdown("### 💬 Chat Analytics")
    
    chat_metrics = summary.get('chat_metrics', {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Chats",
            chat_metrics.get('total_chats', 0)
        )
    
    with col2:
        st.metric(
            "Avg. Conversation Length",
            f"{chat_metrics.get('avg_conversation_length', 0):.1f} messages"
        )
    
    with col3:
        st.metric(
            "Unique Chat Users",
            chat_metrics.get('unique_users', 0)
        )
    
    # Popular Features
    st.markdown("---")
    st.markdown("### 🌟 Popular Features")
    
    popular_features = summary.get('popular_features', [])
    if popular_features:
        for i, feature in enumerate(popular_features, 1):
            st.write(f"{i}. **{feature['feature']}** - {feature['usage_count']} uses")
    else:
        st.info("No feature data available")
    
    # User Retention
    st.markdown("---")
    st.markdown("### 👥 User Retention")
    
    retention = summary.get('user_retention', {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Users",
            retention.get('total_users', 0)
        )
    
    with col2:
        st.metric(
            "Returning Users",
            retention.get('returning_users', 0)
        )
    
    with col3:
        retention_rate = retention.get('retention_rate', 0)
        st.metric(
            "Retention Rate",
            f"{retention_rate:.1f}%"
        )
    
    # Export Options
    st.markdown("---")
    st.markdown("### 📥 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "JSON", "Excel"]
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 Export Analytics"):
            with st.spinner("Exporting data..."):
                try:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days)
                    
                    file_path = analytics.export_analytics_data(
                        start_date=start_date,
                        end_date=end_date,
                        export_format=export_format.lower()
                    )
                    
                    st.success(f"✅ Data exported to: {file_path}")
                    
                    # Provide download link
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Export",
                            data=f.read(),
                            file_name=file_path.split('/')[-1],
                            mime="application/octet-stream"
                        )
                except Exception as e:
                    st.error(f"Export failed: {e}")
    
    # Footer
    create_uvu_footer()


if __name__ == "__main__":
    main()

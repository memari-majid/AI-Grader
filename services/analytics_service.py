"""
Analytics and Logging Service for CS AI Grader
Comprehensive data collection for app improvement
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
from pathlib import Path
import hashlib
import uuid

from database.db_manager import db


class AnalyticsService:
    """Service for comprehensive analytics and data collection"""
    
    def __init__(self):
        """Initialize analytics service"""
        self.analytics_dir = Path("analytics_data")
        self.analytics_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different types of data
        self.chat_logs_dir = self.analytics_dir / "chat_logs"
        self.grading_logs_dir = self.analytics_dir / "grading_sessions"
        self.usage_logs_dir = self.analytics_dir / "usage_metrics"
        self.error_logs_dir = self.analytics_dir / "error_logs"
        self.feedback_logs_dir = self.analytics_dir / "user_feedback"
        
        for dir_path in [self.chat_logs_dir, self.grading_logs_dir, 
                         self.usage_logs_dir, self.error_logs_dir, self.feedback_logs_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def log_chat_interaction(self, user_id: int, conversation: List[Dict], 
                           context: Dict[str, Any], model_used: str,
                           tokens_used: Optional[int] = None) -> str:
        """
        Log chat interaction for analysis
        
        Args:
            user_id: User ID
            conversation: Full conversation history
            context: Context data (assignment, course, etc.)
            model_used: OpenAI model used
            tokens_used: Optional token count
            
        Returns:
            Log ID for reference
        """
        log_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Anonymize sensitive data
        anonymized_conversation = self._anonymize_conversation(conversation)
        
        log_data = {
            'log_id': log_id,
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'user_role': context.get('user_role', 'unknown'),
            'model_used': model_used,
            'tokens_used': tokens_used,
            'conversation_length': len(conversation),
            'conversation': anonymized_conversation,
            'context': {
                'course': context.get('course'),
                'assignment_type': context.get('assignment_type'),
                'has_document': context.get('has_document', False),
                'document_type': context.get('document_type'),
                'grading_context': context.get('grading_context', False)
            },
            'metrics': self._calculate_chat_metrics(conversation)
        }
        
        # Save to file
        file_path = self.chat_logs_dir / f"chat_{timestamp.strftime('%Y%m%d')}_{log_id}.json"
        with open(file_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Also save to database for quick queries
        db.log_analytics_event(
            event_type='chat_interaction',
            user_id=user_id,
            event_data=log_data,
            timestamp=timestamp
        )
        
        return log_id
    
    def log_grading_session(self, user_id: int, grading_data: Dict[str, Any]) -> str:
        """
        Log complete grading session data
        
        Args:
            user_id: User ID
            grading_data: All grading session data
            
        Returns:
            Session ID for reference
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        log_data = {
            'session_id': session_id,
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'course': grading_data.get('course'),
            'assignment_name': grading_data.get('assignment_name'),
            'assignment_type': grading_data.get('assignment_type', 'unknown'),
            'is_synthetic': grading_data.get('is_synthetic', False),
            'rubric_items_count': len(grading_data.get('rubric', {})),
            'code_metrics': grading_data.get('code_metrics', {}),
            'grading_results': {
                'total_score': grading_data.get('total_score'),
                'max_score': grading_data.get('max_score'),
                'percentage': grading_data.get('percentage'),
                'score_distribution': grading_data.get('score_distribution', {}),
                'time_taken_seconds': grading_data.get('time_taken'),
                'ai_calls_made': grading_data.get('ai_calls_made', 0)
            },
            'feedback_quality': self._analyze_feedback_quality(
                grading_data.get('feedback', {}),
                grading_data.get('justifications', {})
            ),
            'user_actions': grading_data.get('user_actions', [])
        }
        
        # Save to file
        file_path = self.grading_logs_dir / f"grading_{timestamp.strftime('%Y%m%d')}_{session_id}.json"
        with open(file_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Save to database
        db.log_analytics_event(
            event_type='grading_session',
            user_id=user_id,
            event_data=log_data,
            timestamp=timestamp
        )
        
        return session_id
    
    def log_usage_metric(self, user_id: int, feature: str, action: str, 
                        metadata: Optional[Dict] = None) -> None:
        """
        Log feature usage metrics
        
        Args:
            user_id: User ID
            feature: Feature name (e.g., 'quick_test', 'rubric_generator')
            action: Action taken (e.g., 'clicked', 'completed', 'abandoned')
            metadata: Additional metadata
        """
        timestamp = datetime.now()
        
        log_data = {
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'feature': feature,
            'action': action,
            'metadata': metadata or {},
            'session_id': self._get_session_id()
        }
        
        # Append to daily usage log
        file_path = self.usage_logs_dir / f"usage_{timestamp.strftime('%Y%m%d')}.jsonl"
        with open(file_path, 'a') as f:
            f.write(json.dumps(log_data) + '\n')
        
        # Quick database log
        db.log_analytics_event(
            event_type='usage_metric',
            user_id=user_id,
            event_data=log_data,
            timestamp=timestamp
        )
    
    def log_error(self, user_id: Optional[int], error_type: str, 
                  error_details: Dict[str, Any]) -> None:
        """
        Log errors for debugging and improvement
        
        Args:
            user_id: User ID (optional)
            error_type: Type of error
            error_details: Error details including traceback
        """
        timestamp = datetime.now()
        
        log_data = {
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'error_type': error_type,
            'error_details': error_details,
            'session_id': self._get_session_id(),
            'app_state': self._get_app_state_summary()
        }
        
        # Save to error log
        file_path = self.error_logs_dir / f"errors_{timestamp.strftime('%Y%m%d')}.jsonl"
        with open(file_path, 'a') as f:
            f.write(json.dumps(log_data) + '\n')
    
    def log_user_feedback(self, user_id: int, feedback_type: str, 
                         feedback_data: Dict[str, Any]) -> None:
        """
        Log user feedback for improvement
        
        Args:
            user_id: User ID
            feedback_type: Type of feedback
            feedback_data: Feedback details
        """
        timestamp = datetime.now()
        
        log_data = {
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'feedback_type': feedback_type,
            'feedback_data': feedback_data,
            'context': self._get_current_context()
        }
        
        # Save feedback
        file_path = self.feedback_logs_dir / f"feedback_{timestamp.strftime('%Y%m%d')}_{user_id}.jsonl"
        with open(file_path, 'a') as f:
            f.write(json.dumps(log_data) + '\n')
        
        # Save to database
        db.log_analytics_event(
            event_type='user_feedback',
            user_id=user_id,
            event_data=log_data,
            timestamp=timestamp
        )
    
    def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get analytics summary for dashboard
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Analytics summary data
        """
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=days)
        
        # Get data from database
        events = db.get_analytics_events(start_date, end_date)
        
        summary = {
            'period': f'{days} days',
            'total_users': len(set(e['user_id'] for e in events if e['user_id'])),
            'total_sessions': len([e for e in events if e['event_type'] == 'grading_session']),
            'total_chats': len([e for e in events if e['event_type'] == 'chat_interaction']),
            'feature_usage': self._calculate_feature_usage(events),
            'error_rate': self._calculate_error_rate(events),
            'average_scores': self._calculate_average_scores(events),
            'chat_metrics': self._calculate_chat_analytics(events),
            'popular_features': self._get_popular_features(events),
            'user_retention': self._calculate_retention(events)
        }
        
        return summary
    
    def export_analytics_data(self, start_date: datetime, end_date: datetime,
                            export_format: str = 'csv') -> str:
        """
        Export analytics data for external analysis
        
        Args:
            start_date: Start date
            end_date: End date
            export_format: Format ('csv', 'json', 'excel')
            
        Returns:
            Path to exported file
        """
        events = db.get_analytics_events(start_date, end_date)
        
        export_dir = self.analytics_dir / "exports"
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'csv':
            df = pd.DataFrame(events)
            file_path = export_dir / f"analytics_export_{timestamp}.csv"
            df.to_csv(file_path, index=False)
        elif export_format == 'json':
            file_path = export_dir / f"analytics_export_{timestamp}.json"
            with open(file_path, 'w') as f:
                json.dump(events, f, indent=2)
        elif export_format == 'excel':
            df = pd.DataFrame(events)
            file_path = export_dir / f"analytics_export_{timestamp}.xlsx"
            df.to_excel(file_path, index=False)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        return str(file_path)
    
    # Helper methods
    def _anonymize_conversation(self, conversation: List[Dict]) -> List[Dict]:
        """Anonymize sensitive data in conversations"""
        anonymized = []
        for msg in conversation:
            anonymized_msg = msg.copy()
            # Remove any potential student names or IDs
            anonymized_msg['content'] = self._remove_pii(msg.get('content', ''))
            anonymized.append(anonymized_msg)
        return anonymized
    
    def _remove_pii(self, text: str) -> str:
        """Remove potential PII from text"""
        # Simple implementation - can be enhanced with NLP
        import re
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '[EMAIL]', text)
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        # Remove potential student IDs (adjust pattern as needed)
        text = re.sub(r'\b\d{6,10}\b', '[ID]', text)
        return text
    
    def _calculate_chat_metrics(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics from chat conversation"""
        user_messages = [m for m in conversation if m.get('role') == 'user']
        assistant_messages = [m for m in conversation if m.get('role') == 'assistant']
        
        return {
            'total_messages': len(conversation),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'avg_user_message_length': sum(len(m.get('content', '')) for m in user_messages) / max(len(user_messages), 1),
            'avg_assistant_message_length': sum(len(m.get('content', '')) for m in assistant_messages) / max(len(assistant_messages), 1),
            'conversation_duration_estimate': len(conversation) * 30  # Rough estimate in seconds
        }
    
    def _analyze_feedback_quality(self, feedback: Dict, justifications: Dict) -> Dict[str, Any]:
        """Analyze the quality of generated feedback"""
        total_feedback_length = sum(len(str(f)) for f in feedback.values())
        total_justification_length = sum(len(str(j)) for j in justifications.values())
        
        return {
            'feedback_items': len(feedback),
            'justification_items': len(justifications),
            'avg_feedback_length': total_feedback_length / max(len(feedback), 1),
            'avg_justification_length': total_justification_length / max(len(justifications), 1),
            'has_empty_feedback': any(not f for f in feedback.values()),
            'has_empty_justifications': any(not j for j in justifications.values())
        }
    
    def _get_session_id(self) -> str:
        """Get or create session ID"""
        # In a real app, this would come from session state
        return str(uuid.uuid4())
    
    def _get_app_state_summary(self) -> Dict[str, Any]:
        """Get summary of current app state for error context"""
        # This would capture relevant app state
        return {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current context for feedback"""
        return {
            'timestamp': datetime.now().isoformat(),
            'page': 'unknown',  # Would come from session state
            'feature': 'unknown'
        }
    
    def _calculate_feature_usage(self, events: List[Dict]) -> Dict[str, int]:
        """Calculate feature usage statistics"""
        usage_events = [e for e in events if e['event_type'] == 'usage_metric']
        feature_counts = {}
        
        for event in usage_events:
            feature = event.get('event_data', {}).get('feature', 'unknown')
            feature_counts[feature] = feature_counts.get(feature, 0) + 1
        
        return feature_counts
    
    def _calculate_error_rate(self, events: List[Dict]) -> float:
        """Calculate error rate"""
        total_events = len(events)
        error_events = len([e for e in events if 'error' in e.get('event_type', '').lower()])
        
        return (error_events / max(total_events, 1)) * 100
    
    def _calculate_average_scores(self, events: List[Dict]) -> Dict[str, float]:
        """Calculate average grading scores"""
        grading_sessions = [e for e in events if e['event_type'] == 'grading_session']
        
        if not grading_sessions:
            return {'average_percentage': 0, 'sessions_count': 0}
        
        percentages = []
        for session in grading_sessions:
            percentage = session.get('event_data', {}).get('grading_results', {}).get('percentage', 0)
            if percentage:
                percentages.append(percentage)
        
        return {
            'average_percentage': sum(percentages) / max(len(percentages), 1),
            'sessions_count': len(grading_sessions)
        }
    
    def _calculate_chat_analytics(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate chat-specific analytics"""
        chat_events = [e for e in events if e['event_type'] == 'chat_interaction']
        
        if not chat_events:
            return {'total_chats': 0, 'avg_conversation_length': 0}
        
        conversation_lengths = []
        for chat in chat_events:
            length = chat.get('event_data', {}).get('conversation_length', 0)
            conversation_lengths.append(length)
        
        return {
            'total_chats': len(chat_events),
            'avg_conversation_length': sum(conversation_lengths) / max(len(conversation_lengths), 1),
            'unique_users': len(set(e['user_id'] for e in chat_events if e.get('user_id')))
        }
    
    def _get_popular_features(self, events: List[Dict]) -> List[Dict[str, Any]]:
        """Get most popular features"""
        feature_usage = self._calculate_feature_usage(events)
        
        # Sort by usage count
        sorted_features = sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'feature': feature, 'usage_count': count}
            for feature, count in sorted_features[:5]  # Top 5
        ]
    
    def _calculate_retention(self, events: List[Dict]) -> Dict[str, float]:
        """Calculate user retention metrics"""
        # Group events by user and date
        user_dates = {}
        for event in events:
            user_id = event.get('user_id')
            if user_id:
                date = datetime.fromisoformat(event['timestamp']).date()
                if user_id not in user_dates:
                    user_dates[user_id] = set()
                user_dates[user_id].add(date)
        
        # Calculate daily active users
        returning_users = 0
        for user_id, dates in user_dates.items():
            if len(dates) > 1:
                returning_users += 1
        
        total_users = len(user_dates)
        
        return {
            'total_users': total_users,
            'returning_users': returning_users,
            'retention_rate': (returning_users / max(total_users, 1)) * 100
        }


# Global analytics instance
analytics = AnalyticsService()

#!/usr/bin/env python3
"""
🔍 ADVANCED FILTER SYSTEM - BIG DATA PROCESSING
Ultimate Group King Bot - Advanced Filtering & Analytics
Author: Nikhil Mehra (NikkuAi09)
Features:
- Real-time data filtering
- Advanced analytics
- Pattern recognition
- Automated reporting
- Data visualization
"""

import json
import time
import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from collections import defaultdict, Counter
from dataclasses import dataclass
from enum import Enum

from admin_data import super_admin_system
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FilterType(Enum):
    """Filter types for different data operations"""
    NUMERIC = "numeric"
    TEXT = "text"
    DATE = "date"
    BOOLEAN = "boolean"
    LIST = "list"

class ComparisonOperator(Enum):
    """Comparison operators for filtering"""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"

@dataclass
class FilterCondition:
    """Individual filter condition"""
    field: str
    operator: ComparisonOperator
    value: Any
    filter_type: FilterType
    case_sensitive: bool = True

@dataclass
class FilterResult:
    """Filter operation result"""
    total_records: int
    filtered_records: int
    data: List[Dict]
    execution_time: float
    filter_summary: str

class AdvancedFilterSystem:
    """Advanced filtering system with big data capabilities"""
    
    def __init__(self):
        self.db = Database()
        self.db.connect()
        
        # Filter cache
        self.filter_cache = {}
        self.cache_timeout = 600  # 10 minutes
        
        # Performance tracking
        self.filter_performance = defaultdict(list)
        self.filter_usage_stats = defaultdict(int)
        
        # Data processors
        self.data_processors = {
            'users': self._process_user_data,
            'groups': self._process_group_data,
            'commands': self._process_command_data,
            'transactions': self._process_transaction_data,
            'activities': self._process_activity_data
        }
        
        # Advanced filters
        self.advanced_filters = {
            'behavioral_analysis': self._behavioral_analysis_filter,
            'anomaly_detection': self._anomaly_detection_filter,
            'trend_analysis': self._trend_analysis_filter,
            'sentiment_analysis': self._sentiment_analysis_filter,
            'engagement_scoring': self._engagement_scoring_filter,
            'risk_assessment': self._risk_assessment_filter,
            'performance_metrics': self._performance_metrics_filter,
            'predictive_analysis': self._predictive_analysis_filter
        }
    
    async def apply_advanced_filter(self, 
                                  data_source: str, 
                                  conditions: List[FilterCondition],
                                  advanced_filter: str = None,
                                  limit: int = 1000,
                                  offset: int = 0) -> FilterResult:
        """Apply advanced filtering with multiple conditions"""
        start_time = time.time()
        
        # Check cache
        cache_key = self._generate_cache_key(data_source, conditions, advanced_filter)
        if cache_key in self.filter_cache:
            cached_time, cached_result = self.filter_cache[cache_key]
            if time.time() - cached_time < self.cache_timeout:
                return cached_result
        
        try:
            # Get raw data
            raw_data = await self._get_data_source(data_source)
            
            # Apply basic conditions
            filtered_data = self._apply_conditions(raw_data, conditions)
            
            # Apply advanced filter if specified
            if advanced_filter and advanced_filter in self.advanced_filters:
                filtered_data = await self.advanced_filters[advanced_filter](filtered_data)
            
            # Apply pagination
            total_records = len(filtered_data)
            paginated_data = filtered_data[offset:offset + limit]
            
            # Create result
            execution_time = time.time() - start_time
            result = FilterResult(
                total_records=total_records,
                filtered_records=len(paginated_data),
                data=paginated_data,
                execution_time=execution_time,
                filter_summary=self._generate_filter_summary(conditions, advanced_filter)
            )
            
            # Cache result
            self.filter_cache[cache_key] = (time.time(), result)
            
            # Update performance tracking
            self.filter_performance[data_source].append(execution_time)
            self.filter_usage_stats[f"{data_source}_{advanced_filter or 'basic'}"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying filter: {e}")
            return FilterResult(
                total_records=0,
                filtered_records=0,
                data=[],
                execution_time=time.time() - start_time,
                filter_summary=f"Error: {str(e)}"
            )
    
    def _apply_conditions(self, data: List[Dict], conditions: List[FilterCondition]) -> List[Dict]:
        """Apply multiple filter conditions to data"""
        filtered_data = data.copy()
        
        for condition in conditions:
            filtered_data = self._apply_single_condition(filtered_data, condition)
        
        return filtered_data
    
    def _apply_single_condition(self, data: List[Dict], condition: FilterCondition) -> List[Dict]:
        """Apply single filter condition"""
        filtered_data = []
        
        for record in data:
            try:
                field_value = self._get_field_value(record, condition.field)
                
                if self._evaluate_condition(field_value, condition):
                    filtered_data.append(record)
                    
            except Exception as e:
                logger.warning(f"Error evaluating condition on record: {e}")
                continue
        
        return filtered_data
    
    def _get_field_value(self, record: Dict, field_path: str) -> Any:
        """Get field value from nested dictionary"""
        keys = field_path.split('.')
        value = record
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit():
                index = int(key)
                value = value[index] if 0 <= index < len(value) else None
            else:
                return None
        
        return value
    
    def _evaluate_condition(self, field_value: Any, condition: FilterCondition) -> bool:
        """Evaluate single condition"""
        if field_value is None:
            return False
        
        # Handle case sensitivity for text fields
        if condition.filter_type == FilterType.TEXT and not condition.case_sensitive:
            if isinstance(field_value, str):
                field_value = field_value.lower()
            if isinstance(condition.value, str):
                condition.value = condition.value.lower()
        
        # Evaluate based on operator
        if condition.operator == ComparisonOperator.EQUALS:
            return field_value == condition.value
        elif condition.operator == ComparisonOperator.NOT_EQUALS:
            return field_value != condition.value
        elif condition.operator == ComparisonOperator.GREATER_THAN:
            return field_value > condition.value
        elif condition.operator == ComparisonOperator.LESS_THAN:
            return field_value < condition.value
        elif condition.operator == ComparisonOperator.GREATER_EQUAL:
            return field_value >= condition.value
        elif condition.operator == ComparisonOperator.LESS_EQUAL:
            return field_value <= condition.value
        elif condition.operator == ComparisonOperator.CONTAINS:
            return condition.value in str(field_value)
        elif condition.operator == ComparisonOperator.STARTS_WITH:
            return str(field_value).startswith(str(condition.value))
        elif condition.operator == ComparisonOperator.ENDS_WITH:
            return str(field_value).endswith(str(condition.value))
        elif condition.operator == ComparisonOperator.IN:
            return field_value in condition.value
        elif condition.operator == ComparisonOperator.NOT_IN:
            return field_value not in condition.value
        elif condition.operator == ComparisonOperator.REGEX:
            import re
            pattern = re.compile(str(condition.value))
            return bool(pattern.search(str(field_value)))
        
        return False
    
    async def _get_data_source(self, data_source: str) -> List[Dict]:
        """Get data from specified source"""
        if data_source in self.data_processors:
            return await self.data_processors[data_source]()
        else:
            return []
    
    async def _process_user_data(self) -> List[Dict]:
        """Process user data for filtering"""
        users_collection = self.db.get_collection('users')
        if not users_collection:
            return []
        
        # Get all users with their activity
        users = list(users_collection.find({}))
        
        # Enhance with activity data
        for user in users:
            user_id = user.get('_id')
            if user_id in super_admin_system.user_activity:
                activities = super_admin_system.user_activity[user_id]
                user['activity_count'] = len(activities)
                user['last_activity'] = max(a['timestamp'] for a in activities) if activities else None
                user['first_activity'] = min(a['timestamp'] for a in activities) if activities else None
                user['avg_daily_activity'] = len(activities) / max(1, (datetime.now() - user['first_activity']).days)
            else:
                user['activity_count'] = 0
                user['last_activity'] = None
                user['first_activity'] = None
                user['avg_daily_activity'] = 0
        
        return users
    
    async def _process_group_data(self) -> List[Dict]:
        """Process group data for filtering"""
        groups_collection = self.db.get_collection('groups')
        if not groups_collection:
            return []
        
        groups = list(groups_collection.find({}))
        
        # Enhance with statistics
        for group in groups:
            chat_id = group.get('_id')
            if chat_id in super_admin_system.group_stats:
                stats = super_admin_system.group_stats[chat_id]
                group.update(stats)
            else:
                group['message_count'] = 0
                group['user_count'] = 0
                group['last_activity'] = None
        
        return groups
    
    async def _process_command_data(self) -> List[Dict]:
        """Process command data for filtering"""
        commands_collection = self.db.get_collection('command_logs')
        if not commands_collection:
            # Use in-memory data as fallback
            return [
                {
                    'command': cmd,
                    'usage_count': count,
                    'last_used': datetime.now(),
                    'avg_usage_per_day': count / 30  # Assume 30 days
                }
                for cmd, count in super_admin_system.command_stats.items()
            ]
        
        commands = list(commands_collection.find({}))
        return commands
    
    async def _process_transaction_data(self) -> List[Dict]:
        """Process transaction data for filtering"""
        transactions_collection = self.db.get_collection('transactions')
        if not transactions_collection:
            return []
        
        return list(transactions_collection.find({}))
    
    async def _process_activity_data(self) -> List[Dict]:
        """Process activity data for filtering"""
        activities_collection = self.db.get_collection('activities')
        if not activities_collection:
            # Use in-memory data
            activities = []
            for user_id, user_activities in super_admin_system.user_activity.items():
                for activity in user_activities:
                    activities.append({
                        'user_id': user_id,
                        'action': activity['action'],
                        'timestamp': activity['timestamp'],
                        'chat_id': activity.get('chat_id'),
                        'content': activity.get('content')
                    })
            return activities
        
        return list(activities_collection.find({}))
    
    # Advanced filter methods
    async def _behavioral_analysis_filter(self, data: List[Dict]) -> List[Dict]:
        """Behavioral analysis filter"""
        analyzed_data = []
        
        for record in data:
            behavior_score = self._calculate_behavior_score(record)
            record['behavior_score'] = behavior_score
            record['behavior_category'] = self._categorize_behavior(behavior_score)
            analyzed_data.append(record)
        
        return analyzed_data
    
    async def _anomaly_detection_filter(self, data: List[Dict]) -> List[Dict]:
        """Anomaly detection filter"""
        if not data:
            return data
        
        # Calculate statistical values
        numeric_fields = self._identify_numeric_fields(data)
        anomalies = []
        
        for record in data:
            anomaly_score = 0
            anomaly_reasons = []
            
            for field in numeric_fields:
                value = self._get_field_value(record, field)
                if value is not None:
                    z_score = self._calculate_z_score(data, field, value)
                    if abs(z_score) > 2:  # 2 standard deviations
                        anomaly_score += abs(z_score)
                        anomaly_reasons.append(f"{field}: {z_score:.2f}")
            
            record['anomaly_score'] = anomaly_score
            record['anomaly_reasons'] = anomaly_reasons
            record['is_anomaly'] = anomaly_score > 3
            
            if record['is_anomaly']:
                anomalies.append(record)
        
        return anomalies
    
    async def _trend_analysis_filter(self, data: List[Dict]) -> List[Dict]:
        """Trend analysis filter"""
        # Sort by timestamp
        sorted_data = sorted(data, key=lambda x: x.get('timestamp', datetime.min))
        
        # Calculate trends
        for i, record in enumerate(sorted_data):
            if i > 0:
                prev_record = sorted_data[i-1]
                record['trend_direction'] = self._calculate_trend(prev_record, record)
                record['trend_strength'] = self._calculate_trend_strength(prev_record, record)
            else:
                record['trend_direction'] = 'neutral'
                record['trend_strength'] = 0
        
        return sorted_data
    
    async def _sentiment_analysis_filter(self, data: List[Dict]) -> List[Dict]:
        """Sentiment analysis filter"""
        for record in data:
            text_content = self._extract_text_content(record)
            if text_content:
                sentiment = self._analyze_sentiment(text_content)
                record['sentiment'] = sentiment['sentiment']
                record['sentiment_score'] = sentiment['score']
                record['sentiment_confidence'] = sentiment['confidence']
            else:
                record['sentiment'] = 'neutral'
                record['sentiment_score'] = 0.5
                record['sentiment_confidence'] = 0.0
        
        return data
    
    async def _engagement_scoring_filter(self, data: List[Dict]) -> List[Dict]:
        """Engagement scoring filter"""
        for record in data:
            score = self._calculate_engagement_score(record)
            record['engagement_score'] = score
            record['engagement_level'] = self._categorize_engagement(score)
        
        return data
    
    async def _risk_assessment_filter(self, data: List[Dict]) -> List[Dict]:
        """Risk assessment filter"""
        for record in data:
            risk_score = self._calculate_risk_score(record)
            record['risk_score'] = risk_score
            record['risk_level'] = self._categorize_risk(risk_score)
            record['risk_factors'] = self._identify_risk_factors(record)
        
        return data
    
    async def _performance_metrics_filter(self, data: List[Dict]) -> List[Dict]:
        """Performance metrics filter"""
        for record in data:
            metrics = self._calculate_performance_metrics(record)
            record.update(metrics)
        
        return data
    
    async def _predictive_analysis_filter(self, data: List[Dict]) -> List[Dict]:
        """Predictive analysis filter"""
        for record in data:
            predictions = self._make_predictions(record)
            record['predictions'] = predictions
            record['confidence'] = predictions.get('confidence', 0.0)
        
        return data
    
    # Helper methods
    def _calculate_behavior_score(self, record: Dict) -> float:
        """Calculate behavior score"""
        score = 0.0
        
        # Activity frequency
        activity_count = record.get('activity_count', 0)
        score += min(activity_count / 100, 1.0) * 0.3
        
        # Recency
        last_activity = record.get('last_activity')
        if last_activity:
            days_since = (datetime.now() - last_activity).days
            score += max(0, 1 - days_since / 30) * 0.2
        
        # Engagement
        engagement = record.get('engagement_score', 0)
        score += engagement * 0.3
        
        # Positive indicators
        if record.get('warnings', 0) == 0:
            score += 0.1
        if record.get('balance', 0) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _categorize_behavior(self, score: float) -> str:
        """Categorize behavior based on score"""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.6:
            return 'good'
        elif score >= 0.4:
            return 'moderate'
        elif score >= 0.2:
            return 'poor'
        else:
            return 'very_poor'
    
    def _identify_numeric_fields(self, data: List[Dict]) -> List[str]:
        """Identify numeric fields in data"""
        numeric_fields = []
        
        if data:
            first_record = data[0]
            for field, value in first_record.items():
                if isinstance(value, (int, float)):
                    numeric_fields.append(field)
        
        return numeric_fields
    
    def _calculate_z_score(self, data: List[Dict], field: str, value: float) -> float:
        """Calculate z-score for anomaly detection"""
        values = [self._get_field_value(record, field) for record in data 
                 if self._get_field_value(record, field) is not None]
        
        if not values:
            return 0.0
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return 0.0
        
        return (value - mean) / std
    
    def _calculate_trend(self, prev_record: Dict, current_record: Dict) -> str:
        """Calculate trend direction"""
        # Simple trend calculation based on numeric fields
        numeric_fields = self._identify_numeric_fields([prev_record, current_record])
        
        if not numeric_fields:
            return 'neutral'
        
        trends = []
        for field in numeric_fields:
            prev_val = self._get_field_value(prev_record, field)
            curr_val = self._get_field_value(current_record, field)
            
            if prev_val is not None and curr_val is not None:
                if curr_val > prev_val:
                    trends.append('up')
                elif curr_val < prev_val:
                    trends.append('down')
                else:
                    trends.append('stable')
        
        if trends.count('up') > trends.count('down'):
            return 'up'
        elif trends.count('down') > trends.count('up'):
            return 'down'
        else:
            return 'stable'
    
    def _calculate_trend_strength(self, prev_record: Dict, current_record: Dict) -> float:
        """Calculate trend strength"""
        # Simplified calculation
        return 0.5  # Placeholder
    
    def _extract_text_content(self, record: Dict) -> str:
        """Extract text content for sentiment analysis"""
        text_fields = ['message', 'content', 'text', 'description']
        
        for field in text_fields:
            value = self._get_field_value(record, field)
            if value and isinstance(value, str):
                return value
        
        return ""
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        # Simplified sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'happy', 'awesome']
        negative_words = ['bad', 'terrible', 'hate', 'angry', 'sad', 'awful', 'worst']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return {'sentiment': 'neutral', 'score': 0.5, 'confidence': 0.0}
        
        sentiment_score = positive_count / total_sentiment_words
        
        if sentiment_score > 0.6:
            sentiment = 'positive'
        elif sentiment_score < 0.4:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        confidence = min(total_sentiment_words / 10, 1.0)
        
        return {
            'sentiment': sentiment,
            'score': sentiment_score,
            'confidence': confidence
        }
    
    def _calculate_engagement_score(self, record: Dict) -> float:
        """Calculate engagement score"""
        score = 0.0
        
        # Activity frequency
        activity_count = record.get('activity_count', 0)
        score += min(activity_count / 50, 1.0) * 0.4
        
        # Command diversity
        commands_used = record.get('commands_used', {})
        command_diversity = len(commands_used)
        score += min(command_diversity / 10, 1.0) * 0.3
        
        # Social interaction
        message_count = record.get('message_count', 0)
        score += min(message_count / 100, 1.0) * 0.3
        
        return min(score, 1.0)
    
    def _categorize_engagement(self, score: float) -> str:
        """Categorize engagement level"""
        if score >= 0.8:
            return 'highly_engaged'
        elif score >= 0.6:
            return 'engaged'
        elif score >= 0.4:
            return 'moderately_engaged'
        elif score >= 0.2:
            return 'minimally_engaged'
        else:
            return 'disengaged'
    
    def _calculate_risk_score(self, record: Dict) -> float:
        """Calculate risk score"""
        score = 0.0
        
        # Warnings
        warnings = record.get('warnings', 0)
        score += min(warnings / 5, 1.0) * 0.3
        
        # Suspicious activity
        anomaly_score = record.get('anomaly_score', 0)
        score += min(anomaly_score / 10, 1.0) * 0.4
        
        # Negative sentiment
        sentiment_score = record.get('sentiment_score', 0.5)
        if sentiment_score < 0.3:
            score += (1 - sentiment_score) * 0.3
        
        return min(score, 1.0)
    
    def _categorize_risk(self, score: float) -> str:
        """Categorize risk level"""
        if score >= 0.8:
            return 'high_risk'
        elif score >= 0.6:
            return 'medium_risk'
        elif score >= 0.4:
            return 'low_risk'
        else:
            return 'minimal_risk'
    
    def _identify_risk_factors(self, record: Dict) -> List[str]:
        """Identify risk factors"""
        risk_factors = []
        
        if record.get('warnings', 0) > 0:
            risk_factors.append(f"warnings: {record['warnings']}")
        
        if record.get('anomaly_score', 0) > 2:
            risk_factors.append(f"anomaly_score: {record['anomaly_score']:.2f}")
        
        if record.get('sentiment_score', 0.5) < 0.3:
            risk_factors.append(f"negative_sentiment: {record['sentiment_score']:.2f}")
        
        return risk_factors
    
    def _calculate_performance_metrics(self, record: Dict) -> Dict:
        """Calculate performance metrics"""
        return {
            'efficiency_score': 0.8,  # Placeholder
            'productivity_score': 0.7,  # Placeholder
            'quality_score': 0.9,  # Placeholder
            'responsiveness': 0.6  # Placeholder
        }
    
    def _make_predictions(self, record: Dict) -> Dict:
        """Make predictions based on data"""
        # Simplified predictive analysis
        return {
            'likely_churn_risk': 0.1,  # Placeholder
            'predicted_growth': 0.8,  # Placeholder
            'next_month_activity': 50,  # Placeholder
            'confidence': 0.7
        }
    
    def _generate_cache_key(self, data_source: str, conditions: List[FilterCondition], advanced_filter: str) -> str:
        """Generate cache key for filter operation"""
        conditions_str = json.dumps([{
            'field': c.field,
            'operator': c.operator.value,
            'value': c.value,
            'type': c.filter_type.value
        } for c in conditions], sort_keys=True)
        
        return f"{data_source}_{conditions_str}_{advanced_filter or 'none'}"
    
    def _generate_filter_summary(self, conditions: List[FilterCondition], advanced_filter: str) -> str:
        """Generate human-readable filter summary"""
        summary_parts = []
        
        for condition in conditions:
            summary_parts.append(f"{condition.field} {condition.operator.value} {condition.value}")
        
        if advanced_filter:
            summary_parts.append(f"Advanced: {advanced_filter}")
        
        return " AND ".join(summary_parts)
    
    def get_filter_performance_stats(self) -> Dict:
        """Get filter performance statistics"""
        stats = {}
        
        for data_source, times in self.filter_performance.items():
            if times:
                stats[data_source] = {
                    'avg_execution_time': sum(times) / len(times),
                    'min_execution_time': min(times),
                    'max_execution_time': max(times),
                    'total_executions': len(times)
                }
        
        return stats
    
    def get_usage_statistics(self) -> Dict:
        """Get filter usage statistics"""
        return dict(self.filter_usage_stats)
    
    def clear_cache(self):
        """Clear filter cache"""
        self.filter_cache.clear()
        logger.info("Filter cache cleared")

# Initialize advanced filter system
advanced_filter_system = AdvancedFilterSystem()

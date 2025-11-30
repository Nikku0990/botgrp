#!/usr/bin/env python3
"""
🔰 SUPER ADMIN SYSTEM - BIG DATA ANALYTICS
Ultimate Group King Bot - Advanced Admin Analytics
Author: Nikhil Mehra (NikkuAi09)
Features:
- Real-time big data analytics
- Advanced filtering system
- User behavior tracking
- Group statistics
- Performance monitoring
"""

import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import Database
from config import OWNER_ID

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuperAdminSystem:
    """Advanced super admin system with big data analytics"""
    
    def __init__(self):
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
        
        # Analytics cache
        self.analytics_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
        # Big data collectors
        self.user_activity = defaultdict(list)
        self.command_stats = defaultdict(int)
        self.group_stats = defaultdict(dict)
        self.error_logs = []
        self.performance_metrics = {}
        
        # Filter system
        self.active_filters = {}
        self.filter_presets = {
            'spam_users': {'message_count': '>100', 'timeframe': '1h'},
            'inactive_users': {'message_count': '<5', 'timeframe': '24h'},
            'new_users': {'join_time': '>7d'},
            'vip_users': {'balance': '>1000', 'commands': '>50'},
            'problematic_users': {'warnings': '>3', 'kicks': '>1'}
        }
    
    async def is_super_admin(self, user_id: int) -> bool:
        """Check if user is super admin"""
        return user_id == OWNER_ID
    
    def collect_big_data(self, update: Update = None, context: ContextTypes = None):
        """Collect big data from bot activities"""
        timestamp = datetime.now()
        
        if update:
            # User activity tracking
            user_id = update.effective_user.id
            self.user_activity[user_id].append({
                'timestamp': timestamp,
                'action': 'message' if update.message else 'command',
                'chat_id': update.effective_chat.id if update.effective_chat else None,
                'content': update.message.text if update.message else None
            })
            
            # Command statistics
            if update.message and update.message.text:
                command = update.message.text.split()[0]
                self.command_stats[command] += 1
            
            # Group statistics
            if update.effective_chat:
                chat_id = update.effective_chat.id
                if chat_id not in self.group_stats:
                    self.group_stats[chat_id] = {
                        'message_count': 0,
                        'user_count': 0,
                        'last_activity': timestamp,
                        'commands_used': defaultdict(int)
                    }
                
                self.group_stats[chat_id]['message_count'] += 1
                self.group_stats[chat_id]['last_activity'] = timestamp
                
                if update.message and update.message.text:
                    command = update.message.text.split()[0]
                    self.group_stats[chat_id]['commands_used'][command] += 1
        
        # Performance metrics
        self.performance_metrics['last_update'] = timestamp
        self.performance_metrics['total_users'] = len(self.user_activity)
        self.performance_metrics['total_commands'] = sum(self.command_stats.values())
        self.performance_metrics['active_groups'] = len(self.group_stats)
    
    def apply_filters(self, data: List[Dict], filters: Dict) -> List[Dict]:
        """Apply advanced filters to data"""
        filtered_data = data.copy()
        
        # Message count filter
        if 'message_count' in filters:
            filter_val = filters['message_count']
            if filter_val.startswith('>'):
                min_count = int(filter_val[1:])
                filtered_data = [d for d in filtered_data if len(d.get('messages', [])) > min_count]
            elif filter_val.startswith('<'):
                max_count = int(filter_val[1:])
                filtered_data = [d for d in filtered_data if len(d.get('messages', [])) < max_count]
        
        # Timeframe filter
        if 'timeframe' in filters:
            timeframe = filters['timeframe']
            if timeframe.endswith('h'):
                hours = int(timeframe[:-1])
                cutoff = datetime.now() - timedelta(hours=hours)
                filtered_data = [d for d in filtered_data if d.get('last_activity', datetime.min) > cutoff]
            elif timeframe.endswith('d'):
                days = int(timeframe[:-1])
                cutoff = datetime.now() - timedelta(days=days)
                filtered_data = [d for d in filtered_data if d.get('last_activity', datetime.min) > cutoff]
        
        # Balance filter
        if 'balance' in filters:
            filter_val = filters['balance']
            if filter_val.startswith('>'):
                min_balance = float(filter_val[1:])
                filtered_data = [d for d in filtered_data if d.get('balance', 0) > min_balance]
        
        # Join time filter
        if 'join_time' in filters:
            filter_val = filters['join_time']
            if filter_val.startswith('>'):
                days = int(filter_val[1:])
                cutoff = datetime.now() - timedelta(days=days)
                filtered_data = [d for d in filtered_data if d.get('join_date', datetime.min) > cutoff]
        
        # Warnings filter
        if 'warnings' in filters:
            filter_val = filters['warnings']
            if filter_val.startswith('>'):
                min_warnings = int(filter_val[1:])
                filtered_data = [d for d in filtered_data if d.get('warnings', 0) > min_warnings]
        
        return filtered_data
    
    def generate_analytics_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        cache_key = 'analytics_report'
        current_time = time.time()
        
        # Check cache
        if cache_key in self.analytics_cache:
            cache_time, cached_data = self.analytics_cache[cache_key]
            if current_time - cache_time < self.cache_timeout:
                return cached_data
        
        # Generate new report
        report = {
            'timestamp': datetime.now().isoformat(),
            'user_analytics': self._analyze_users(),
            'group_analytics': self._analyze_groups(),
            'command_analytics': self._analyze_commands(),
            'performance_metrics': self._analyze_performance(),
            'trending_data': self._analyze_trends(),
            'anomaly_detection': self._detect_anomalies()
        }
        
        # Cache the report
        self.analytics_cache[cache_key] = (current_time, report)
        
        return report
    
    def _analyze_users(self) -> Dict:
        """Analyze user data"""
        total_users = len(self.user_activity)
        active_users = sum(1 for activities in self.user_activity.values() 
                          if activities and activities[-1]['timestamp'] > datetime.now() - timedelta(hours=24))
        
        # User activity distribution
        activity_levels = Counter()
        for user_id, activities in self.user_activity.items():
            if len(activities) > 100:
                activity_levels['very_active'] += 1
            elif len(activities) > 50:
                activity_levels['active'] += 1
            elif len(activities) > 10:
                activity_levels['moderate'] += 1
            else:
                activity_levels['low'] += 1
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'activity_levels': dict(activity_levels),
            'user_growth_rate': self._calculate_growth_rate(),
            'top_users': self._get_top_users(10)
        }
    
    def _analyze_groups(self) -> Dict:
        """Analyze group data"""
        total_groups = len(self.group_stats)
        active_groups = sum(1 for stats in self.group_stats.values() 
                           if stats['last_activity'] > datetime.now() - timedelta(hours=24))
        
        # Group size distribution
        group_sizes = Counter()
        for chat_id, stats in self.group_stats.items():
            if stats['message_count'] > 1000:
                group_sizes['very_active'] += 1
            elif stats['message_count'] > 500:
                group_sizes['active'] += 1
            elif stats['message_count'] > 100:
                group_sizes['moderate'] += 1
            else:
                group_sizes['low'] += 1
        
        return {
            'total_groups': total_groups,
            'active_groups': active_groups,
            'group_distribution': dict(group_sizes),
            'top_groups': self._get_top_groups(10),
            'group_growth': self._calculate_group_growth()
        }
    
    def _analyze_commands(self) -> Dict:
        """Analyze command usage"""
        total_commands = sum(self.command_stats.values())
        
        # Command popularity
        popular_commands = sorted(self.command_stats.items(), 
                                 key=lambda x: x[1], reverse=True)[:20]
        
        # Command categories
        command_categories = defaultdict(int)
        for command, count in self.command_stats.items():
            if command.startswith('/admin'):
                command_categories['admin'] += count
            elif command.startswith('/fun'):
                command_categories['fun'] += count
            elif command.startswith('/economy'):
                command_categories['economy'] += count
            else:
                command_categories['general'] += count
        
        return {
            'total_commands': total_commands,
            'unique_commands': len(self.command_stats),
            'popular_commands': popular_commands,
            'command_categories': dict(command_categories),
            'command_growth': self._calculate_command_growth()
        }
    
    def _analyze_performance(self) -> Dict:
        """Analyze system performance"""
        return {
            'response_time': self._calculate_avg_response_time(),
            'error_rate': self._calculate_error_rate(),
            'uptime': self._calculate_uptime(),
            'memory_usage': self._get_memory_usage(),
            'cpu_usage': self._get_cpu_usage(),
            'database_performance': self._get_db_performance()
        }
    
    def _analyze_trends(self) -> Dict:
        """Analyze trending data"""
        # Hourly activity
        hourly_activity = defaultdict(int)
        for activities in self.user_activity.values():
            for activity in activities:
                hour = activity['timestamp'].hour
                hourly_activity[hour] += 1
        
        # Daily growth
        daily_growth = defaultdict(int)
        for activities in self.user_activity.values():
            for activity in activities:
                date = activity['timestamp'].date()
                daily_growth[str(date)] += 1
        
        return {
            'hourly_activity': dict(hourly_activity),
            'daily_growth': dict(daily_growth),
            'trending_commands': self._get_trending_commands(),
            'user_retention': self._calculate_retention_rate()
        }
    
    def _detect_anomalies(self) -> Dict:
        """Detect anomalies in data"""
        anomalies = []
        
        # Spam detection
        for user_id, activities in self.user_activity.items():
            if len(activities) > 1000:  # Unusually high activity
                anomalies.append({
                    'type': 'spam_suspicion',
                    'user_id': user_id,
                    'message_count': len(activities),
                    'severity': 'high'
                })
        
        # Inactive groups
        for chat_id, stats in self.group_stats.items():
            if stats['last_activity'] < datetime.now() - timedelta(days=7):
                anomalies.append({
                    'type': 'inactive_group',
                    'chat_id': chat_id,
                    'last_activity': stats['last_activity'].isoformat(),
                    'severity': 'medium'
                })
        
        return {
            'total_anomalies': len(anomalies),
            'anomalies': anomalies[:20],  # Limit to 20
            'anomaly_trends': self._analyze_anomaly_trends()
        }
    
    # Helper methods
    def _calculate_growth_rate(self) -> float:
        """Calculate user growth rate"""
        # Simplified calculation
        if len(self.user_activity) < 2:
            return 0.0
        
        recent_users = sum(1 for activities in self.user_activity.values() 
                          if activities and activities[-1]['timestamp'] > datetime.now() - timedelta(days=7))
        
        return (recent_users / len(self.user_activity)) * 100
    
    def _get_top_users(self, limit: int) -> List[Dict]:
        """Get top users by activity"""
        user_scores = {}
        for user_id, activities in self.user_activity.items():
            user_scores[user_id] = len(activities)
        
        top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{'user_id': uid, 'activity_score': score} for uid, score in top_users]
    
    def _get_top_groups(self, limit: int) -> List[Dict]:
        """Get top groups by activity"""
        top_groups = sorted(self.group_stats.items(), 
                           key=lambda x: x[1]['message_count'], reverse=True)[:limit]
        return [{'chat_id': chat_id, 'message_count': stats['message_count']} 
                for chat_id, stats in top_groups]
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        # Placeholder for actual implementation
        return 0.5  # seconds
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate"""
        if not self.error_logs:
            return 0.0
        
        recent_errors = [e for e in self.error_logs 
                        if e['timestamp'] > datetime.now() - timedelta(hours=24)]
        
        return (len(recent_errors) / len(self.error_logs)) * 100
    
    def _calculate_uptime(self) -> float:
        """Calculate system uptime"""
        # Placeholder for actual implementation
        return 99.9  # percentage
    
    def _get_memory_usage(self) -> Dict:
        """Get memory usage statistics"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage"""
        import psutil
        return psutil.cpu_percent()
    
    def _get_db_performance(self) -> Dict:
        """Get database performance metrics"""
        # Placeholder for actual implementation
        return {
            'query_time': 0.1,  # seconds
            'connection_pool': 'healthy',
            'cache_hit_rate': 85.0  # percentage
        }
    
    def _get_trending_commands(self) -> List[Dict]:
        """Get trending commands"""
        # Simplified trend calculation
        recent_commands = defaultdict(int)
        for activities in self.user_activity.values():
            for activity in activities:
                if activity['timestamp'] > datetime.now() - timedelta(hours=24):
                    if activity['action'] == 'command':
                        command = activity.get('content', '')
                        if command:
                            recent_commands[command] += 1
        
        trending = sorted(recent_commands.items(), key=lambda x: x[1], reverse=True)[:10]
        return [{'command': cmd, 'count': count} for cmd, count in trending]
    
    def _calculate_retention_rate(self) -> float:
        """Calculate user retention rate"""
        if len(self.user_activity) < 2:
            return 0.0
        
        # Users who came back after 24 hours
        retained_users = 0
        for activities in self.user_activity.values():
            if len(activities) > 1:
                first_activity = activities[0]['timestamp']
                last_activity = activities[-1]['timestamp']
                if (last_activity - first_activity).days > 0:
                    retained_users += 1
        
        return (retained_users / len(self.user_activity)) * 100
    
    def _calculate_group_growth(self) -> float:
        """Calculate group growth rate"""
        # Placeholder for actual implementation
        return 5.0  # percentage
    
    def _calculate_command_growth(self) -> float:
        """Calculate command usage growth"""
        # Placeholder for actual implementation
        return 12.5  # percentage
    
    def _analyze_anomaly_trends(self) -> Dict:
        """Analyze anomaly trends over time"""
        # Placeholder for actual implementation
        return {
            'spam_trend': 'increasing',
            'inactive_trend': 'stable',
            'error_trend': 'decreasing'
        }

class FilterSystem:
    """Advanced filtering system for big data"""
    
    def __init__(self, super_admin_system: SuperAdminSystem):
        self.super_admin = super_admin_system
        self.custom_filters = {}
        self.filter_history = []
    
    def create_custom_filter(self, name: str, conditions: Dict) -> bool:
        """Create custom filter"""
        try:
            self.custom_filters[name] = conditions
            self.filter_history.append({
                'action': 'create_filter',
                'filter_name': name,
                'conditions': conditions,
                'timestamp': datetime.now()
            })
            return True
        except Exception as e:
            logger.error(f"Error creating filter: {e}")
            return False
    
    def apply_filter(self, filter_name: str, data_source: str = 'users') -> List[Dict]:
        """Apply filter to data source"""
        if filter_name in self.super_admin.filter_presets:
            conditions = self.super_admin.filter_presets[filter_name]
        elif filter_name in self.custom_filters:
            conditions = self.custom_filters[filter_name]
        else:
            return []
        
        # Get data based on source
        if data_source == 'users':
            data = self._get_user_data()
        elif data_source == 'groups':
            data = self._get_group_data()
        elif data_source == 'commands':
            data = self._get_command_data()
        else:
            return []
        
        # Apply filters
        filtered_data = self.super_admin.apply_filters(data, conditions)
        
        # Log filter usage
        self.filter_history.append({
            'action': 'apply_filter',
            'filter_name': filter_name,
            'data_source': data_source,
            'result_count': len(filtered_data),
            'timestamp': datetime.now()
        })
        
        return filtered_data
    
    def _get_user_data(self) -> List[Dict]:
        """Get user data for filtering"""
        user_data = []
        for user_id, activities in self.super_admin.user_activity.items():
            user_data.append({
                'user_id': user_id,
                'messages': activities,
                'message_count': len(activities),
                'last_activity': activities[-1]['timestamp'] if activities else datetime.min,
                'warnings': 0,  # Placeholder
                'balance': 0,    # Placeholder
                'join_date': activities[0]['timestamp'] if activities else datetime.min
            })
        return user_data
    
    def _get_group_data(self) -> List[Dict]:
        """Get group data for filtering"""
        group_data = []
        for chat_id, stats in self.super_admin.group_stats.items():
            group_data.append({
                'chat_id': chat_id,
                'message_count': stats['message_count'],
                'user_count': stats['user_count'],
                'last_activity': stats['last_activity'],
                'commands_used': stats['commands_used']
            })
        return group_data
    
    def _get_command_data(self) -> List[Dict]:
        """Get command data for filtering"""
        command_data = []
        for command, count in self.super_admin.command_stats.items():
            command_data.append({
                'command': command,
                'usage_count': count,
                'last_used': datetime.now()  # Placeholder
            })
        return command_data
    
    def get_filter_statistics(self) -> Dict:
        """Get filter usage statistics"""
        return {
            'total_filters': len(self.custom_filters) + len(self.super_admin.filter_presets),
            'custom_filters': len(self.custom_filters),
            'preset_filters': len(self.super_admin.filter_presets),
            'usage_history': self.filter_history[-50:],  # Last 50 uses
            'popular_filters': self._get_popular_filters()
        }
    
    def _get_popular_filters(self) -> List[Dict]:
        """Get most popular filters"""
        filter_usage = defaultdict(int)
        for history in self.filter_history:
            if history['action'] == 'apply_filter':
                filter_usage[history['filter_name']] += 1
        
        popular = sorted(filter_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        return [{'filter_name': name, 'usage_count': count} for name, count in popular]

# Initialize systems
super_admin_system = SuperAdminSystem()
filter_system = FilterSystem(super_admin_system)

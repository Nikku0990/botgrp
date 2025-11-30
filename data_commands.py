#!/usr/bin/env python3
"""
📊 BIG DATA COMMANDS - SUPER ADMIN FILTERS
Ultimate Group King Bot - Big Data Analytics Commands
Author: Nikhil Mehra (NikkuAi09)
Features:
- Real-time analytics dashboard
- Advanced filtering commands
- Data visualization
- Automated reporting
- Performance monitoring
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from admin_data import super_admin_system, filter_system
from data_filters import advanced_filter_system, FilterCondition, FilterType, ComparisonOperator

class BigDataCommands:
    """Big data analytics commands for super admin"""
    
    def __init__(self):
        self.report_cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    async def analytics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show comprehensive analytics dashboard"""
        user = update.effective_user
        
        # Super admin check
        if not await super_admin_system.is_super_admin(user.id):
            await update.message.reply_text("❌ Super Admin command only!")
            return
        
        await update.message.reply_text("📊 Generating analytics report...")
        
        try:
            # Generate comprehensive report
            report = super_admin_system.generate_analytics_report()
            
            # Format report
            report_text = self._format_analytics_report(report)
            
            # Create inline keyboard for detailed views
            keyboard = [
                [
                    InlineKeyboardButton("👥 User Analytics", callback_data="analytics_users"),
                    InlineKeyboardButton("📱 Group Analytics", callback_data="analytics_groups")
                ],
                [
                    InlineKeyboardButton("⚡ Command Stats", callback_data="analytics_commands"),
                    InlineKeyboardButton("📈 Performance", callback_data="analytics_performance")
                ],
                [
                    InlineKeyboardButton("🔍 Trending Data", callback_data="analytics_trends"),
                    InlineKeyboardButton("⚠️ Anomalies", callback_data="analytics_anomalies")
                ],
                [
                    InlineKeyboardButton("📥 Export Report", callback_data="analytics_export"),
                    InlineKeyboardButton("🔄 Refresh", callback_data="analytics_refresh")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                report_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error generating analytics: {e}")
    
    async def filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Advanced filtering command"""
        user = update.effective_user
        
        # Super admin check
        if not await super_admin_system.is_super_admin(user.id):
            await update.message.reply_text("❌ Super Admin command only!")
            return
        
        # Usage: /filter <data_source> <field> <operator> <value>
        if len(context.args) < 4:
            await update.message.reply_text(
                "❌ Usage: `/filter <data_source> <field> <operator> <value>`\n\n"
                "**Data Sources:** users, groups, commands, transactions, activities\n"
                "**Operators:** ==, !=, >, <, >=, <=, contains, starts_with, ends_with\n\n"
                "**Examples:**\n"
                "• `/filter users activity_count > 100`\n"
                "• `/filter groups message_count >= 500`\n"
                "• `/filter commands usage_count > 50`"
            )
            return
        
        data_source = context.args[0]
        field = context.args[1]
        operator_str = context.args[2]
        value_str = " ".join(context.args[3:])
        
        # Parse operator
        operator_map = {
            '==': ComparisonOperator.EQUALS,
            '!=': ComparisonOperator.NOT_EQUALS,
            '>': ComparisonOperator.GREATER_THAN,
            '<': ComparisonOperator.LESS_THAN,
            '>=': ComparisonOperator.GREATER_EQUAL,
            '<=': ComparisonOperator.LESS_EQUAL,
            'contains': ComparisonOperator.CONTAINS,
            'starts_with': ComparisonOperator.STARTS_WITH,
            'ends_with': ComparisonOperator.ENDS_WITH
        }
        
        if operator_str not in operator_map:
            await update.message.reply_text("❌ Invalid operator!")
            return
        
        operator = operator_map[operator_str]
        
        # Parse value
        try:
            if value_str.isdigit():
                value = int(value_str)
            elif value_str.replace('.', '').isdigit():
                value = float(value_str)
            else:
                value = value_str
        except:
            value = value_str
        
        # Determine filter type
        if isinstance(value, (int, float)):
            filter_type = FilterType.NUMERIC
        else:
            filter_type = FilterType.TEXT
        
        # Create filter condition
        condition = FilterCondition(
            field=field,
            operator=operator,
            value=value,
            filter_type=filter_type
        )
        
        await update.message.reply_text("🔍 Applying filter...")
        
        try:
            # Apply filter
            result = await advanced_filter_system.apply_advanced_filter(
                data_source=data_source,
                conditions=[condition],
                limit=50
            )
            
            # Format results
            if result.filtered_records > 0:
                results_text = self._format_filter_results(result)
                
                # Create inline keyboard for actions
                keyboard = [
                    [
                        InlineKeyboardButton("📥 Export Results", callback_data=f"export_filter_{data_source}_{field}_{operator_str}_{value_str}"),
                        InlineKeyboardButton("🔍 Refine Filter", callback_data=f"refine_filter_{data_source}")
                    ],
                    [
                        InlineKeyboardButton("📊 Apply Advanced Filter", callback_data=f"advanced_filter_{data_source}"),
                        InlineKeyboardButton("🔄 New Filter", callback_data="new_filter")
                    ]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    results_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text("📭 No results found for this filter.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error applying filter: {e}")
    
    async def advanced_filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show advanced filtering options"""
        user = update.effective_user
        
        # Super admin check
        if not await super_admin_system.is_super_admin(user.id):
            await update.message.reply_text("❌ Super Admin command only!")
            return
        
        # Usage: /advanced_filter <data_source>
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/advanced_filter <data_source>`\n\n"
                "**Data Sources:** users, groups, commands, transactions, activities\n\n"
                "**Advanced Filters:**\n"
                "• behavioral_analysis - User behavior patterns\n"
                "• anomaly_detection - Detect unusual activity\n"
                "• trend_analysis - Identify trends\n"
                "• sentiment_analysis - Analyze sentiment\n"
                "• engagement_scoring - Calculate engagement\n"
                "• risk_assessment - Assess risk levels\n"
                "• performance_metrics - Performance analysis\n"
                "• predictive_analysis - Make predictions"
            )
            return
        
        data_source = context.args[0]
        
        # Create keyboard for advanced filters
        keyboard = []
        for filter_name in advanced_filter_system.advanced_filters.keys():
            keyboard.append([
                InlineKeyboardButton(f"🔍 {filter_name.replace('_', ' ').title()}", 
                                   callback_data=f"apply_advanced_{data_source}_{filter_name}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Back to Filters", callback_data="back_to_filters")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📊 **Advanced Filters for {data_source.title()}**\n\n"
            "Choose an advanced filter to apply:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def preset_filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show preset filters"""
        user = update.effective_user
        
        # Super admin check
        if not await super_admin_system.is_super_admin(user.id):
            await update.message.reply_text("❌ Super Admin command only!")
            return
        
        # Create keyboard for preset filters
        keyboard = []
        for filter_name, conditions in super_admin_system.filter_presets.items():
            keyboard.append([
                InlineKeyboardButton(f"🔍 {filter_name.replace('_', ' ').title()}", 
                                   callback_data=f"apply_preset_{filter_name}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("➕ Create Custom Filter", callback_data="create_custom_filter"),
            InlineKeyboardButton("📋 Filter Statistics", callback_data="filter_stats")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 **Preset Filters**\n\n"
            "Choose a preset filter to apply:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def big_data_monitor_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Real-time big data monitoring"""
        user = update.effective_user
        
        # Super admin check
        if not await super_admin_system.is_super_admin(user.id):
            await update.message.reply_text("❌ Super Admin command only!")
            return
        
        # Get real-time metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'total_users': len(super_admin_system.user_activity),
            'active_users': sum(1 for activities in super_admin_system.user_activity.values() 
                              if activities and activities[-1]['timestamp'] > datetime.now() - timedelta(hours=1)),
            'total_commands': sum(super_admin_system.command_stats.values()),
            'active_groups': len(super_admin_system.group_stats),
            'recent_activities': sum(1 for activities in super_admin_system.user_activity.values() 
                                   if activities and activities[-1]['timestamp'] > datetime.now() - timedelta(minutes=5)),
            'error_rate': len(super_admin_system.error_logs) / max(1, sum(super_admin_system.command_stats.values())) * 100,
            'performance_metrics': super_admin_system.performance_metrics
        }
        
        # Format monitoring dashboard
        monitor_text = f"""
📊 **REAL-TIME BIG DATA MONITOR**
🕐 Generated: {metrics['timestamp']}

👥 **User Metrics:**
• Total Users: {metrics['total_users']:,}
• Active Users (1h): {metrics['active_users']:,}
• Recent Activity (5m): {metrics['recent_activities']:,}

⚡ **Command Metrics:**
• Total Commands: {metrics['total_commands']:,}
• Commands/min: {metrics['total_commands'] / 60:.1f}

📱 **Group Metrics:**
• Active Groups: {metrics['active_groups']:,}
• Avg Messages/Group: {sum(stats['message_count'] for stats in super_admin_system.group_stats.values()) / max(1, metrics['active_groups']):.1f}

⚠️ **System Health:**
• Error Rate: {metrics['error_rate']:.2f}%
• Cache Hits: {super_admin_system.analytics_cache.get('cache_hits', 0):,}
• Memory Usage: {super_admin_system._get_memory_usage()['percent']:.1f}%

🔄 **Auto-refresh every 30 seconds**
        """.strip()
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="monitor_refresh"),
                InlineKeyboardButton("📥 Export Data", callback_data="monitor_export")
            ],
            [
                InlineKeyboardButton("📈 Detailed Analytics", callback_data="analytics_detailed"),
                InlineKeyboardButton("⚙️ Settings", callback_data="monitor_settings")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            monitor_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def export_data_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export filtered data"""
        user = update.effective_user
        
        # Super admin check
        if not await super_admin_system.is_super_admin(user.id):
            await update.message.reply_text("❌ Super Admin command only!")
            return
        
        # Usage: /export <data_source> <format>
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Usage: `/export <data_source> <format>`\n\n"
                "**Data Sources:** users, groups, commands, transactions, activities\n"
                "**Formats:** json, csv, xlsx\n\n"
                "**Examples:**\n"
                "• `/export users json`\n"
                "• `/export groups csv`\n"
                "• `/export commands xlsx`"
            )
            return
        
        data_source = context.args[0]
        format_type = context.args[1]
        
        if format_type not in ['json', 'csv', 'xlsx']:
            await update.message.reply_text("❌ Invalid format! Use: json, csv, or xlsx")
            return
        
        await update.message.reply_text("📥 Exporting data...")
        
        try:
            # Get data
            data = await advanced_filter_system._get_data_source(data_source)
            
            if not data:
                await update.message.reply_text("📭 No data found to export.")
                return
            
            # Export based on format
            if format_type == 'json':
                filename = f"{data_source}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                await update.message.reply_document(
                    open(filename, 'rb'),
                    caption=f"📊 **{data_source.title()} Export**\n"
                           f"📄 Format: JSON\n"
                           f"📊 Records: {len(data):,}\n"
                           f"🕐 Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
            elif format_type == 'csv':
                import pandas as pd
                filename = f"{data_source}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False)
                
                await update.message.reply_document(
                    open(filename, 'rb'),
                    caption=f"📊 **{data_source.title()} Export**\n"
                           f"📄 Format: CSV\n"
                           f"📊 Records: {len(data):,}\n"
                           f"🕐 Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
            elif format_type == 'xlsx':
                import pandas as pd
                filename = f"{data_source}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df = pd.DataFrame(data)
                df.to_excel(filename, index=False)
                
                await update.message.reply_document(
                    open(filename, 'rb'),
                    caption=f"📊 **{data_source.title()} Export**\n"
                           f"📄 Format: Excel\n"
                           f"📊 Records: {len(data):,}\n"
                           f"🕐 Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error exporting data: {e}")
    
    async def filter_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show filter statistics"""
        user = update.effective_user
        
        # Super admin check
        if not await super_admin_system.is_super_admin(user.id):
            await update.message.reply_text("❌ Super Admin command only!")
            return
        
        # Get statistics
        filter_stats = filter_system.get_filter_statistics()
        performance_stats = advanced_filter_system.get_filter_performance_stats()
        usage_stats = advanced_filter_system.get_usage_statistics()
        
        # Format statistics
        stats_text = f"""
📊 **FILTER SYSTEM STATISTICS**
🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 **Filter Overview:**
• Total Filters: {filter_stats['total_filters']}
• Custom Filters: {filter_stats['custom_filters']}
• Preset Filters: {filter_stats['preset_filters']}

⚡ **Performance Stats:**
"""
        
        for data_source, stats in performance_stats.items():
            stats_text += f"\n• {data_source.title()}: {stats['avg_execution_time']:.3f}s avg"
        
        stats_text += f"\n\n📈 **Usage Statistics:**"
        for filter_name, usage_count in sorted(usage_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            stats_text += f"\n• {filter_name}: {usage_count} uses"
        
        await update.message.reply_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    def _format_analytics_report(self, report: Dict) -> str:
        """Format analytics report for display"""
        user_analytics = report['user_analytics']
        group_analytics = report['group_analytics']
        command_analytics = report['command_analytics']
        
        report_text = f"""
📊 **COMPREHENSIVE ANALYTICS REPORT**
🕐 Generated: {report['timestamp']}

👥 **User Analytics:**
• Total Users: {user_analytics['total_users']:,}
• Active Users: {user_analytics['active_users']:,}
• Growth Rate: {user_analytics['user_growth_rate']:.1f}%

📱 **Group Analytics:**
• Total Groups: {group_analytics['total_groups']:,}
• Active Groups: {group_analytics['active_groups']:,}
• Group Growth: {group_analytics['group_growth']:.1f}%

⚡ **Command Analytics:**
• Total Commands: {command_analytics['total_commands']:,}
• Unique Commands: {command_analytics['unique_commands']}
• Command Growth: {command_analytics['command_growth']:.1f}%

📈 **Top Commands:**
"""
        
        for cmd, count in command_analytics['popular_commands'][:5]:
            report_text += f"• {cmd}: {count:,} uses\n"
        
        report_text += f"""
⚠️ **Anomalies Detected:**
• Total Anomalies: {report['anomaly_detection']['total_anomalies']}
        """.strip()
        
        return report_text
    
    def _format_filter_results(self, result) -> str:
        """Format filter results for display"""
        results_text = f"""
🔍 **FILTER RESULTS**
📊 Records Found: {result.filtered_records:,} / {result.total_records:,}
⏱️ Execution Time: {result.execution_time:.3f}s

📋 **Filter Summary:**
{result.filter_summary}

📄 **Sample Results:**
"""
        
        for i, record in enumerate(result.data[:5]):
            results_text += f"\n{i+1}. {record.get('_id', 'N/A')}"
            
            # Show relevant fields
            for key, value in record.items():
                if key not in ['_id', '_rev'] and not key.startswith('_'):
                    if isinstance(value, (int, float)):
                        results_text += f"\n   • {key}: {value:,}"
                    elif isinstance(value, str) and len(value) < 50:
                        results_text += f"\n   • {key}: {value}"
        
        if result.total_records > 5:
            results_text += f"\n\n... and {result.total_records - 5} more records"
        
        return results_text

# Initialize big data commands
big_data_commands = BigDataCommands()

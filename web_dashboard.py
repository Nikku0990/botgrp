#!/usr/bin/env python3
"""
🌐 WEB DASHBOARD
Ultimate Group King Bot - Web Interface for Monitoring & Control
Author: Nikhil Mehra (NikkuAi09)
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit
from typing import Dict, List, Any, Optional
import threading
import time

from config import WEB_HOST, WEB_PORT, FLASK_SECRET_KEY
from config import WEB_HOST, WEB_PORT, FLASK_SECRET_KEY
from database import Database
from payment_system import payment_system

class WebDashboard:
    """Web dashboard for bot monitoring and control"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = FLASK_SECRET_KEY or 'dev-secret-key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
        
        self.bot_stats = {
            'start_time': datetime.now(),
            'total_messages': 0,
            'total_commands': 0,
            'active_users': set(),
            'active_chats': set(),
            'errors': []
        }
        
        self.real_time_logs = []
        self.max_logs = 1000
        
        self._setup_routes()
        self._setup_socketio()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            
            return render_template('dashboard.html', 
                                 stats=self._get_dashboard_stats(),
                                 recent_logs=self._get_recent_logs())
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Login page"""
            if request.method == 'POST':
                password = request.form.get('password')
                if password == 'admin123':  # In production, use secure authentication
                    session['logged_in'] = True
                    session['login_time'] = datetime.now().isoformat()
                    return redirect(url_for('index'))
                else:
                    return render_template('login.html', error='Invalid password')
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            """Logout"""
            session.clear()
            return redirect(url_for('login'))
        
        @self.app.route('/api/stats')
        def api_stats():
            """Get bot statistics"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            return jsonify(self._get_dashboard_stats())
        
        @self.app.route('/api/logs')
        def api_logs():
            """Get recent logs"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            limit = request.args.get('limit', 50, type=int)
            return jsonify(self._get_recent_logs(limit))
        
        @self.app.route('/api/users')
        def api_users():
            """Get user statistics"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            chat_id = request.args.get('chat_id', type=int)
            limit = request.args.get('limit', 20, type=int)
            
            if chat_id:
                users = db.get_top_users(chat_id, limit, 'exp')
            else:
                users = db.get_all_users(limit)
            
            return jsonify({'users': users})
        
        @self.app.route('/api/chats')
        def api_chats():
            """Get chat statistics"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            chats = db.get_all_chats()
            return jsonify({'chats': chats})
        
        @self.app.route('/api/commands')
        def api_commands():
            """Get command statistics"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            chat_id = request.args.get('chat_id', type=int)
            
            if chat_id:
                commands = db.get_command_stats(chat_id)
            else:
                commands = db.get_all_command_stats()
            
            return jsonify({'commands': commands})
        
        @self.app.route('/api/tasks')
        def api_tasks():
            """Get task statistics"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            chat_id = request.args.get('chat_id', type=int)
            user_id = request.args.get('user_id', type=int)
            
            if user_id and chat_id:
                tasks = db.get_user_tasks(user_id, chat_id)
            elif chat_id:
                tasks = db.get_chat_task_stats(chat_id)
            else:
                tasks = db.get_all_task_stats()
            
            return jsonify({'tasks': tasks})

        @self.app.route('/api/withdrawals')
        def api_withdrawals():
            """Get pending withdrawals"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            withdrawals = payment_system.get_pending_withdrawals()
            return jsonify({'withdrawals': withdrawals})
        
        @self.app.route('/api/withdrawals/approve', methods=['POST'])
        def api_approve_withdrawal():
            """Approve withdrawal (Simulation)"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            tx_id = data.get('transaction_id')
            
            # In real system, this would trigger bank transfer
            # Here we just mark as completed in DB
            try:
                with db.connect() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE transactions SET status = 'COMPLETED' WHERE transaction_id = ?", (tx_id,))
                    conn.commit()
                
                self._add_log('INFO', f'Withdrawal {tx_id} approved')
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/backup')
        def api_backup():
            """Create backup"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            backup_data = self._create_backup()
            return jsonify(backup_data)
        
        @self.app.route('/api/broadcast', methods=['POST'])
        def api_broadcast():
            """Send broadcast message"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            data = request.get_json()
            message = data.get('message', '')
            chat_ids = data.get('chat_ids', [])
            
            if not message:
                return jsonify({'error': 'Message required'}), 400
            
            # In real implementation, send broadcast via bot
            result = {'sent': len(chat_ids), 'message': 'Broadcast queued'}
            
            self._add_log('INFO', f'Broadcast queued for {len(chat_ids)} chats')
            
            return jsonify(result)
        
        @self.app.route('/api/restart')
        def api_restart():
            """Restart bot"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            # In real implementation, restart the bot
            self._add_log('INFO', 'Bot restart requested from web dashboard')
            
            return jsonify({'message': 'Restart queued'})
        
        @self.app.route('/api/shutdown')
        def api_shutdown():
            """Shutdown bot"""
            if not session.get('logged_in'):
                return jsonify({'error': 'Unauthorized'}), 401
            
            # In real implementation, shutdown the bot
            self._add_log('INFO', 'Bot shutdown requested from web dashboard')
            
            return jsonify({'message': 'Shutdown queued'})
        
        @self.app.route('/users')
        def users_page():
            """Users management page"""
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            
            return render_template('users.html')
        
        @self.app.route('/chats')
        def chats_page():
            """Chats management page"""
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            
            return render_template('chats.html')
        
        @self.app.route('/commands')
        def commands_page():
            """Commands statistics page"""
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            
            return render_template('commands.html')
        
        @self.app.route('/tasks')
        def tasks_page():
            """Tasks management page"""
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            
            return render_template('tasks.html')
        

        @self.app.route('/settings')
        def settings_page():
            """Settings page"""
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            
            return render_template('settings.html')

        @self.app.route('/withdrawals')
        def withdrawals_page():
            """Withdrawals management page"""
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            
            return render_template('withdrawals.html')
        
        @self.app.route('/logs')
        def logs_page():
            """Logs page"""
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            
            return render_template('logs.html')
    
    def _setup_socketio(self):
        """Setup SocketIO for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            if not session.get('logged_in'):
                return False
            
            emit('status', {'connected': True})
            self._add_log('INFO', 'Web dashboard client connected')
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            self._add_log('INFO', 'Web dashboard client disconnected')
        
        @self.socketio.on('get_stats')
        def handle_get_stats():
            """Handle stats request"""
            if not session.get('logged_in'):
                return
            
            emit('stats_update', self._get_dashboard_stats())
        
        @self.socketio.on('get_logs')
        def handle_get_logs():
            """Handle logs request"""
            if not session.get('logged_in'):
                return
            
            emit('logs_update', self._get_recent_logs())
    
    def _get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        now = datetime.now()
        uptime = now - self.bot_stats['start_time']
        
        stats = {
            'uptime': str(uptime),
            'uptime_seconds': uptime.total_seconds(),
            'total_messages': self.bot_stats['total_messages'],
            'total_commands': self.bot_stats['total_commands'],
            'active_users': len(self.bot_stats['active_users']),
            'active_chats': len(self.bot_stats['active_chats']),
            'errors': len(self.bot_stats['errors']),
            'memory_usage': self._get_memory_usage(),
            'cpu_usage': self._get_cpu_usage(),
            'database_stats': self._get_database_stats(),
            'last_update': now.isoformat()
        }
        
        return stats
    
    def _get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent logs"""
        return self.real_time_logs[-limit:]
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        import psutil
        process = psutil.Process()
        
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,  # Physical memory
            'vms': memory_info.vms,  # Virtual memory
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available
        }
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        import psutil
        return psutil.cpu_percent(interval=1)
    
    def _get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = db.get_database_stats()
            return {
                'tables': len(stats),
                'total_records': sum(stats.values()) if stats else 0,
                'details': stats
            }
        except:
            return {'tables': 0, 'total_records': 0, 'details': {}}
    
    def _create_backup(self) -> Dict[str, Any]:
        """Create backup of bot data"""
        try:
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'stats': self.bot_stats,
                'users': db.get_all_users(),
                'chats': db.get_all_chats(),
                'commands': db.get_all_command_stats(),
                'tasks': db.get_all_task_stats()
            }
            
            # Save backup to file
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(f"backups/{backup_filename}", 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            self._add_log('INFO', f'Backup created: {backup_filename}')
            
            return {
                'success': True,
                'filename': backup_filename,
                'size': len(json.dumps(backup_data))
            }
            
        except Exception as e:
            self._add_log('ERROR', f'Backup failed: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def _add_log(self, level: str, message: str):
        """Add log entry"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        
        self.real_time_logs.append(log_entry)
        
        # Keep only recent logs
        if len(self.real_time_logs) > self.max_logs:
            self.real_time_logs = self.real_time_logs[-self.max_logs:]
        
        # Emit to connected clients
        self.socketio.emit('log_update', log_entry)
    
    def update_stats(self, event_type: str, data: Any = None):
        """Update bot statistics"""
        if event_type == 'message':
            self.bot_stats['total_messages'] += 1
            if data and 'user_id' in data:
                self.bot_stats['active_users'].add(data['user_id'])
            if data and 'chat_id' in data:
                self.bot_stats['active_chats'].add(data['chat_id'])
        
        elif event_type == 'command':
            self.bot_stats['total_commands'] += 1
        
        elif event_type == 'error':
            self.bot_stats['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(data)
            })
            self._add_log('ERROR', str(data))
        
        # Emit stats update
        self.socketio.emit('stats_update', self._get_dashboard_stats())
    
    def run(self, host: str = WEB_HOST, port: int = WEB_PORT, debug: bool = False):
        """Run the web dashboard"""
        self._add_log('INFO', f'Starting web dashboard on {host}:{port}')
        
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )

# Create HTML templates
def create_templates():
    """Create HTML templates for the dashboard"""
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Base template
    base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Ultimate Group King Bot Dashboard{% endblock %}</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; color: #fff; }
        .header { background: #2d2d2d; padding: 1rem; border-bottom: 2px solid #00ff88; }
        .nav { display: flex; gap: 1rem; align-items: center; }
        .nav a { color: #00ff88; text-decoration: none; padding: 0.5rem 1rem; border-radius: 5px; transition: all 0.3s; }
        .nav a:hover { background: #00ff88; color: #1a1a1a; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .card { background: #2d2d2d; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid #444; }
        .card h2 { color: #00ff88; margin-bottom: 1rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
        .stat-card { background: #3d3d3d; padding: 1rem; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #00ff88; }
        .stat-label { color: #aaa; margin-top: 0.5rem; }
        .btn { background: #00ff88; color: #1a1a1a; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer; transition: all 0.3s; }
        .btn:hover { background: #00cc66; }
        .btn-danger { background: #ff4444; color: #fff; }
        .btn-danger:hover { background: #cc0000; }
        .log-entry { padding: 0.5rem; border-left: 3px solid #00ff88; margin-bottom: 0.5rem; background: #3d3d3d; }
        .log-error { border-left-color: #ff4444; }
        .log-warning { border-left-color: #ffaa00; }
        .log-info { border-left-color: #00aaff; }
        .status-online { color: #00ff88; }
        .status-offline { color: #ff4444; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; color: #aaa; }
        .form-group input, .form-group textarea { width: 100%; padding: 0.5rem; background: #3d3d3d; border: 1px solid #555; border-radius: 5px; color: #fff; }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #444; }
        .table th { background: #3d3d3d; color: #00ff88; }
        .table tr:hover { background: #3d3d3d; }
    </style>
</head>
<body>
    <div class="header">
        <div class="nav">
            <h1>🚀 Ultimate Group King Bot</h1>
            <a href="/">Dashboard</a>
            <a href="/users">Users</a>
            <a href="/chats">Chats</a>
            <a href="/commands">Commands</a>
            <a href="/tasks">Tasks</a>
            <a href="/tasks">Tasks</a>
            <a href="/withdrawals">Withdrawals</a>
            <a href="/logs">Logs</a>
            <a href="/settings">Settings</a>
            <a href="/logout" class="btn btn-danger">Logout</a>
        </div>
    </div>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    <script>
        const socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to dashboard');
        });
        
        socket.on('stats_update', function(stats) {
            updateStats(stats);
        });
        
        socket.on('log_update', function(log) {
            addLogEntry(log);
        });
        
        function updateStats(stats) {
            // Update stats on page
            document.querySelectorAll('[data-stat]').forEach(element => {
                const statName = element.getAttribute('data-stat');
                if (stats[statName] !== undefined) {
                    element.textContent = stats[statName];
                }
            });
        }
        
        function addLogEntry(log) {
            // Add log entry to page
            console.log('New log:', log);
        }
        
        // Request updates every 5 seconds
        setInterval(() => {
            socket.emit('get_stats');
            socket.emit('get_logs');
        }, 5000);
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>
    """
    
    # Dashboard template
    dashboard_template = """
{% extends "base.html" %}

{% block title %}Dashboard - Ultimate Group King Bot{% endblock %}

{% block content %}
<div class="card">
    <h2>📊 Bot Statistics</h2>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" data-stat="total_messages">{{ stats.total_messages }}</div>
            <div class="stat-label">Total Messages</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" data-stat="total_commands">{{ stats.total_commands }}</div>
            <div class="stat-label">Total Commands</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" data-stat="active_users">{{ stats.active_users }}</div>
            <div class="stat-label">Active Users</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" data-stat="active_chats">{{ stats.active_chats }}</div>
            <div class="stat-label">Active Chats</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" data-stat="errors">{{ stats.errors }}</div>
            <div class="stat-label">Errors</div>
        </div>
        <div class="stat-card">
            <div class="stat-value status-online">●</div>
            <div class="stat-label">Status</div>
        </div>
    </div>
</div>

<div class="card">
    <h2>⏱️ System Information</h2>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{{ stats.uptime }}</div>
            <div class="stat-label">Uptime</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ "%.1f"|format(stats.cpu_usage) }}%</div>
            <div class="stat-label">CPU Usage</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ "%.1f"|format(stats.memory_usage.percent) }}%</div>
            <div class="stat-label">Memory Usage</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ stats.database_stats.total_records }}</div>
            <div class="stat-label">Database Records</div>
        </div>
    </div>
</div>

<div class="card">
    <h2>📋 Recent Activity</h2>
    <div id="recent-logs">
        {% for log in recent_logs[:10] %}
        <div class="log-entry log-{{ log.level.lower() }}">
            <strong>{{ log.timestamp }}</strong> [{{ log.level }}] {{ log.message }}
        </div>
        {% endfor %}
    </div>
</div>

<div class="card">
    <h2>🎮 Quick Actions</h2>
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <button class="btn" onclick="createBackup()">📦 Create Backup</button>
        <button class="btn" onclick="showBroadcastModal()">📢 Broadcast</button>
        <button class="btn btn-danger" onclick="restartBot()">🔄 Restart Bot</button>
        <button class="btn btn-danger" onclick="shutdownBot()">🛑 Shutdown Bot</button>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function createBackup() {
    fetch('/api/backup')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Backup created successfully!');
            } else {
                alert('Backup failed: ' + data.error);
            }
        });
}

function showBroadcastModal() {
    const message = prompt('Enter broadcast message:');
    if (message) {
        fetch('/api/broadcast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            alert('Broadcast queued for ' + data.sent + ' chats');
        });
    }
}

function restartBot() {
    if (confirm('Are you sure you want to restart the bot?')) {
        fetch('/api/restart')
            .then(response => response.json())
            .then(data => {
                alert('Restart queued!');
            });
    }
}

function shutdownBot() {
    if (confirm('Are you sure you want to shutdown the bot?')) {
        fetch('/api/shutdown')
            .then(response => response.json())
            .then(data => {
                alert('Shutdown queued!');
            });
    }
}
</script>
{% endblock %}
    """
    
    # Login template
    login_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Ultimate Group King Bot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; color: #fff; height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: #2d2d2d; padding: 2rem; border-radius: 10px; border: 1px solid #444; min-width: 300px; }
        .login-container h1 { color: #00ff88; margin-bottom: 1.5rem; text-align: center; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; color: #aaa; }
        .form-group input { width: 100%; padding: 0.75rem; background: #3d3d3d; border: 1px solid #555; border-radius: 5px; color: #fff; font-size: 1rem; }
        .btn { width: 100%; background: #00ff88; color: #1a1a1a; border: none; padding: 0.75rem; border-radius: 5px; cursor: pointer; font-size: 1rem; font-weight: bold; transition: all 0.3s; }
        .btn:hover { background: #00cc66; }
        .error { color: #ff4444; margin-top: 1rem; text-align: center; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🚀 Bot Dashboard</h1>
        <form method="POST">
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
    """
    
    # Save templates
    with open('templates/base.html', 'w') as f:
        f.write(base_template)
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(dashboard_template)
    
    with open('templates/login.html', 'w') as f:
        f.write(login_template)
    
    # Create other basic templates
    other_templates = {
        'users.html': '{% extends "base.html" %}{% block content %}<div class="card"><h2>👥 Users Management</h2><p>User management features coming soon...</p></div>{% endblock %}',
        'chats.html': '{% extends "base.html" %}{% block content %}<div class="card"><h2>💬 Chats Management</h2><p>Chat management features coming soon...</p></div>{% endblock %}',
        'commands.html': '{% extends "base.html" %}{% block content %}<div class="card"><h2>⚡ Commands Statistics</h2><p>Command statistics coming soon...</p></div>{% endblock %}',
        'tasks.html': '{% extends "base.html" %}{% block content %}<div class="card"><h2>📋 Tasks Management</h2><p>Task management features coming soon...</p></div>{% endblock %}',
        'settings.html': '{% extends "base.html" %}{% block content %}<div class="card"><h2>⚙️ Settings</h2><p>Settings management coming soon...</p></div>{% endblock %}',
        'logs.html': '{% extends "base.html" %}{% block content %}<div class="card"><h2>📋 System Logs</h2><div id="logs-container"><p>Real-time logs will appear here...</p></div></div>{% block scripts %}<script>setInterval(() => fetch("/api/logs").then(r => r.json()).then(logs => { const container = document.getElementById("logs-container"); container.innerHTML = logs.map(log => `<div class="log-entry log-${log.level.toLowerCase()}"><strong>${log.timestamp}</strong> [${log.level}] ${log.message}</div>`).join(""); }), 1000);</script>{% endblock %}',
        'withdrawals.html': '{% extends "base.html" %}{% block content %}<div class="card"><h2>💸 Pending Withdrawals</h2><table class="table"><thead><tr><th>ID</th><th>User ID</th><th>Amount</th><th>Description</th><th>Date</th><th>Action</th></tr></thead><tbody id="withdrawals-table"></tbody></table></div>{% block scripts %}<script>function loadWithdrawals(){fetch("/api/withdrawals").then(r=>r.json()).then(data=>{const tbody=document.getElementById("withdrawals-table");if(data.withdrawals.length===0){tbody.innerHTML="<tr><td colspan=\'6\'>No pending withdrawals</td></tr>";return;}tbody.innerHTML=data.withdrawals.map(w=>`<tr><td>${w.transaction_id}</td><td>${w.user_id}</td><td>${w.amount}</td><td>${w.description}</td><td>${w.created_at}</td><td><button class="btn" onclick="approve(\'${w.transaction_id}\')">Approve</button></td></tr>`).join("");});}function approve(id){if(confirm("Approve withdrawal?")){fetch("/api/withdrawals/approve",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({transaction_id:id})}).then(r=>r.json()).then(d=>{if(d.success){alert("Approved!");loadWithdrawals();}else{alert("Error: "+d.error);}});}}loadWithdrawals();setInterval(loadWithdrawals,10000);</script>{% endblock %}'
    }
    
    for filename, content in other_templates.items():
        with open(f'templates/{filename}', 'w') as f:
            f.write(content)

# Initialize dashboard
web_dashboard = WebDashboard()

def start_dashboard(host: str = WEB_HOST, port: int = WEB_PORT):
    """Start the web dashboard"""
    # Create templates
    create_templates()
    
    print(f"🌐 Starting Web Dashboard on http://{host}:{port}")
    print("🔐 Login with password: admin123")
    
    # Run in separate thread
    dashboard_thread = threading.Thread(
        target=web_dashboard.run,
        kwargs={'host': host, 'port': port, 'debug': False},
        daemon=True
    )
    dashboard_thread.start()
    
    return web_dashboard

if __name__ == "__main__":
    # Create templates and run dashboard
    create_templates()
    web_dashboard.run(debug=True)

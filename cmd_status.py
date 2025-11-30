#!/usr/bin/env python3
"""
🔍 COMMAND STATUS CHECKER
Ultimate Group King Bot - Command Status Monitor
Author: Nikhil Mehra (NikkuAi09)
"""

import os
import sys
from datetime import datetime

def check_bot_status():
    """Check overall bot status"""
    status = {
        "bot_files": [],
        "database": False,
        "config": False,
        "modules": {},
        "errors": []
    }
    
    # Check main bot files
    bot_files = [
        "bot_launcher.py",
        "config.py", 
        "database.py",
        "smart_detection.py",
        "magical_features.py",
        "working_commands.py",
        "admin_commands.py",
        "economy_commands.py",
        "custom_commands.py",
        "error_handler.py"
    ]
    
    for file in bot_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            status["bot_files"].append(f"✅ {file} ({size} bytes)")
        else:
            status["bot_files"].append(f"❌ {file} (MISSING)")
            status["errors"].append(f"Missing file: {file}")
    
    # Check database (Astra DB)
    if os.path.exists("database.py"):
        try:
            import database
            # Test Astra DB connection
            db_test = database.Database()
            if db_test.connect():
                status["database"] = True
                status["bot_files"].append(f"✅ Astra DB connected")
            else:
                status["bot_files"].append(f"❌ Astra DB connection failed")
                status["errors"].append("Astra DB connection failed")
        except Exception as e:
            status["bot_files"].append(f"❌ Database error: {e}")
            status["errors"].append(f"Database error: {e}")
    else:
        status["bot_files"].append(f"❌ database.py missing")
        status["errors"].append("Database file missing")
    
    # Check config
    if os.path.exists("config.py"):
        try:
            import config
            status["config"] = True
            status["bot_files"].append(f"✅ Config loaded")
        except Exception as e:
            status["bot_files"].append(f"❌ Config error: {e}")
            status["errors"].append(f"Config error: {e}")
    
    # Check modules
    modules = {
        "working_commands": "WorkingCommands",
        "magical_features": "MagicalFeatures", 
        "admin_commands": "AdminCommands",
        "economy_commands": "EconomyCommands",
        "custom_commands": "CustomCommands",
        "smart_detection": "SmartDetection",
        "error_handler": "ErrorHandler"
    }
    
    for module, class_name in modules.items():
        if os.path.exists(f"{module}.py"):
            try:
                mod = __import__(module)
                if hasattr(mod, class_name):
                    status["modules"][module] = f"✅ {class_name} available"
                else:
                    status["modules"][module] = f"❌ {class_name} missing"
                    status["errors"].append(f"Class {class_name} missing in {module}")
            except Exception as e:
                status["modules"][module] = f"❌ Import error: {e}"
                status["errors"].append(f"Import error {module}: {e}")
        else:
            status["modules"][module] = f"❌ File missing"
            status["errors"].append(f"Module file missing: {module}")
    
    return status

def print_status_report():
    """Print detailed status report"""
    print("🔍 **BOT COMMAND STATUS REPORT** 🔍")
    print("=" * 50)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    status = check_bot_status()
    
    # Files Status
    print("📁 **FILES STATUS:**")
    for file_status in status["bot_files"]:
        print(f"  {file_status}")
    print()
    
    # Modules Status
    print("🔧 **MODULES STATUS:**")
    for module, mod_status in status["modules"].items():
        print(f"  {module}: {mod_status}")
    print()
    
    # Overall Status
    print("📊 **OVERALL STATUS:**")
    if status["config"] and status["database"] and len(status["errors"]) == 0:
        print("  🟢 **BOT READY** - All systems operational")
    elif len(status["errors"]) <= 2:
        print("  🟡 **BOT WARNING** - Minor issues detected")
    else:
        print("  🔴 **BOT ERROR** - Major issues detected")
    
    # Errors
    if status["errors"]:
        print()
        print("❌ **ERRORS FOUND:**")
        for error in status["errors"]:
            print(f"  • {error}")
    
    print()
    print("=" * 50)
    print("🚀 **COMMAND STATUS CHECK COMPLETE** 🚀")

if __name__ == "__main__":
    print_status_report()

#!/usr/bin/env python3
"""
Debug script for monitoring threading issues in the Financial Agent app.
Helps diagnose virtual environment and Dash hot reloader problems.
"""

import threading
import time
import os
import subprocess
import sys

def get_app_processes():
    """Get running Financial Agent processes"""
    try:
        result = subprocess.run(['lsof', '-i', ':8050'], capture_output=True, text=True, check=False)
        return result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return "Could not check processes"

def get_active_threads():
    """Get information about active threads"""
    active_threads = threading.enumerate()
    return {
        'count': len(active_threads),
        'threads': [(t.name, t.ident, t.is_alive(), t.daemon) for t in active_threads]
    }

def monitor_threads(monitor_duration=30):
    """Monitor thread activity for a specified duration"""
    print(f"🔍 Monitoring threads for {monitor_duration} seconds...")
    print("=" * 60)
    
    start_time = time.time()
    while time.time() - start_time < monitor_duration:
        threads_info = get_active_threads()
        timestamp = time.strftime("%H:%M:%S")
        
        print(f"[{timestamp}] Active threads: {threads_info['count']}")
        for name, ident, is_alive, is_daemon in threads_info['threads']:
            status = "✓" if is_alive else "✗"
            daemon_status = "D" if is_daemon else "M"
            print(f"  {status} {name} (ID: {ident}) [{daemon_status}]")
        
        print("-" * 40)
        time.sleep(5)

def test_environment_variables():
    """Test debugging environment variables"""
    print("🧪 Environment Variables Test:")
    print("=" * 40)
    
    debug_vars = {
        'DEBUG_THREADING': os.getenv('DEBUG_THREADING', 'false'),
        'DISABLE_BACKGROUND_THREADS': os.getenv('DISABLE_BACKGROUND_THREADS', 'false'),
        'SIMULATE_ANALYSIS_RESULTS': os.getenv('SIMULATE_ANALYSIS_RESULTS', 'false'),
        'VIRTUAL_ENV': os.getenv('VIRTUAL_ENV', 'Not set')
    }
    
    for var, value in debug_vars.items():
        status = "✓" if value not in ['false', 'Not set'] else "✗"
        print(f"  {status} {var}: {value}")
    
    print()

def check_app_status():
    """Check if the Financial Agent app is running"""
    print("📊 App Status Check:")
    print("=" * 30)
    
    processes = get_app_processes()
    if "python" in processes.lower():
        print("✓ Financial Agent app is running")
        print("Process details:")
        print(processes)
    else:
        print("✗ Financial Agent app is not running")
    print()

def run_threading_test():
    """Run a comprehensive threading test"""
    print("🚀 Financial Agent Threading Debug Tool")
    print("=" * 50)
    print()
    
    # Check environment
    test_environment_variables()
    
    # Check app status
    check_app_status()
    
    # Monitor threads
    try:
        monitor_threads(30)
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
    
    print("\n📋 Debug Recommendations:")
    print("=" * 30)
    
    threads_info = get_active_threads()
    if threads_info['count'] > 10:
        print("⚠️  High thread count detected. Consider:")
        print("   - Setting DISABLE_BACKGROUND_THREADS=true")
        print("   - Restarting the app")
    
    if os.getenv('DEBUG_THREADING') != 'true':
        print("💡 Enable thread debugging with:")
        print("   export DEBUG_THREADING=true")
    
    if os.getenv('VIRTUAL_ENV') == 'Not set':
        print("⚠️  Virtual environment not activated")
        print("   source venv/bin/activate")

def quick_debug_setup():
    """Set up debugging environment variables"""
    print("⚙️  Setting up debug environment...")
    
    commands = [
        "export DEBUG_THREADING=true",
        "export SIMULATE_ANALYSIS_RESULTS=true",
        "echo 'Debug environment setup complete'"
    ]
    
    print("Run these commands in your terminal:")
    for cmd in commands:
        print(f"  {cmd}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            quick_debug_setup()
        elif sys.argv[1] == "monitor":
            duration_arg = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            monitor_threads(duration_arg)
        elif sys.argv[1] == "status":
            check_app_status()
        else:
            print("Usage: python debug_threading.py [setup|monitor|status]")
    else:
        run_threading_test()

#!/usr/bin/env python3
"""
Emergency Server Stop Script
Use this when the Financial Agent server becomes unresponsive.
"""

import os
import subprocess
import signal
import time

def find_and_kill_server():
    """Find and kill the Financial Agent server process"""
    print("🔍 Searching for Financial Agent server processes...")
    
    # Method 1: Using ps and grep
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        killed_count = 0
        for line in lines:
            if 'python' in line and 'app.py' in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    print(f"📍 Found server process: PID {pid}")
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"✅ Sent SIGTERM to PID {pid}")
                        killed_count += 1
                    except ProcessLookupError:
                        print(f"⚠️  Process {pid} already terminated")
                    except PermissionError:
                        print(f"❌ Permission denied to kill PID {pid}")
        
        if killed_count > 0:
            print(f"⏰ Waiting 3 seconds for graceful shutdown...")
            time.sleep(3)
            
            # Force kill if still running
            force_kill_remaining()
        else:
            print("✅ No server processes found")
            
    except Exception as e:
        print(f"❌ Error finding processes: {e}")
        print("🔄 Trying alternative methods...")
        
        # Method 2: Using pkill
        try:
            subprocess.run(['pkill', '-f', 'python.*app.py'], check=False)
            print("✅ Executed pkill command")
        except Exception as e:
            print(f"❌ pkill failed: {e}")

def force_kill_remaining():
    """Force kill any remaining server processes"""
    print("🔍 Checking for remaining processes...")
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'python' in line and 'app.py' in line:
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    print(f"💀 Force killing PID {pid}")
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                        print(f"✅ Force killed PID {pid}")
                    except ProcessLookupError:
                        print(f"ℹ️  Process {pid} already terminated")
                    except PermissionError:
                        print(f"❌ Permission denied to kill PID {pid}")
        
    except Exception as e:
        print(f"❌ Error in force kill: {e}")

def check_port_8050():
    """Check if port 8050 is still in use"""
    try:
        result = subprocess.run(['lsof', '-i', ':8050'], capture_output=True, text=True)
        if result.stdout:
            print("⚠️  Port 8050 is still in use:")
            print(result.stdout)
            
            # Try to kill processes using port 8050
            lines = result.stdout.split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        print(f"🔌 Killing process using port 8050: PID {pid}")
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                        except (ProcessLookupError, PermissionError, ValueError):
                            pass
        else:
            print("✅ Port 8050 is free")
    except Exception as e:
        print(f"ℹ️  Could not check port 8050: {e}")

def main():
    print("🚨 Emergency Financial Agent Server Stop")
    print("=" * 50)
    
    # Step 1: Find and kill server processes
    find_and_kill_server()
    
    # Step 2: Check port usage
    check_port_8050()
    
    # Step 3: Final verification
    print("\n🔍 Final verification...")
    time.sleep(2)
    
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        server_processes = [line for line in result.stdout.split('\n') 
                          if 'python' in line and 'app.py' in line]
        
        if server_processes:
            print("⚠️  Some processes may still be running:")
            for proc in server_processes:
                print(f"  {proc}")
        else:
            print("✅ No server processes found - shutdown complete")
            
    except Exception as e:
        print(f"❌ Error in final verification: {e}")
    
    print("\n🎯 Server shutdown procedure completed")
    print("💡 You can now restart the server safely")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Financial Agent Server Monitor
Helps prevent and debug callback conflicts and server crashes.
"""

import os
import time
import psutil
import subprocess
import signal
import sys
from datetime import datetime

class ServerMonitor:
    def __init__(self):
        self.process = None
        self.start_time = None
        
    def find_server_process(self):
        """Find the running Financial Agent server process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'app.py' in ' '.join(proc.info['cmdline']):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def start_server(self):
        """Start the server with monitoring"""
        print("🚀 Starting Financial Agent Server...")
        
        # Set environment variables for safer operation
        env = os.environ.copy()
        env['DEBUG_THREADING'] = 'true'
        env['DISABLE_BACKGROUND_THREADS'] = 'false'  # Set to 'true' for debugging
        env['SIMULATE_ANALYSIS_RESULTS'] = 'true'    # Set to 'false' for real analysis
        
        self.process = subprocess.Popen(
            ['python', 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        self.start_time = datetime.now()
        print(f"✅ Server started with PID: {self.process.pid}")
        print(f"🌐 Access at: http://localhost:8050")
        print("📊 Monitoring for callback conflicts and crashes...")
        print("🛑 Press Ctrl+C to stop monitoring and shutdown server gracefully")
        
        return self.process
    
    def monitor_server(self):
        """Monitor server output for issues"""
        error_patterns = [
            "Callback failed",
            "server did not respond",
            "allow_duplicate",
            "circular dependency",
            "Exception in callback",
            "RuntimeError",
            "ConnectionError"
        ]
        
        warning_patterns = [
            "BACKGROUND ANALYSIS",
            "Thread started",
            "Active threads",
            "Callback conflict"
        ]
        
        if not self.process:
            print("❌ No server process to monitor")
            return
        
        print("\n📋 Server Output Monitor:")
        print("-" * 50)
        
        try:
            while self.process.poll() is None:
                # Read stdout
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        self.analyze_output(line.strip(), error_patterns, warning_patterns)
                
                # Read stderr
                if self.process.stderr:
                    line = self.process.stderr.readline()
                    if line:
                        self.analyze_output(line.strip(), error_patterns, warning_patterns, is_error=True)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitor interrupted by user")
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
        finally:
            self.shutdown_server()
    
    def analyze_output(self, line, error_patterns, warning_patterns, is_error=False):
        """Analyze server output for issues"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Check for error patterns
        for pattern in error_patterns:
            if pattern.lower() in line.lower():
                print(f"🚨 [{timestamp}] ERROR: {line}")
                return
        
        # Check for warning patterns
        for pattern in warning_patterns:
            if pattern.lower() in line.lower():
                print(f"⚠️  [{timestamp}] WARNING: {line}")
                return
        
        # Regular output
        if is_error:
            print(f"❌ [{timestamp}] {line}")
        else:
            print(f"ℹ️  [{timestamp}] {line}")
    
    def shutdown_server(self):
        """Gracefully shutdown the server"""
        print("\n🔄 Shutting down server...")
        
        if self.process:
            try:
                # Try graceful shutdown first
                self.process.send_signal(signal.SIGINT)
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=5)
                    print("✅ Server shutdown gracefully")
                except subprocess.TimeoutExpired:
                    print("⏰ Graceful shutdown timed out, forcing termination...")
                    self.process.kill()
                    self.process.wait()
                    print("💀 Server terminated forcefully")
                    
            except Exception as e:
                print(f"❌ Error during shutdown: {e}")
        
        # Also kill any remaining processes
        self.force_kill_server()
        
        if self.start_time:
            duration = datetime.now() - self.start_time
            print(f"📊 Server ran for: {duration}")
    
    def force_kill_server(self):
        """Force kill any remaining server processes"""
        print("🔍 Checking for remaining server processes...")
        
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'app.py' in ' '.join(proc.info['cmdline']):
                    print(f"💀 Killing process {proc.info['pid']}: {' '.join(proc.info['cmdline'])}")
                    proc.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed_count > 0:
            print(f"💀 Killed {killed_count} server process(es)")
        else:
            print("✅ No remaining server processes found")
    
    def health_check(self):
        """Check server health"""
        import requests
        
        try:
            response = requests.get("http://localhost:8050", timeout=5)
            if response.status_code == 200:
                print("✅ Server is healthy and responding")
                return True
            else:
                print(f"⚠️  Server responding with status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Server health check failed: {e}")
            return False

def main():
    monitor = ServerMonitor()
    
    # Check if server is already running
    existing_process = monitor.find_server_process()
    if existing_process:
        print(f"⚠️  Server already running with PID: {existing_process.pid}")
        choice = input("Kill existing server and start new one? (y/n): ")
        if choice.lower() == 'y':
            monitor.force_kill_server()
            time.sleep(2)
        else:
            print("🔍 Monitoring existing server...")
            monitor.process = existing_process
            monitor.monitor_server()
            return
    
    # Start and monitor server
    try:
        monitor.start_server()
        monitor.monitor_server()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Monitor failed: {e}")
    finally:
        monitor.shutdown_server()

if __name__ == "__main__":
    main()

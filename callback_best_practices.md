# Dash Callback Best Practices - Preventing Server Crashes

## 1. Avoid Multiple Callbacks with `allow_duplicate=True`

### ❌ Problem Pattern (What Caused the Crash)
```python
@app.callback(
    [Output('analysis-report-display', 'children', allow_duplicate=True),
     Output('translate-button', 'style', allow_duplicate=True)],
    [Input('progress-interval', 'n_intervals')],
    prevent_initial_call=True
)
def update_analysis_progress(...):
    # This callback runs every 3 seconds

@app.callback(
    [Output('analysis-report-display', 'children', allow_duplicate=True),
     Output('translate-button', 'style', allow_duplicate=True)],
    [Input('translate-button', 'n_clicks')],
    prevent_initial_call=True
)
def translate_report_callback(...):
    # This callback runs when button is clicked
```

### ✅ Solution: Use a Single State Manager
```python
@app.callback(
    [Output('analysis-report-display', 'children'),
     Output('translate-button', 'style'),
     Output('show-original-button', 'style')],
    [Input('progress-interval', 'n_intervals'),
     Input('translate-button', 'n_clicks'),
     Input('show-original-button', 'n_clicks')],
    [State('url', 'pathname')],
    prevent_initial_call=True
)
def unified_report_manager(n_intervals, translate_clicks, original_clicks, pathname):
    # Single callback handles all state changes
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'progress-interval':
        # Handle progress updates
        return handle_progress_update(pathname)
    elif trigger_id == 'translate-button':
        # Handle translation
        return handle_translation()
    elif trigger_id == 'show-original-button':
        # Handle show original
        return handle_show_original()
```

## 2. Proper Thread Management

### ❌ Problem Pattern
```python
# Uncontrolled thread creation
analysis_thread = threading.Thread(target=run_analysis)
analysis_thread.daemon = True
analysis_thread.start()  # No tracking or cleanup
```

### ✅ Solution: Thread Pool with Proper Management
```python
import concurrent.futures
import threading

class ThreadManager:
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.active_futures = {}
        self.lock = threading.Lock()
    
    def submit_analysis(self, task_id, func, *args, **kwargs):
        with self.lock:
            # Cancel any existing task
            if task_id in self.active_futures:
                self.active_futures[task_id].cancel()
            
            # Submit new task
            future = self.executor.submit(func, *args, **kwargs)
            self.active_futures[task_id] = future
            return future
    
    def is_running(self, task_id):
        with self.lock:
            return task_id in self.active_futures and not self.active_futures[task_id].done()
```

## 3. State Management Best Practices

### ❌ Problem Pattern
```python
# Global state modified by multiple threads
analysis_progress = {'status': 'idle', 'result': ''}

def background_thread():
    global analysis_progress
    analysis_progress['status'] = 'running'  # Race condition!
```

### ✅ Solution: Thread-Safe State Manager
```python
import threading
from dataclasses import dataclass
from typing import Optional

@dataclass
class AnalysisState:
    status: str = 'idle'
    message: str = 'Ready'
    result: str = ''
    current_language: str = 'en'
    original_report: str = ''
    translated_report: str = ''

class StateManager:
    def __init__(self):
        self._state = AnalysisState()
        self._lock = threading.Lock()
    
    def update_status(self, status: str, message: str = ''):
        with self._lock:
            self._state.status = status
            if message:
                self._state.message = message
    
    def get_state(self) -> AnalysisState:
        with self._lock:
            return AnalysisState(**self._state.__dict__)
```

## 4. Error Handling and Recovery

### ❌ Problem Pattern
```python
def callback_function():
    try:
        # Some operation
        return result
    except Exception as e:
        # No proper error handling
        raise e
```

### ✅ Solution: Comprehensive Error Handling
```python
def safe_callback_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error
            logger.error(f"Callback error in {func.__name__}: {str(e)}")
            
            # Return safe default values
            return get_safe_defaults_for_callback(func)
    return wrapper

@safe_callback_wrapper
def my_callback():
    # Your callback logic here
    pass
```

## 5. Prevent Circular Dependencies

### ❌ Problem Pattern
```python
# Callback A updates output that triggers Callback B
# Callback B updates output that triggers Callback A
```

### ✅ Solution: Use `prevent_initial_call` and Context Checking
```python
@app.callback(
    Output('component-a', 'children'),
    Input('component-b', 'value'),
    prevent_initial_call=True
)
def update_a(value):
    # Check if this is a user-initiated change
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update
    
    # Process only if triggered by user action
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'component-b':
        return process_update(value)
    
    return no_update
```

## 6. Debugging Tools

### Add Debug Middleware
```python
import functools
import time

def debug_callback(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            print(f"✓ {func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f"✗ {func.__name__} failed after {duration:.2f}s: {str(e)}")
            raise
    return wrapper
```

## 7. Server Stability Checklist

Before deployment, ensure:

- [ ] No `allow_duplicate=True` unless absolutely necessary
- [ ] All callbacks have proper error handling
- [ ] Thread management is implemented
- [ ] State is managed thread-safely
- [ ] Circular dependencies are avoided
- [ ] Proper logging is in place
- [ ] Graceful shutdown handling exists

## 8. Emergency Stop Procedures

### Force Kill Server
```bash
# Find the process
ps aux | grep "python app.py"

# Kill by process ID
kill -9 <PID>

# Or kill by name
pkill -f "python app.py"
```

### Graceful Shutdown Handler
```python
import signal
import sys

def signal_handler(sig, frame):
    print('Gracefully shutting down...')
    # Cleanup code here
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

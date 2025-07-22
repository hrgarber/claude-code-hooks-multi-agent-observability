# Hook Adaptations for Observability

This document describes the minimal changes needed to adapt the original Claude Code hooks to send events to the observability server.

## Philosophy
Keep the original hook code as intact as possible. The author's hooks are already well-designed - they log locally and fail silently. We just need to add event sending with the same patterns.

## Required Changes

### 1. Add Dependencies
Each hook needs `requests` added to its script dependencies:

```python
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests",  # Add this line
# ]
# ///
```

### 2. Add Imports
Add these imports after existing imports:
```python
import os
import requests
```

### 3. Add Event Sending
After the hook writes to its local JSON file, add this block:

```python
# Send to observability server
try:
    requests.post("http://localhost:4000/events", json={
        "source_app": os.path.basename(os.getcwd()),
        "session_id": session_id,
        "hook_event_type": "hook_name_here",  # e.g. "user_prompt_submit"
        "payload": input_data
    }, timeout=1)
except:
    pass  # Never interrupt Claude
```

## Why This Works
- **Minimal changes**: ~10 lines added per hook
- **Same patterns**: Uses the author's fail-silently approach
- **No new files**: No utils or helpers needed
- **Local logging preserved**: Still writes JSON files as backup
- **Zero config**: Hardcoded localhost URL

## What NOT to Change
- Don't refactor the existing code
- Don't use hook_utils.py (that's for future hooks)
- Don't change how hooks parse input or validate
- Don't add error logging or debugging
- Don't make the URL configurable

## Testing
The hooks will automatically start sending events once adapted. Test by:
1. Triggering a Claude Code action
2. Checking the dashboard at localhost:5173
3. Verifying local JSON logs still work

## Future Hooks
New hooks can use hook_utils.py for cleaner code, but existing hooks should stay minimal.
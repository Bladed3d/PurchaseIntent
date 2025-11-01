"""
Test Secret Sanitization in Breadcrumb System

Verifies that API keys, tokens, and secrets are properly redacted before logging.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from lib.breadcrumb_system import BreadcrumbTrail

# Use a test log file
test_log = Path(__file__).parent / "logs" / "test_sanitization.jsonl"
test_log.parent.mkdir(exist_ok=True)

# Clear test log
if test_log.exists():
    test_log.unlink()

# Create test trail
trail = BreadcrumbTrail("TestSecretSanitization", log_file=str(test_log))

print("="*60)
print("Testing Secret Sanitization")
print("="*60)

# Test 1: Google API key by name
print("\nTest 1: API key by field name")
trail.light(1000, {
    "action": "google_trends_query",
    "api_key": "AIzaSyDemoKey12345678901234567890123",  # Should be redacted
    "query": "meditation books"
})

# Test 2: Secret in value (Google API key pattern)
print("\nTest 2: Google API key in URL")
trail.light(1001, {
    "action": "api_call",
    "url": "https://trends.google.com?key=AIzaSyDemoKey12345678901234567890123"  # Should be redacted
})

# Test 3: OpenAI token
print("\nTest 3: OpenAI token in auth header")
trail.light(1002, {
    "action": "openai_request",
    "authorization": "Bearer sk-proj-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFG"  # Should be redacted
})

# Test 4: Safe data (should NOT be redacted)
print("\nTest 4: Safe data (should pass through)")
trail.light(1003, {
    "action": "data_processing",
    "topic": "meditation",
    "score": 85,
    "url": "https://reddit.com/r/meditation"  # No secrets, should be fine
})

# Test 5: Error with secret in message
print("\nTest 5: Error message with embedded token")
try:
    raise ValueError("API failed: https://api.example.com?token=ghp_1234567890123456789012345678901234567")
except Exception as e:
    trail.fail(1004, e)  # Error message should be sanitized

print("\n" + "="*60)
print("Checking Test Results")
print("="*60)

# Read and verify log file
with open(test_log, 'r') as f:
    lines = f.readlines()

print(f"\n✅ Wrote {len(lines)} log entries")

# Parse and check each entry
for i, line in enumerate(lines, 1):
    entry = json.loads(line)
    print(f"\nEntry {i} (LED {entry['id']}):")

    # Check for exposed secrets
    entry_str = json.dumps(entry)

    if 'AIza' in entry_str and 'REDACTED' not in entry_str:
        print(f"  ❌ FAIL: Google API key NOT redacted!")
        print(f"     Data: {entry.get('data')}")
    elif 'sk-' in entry_str and 'REDACTED' not in entry_str:
        print(f"  ❌ FAIL: OpenAI key NOT redacted!")
        print(f"     Data: {entry.get('data')}")
    elif 'ghp_' in entry_str and 'REDACTED' not in entry_str:
        print(f"  ❌ FAIL: GitHub token NOT redacted!")
        print(f"     Error: {entry.get('error')}")
    else:
        print(f"  ✅ PASS: No secrets exposed")
        if entry.get('data'):
            print(f"     Data: {entry['data']}")
        if entry.get('error'):
            print(f"     Error: {entry['error'][:100]}...")

print("\n" + "="*60)
print("Test Complete")
print("="*60)

print("\nIf all tests show ✅ PASS, sanitization is working correctly.")
print("Check test log file:", test_log)

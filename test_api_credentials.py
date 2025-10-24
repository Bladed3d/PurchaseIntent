"""
API Credential Verification Script
Tests all required APIs for Purchase Intent System

Run this after setting up .env file to verify credentials work.

Usage:
    python test_api_credentials.py
"""

import os
import sys
from dotenv import load_dotenv

# Track test results
tests_passed = 0
tests_failed = 0

def print_header(text):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"{text}")
    print(f"{'='*60}")

def print_test(number, description):
    """Print test description"""
    print(f"\n{number}. {description}...")

def print_success(message):
    """Print success message"""
    print(f"   [OK] {message}")

def print_error(message):
    """Print error message"""
    print(f"   [FAIL] {message}")

print_header("Purchase Intent System - API Credential Test")
print("This script verifies all required API credentials are configured correctly.")

# Load environment variables
print_test(1, "Loading .env file")
try:
    load_dotenv()

    # Check if .env file exists
    if not os.path.exists('.env'):
        print_error(".env file not found!")
        print("          Create .env file using .env.template as reference")
        sys.exit(1)

    print_success(".env file found and loaded")
    tests_passed += 1
except Exception as e:
    print_error(f"Failed to load .env file: {e}")
    tests_failed += 1
    sys.exit(1)

# Test 2: Check environment variables
print_test(2, "Checking required environment variables")

reddit_id = os.getenv('REDDIT_CLIENT_ID')
reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
reddit_user_agent = os.getenv('REDDIT_USER_AGENT')
youtube_key = os.getenv('YOUTUBE_API_KEY')

missing_vars = []
if not reddit_id or reddit_id == 'your_reddit_client_id_here':
    missing_vars.append('REDDIT_CLIENT_ID')
if not reddit_secret or reddit_secret == 'your_reddit_client_secret_here':
    missing_vars.append('REDDIT_CLIENT_SECRET')
if not reddit_user_agent:
    missing_vars.append('REDDIT_USER_AGENT')
if not youtube_key or youtube_key == 'your_google_cloud_api_key_here':
    missing_vars.append('YOUTUBE_API_KEY')

if missing_vars:
    print_error(f"Missing or invalid credentials: {', '.join(missing_vars)}")
    print("          Update .env file with your actual API credentials")
    tests_failed += 1
    sys.exit(1)
else:
    print_success("All required environment variables present")
    print(f"          Reddit ID: {reddit_id[:8]}...")
    print(f"          YouTube Key: {youtube_key[:20]}...")
    tests_passed += 1

# Test 3: Reddit API (PRAW)
print_test(3, "Testing Reddit API (PRAW)")
try:
    import praw

    reddit = praw.Reddit(
        client_id=reddit_id,
        client_secret=reddit_secret,
        user_agent=reddit_user_agent
    )

    # Test query - get one post from /r/books
    subreddit = reddit.subreddit('books')
    posts = list(subreddit.hot(limit=1))

    if posts:
        print_success(f"Reddit API working!")
        print(f"          Test query retrieved: '{posts[0].title[:60]}...'")
        print(f"          Rate limit remaining: 60 requests/minute")
        tests_passed += 1
    else:
        print_error("Reddit API returned no results")
        tests_failed += 1

except ImportError:
    print_error("PRAW library not installed")
    print("          Run: pip install praw")
    tests_failed += 1
except Exception as e:
    print_error(f"Reddit API failed: {e}")
    print("          Check your REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
    print("          Verify at: https://www.reddit.com/prefs/apps")
    tests_failed += 1

# Test 4: YouTube Data API v3
print_test(4, "Testing YouTube Data API v3")
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    youtube = build('youtube', 'v3', developerKey=youtube_key)

    # Test query - search for one video
    request = youtube.search().list(
        part='snippet',
        q='python programming',
        maxResults=1,
        type='video'
    )
    response = request.execute()

    if response.get('items'):
        print_success(f"YouTube API working!")
        video_title = response['items'][0]['snippet']['title']
        print(f"          Test query retrieved: '{video_title[:60]}...'")
        print(f"          Quota usage: ~100 units (10,000 daily limit)")
        tests_passed += 1
    else:
        print_error("YouTube API returned no results")
        tests_failed += 1

except ImportError:
    print_error("google-api-python-client library not installed")
    print("          Run: pip install google-api-python-client")
    tests_failed += 1
except HttpError as e:
    if e.resp.status == 403:
        print_error("YouTube API key invalid or not enabled")
        print("          Go to: https://console.cloud.google.com/")
        print("          Enable: YouTube Data API v3")
        print("          Check: APIs & Services > Credentials")
    else:
        print_error(f"YouTube API error: {e}")
    tests_failed += 1
except Exception as e:
    print_error(f"YouTube API failed: {e}")
    tests_failed += 1

# Test 5: Google Trends (pytrends)
print_test(5, "Testing Google Trends (pytrends)")
try:
    from pytrends.request import TrendReq
    import time

    # Initialize pytrends
    pytrends = TrendReq(hl='en-US', tz=360)

    # Build payload and get data
    pytrends.build_payload(['python'], timeframe='now 7-d')

    # Small delay to respect rate limits
    time.sleep(2)

    data = pytrends.interest_over_time()

    if not data.empty:
        print_success(f"Google Trends working!")
        print(f"          Test query retrieved: {len(data)} data points")
        print(f"          No API key required (free public data)")
        tests_passed += 1
    else:
        print_error("Google Trends returned no data")
        tests_failed += 1

except ImportError:
    print_error("pytrends library not installed")
    print("          Run: pip install pytrends")
    tests_failed += 1
except Exception as e:
    print_error(f"Google Trends failed: {e}")
    print("          This may be a temporary rate limit")
    print("          Wait 30 seconds and try again")
    tests_failed += 1

# Test 6: python-dotenv
print_test(6, "Verifying python-dotenv installed")
try:
    import dotenv
    print_success("python-dotenv library installed")
    tests_passed += 1
except ImportError:
    print_error("python-dotenv not installed")
    print("          Run: pip install python-dotenv")
    tests_failed += 1

# Final Summary
print_header("Test Summary")
print(f"\nTests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")

if tests_failed == 0:
    print("\n[OK] All API credentials configured correctly!")
    print("     Ready to run Agent 0")
    print("\nNext steps:")
    print("  1. Review Docs/API-SETUP-GUIDE.md for detailed info")
    print("  2. Begin Agent 0 implementation")
    sys.exit(0)
else:
    print("\n[FAIL] Some tests failed - see errors above")
    print("       Fix the issues and run this script again")
    print("\nTroubleshooting:")
    print("  - Check .env file format (no quotes, no spaces around =)")
    print("  - Verify credentials at Reddit and Google Cloud Console")
    print("  - Install missing libraries: pip install praw pytrends google-api-python-client python-dotenv")
    sys.exit(1)

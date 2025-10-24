# API Setup Guide - Purchase Intent System

**Required APIs for MVP:**
1. ✅ Google Cloud API (YouTube Data API v3) - You already have this!
2. ⚠️ Reddit API (PRAW) - Need to create app credentials
3. ✅ Google Trends (pytrends) - No API key required

---

## 1. Google Cloud API (YouTube Data API v3)

### ✅ You Already Have Google Cloud API!

**What you need to do:**

#### Step 1: Enable YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to: **APIs & Services** → **Library**
4. Search for: **"YouTube Data API v3"**
5. Click **Enable**

#### Step 2: Create API Key (if you don't have one)

1. Go to: **APIs & Services** → **Credentials**
2. Click: **+ CREATE CREDENTIALS** → **API key**
3. Copy the API key (looks like: `AIzaSyAbc123...`)
4. (Optional) Click **Restrict Key**:
   - **API restrictions**: Select **YouTube Data API v3**
   - This prevents unauthorized use

#### Step 3: Verify Quota

1. Go to: **APIs & Services** → **Dashboard**
2. Click on **YouTube Data API v3**
3. Check quota: **10,000 units/day** (free tier)

**Quota Usage:**
- Search query: ~100 units
- Video details: ~1 unit
- Comments: ~1 unit per page
- **Agent 0 typical usage:** ~200-500 units per run (well within free tier)

---

## 2. Reddit API (PRAW) - Need to Set Up

### Step 1: Create Reddit Account (if needed)

1. Go to [reddit.com](https://www.reddit.com)
2. Sign up or log in

### Step 2: Create Reddit App

1. Go to: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Scroll to bottom, click: **"create another app..."** or **"are you a developer? create an app..."**

3. Fill out the form:
   ```
   Name: Purchase-Intent-Research
   App type: ● script
   Description: Research tool for analyzing topic demand and demographics
   About URL: (leave blank)
   Redirect URI: http://localhost:8080
   ```

4. Click **"create app"**

### Step 3: Get Credentials

After creating, you'll see:

```
Purchase-Intent-Research
personal use script
[LONG STRING OF CHARACTERS] ← This is your CLIENT_ID
secret: [ANOTHER LONG STRING] ← This is your CLIENT_SECRET
```

**Example:**
```
CLIENT_ID: abc123XYZ456def789
CLIENT_SECRET: ghi789JKL012mno345pqr678
```

### Step 4: Note Rate Limits

**Reddit API Free Tier:**
- **60 requests per minute** (plenty for Agent 0)
- No daily quota limit
- Agent 0 makes ~10-20 requests per run

---

## 3. Google Trends (pytrends) - No Setup Needed!

**Good news:** Google Trends via `pytrends` library requires **NO API key**!

**How it works:**
- Python library that scrapes Google Trends public data
- Free, no authentication required
- Rate limit: ~5 seconds between queries (built-in delay)

**Agent 0 will handle this automatically** - no credentials needed.

---

## 4. Create `.env` File

### Step 1: Create the file

Create a file named `.env` in the project root:

```bash
# Location: D:/Projects/Ai/Purchase-Intent/.env
```

### Step 2: Add your credentials

```env
# Reddit API Credentials (REQUIRED)
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=Purchase-Intent-Research/1.0 by YourRedditUsername

# YouTube Data API v3 (REQUIRED)
YOUTUBE_API_KEY=your_google_cloud_api_key_here

# Google Trends (NO CREDENTIALS NEEDED - pytrends library)
# No configuration required

# Agent Configuration (OPTIONAL)
AGENT_0_RATE_LIMIT_DELAY=2.5  # Seconds between API calls
AGENT_0_MAX_TOPICS=10          # Max topics to analyze
```

### Step 3: Replace placeholders with your actual credentials

**Example (with fake credentials):**
```env
REDDIT_CLIENT_ID=abc123XYZ456def789
REDDIT_CLIENT_SECRET=ghi789JKL012mno345pqr678
REDDIT_USER_AGENT=Purchase-Intent-Research/1.0 by u/YourUsername

YOUTUBE_API_KEY=AIzaSyAbc123def456ghi789jkl012mno345pqr678

AGENT_0_RATE_LIMIT_DELAY=2.5
AGENT_0_MAX_TOPICS=10
```

---

## 5. Verify `.env` is in `.gitignore`

**CRITICAL:** Never commit API keys to git!

Check `.gitignore` contains:
```
.env
.env.local
.env.*.local
```

Let's verify:

```bash
grep -E "^\.env" .gitignore
```

If missing, add it:
```bash
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore
```

---

## 6. Install Required Python Libraries

```bash
# Navigate to project
cd "D:/Projects/Ai/Purchase-Intent"

# Install dependencies
pip install python-dotenv praw pytrends google-api-python-client
```

**What each library does:**
- `python-dotenv`: Loads .env file into environment variables
- `praw`: Reddit API wrapper
- `pytrends`: Google Trends scraper (no API key needed)
- `google-api-python-client`: YouTube Data API v3 client

---

## 7. Test API Credentials

Create a test script to verify everything works:

**File: `test_api_credentials.py`**

```python
import os
from dotenv import load_dotenv
import praw
from pytrends.request import TrendReq
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

print("Testing API credentials...\n")

# Test 1: Environment variables loaded
print("1. Checking .env file...")
reddit_id = os.getenv('REDDIT_CLIENT_ID')
reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
youtube_key = os.getenv('YOUTUBE_API_KEY')

if reddit_id and reddit_secret and youtube_key:
    print("   ✅ .env file loaded successfully")
    print(f"   Reddit ID: {reddit_id[:8]}...")
    print(f"   YouTube Key: {youtube_key[:20]}...")
else:
    print("   ❌ Missing credentials in .env file")
    exit(1)

# Test 2: Reddit API
print("\n2. Testing Reddit API (PRAW)...")
try:
    reddit = praw.Reddit(
        client_id=reddit_id,
        client_secret=reddit_secret,
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    # Test query
    subreddit = reddit.subreddit('books')
    posts = list(subreddit.hot(limit=1))
    print(f"   ✅ Reddit API working! Retrieved post: '{posts[0].title[:50]}...'")
except Exception as e:
    print(f"   ❌ Reddit API failed: {e}")

# Test 3: YouTube API
print("\n3. Testing YouTube Data API v3...")
try:
    youtube = build('youtube', 'v3', developerKey=youtube_key)
    request = youtube.search().list(
        part='snippet',
        q='test',
        maxResults=1
    )
    response = request.execute()
    print(f"   ✅ YouTube API working! Retrieved video: '{response['items'][0]['snippet']['title'][:50]}...'")
except Exception as e:
    print(f"   ❌ YouTube API failed: {e}")

# Test 4: Google Trends
print("\n4. Testing Google Trends (pytrends)...")
try:
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(['python'], timeframe='now 7-d')
    data = pytrends.interest_over_time()
    print(f"   ✅ Google Trends working! Retrieved {len(data)} data points")
except Exception as e:
    print(f"   ❌ Google Trends failed: {e}")

print("\n" + "="*50)
print("API Credential Test Complete!")
print("="*50)
```

**Run the test:**
```bash
python test_api_credentials.py
```

**Expected output:**
```
Testing API credentials...

1. Checking .env file...
   ✅ .env file loaded successfully
   Reddit ID: abc123XY...
   YouTube Key: AIzaSyAbc123def456...

2. Testing Reddit API (PRAW)...
   ✅ Reddit API working! Retrieved post: 'What books are you reading this week?...'

3. Testing YouTube Data API v3...
   ✅ YouTube API working! Retrieved video: 'Python Tutorial for Beginners...'

4. Testing Google Trends (pytrends)...
   ✅ Google Trends working! Retrieved 8 data points

==================================================
API Credential Test Complete!
==================================================
```

---

## 8. Troubleshooting

### Issue: "Invalid client_id" (Reddit)

**Cause:** Wrong CLIENT_ID copied

**Fix:**
1. Go back to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Find your app
3. The CLIENT_ID is the **short string** directly under the app name (not the secret)
4. Update `.env` file

---

### Issue: "Invalid API key" (YouTube)

**Cause:** API key not enabled for YouTube Data API v3

**Fix:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** → **Credentials**
3. Click your API key
4. Under **API restrictions**, select **YouTube Data API v3**
5. Save

---

### Issue: "Quota exceeded" (YouTube)

**Cause:** Used more than 10,000 quota units today

**Fix:**
- Wait until tomorrow (quota resets daily at midnight Pacific Time)
- OR reduce Agent 0 query scope (analyze fewer topics)
- Each topic search uses ~100 units, Agent 0 should use ~200-500 total

---

### Issue: "429 Too Many Requests" (Reddit)

**Cause:** Exceeded 60 requests/minute rate limit

**Fix:**
- Agent 0 has built-in 2-3 second delays between requests
- Should never hit this unless running multiple instances
- Wait 1 minute and retry

---

### Issue: "TooManyRequestsError" (Google Trends)

**Cause:** Querying too fast

**Fix:**
- pytrends requires 5+ second delays between queries
- Agent 0 implements this automatically
- If testing manually, add `time.sleep(5)` between calls

---

## 9. Security Best Practices

### ✅ DO:
- Store credentials in `.env` file only
- Add `.env` to `.gitignore`
- Use environment variables in code: `os.getenv('REDDIT_CLIENT_ID')`
- Restrict Google API key to YouTube Data API v3 only

### ❌ DON'T:
- Commit `.env` file to git
- Hard-code credentials in Python files
- Share API keys publicly
- Use production Reddit account (create separate dev account)

---

## 10. Rate Limiting Strategy (Built into Agent 0)

```python
import time

# Between different API calls
time.sleep(2.5)  # AGENT_0_RATE_LIMIT_DELAY

# Google Trends specific (stricter)
time.sleep(5.0)  # pytrends requirement
```

**Agent 0 Timeline:**
- Google Trends query: 5 seconds
- Reddit query: 2.5 seconds delay + ~2 seconds execution
- YouTube query: 2.5 seconds delay + ~1 second execution
- **Total per topic:** ~15-20 seconds
- **For 10 topics:** ~2-3 minutes total

---

## Summary Checklist

- [ ] Enable YouTube Data API v3 in Google Cloud Console
- [ ] Copy YouTube API key
- [ ] Create Reddit app at reddit.com/prefs/apps
- [ ] Copy Reddit CLIENT_ID and CLIENT_SECRET
- [ ] Create `.env` file with all credentials
- [ ] Verify `.env` in `.gitignore`
- [ ] Install Python libraries: `pip install python-dotenv praw pytrends google-api-python-client`
- [ ] Run `test_api_credentials.py` to verify all APIs work
- [ ] All tests pass ✅

---

## Next Steps

Once all APIs are configured and tested:

1. **Agent 0 is ready to build!** All external dependencies configured
2. Define Agent 0 → Agent 1 data handoff schema (quick task)
3. Implement Agent 0 using LED breadcrumb system
4. Test with 5-10 topics to validate approach

---

**Questions?**

If you encounter any issues:
1. Check the Troubleshooting section above
2. Run `test_api_credentials.py` to identify which API is failing
3. Verify `.env` file format (no quotes around values, no spaces around `=`)

**Your Google Cloud API is already set up - that's a great head start! Just need to enable YouTube Data API v3 and set up Reddit.**

"""
Agent 0 Purchase Intent Analyzer
Analyzes Reddit discussions for purchase intent signals and willingness to pay

LED Range: 525-529 (Reddit Purchase Intent Analysis)
"""

import re
from typing import Dict, List
from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class PurchaseIntentAnalyzer:
    """
    Analyzes Reddit posts and comments for purchase intent signals

    Purchase Intent Signals:
    - Direct purchase questions ("should I buy", "worth it", "best to buy")
    - Price mentions ($10, $50/month, "cheap", "expensive")
    - Recommendation requests ("best X for...", "recommend")
    - Problem frequency (same question asked repeatedly)
    - Affiliate link presence (existing monetization)
    - Sentiment about paid solutions
    """

    # LED breadcrumb assignments
    LED_PURCHASE_INTENT_START = 525
    LED_KEYWORD_ANALYSIS = 525
    LED_PRICE_ANALYSIS = 526
    LED_PROBLEM_ANALYSIS = 527
    LED_MONETIZATION_ANALYSIS = 528
    LED_INTENT_SCORE_COMPLETE = 529

    # Purchase intent keywords (case-insensitive patterns)
    PURCHASE_KEYWORDS = {
        'buy': r'\b(buy|buying|bought|purchase|purchased)\b',
        'worth': r'\b(worth|value|worthwhile)\b',
        'recommend': r'\b(recommend|suggestion|suggest|best)\b',
        'price': r'\b(price|cost|expensive|cheap|affordable|budget)\b',
        'pay': r'\b(pay|paid|paying|subscription|subscribe)\b',
        'comparison': r'\b(vs|versus|compare|comparison|alternative)\b',
        'question': r'\b(should I|which one|what\'s the best|how much)\b'
    }

    # Price pattern (matches $10, $99.99, $10/mo, etc.)
    PRICE_PATTERN = r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:/\s*(?:mo|month|yr|year))?'

    # Affiliate/monetization indicators
    MONETIZATION_KEYWORDS = [
        'affiliate', 'commission', 'sponsored', 'ad', 'promo code',
        'discount code', 'referral', 'link in bio'
    ]

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

    def analyze_purchase_intent(self, keyword: str, posts: List) -> Dict:
        """
        Analyze Reddit posts for purchase intent signals

        Args:
            keyword: The search topic
            posts: List of PRAW submission objects

        Returns:
            Dict with purchase intent metrics:
            - purchase_intent_score: 0-100 overall score
            - keyword_matches: Dict of keyword category counts
            - price_mentions: List of prices found
            - price_range: (min, max) if prices found
            - problem_frequency: Count of repeated questions
            - monetization_signals: Count of affiliate/ad indicators
            - willingness_to_pay_score: 0-100 based on price discussions
            - purchase_signals: List of specific signals found
        """
        self.trail.light(self.LED_KEYWORD_ANALYSIS, {
            "action": "analyze_purchase_intent",
            "keyword": keyword,
            "total_posts": len(posts)
        })

        if not posts:
            return self._empty_result()

        # Analyze purchase keywords
        keyword_matches = self._analyze_purchase_keywords(posts)

        # Analyze price mentions
        price_data = self._analyze_price_mentions(posts)

        # Analyze problem frequency
        problem_data = self._analyze_problem_frequency(posts)

        # Analyze monetization signals
        monetization_data = self._analyze_monetization_signals(posts)

        # Calculate composite purchase intent score
        intent_score = self._calculate_purchase_intent_score(
            keyword_matches,
            price_data,
            problem_data,
            monetization_data,
            len(posts)
        )

        # Calculate willingness to pay score
        willingness_score = self._calculate_willingness_to_pay(
            price_data,
            keyword_matches,
            len(posts)
        )

        # Generate specific purchase signals list
        signals = self._generate_purchase_signals(
            keyword_matches,
            price_data,
            problem_data,
            monetization_data
        )

        result = {
            "purchase_intent_score": round(intent_score, 2),
            "willingness_to_pay_score": round(willingness_score, 2),
            "keyword_matches": keyword_matches,
            "price_mentions": price_data['prices'],
            "price_range": price_data['range'],
            "avg_price": price_data['avg_price'],
            "problem_frequency": problem_data['frequency'],
            "repeated_questions": problem_data['repeated_count'],
            "monetization_signals": monetization_data['count'],
            "monetization_types": monetization_data['types'],
            "purchase_signals": signals,
            "total_analyzed": len(posts)
        }

        self.trail.light(self.LED_INTENT_SCORE_COMPLETE, {
            "action": "purchase_intent_complete",
            "keyword": keyword,
            "purchase_intent_score": intent_score,
            "willingness_to_pay_score": willingness_score,
            "signal_count": len(signals)
        })

        return result

    def _analyze_purchase_keywords(self, posts: List) -> Dict[str, int]:
        """
        Count purchase-related keywords in titles and selftext

        Returns dict with counts per keyword category
        """
        self.trail.light(self.LED_KEYWORD_ANALYSIS, {
            "action": "analyzing_purchase_keywords"
        })

        keyword_counts = {key: 0 for key in self.PURCHASE_KEYWORDS.keys()}

        for post in posts:
            # Combine title and selftext
            text = f"{post.title} {post.selftext}".lower()

            # Count matches for each keyword pattern
            for category, pattern in self.PURCHASE_KEYWORDS.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                keyword_counts[category] += len(matches)

        self.trail.light(self.LED_KEYWORD_ANALYSIS + 1, {
            "action": "keyword_analysis_complete",
            **keyword_counts
        })

        return keyword_counts

    def _analyze_price_mentions(self, posts: List) -> Dict:
        """
        Extract and analyze price mentions from posts

        Returns dict with:
        - prices: List of prices found
        - range: (min, max) tuple
        - avg_price: Average price
        """
        self.trail.light(self.LED_PRICE_ANALYSIS, {
            "action": "analyzing_price_mentions"
        })

        prices = []

        for post in posts:
            text = f"{post.title} {post.selftext}"
            matches = re.findall(self.PRICE_PATTERN, text)

            for match in matches:
                # Remove commas and convert to float
                price = float(match.replace(',', ''))
                # Filter out unrealistic prices (0-10000 range)
                if 0 < price <= 10000:
                    prices.append(price)

        if prices:
            price_range = (min(prices), max(prices))
            avg_price = sum(prices) / len(prices)
        else:
            price_range = None
            avg_price = 0

        self.trail.light(self.LED_PRICE_ANALYSIS + 1, {
            "action": "price_analysis_complete",
            "prices_found": len(prices),
            "price_range": price_range,
            "avg_price": round(avg_price, 2) if avg_price else 0
        })

        return {
            "prices": prices,
            "range": price_range,
            "avg_price": avg_price
        }

    def _analyze_problem_frequency(self, posts: List) -> Dict:
        """
        Analyze how often similar questions/problems are repeated

        High frequency of same question = market gap / unmet need

        Returns dict with:
        - frequency: Overall problem mention frequency
        - repeated_count: Number of posts with repeated themes
        """
        self.trail.light(self.LED_PROBLEM_ANALYSIS, {
            "action": "analyzing_problem_frequency"
        })

        # Look for question patterns
        question_patterns = [
            r'how (?:do|can) (?:i|you)',
            r'what(?:\'s| is) the best',
            r'should i',
            r'which (?:one|is better)',
            r'looking for',
            r'need (?:help|advice|recommendation)'
        ]

        question_posts = 0
        for post in posts:
            text = f"{post.title} {post.selftext}".lower()
            for pattern in question_patterns:
                if re.search(pattern, text):
                    question_posts += 1
                    break

        # Calculate frequency
        total_posts = len(posts)
        frequency = (question_posts / total_posts * 100) if total_posts > 0 else 0

        self.trail.light(self.LED_PROBLEM_ANALYSIS + 1, {
            "action": "problem_analysis_complete",
            "question_posts": question_posts,
            "total_posts": total_posts,
            "frequency_pct": round(frequency, 1)
        })

        return {
            "frequency": frequency,
            "repeated_count": question_posts
        }

    def _analyze_monetization_signals(self, posts: List) -> Dict:
        """
        Detect existing monetization attempts (affiliate links, sponsored posts)

        Indicates market is already being monetized (validates demand)

        Returns dict with:
        - count: Number of posts with monetization signals
        - types: List of monetization types found
        """
        self.trail.light(self.LED_MONETIZATION_ANALYSIS, {
            "action": "analyzing_monetization_signals"
        })

        monetization_count = 0
        types_found = set()

        for post in posts:
            text = f"{post.title} {post.selftext}".lower()

            for keyword in self.MONETIZATION_KEYWORDS:
                if keyword in text:
                    monetization_count += 1
                    types_found.add(keyword)
                    break  # Count once per post

        self.trail.light(self.LED_MONETIZATION_ANALYSIS + 1, {
            "action": "monetization_analysis_complete",
            "signals_found": monetization_count,
            "types_count": len(types_found)
        })

        return {
            "count": monetization_count,
            "types": list(types_found)
        }

    def _calculate_purchase_intent_score(
        self,
        keyword_matches: Dict[str, int],
        price_data: Dict,
        problem_data: Dict,
        monetization_data: Dict,
        total_posts: int
    ) -> float:
        """
        Calculate composite purchase intent score (0-100)

        Weighted formula:
        - Purchase keywords: 30% (buy, worth, pay mentions)
        - Price mentions: 25% (price discussions indicate buying interest)
        - Problem frequency: 25% (repeated questions = unmet need)
        - Monetization: 20% (existing monetization validates market)
        """
        if total_posts == 0:
            return 0.0

        # 1. Purchase keyword score (0-100)
        # Weight: buy > pay > worth > recommend
        purchase_keywords_score = min(
            (keyword_matches['buy'] * 3 +
             keyword_matches['pay'] * 2.5 +
             keyword_matches['worth'] * 2 +
             keyword_matches['recommend'] * 1.5 +
             keyword_matches['price'] * 1 +
             keyword_matches['comparison'] * 1.5 +
             keyword_matches['question'] * 1) / total_posts * 10,
            100
        )

        # 2. Price mention score (0-100)
        # More price mentions = more buying interest
        price_score = min((len(price_data['prices']) / total_posts) * 200, 100)

        # 3. Problem frequency score (0-100)
        # Already a percentage
        problem_score = problem_data['frequency']

        # 4. Monetization score (0-100)
        # Existing monetization validates market
        monetization_score = min((monetization_data['count'] / total_posts) * 300, 100)

        # Weighted composite
        composite_score = (
            purchase_keywords_score * 0.30 +
            price_score * 0.25 +
            problem_score * 0.25 +
            monetization_score * 0.20
        )

        return composite_score

    def _calculate_willingness_to_pay(
        self,
        price_data: Dict,
        keyword_matches: Dict[str, int],
        total_posts: int
    ) -> float:
        """
        Calculate willingness to pay score (0-100)

        Based on:
        - Price discussions (people talking about prices = willing to consider)
        - Pay/subscription keywords
        - Price range (higher prices = higher willingness)
        """
        if total_posts == 0:
            return 0.0

        # 1. Price discussion frequency
        price_discussion_score = min((len(price_data['prices']) / total_posts) * 100, 50)

        # 2. Pay keyword frequency
        pay_keyword_score = min((keyword_matches['pay'] / total_posts) * 200, 30)

        # 3. Price level indicator (higher prices = higher willingness)
        avg_price = price_data['avg_price']
        if avg_price > 0:
            # Scale: $10 = 5 points, $50 = 15 points, $100 = 20 points
            price_level_score = min(avg_price / 5, 20)
        else:
            price_level_score = 0

        willingness_score = price_discussion_score + pay_keyword_score + price_level_score

        return min(willingness_score, 100)

    def _generate_purchase_signals(
        self,
        keyword_matches: Dict[str, int],
        price_data: Dict,
        problem_data: Dict,
        monetization_data: Dict
    ) -> List[str]:
        """
        Generate human-readable list of purchase intent signals found

        Returns list of signal descriptions
        """
        signals = []

        # Purchase keyword signals
        if keyword_matches['buy'] > 5:
            signals.append(f"✅ {keyword_matches['buy']} posts mention buying/purchasing")

        if keyword_matches['worth'] > 3:
            signals.append(f"✅ {keyword_matches['worth']} posts ask if it's worth it")

        if keyword_matches['pay'] > 3:
            signals.append(f"✅ {keyword_matches['pay']} posts discuss paid/subscription options")

        if keyword_matches['recommend'] > 10:
            signals.append(f"✅ {keyword_matches['recommend']} posts request recommendations")

        # Price signals
        if price_data['prices']:
            min_price, max_price = price_data['range']
            avg_price = price_data['avg_price']
            signals.append(f"💰 {len(price_data['prices'])} price mentions (${min_price:.0f}-${max_price:.0f}, avg ${avg_price:.0f})")

        # Problem frequency signals
        if problem_data['frequency'] > 40:
            signals.append(f"❓ {problem_data['repeated_count']} posts ask similar questions ({problem_data['frequency']:.0f}% of posts)")

        # Monetization signals
        if monetization_data['count'] > 0:
            signals.append(f"💵 {monetization_data['count']} posts show existing monetization ({', '.join(monetization_data['types'][:3])})")

        # Engagement signal (if high)
        if keyword_matches['comparison'] > 5:
            signals.append(f"⚖️ {keyword_matches['comparison']} posts compare options (active decision-making)")

        return signals

    def _empty_result(self) -> Dict:
        """Return empty result when no posts available"""
        return {
            "purchase_intent_score": 0,
            "willingness_to_pay_score": 0,
            "keyword_matches": {key: 0 for key in self.PURCHASE_KEYWORDS.keys()},
            "price_mentions": [],
            "price_range": None,
            "avg_price": 0,
            "problem_frequency": 0,
            "repeated_questions": 0,
            "monetization_signals": 0,
            "monetization_types": [],
            "purchase_signals": [],
            "total_analyzed": 0
        }

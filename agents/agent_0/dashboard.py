"""
Agent 0 Dashboard Generator
Creates HTML dashboard and JSON output for topic selection
"""

import json
import os
import webbrowser
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class DashboardGenerator:
    """Generates HTML dashboard and JSON output"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

    def generate_html(self, ranked_topics: List[Dict], output_path: str) -> str:
        """
        Generate HTML dashboard with topic rankings

        Args:
            ranked_topics: List of topic data dicts (sorted by score)
            output_path: Path to save HTML file

        Returns:
            Path to generated HTML file
        """
        self.trail.light(Config.LED_DASHBOARD_START, {
            "action": "generate_html",
            "topics_count": len(ranked_topics)
        })

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent 0 - Topic Research Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
        }}
        .topic-card {{
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            transition: border-color 0.3s;
        }}
        .topic-card:hover {{
            border-color: #4CAF50;
        }}
        .topic-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .topic-title {{
            font-size: 20px;
            font-weight: 600;
            color: #333;
        }}
        .topic-rank {{
            background: #4CAF50;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
        }}
        .score-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        .score-item {{
            background: #f9f9f9;
            padding: 12px;
            border-radius: 6px;
        }}
        .score-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .score-value {{
            font-size: 24px;
            font-weight: 600;
            color: #333;
        }}
        .score-composite {{ color: #4CAF50; }}
        .score-trends {{ color: #2196F3; }}
        .score-reddit {{ color: #FF5722; }}
        .score-youtube {{ color: #f44336; }}
        .confidence-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 5px;
        }}
        .confidence-high {{ background: #4CAF50; color: white; }}
        .confidence-medium {{ background: #FF9800; color: white; }}
        .confidence-low {{ background: #9E9E9E; color: white; }}
        .data-details {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
            font-size: 14px;
            color: #666;
        }}
        .detail-item {{
            padding: 8px;
            background: #fafafa;
            border-radius: 4px;
        }}
        .detail-label {{
            font-weight: 600;
            color: #333;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #999;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Topic Research Dashboard</h1>
        <p class="subtitle">Agent 0 - Purchase Intent Analysis | Generated: {timestamp}</p>
"""

        # Add topic cards
        for idx, topic_data in enumerate(ranked_topics, 1):
            topic = topic_data['topic']
            scores = topic_data['scores']
            trends = topic_data.get('trends_data', {})
            reddit = topic_data.get('reddit_data', {})
            youtube = topic_data.get('youtube_data', {})

            # Confidence badge
            confidence = scores['confidence']
            if confidence >= 80:
                conf_class = "confidence-high"
                conf_label = "HIGH"
            elif confidence >= 50:
                conf_class = "confidence-medium"
                conf_label = "MEDIUM"
            else:
                conf_class = "confidence-low"
                conf_label = "LOW"

            html += f"""
        <div class="topic-card">
            <div class="topic-header">
                <div class="topic-title">#{idx} {topic}</div>
                <div class="topic-rank">Score: {scores['composite_score']}</div>
            </div>

            <div class="score-row">
                <div class="score-item">
                    <div class="score-label">Composite Score</div>
                    <div class="score-value score-composite">{scores['composite_score']}</div>
                    <span class="{conf_class} confidence-badge">{conf_label} CONFIDENCE ({confidence}%)</span>
                </div>
                <div class="score-item">
                    <div class="score-label">Google Trends</div>
                    <div class="score-value score-trends">{scores['trends_score']}</div>
                </div>
                <div class="score-item">
                    <div class="score-label">Reddit</div>
                    <div class="score-value score-reddit">{scores['reddit_score']}</div>
                </div>
                <div class="score-item">
                    <div class="score-label">YouTube</div>
                    <div class="score-value score-youtube">{scores['youtube_score']}</div>
                </div>
            </div>

            <div class="data-details">
                <div class="detail-item">
                    <span class="detail-label">Trends:</span>
                    {trends.get('average_interest', 0):.1f} avg interest,
                    {trends.get('trend_direction', 'unknown')} trend
                </div>
                <div class="detail-item">
                    <span class="detail-label">Reddit:</span>
                    {reddit.get('total_posts', 0)} posts,
                    {reddit.get('avg_engagement', 0):.0f} avg score
                </div>
                <div class="detail-item">
                    <span class="detail-label">YouTube:</span>
                    {youtube.get('total_videos', 0)} videos,
                    {youtube.get('avg_views', 0):,.0f} avg views
                </div>
            </div>
        </div>
"""

        html += """
        <div class="footer">
            <p>Purchase Intent System - Agent 0: Topic Research Agent</p>
            <p>LED Range: 500-599 | Data sources: Google Trends, Reddit, YouTube</p>
        </div>
    </div>
</body>
</html>
"""

        # Write HTML file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        self.trail.light(Config.LED_DASHBOARD_START + 1, {
            "action": "html_generated",
            "path": output_path
        })

        return output_path

    def generate_json_output(self, ranked_topics: List[Dict], output_path: str) -> str:
        """
        Generate JSON output for Agent 1 handoff

        Schema:
        {
            "selected_topic": str,
            "confidence": float,
            "composite_score": float,
            "sources_analyzed": int,
            "all_topics": List[...]
        }
        """
        self.trail.light(Config.LED_OUTPUT_START, {
            "action": "generate_json",
            "topics_count": len(ranked_topics)
        })

        if not ranked_topics:
            output = {
                "selected_topic": None,
                "confidence": 0,
                "composite_score": 0,
                "sources_analyzed": 0,
                "all_topics": [],
                "error": "No topics analyzed"
            }
        else:
            top_topic = ranked_topics[0]
            output = {
                "selected_topic": top_topic['topic'],
                "confidence": top_topic['scores']['confidence'],
                "composite_score": top_topic['scores']['composite_score'],
                "sources_analyzed": top_topic['scores']['sources_with_data'],
                "all_topics": [
                    {
                        "rank": idx + 1,
                        "topic": t['topic'],
                        "score": t['scores']['composite_score'],
                        "confidence": t['scores']['confidence']
                    }
                    for idx, t in enumerate(ranked_topics)
                ],
                "timestamp": datetime.now().isoformat(),
                "agent": "Agent0_TopicResearch"
            }

        # Write JSON file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

        self.trail.light(Config.LED_OUTPUT_START + 1, {
            "action": "json_generated",
            "path": output_path,
            "selected_topic": output.get('selected_topic')
        })

        return output_path

    def open_dashboard(self, html_path: str) -> None:
        """Open HTML dashboard in default browser"""
        try:
            webbrowser.open(f'file://{os.path.abspath(html_path)}')
            self.trail.light(Config.LED_DASHBOARD_START + 2, {
                "action": "browser_opened",
                "path": html_path
            })
        except Exception as e:
            self.trail.fail(Config.LED_DASHBOARD_START + 2, e)

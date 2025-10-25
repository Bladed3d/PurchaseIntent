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

    def generate_html(self, ranked_topics: List[Dict], output_path: str, queue_manager=None) -> str:
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

    def generate_split_view_html(self, ranked_topics: List[Dict], tree_data: Dict, output_path: str, queue_manager=None) -> str:
        """
        Generate split-view HTML dashboard with tree navigation and chart

        Args:
            ranked_topics: List of topic data dicts (sorted by score)
            tree_data: Tree structure from drill_trail.json
            output_path: Path to save HTML file
            queue_manager: Optional queue manager (not used in dashboard generation)

        Returns:
            Path to generated HTML file
        """
        self.trail.light(Config.LED_DASHBOARD_START, {
            "action": "generate_split_view_html",
            "topics_count": len(ranked_topics)
        })

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Ensure tree_data has required structure
        if tree_data is None:
            tree_data = {"root_nodes": [], "metadata": {}}

        # Extract ALL topics from tree for initial chart display
        all_tree_topics = self._extract_all_topics_from_tree(tree_data.get('root_nodes', []))

        # Use tree topics if available, otherwise use ranked_topics
        topics_for_chart = all_tree_topics if all_tree_topics else ranked_topics

        # Build tree HTML
        tree_html = self._build_tree_html(tree_data.get('root_nodes', []))

        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent 0 - Topic Research Dashboard (Split View)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1"></script>
    <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            overflow: hidden;
        }}

        .split-container {{
            display: grid;
            grid-template-columns: 40% 60%;
            height: 100vh;
            gap: 0;
        }}

        /* LEFT PANEL - Tree Navigation */
        .tree-panel {{
            background: white;
            overflow-y: auto;
            border-right: 3px solid #667eea;
            box-shadow: 4px 0 12px rgba(0,0,0,0.1);
        }}

        .tree-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .tree-header h2 {{
            margin: 0;
            font-size: 20px;
        }}

        .tree-header .subtitle {{
            font-size: 12px;
            opacity: 0.9;
            margin-top: 5px;
        }}

        .tree-content {{
            padding: 20px;
        }}

        .tree-node {{
            margin: 8px 0;
            padding-left: 0;
        }}

        .tree-node.level-1 {{ padding-left: 20px; }}
        .tree-node.level-2 {{ padding-left: 40px; }}
        .tree-node.level-3 {{ padding-left: 60px; }}

        .node-item {{
            display: flex;
            align-items: center;
            padding: 12px 15px;
            background: #f9f9f9;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            border-left: 4px solid #e0e0e0;
            margin-bottom: 8px;
        }}

        .node-checkbox {{
            margin-right: 10px;
            cursor: pointer;
            width: 18px;
            height: 18px;
            flex-shrink: 0;
        }}

        .node-item:hover {{
            background: #e3f2fd;
            border-left-color: #2196F3;
            transform: translateX(4px);
        }}

        .node-item.selected {{
            background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
            border-left-color: #667eea;
            font-weight: 600;
        }}

        .node-item.gold-mine {{ border-left-color: #4CAF50; }}
        .node-item.viable {{ border-left-color: #2196F3; }}
        .node-item.risky {{ border-left-color: #FF9800; }}
        .node-item.avoid {{ border-left-color: #f44336; }}

        .node-icon {{
            margin-right: 10px;
            font-size: 16px;
        }}

        .node-text {{
            flex: 1;
            font-size: 14px;
        }}

        .node-score {{
            font-weight: bold;
            font-size: 13px;
            padding: 4px 8px;
            border-radius: 4px;
        }}

        .node-score.gold-mine {{ background: #C8E6C9; color: #2E7D32; }}
        .node-score.viable {{ background: #BBDEFB; color: #1565C0; }}
        .node-score.risky {{ background: #FFE0B2; color: #E65100; }}
        .node-score.avoid {{ background: #FFCDD2; color: #C62828; }}

        .toggle-btn {{
            cursor: pointer;
            margin-right: 8px;
            font-size: 12px;
            color: #666;
            user-select: none;
        }}

        .tree-children {{
            display: none;
        }}

        .tree-children.expanded {{
            display: block;
        }}

        /* RIGHT PANEL - Chart */
        .chart-panel {{
            background: white;
            overflow-y: auto;
        }}

        .chart-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .chart-header h2 {{
            margin: 0;
            font-size: 20px;
        }}

        .chart-header .subtitle {{
            font-size: 12px;
            opacity: 0.9;
            margin-top: 5px;
        }}

        .chart-container {{
            position: relative;
            height: 700px;
            margin: 20px;
            background: #fafafa;
            border-radius: 8px;
            padding: 15px;
        }}

        .info-popup {{
            display: none;
            position: fixed;
            background: white;
            border: 2px solid #667eea;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
            max-width: 700px;
            max-height: 85vh;
            z-index: 1000;
        }}

        .info-popup.active {{
            display: block;
        }}

        .info-popup h3 {{
            margin: 0 0 15px 0;
            color: #667eea;
        }}

        .info-popup .close-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            cursor: pointer;
            font-size: 24px;
            color: #999;
        }}

        .info-popup .close-btn:hover {{
            color: #333;
        }}

        .info-section {{
            margin: 10px 0;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 4px;
        }}

        .info-section strong {{
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="split-container">
        <!-- LEFT PANEL: Tree Navigation -->
        <div class="tree-panel">
            <div class="tree-header">
                <h2>🌳 Topic Hierarchy</h2>
                <div class="subtitle">Click to explore, expand to drill down</div>
            </div>
            <div class="tree-content">
                {tree_html}
            </div>
        </div>

        <!-- RIGHT PANEL: Chart -->
        <div class="chart-panel">
            <div class="chart-header">
                <h2>📊 Demand vs Competition</h2>
                <div class="subtitle">Hover bubbles for details • Generated: {timestamp}</div>
            </div>
            <div class="chart-container">
                <canvas id="topicChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Info Popup -->
    <div class="info-popup" id="infoPopup">
        <span class="close-btn" onclick="closePopup()">&times;</span>
        <div id="popupContent"></div>
    </div>

    <script>
        // Data
        const allTopics = {json.dumps(topics_for_chart)};
        const treeData = {json.dumps(tree_data)};

        let currentChart = null;
        let selectedTopics = new Set();

        // Plugin to draw richness number inside bubbles
        const centerTextPlugin = {{
            id: 'centerText',
            afterDatasetsDraw(chart) {{
                const ctx = chart.ctx;
                chart.data.datasets.forEach((dataset, i) => {{
                    const meta = chart.getDatasetMeta(i);
                    if (!meta.hidden) {{
                        meta.data.forEach((element) => {{
                            const topicData = dataset.topicData;
                            const richness = topicData?.richness?.richness_stars || topicData?.richness_stars || 5;
                            const {{x, y}} = element.getCenterPoint();

                            // White number with drop shadow for maximum contrast
                            ctx.save();

                            // Draw drop shadow for better visibility
                            ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
                            ctx.shadowBlur = 4;
                            ctx.shadowOffsetX = 2;
                            ctx.shadowOffsetY = 2;

                            ctx.font = 'bold 20px Arial';
                            ctx.fillStyle = 'white';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(richness, x, y);
                            ctx.restore();
                        }});
                    }}
                }});
            }}
        }};

        // Plugin to draw clock-ring recency visualization around bubbles
        const clockRingPlugin = {{
            id: 'clockRing',
            afterDatasetsDraw(chart) {{
                const ctx = chart.ctx;
                chart.data.datasets.forEach((dataset, i) => {{
                    const meta = chart.getDatasetMeta(i);
                    if (!meta.hidden) {{
                        meta.data.forEach((element) => {{
                            const topicData = dataset.topicData;
                            const recencyScore = topicData?.recency?.recency_score || topicData?.recency_score || 0;
                            const {{x, y}} = element.getCenterPoint();
                            const radius = element.options.radius + 3; // Ring outside bubble
                            const ringWidth = 5.5;

                            // Calculate fill percentage (0-100 maps to 0-360 degrees)
                            const fillAngle = (recencyScore / 100) * 2 * Math.PI;

                            ctx.save();
                            ctx.lineWidth = ringWidth;

                            // Draw empty ring (20% opacity purple) - full circle
                            ctx.beginPath();
                            ctx.arc(x, y, radius, 0, 2 * Math.PI);
                            ctx.strokeStyle = 'rgba(124, 77, 255, 0.2)';
                            ctx.stroke();

                            // Draw filled arc (solid purple) - from 12 o'clock clockwise
                            if (fillAngle > 0) {{
                                ctx.beginPath();
                                // Start at -90 degrees (12 o'clock) and go clockwise
                                ctx.arc(x, y, radius, -Math.PI / 2, -Math.PI / 2 + fillAngle);
                                ctx.strokeStyle = '#7C4DFF';
                                ctx.stroke();
                            }}

                            ctx.restore();
                        }});
                    }}
                }});
            }}
        }};

        // Initialize
        window.addEventListener('load', () => {{
            collectAllNodeIds(treeData.root_nodes);
            updateChartFromSelection();
        }});

        function collectAllNodeIds(nodes) {{
            if (!nodes) return;
            for (const node of nodes) {{
                selectedTopics.add(node.id);
                if (node.children) {{
                    collectAllNodeIds(node.children);
                }}
            }}
        }}

        function toggleTopicSelection(nodeId) {{
            const checkbox = document.getElementById(`check-${{nodeId}}`);
            const isChecked = checkbox.checked;

            // Update this node
            if (isChecked) {{
                selectedTopics.add(nodeId);
            }} else {{
                selectedTopics.delete(nodeId);
            }}

            // Find node and cascade to children
            const node = findNodeById(treeData.root_nodes, nodeId);
            if (node && node.children) {{
                cascadeCheckboxes(node.children, isChecked);
            }}

            updateChartFromSelection();
        }}

        function cascadeCheckboxes(nodes, checked) {{
            if (!nodes) return;
            for (const node of nodes) {{
                const childCheckbox = document.getElementById(`check-${{node.id}}`);
                if (childCheckbox) {{
                    childCheckbox.checked = checked;
                    if (checked) {{
                        selectedTopics.add(node.id);
                    }} else {{
                        selectedTopics.delete(node.id);
                    }}
                }}
                if (node.children) {{
                    cascadeCheckboxes(node.children, checked);
                }}
            }}
        }}

        function updateChartFromSelection() {{
            const topicsToShow = [];
            for (const nodeId of selectedTopics) {{
                const node = findNodeById(treeData.root_nodes, nodeId);
                if (node && node.data) {{
                    topicsToShow.push(node.data);
                }}
            }}
            // Show only checked topics (empty array = no bubbles if nothing checked)
            updateChart(topicsToShow);
        }}

        function selectNode(nodeId) {{
            const node = findNodeById(treeData.root_nodes, nodeId);
            if (!node) return;

            document.querySelectorAll('.node-item').forEach(el => el.classList.remove('selected'));
            const selectedEl = document.querySelector(`[data-node-id="${{nodeId}}"]`);
            if (selectedEl) selectedEl.classList.add('selected');

            let topicsToShow = [];
            if (node.children && node.children.length > 0) {{
                topicsToShow = node.children.map(child => child.data);
            }} else {{
                topicsToShow = [node.data];
            }}

            updateChart(topicsToShow);
        }}

        function findNodeById(nodes, id) {{
            if (!nodes) return null;
            for (const node of nodes) {{
                if (node.id === id) return node;
                if (node.children) {{
                    const found = findNodeById(node.children, id);
                    if (found) return found;
                }}
            }}
            return null;
        }}

        function toggleChildren(nodeId) {{
            const childrenDiv = document.getElementById(`children-${{nodeId}}`);
            const toggleBtn = document.getElementById(`toggle-${{nodeId}}`);
            if (childrenDiv) {{
                const isExpanded = childrenDiv.classList.toggle('expanded');
                if (toggleBtn) {{
                    toggleBtn.textContent = isExpanded ? '▼' : '▶';
                }}
            }}
        }}

        function showInfo(topicData) {{
            const popup = document.getElementById('infoPopup');
            const content = document.getElementById('popupContent');

            const scores = topicData.scores || {{}};
            const aiDesc = topicData.ai_description || topicData.description || scores.ai_description || "No description available";
            const demandScore = scores.opportunity?.demand_score || scores.composite_score || 0;
            const compScore = scores.opportunity?.competition_score || scores.competition?.overall_competition || 0;
            const opportunityScore = scores.opportunity?.opportunity_score || 0;
            const category = scores.opportunity?.recommendation || scores.zone || 'Unknown';
            const audienceSize = scores.audience_size || 0;
            const insights = scores.insights || [];

            // Reddit data
            const redditData = topicData.reddit_data || {{}};
            const topSubreddits = redditData.top_subreddits || [];

            // YouTube data
            const youtubeData = topicData.youtube_data || {{}};
            const topChannels = youtubeData.top_channels || [];

            // Build insights HTML
            const insightsHTML = insights.length > 0
                ? insights.map(insight => `<div style="margin: 4px 0;">${{insight}}</div>`).join('')
                : '<div style="color: #999;">No insights available</div>';

            // Build Reddit communities HTML with clickable links
            const redditHTML = topSubreddits.length > 0
                ? topSubreddits.map(sub => `
                    <div style="padding: 8px; background: #f5f5f5; border-radius: 4px; margin: 4px 0;">
                        <a href="https://reddit.com/r/${{sub.name}}" target="_blank" style="color: #667eea; text-decoration: none;">
                            r/${{sub.name}}
                        </a> - ${{sub.count}} members
                    </div>
                `).join('')
                : '<div style="color: #999; padding: 8px;">No Reddit data available</div>';

            // Build YouTube channels HTML with clickable links (encoded for search)
            const youtubeHTML = topChannels.length > 0
                ? topChannels.map(channel => `
                    <div style="padding: 8px; background: #f5f5f5; border-radius: 4px; margin: 4px 0;">
                        <a href="https://youtube.com/results?search_query=${{encodeURIComponent(channel.name)}}" target="_blank" style="color: #667eea; text-decoration: none;">
                            ${{channel.name}}
                        </a> - ${{channel.count}} subscribers
                    </div>
                `).join('')
                : '<div style="color: #999; padding: 8px;">No YouTube data available</div>';

            content.innerHTML = `
                <div style="max-height: calc(85vh - 100px); overflow-y: auto; padding-right: 8px;">
                    <h3 style="margin: 0 0 12px 0; color: #667eea;">${{topicData.topic}}</h3>

                    <div style="background: #e8f5e9; padding: 12px; border-radius: 6px; margin-bottom: 16px;">
                        <div style="font-weight: 600; font-size: 18px;">Score: ${{scores.composite_score?.toFixed(1) || 'N/A'}}</div>
                    </div>

                    <div style="margin-bottom: 16px; padding: 12px; background: #f9f9f9; border-radius: 6px; border-left: 3px solid #667eea;">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #667eea;">AI Description:</div>
                        <div style="font-size: 14px; line-height: 1.6; color: #333;">
                            ${{aiDesc}}
                        </div>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <div style="font-weight: 600; margin-bottom: 8px; display: flex; align-items: center;">
                            <span style="margin-right: 6px;">📊</span> Key Insights
                        </div>
                        <div style="font-size: 14px; line-height: 1.6;">
                            ${{insightsHTML}}
                        </div>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <div style="font-weight: 600; margin-bottom: 8px; display: flex; align-items: center;">
                            <span style="margin-right: 6px;">📈</span> Metrics
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px;">
                            <div style="padding: 12px; background: #f5f5f5; border-radius: 6px; border-left: 3px solid #667eea;">
                                <div style="font-size: 12px; color: #666;">Demand Score</div>
                                <div style="font-size: 20px; font-weight: 600;">${{demandScore.toFixed(1)}}</div>
                            </div>
                            <div style="padding: 12px; background: #f5f5f5; border-radius: 6px; border-left: 3px solid #ff9800;">
                                <div style="font-size: 12px; color: #666;">Competition</div>
                                <div style="font-size: 20px; font-weight: 600;">${{compScore.toFixed(1)}}</div>
                            </div>
                            <div style="padding: 12px; background: #f5f5f5; border-radius: 6px; border-left: 3px solid #4caf50;">
                                <div style="font-size: 12px; color: #666;">Opportunity</div>
                                <div style="font-size: 20px; font-weight: 600;">${{opportunityScore.toFixed(1)}}</div>
                            </div>
                        </div>
                        <div style="padding: 12px; background: #f5f5f5; border-radius: 6px;">
                            <div style="font-size: 12px; color: #666;">Audience Size</div>
                            <div style="font-size: 18px; font-weight: 600;">${{audienceSize.toLocaleString()}}</div>
                        </div>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <div style="font-weight: 600; margin-bottom: 8px; display: flex; align-items: center;">
                            <span style="margin-right: 6px;">🔥</span> Top Reddit Communities
                        </div>
                        <div>
                            ${{redditHTML}}
                        </div>
                    </div>

                    <div style="margin-bottom: 8px;">
                        <div style="font-weight: 600; margin-bottom: 8px; display: flex; align-items: center;">
                            <span style="margin-right: 6px;">📺</span> Top YouTube Channels
                        </div>
                        <div>
                            ${{youtubeHTML}}
                        </div>
                    </div>
                </div>
            `;

            popup.classList.add('active');
            popup.style.left = '50%';
            popup.style.top = '50%';
            popup.style.transform = 'translate(-50%, -50%)';
        }}

        function closePopup() {{
            document.getElementById('infoPopup').classList.remove('active');
        }}

        function showTopicSummary(nodeId) {{
            const node = findNodeById(treeData.root_nodes, nodeId);
            if (!node || !node.data) return;

            showInfo(node.data);
        }}

        function updateChart(topics) {{
            const ctx = document.getElementById('topicChart');
            if (!ctx) return;

            // Zone color mapping
            const zoneColors = {{
                gold_mine: {{ bg: 'rgba(76, 175, 80, 0.6)', border: '#4CAF50' }},
                viable: {{ bg: 'rgba(33, 150, 243, 0.6)', border: '#2196F3' }},
                risky_niche: {{ bg: 'rgba(255, 152, 0, 0.6)', border: '#FF9800' }},
                risky: {{ bg: 'rgba(255, 152, 0, 0.6)', border: '#FF9800' }},
                avoid: {{ bg: 'rgba(244, 67, 54, 0.6)', border: '#f44336' }}
            }};

            // Create one dataset per topic with flattened data structure
            const datasets = topics.map(topicData => {{
                const scores = topicData.scores || {{}};
                const zone = scores.zone || scores.opportunity?.recommendation || 'viable';
                const colors = zoneColors[zone] || zoneColors.viable;

                // Flatten data for plugins
                const flatTopic = {{
                    topic: topicData.topic,
                    demand: scores.composite_score || 0,
                    competition: scores.competition?.overall_competition || scores.opportunity?.competition_score || 0,
                    opportunity: scores.opportunity?.opportunity_score || 0,
                    audience_size: scores.audience_size || 0,
                    zone: zone,
                    confidence: scores.confidence || 100,
                    richness_stars: scores.richness?.richness_stars || 5,
                    richness_score: scores.richness?.richness_score || 100,
                    richness_breakdown: scores.richness?.breakdown || {{}},
                    recency_score: scores.recency?.recency_score || 0,
                    recency_data: scores.recency || {{}}
                }};

                return {{
                    label: flatTopic.topic,
                    data: [{{
                        x: flatTopic.competition,
                        y: flatTopic.demand,
                        r: Math.sqrt(flatTopic.audience_size / 100000) + 15  // Bubble size scales with audience
                    }}],
                    backgroundColor: colors.bg,
                    borderColor: colors.border,
                    borderWidth: 3,
                    topicData: flatTopic
                }};
            }});

            if (currentChart) {{
                currentChart.destroy();
            }}

            currentChart = new Chart(ctx, {{
                type: 'bubble',
                data: {{ datasets }},
                plugins: [centerTextPlugin, clockRingPlugin],
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    onClick: (event, elements) => {{
                        if (elements.length > 0) {{
                            const datasetIndex = elements[0].datasetIndex;
                            showInfo(topics[datasetIndex]);
                        }}
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const topic = context.dataset.topicData;
                                    const stars = '⭐'.repeat(topic.richness_stars);
                                    const breakdown = topic.richness_breakdown || {{}};
                                    const recency = topic.recency_data || {{}};

                                    let lines = [
                                        `Topic: ${{topic.topic}}`,
                                        `Demand: ${{topic.demand.toFixed(1)}}/100`,
                                        `Competition: ${{topic.competition.toFixed(1)}}/100`,
                                        `Opportunity: ${{topic.opportunity.toFixed(1)}}/100`,
                                        `Audience: ${{topic.audience_size.toLocaleString()}}`,
                                        ``,
                                        `Data Richness: ${{stars}} (${{topic.richness_stars}}/5)`
                                    ];

                                    // Add breakdown if available
                                    if (breakdown.trends) {{
                                        lines.push(`├─ Trends: ${{breakdown.trends.data_points}} pts : ${{breakdown.trends.average_interest.toFixed(1)}} interest`);
                                    }}
                                    if (breakdown.reddit) {{
                                        lines.push(`├─ Reddit: ${{breakdown.reddit.total_posts}} posts : ${{breakdown.reddit.avg_engagement.toFixed(0)}} engage`);
                                    }}
                                    if (breakdown.youtube) {{
                                        lines.push(`└─ YouTube: ${{breakdown.youtube.total_videos}} videos : ${{breakdown.youtube.avg_views.toLocaleString()}} views`);
                                    }}

                                    // Add recency information
                                    if (recency.recency_score !== undefined) {{
                                        lines.push(``);
                                        lines.push(`Recency/Urgency: ${{recency.recency_score.toFixed(1)}}/100`);
                                        if (recency.recent_90_days > 0) {{
                                            lines.push(`├─ Recent Activity: ${{recency.recent_activity_pct.toFixed(1)}}% in 90d`);
                                            lines.push(`├─ Last 30 days: ${{recency.recent_30_days}} items`);
                                            lines.push(`├─ Trend: ${{recency.trend_momentum}}`);
                                            lines.push(`└─ Avg Age: ${{recency.avg_content_age_days.toFixed(0)}} days`);
                                        }}
                                    }}

                                    lines.push(``);
                                    lines.push(`Zone: ${{topic.zone.replace('_', ' ').toUpperCase()}}`);

                                    return lines;
                                }}
                            }}
                        }},
                        legend: {{ display: false }},
                        annotation: {{
                            annotations: {{
                                verticalLine: {{
                                    type: 'line',
                                    xMin: 50,
                                    xMax: 50,
                                    borderColor: 'rgba(0, 0, 0, 0.3)',
                                    borderWidth: 2,
                                    borderDash: [5, 5]
                                }},
                                horizontalLine: {{
                                    type: 'line',
                                    yMin: 50,
                                    yMax: 50,
                                    borderColor: 'rgba(0, 0, 0, 0.3)',
                                    borderWidth: 2,
                                    borderDash: [5, 5]
                                }}
                            }}
                        }},
                        zoom: {{
                            zoom: {{
                                wheel: {{
                                    enabled: true,
                                    speed: 0.1
                                }},
                                pinch: {{
                                    enabled: true
                                }},
                                mode: 'xy'
                            }},
                            pan: {{
                                enabled: true,
                                mode: 'xy'
                            }},
                            limits: {{
                                x: {{min: 0, max: 120}},
                                y: {{min: 0, max: 120}}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: 'Competition Level →',
                                font: {{ size: 14, weight: 'bold' }}
                            }},
                            min: 0,
                            max: 120,
                            ticks: {{
                                stepSize: 10,
                                callback: function(value) {{
                                    if (value > 100) return '';
                                    return Math.round(value);
                                }}
                            }},
                            grid: {{
                                color: function(context) {{
                                    return context.tick.value <= 100 ? 'rgba(0, 0, 0, 0.1)' : 'transparent';
                                }}
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: 'Demand Score ↑',
                                font: {{ size: 14, weight: 'bold' }}
                            }},
                            min: 0,
                            max: 120,
                            ticks: {{
                                stepSize: 10,
                                callback: function(value) {{
                                    if (value > 100) return '';
                                    return Math.round(value);
                                }}
                            }},
                            grid: {{
                                color: function(context) {{
                                    return context.tick.value <= 100 ? 'rgba(0, 0, 0, 0.1)' : 'transparent';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        function getColorForCategory(category) {{
            const colors = {{
                'gold-mine': 'rgba(76, 175, 80, 0.6)',
                'viable': 'rgba(33, 150, 243, 0.6)',
                'risky': 'rgba(255, 152, 0, 0.6)',
                'avoid': 'rgba(244, 67, 54, 0.6)'
            }};
            return colors[category] || 'rgba(158, 158, 158, 0.6)';
        }}
    </script>
</body>
</html>"""

        # Write HTML file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        self.trail.light(Config.LED_DASHBOARD_START + 1, {
            "action": "split_view_html_generated",
            "path": output_path,
            "topics_count": len(ranked_topics)
        })

        return output_path

    def _build_tree_html(self, nodes: List[Dict], level: int = 0) -> str:
        """Build HTML for tree nodes recursively"""
        if not nodes:
            return "<p>No topics yet. Run research to populate the tree.</p>"

        html_parts = []
        for node in nodes:
            # Get score and category
            score = node.get('data', {}).get('scores', {}).get('composite_score', 0)
            category = node.get('data', {}).get('scores', {}).get('category', 'unknown')

            # Icon based on level
            if level == 0:
                icon = '🎯'
            elif node.get('children'):
                icon = '📁'
            else:
                icon = '📄'

            # Has children?
            has_children = node.get('children') and len(node.get('children', [])) > 0
            toggle_html = f'<span class="toggle-btn" id="toggle-{node["id"]}" onclick="event.stopPropagation(); toggleChildren(\'{node["id"]}\')">{"▼" if has_children else "  "}</span>' if has_children else ''

            # Build node HTML with checkbox
            # Paper icon shows popup, other elements select node
            icon_click = f"event.stopPropagation(); showTopicSummary('{node['id']}')" if icon == '📄' else f"selectNode('{node['id']}')"

            node_html = f'''
            <div class="tree-node level-{level}">
                <div class="node-item {category}" data-node-id="{node["id"]}">
                    <input type="checkbox" id="check-{node["id"]}" class="node-checkbox" checked onchange="toggleTopicSelection('{node["id"]}')" onclick="event.stopPropagation()">
                    {toggle_html}
                    <span class="node-icon" onclick="{icon_click}">{icon}</span>
                    <span class="node-text" onclick="selectNode('{node["id"]}')">{node["topic"]}</span>
                    <span class="node-score {category}" onclick="selectNode('{node["id"]}')">{score:.1f}</span>
                </div>
            '''

            # Add children
            if has_children:
                children_html = self._build_tree_html(node['children'], level + 1)
                node_html += f'''
                <div class="tree-children expanded" id="children-{node["id"]}">
                    {children_html}
                </div>
                '''

            node_html += '</div>'
            html_parts.append(node_html)

        return '\n'.join(html_parts)

    def _extract_all_topics_from_tree(self, nodes: List[Dict]) -> List[Dict]:
        """Extract all topic data from tree nodes recursively"""
        topics = []
        for node in nodes:
            if node.get('data'):
                topics.append(node['data'])
            if node.get('children'):
                topics.extend(self._extract_all_topics_from_tree(node['children']))
        return topics

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

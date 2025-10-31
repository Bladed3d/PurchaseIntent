"""
Agent 0 Drill-Down Trail Loader
Manages navigation history and parent-child relationships for multi-level research
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class DrillDownTrail:
    """
    Manages drill-down navigation trail for topic research

    Tracks parent-child relationships as user drills deeper into topics,
    enabling navigation back through research history and visualization
    of the complete research tree.

    LED Range: 570-589
    """

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.cache_dir = Path("cache")
        self.trail_file = self.cache_dir / "drill_trail.json"
        self.tree_data = None

        # Ensure cache directory exists
        self.cache_dir.mkdir(exist_ok=True)

        # Load existing trail
        self._load_trail()

    def _load_trail(self):
        """Load existing drill-down trail from disk"""
        self.trail.light(Config.LED_DRILL_DOWN_START + 1, {
            "action": "load_trail",
            "trail_file": str(self.trail_file)
        })

        if self.trail_file.exists():
            try:
                with open(self.trail_file, 'r', encoding='utf-8') as f:
                    self.tree_data = json.load(f)

                self.trail.light(Config.LED_DRILL_DOWN_START + 2, {
                    "action": "trail_loaded",
                    "nodes_count": self._count_nodes(self.tree_data) if self.tree_data else 0
                })
            except Exception as e:
                self.trail.fail(Config.LED_DRILL_DOWN_START + 2, e)
                print(f"[!] Warning: Could not load trail file: {e}")
                self.tree_data = None
        else:
            # Create new empty trail
            self.tree_data = {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "root_nodes": []
            }
            self.trail.light(Config.LED_DRILL_DOWN_START + 2, {
                "action": "new_trail_created"
            })

    def _count_nodes(self, tree_data: Dict) -> int:
        """Recursively count all nodes in tree"""
        if not tree_data or "root_nodes" not in tree_data:
            return 0

        def count_children(node):
            count = 1
            for child in node.get("children", []):
                count += count_children(child)
            return count

        total = 0
        for root in tree_data["root_nodes"]:
            total += count_children(root)
        return total

    def _save_trail(self):
        """Save trail to disk"""
        self.trail.light(Config.LED_DRILL_DOWN_START + 11, {
            "action": "save_trail",
            "trail_file": str(self.trail_file)
        })

        try:
            self.tree_data["last_updated"] = datetime.now().isoformat()

            with open(self.trail_file, 'w', encoding='utf-8') as f:
                json.dump(self.tree_data, f, indent=2, ensure_ascii=False)

            self.trail.light(Config.LED_DRILL_DOWN_START + 12, {
                "action": "trail_saved",
                "nodes_count": self._count_nodes(self.tree_data)
            })
        except Exception as e:
            self.trail.fail(Config.LED_DRILL_DOWN_START + 12, e)
            raise

    def find_parent_topic(self, topic: str) -> Optional[Dict]:
        """
        Find if a topic exists in the trail (potential parent for drill-down)

        Args:
            topic: Topic name to search for

        Returns:
            Node dict if found, None otherwise
        """
        self.trail.light(Config.LED_DRILL_DOWN_START + 3, {
            "action": "find_parent",
            "topic": topic
        })

        def search_node(node, target):
            if node["topic"].lower() == target.lower():
                return node
            for child in node.get("children", []):
                result = search_node(child, target)
                if result:
                    return result
            return None

        if not self.tree_data or not self.tree_data.get("root_nodes"):
            return None

        for root in self.tree_data["root_nodes"]:
            result = search_node(root, topic)
            if result:
                self.trail.light(Config.LED_DRILL_DOWN_START + 4, {
                    "action": "parent_found",
                    "topic": topic,
                    "level": result["level"]
                })
                return result

        return None

    def get_breadcrumb_path(self, topic: str) -> List[str]:
        """
        Get the full path from root to this topic

        Args:
            topic: Topic to find path for

        Returns:
            List of topic names from root to target (e.g., ['meditation', 'guided meditation'])
        """
        self.trail.light(Config.LED_DRILL_DOWN_START + 5, {
            "action": "get_breadcrumb_path",
            "topic": topic
        })

        def find_path(node, target, current_path):
            current_path = current_path + [node["topic"]]

            if node["topic"].lower() == target.lower():
                return current_path

            for child in node.get("children", []):
                result = find_path(child, target, current_path)
                if result:
                    return result

            return None

        if not self.tree_data or not self.tree_data.get("root_nodes"):
            return []

        for root in self.tree_data["root_nodes"]:
            path = find_path(root, topic, [])
            if path:
                self.trail.light(Config.LED_DRILL_DOWN_START + 6, {
                    "action": "path_found",
                    "path": " → ".join(path)
                })
                return path

        return []

    def add_research_session(self, parent_topic: Optional[str], topics: List[Dict], output_file: str):
        """
        Add a research session to the trail

        Args:
            parent_topic: Parent topic name (None for root level)
            topics: List of researched topic dicts with scores
            output_file: Path to output JSON file
        """
        self.trail.light(Config.LED_DRILL_DOWN_START + 7, {
            "action": "add_research_session",
            "parent_topic": parent_topic,
            "topics_count": len(topics)
        })

        session_time = datetime.now().isoformat()

        # Create nodes for all topics
        new_nodes = []
        for topic_data in topics:
            # Deep copy topic_data and remove non-JSON-serializable objects
            import copy
            clean_data = copy.deepcopy(topic_data)

            # Remove Reddit Submission objects (stored in trends_data and reddit_data)
            if 'trends_data' in clean_data and 'posts' in clean_data['trends_data']:
                del clean_data['trends_data']['posts']
            if 'reddit_data' in clean_data and 'posts' in clean_data['reddit_data']:
                del clean_data['reddit_data']['posts']

            node = {
                "id": f"{topic_data['topic'].replace(' ', '_')}_{session_time}",
                "topic": topic_data['topic'],
                "score": topic_data['scores']['composite_score'],
                "level": 0,  # Will be updated based on parent
                "researched_at": session_time,
                "output_file": output_file,
                "data": clean_data,
                "children": []
            }
            new_nodes.append(node)

        if parent_topic:
            # Find parent and add as children
            parent_node = self.find_parent_topic(parent_topic)
            if parent_node:
                # Update level based on parent
                parent_level = parent_node["level"]

                # Deduplicate: only add children that don't already exist
                existing_child_topics = {child["topic"] for child in parent_node["children"]}
                added_count = 0
                for node in new_nodes:
                    if node["topic"] not in existing_child_topics:
                        node["level"] = parent_level + 1
                        parent_node["children"].append(node)
                        added_count += 1

                self.trail.light(Config.LED_DRILL_DOWN_START + 8, {
                    "action": "children_added_to_parent",
                    "parent": parent_topic,
                    "children_count": added_count
                })
            else:
                # Parent not found, add as root nodes
                print(f"[!] Warning: Parent topic '{parent_topic}' not found in trail")
                print(f"[*] Adding topics as root nodes instead")
                self.tree_data["root_nodes"].extend(new_nodes)

                self.trail.light(Config.LED_DRILL_DOWN_START + 8, {
                    "action": "parent_not_found_added_as_roots",
                    "parent": parent_topic,
                    "topics_count": len(new_nodes)
                })
        else:
            # Add as root nodes (with deduplication)
            existing_root_topics = {root["topic"] for root in self.tree_data["root_nodes"]}
            added_count = 0
            for node in new_nodes:
                if node["topic"] not in existing_root_topics:
                    self.tree_data["root_nodes"].append(node)
                    added_count += 1
                else:
                    # Update existing root node data instead of creating duplicate
                    for existing in self.tree_data["root_nodes"]:
                        if existing["topic"] == node["topic"]:
                            existing["data"] = node["data"]
                            existing["score"] = node["score"]
                            existing["researched_at"] = node["researched_at"]
                            break

            self.trail.light(Config.LED_DRILL_DOWN_START + 8, {
                "action": "root_nodes_added",
                "topics_count": added_count,
                "updated_count": len(new_nodes) - added_count
            })

        # Save updated trail
        self._save_trail()

    def get_tree_for_dashboard(self) -> Dict:
        """
        Get tree structure formatted for dashboard visualization

        Returns:
            Tree data ready for JSON serialization to dashboard
        """
        self.trail.light(Config.LED_DRILL_DOWN_START + 9, {
            "action": "get_tree_for_dashboard",
            "nodes_count": self._count_nodes(self.tree_data)
        })

        return self.tree_data if self.tree_data else {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "root_nodes": []
        }

    def clear_trail(self):
        """Clear entire trail (useful for testing)"""
        self.trail.light(Config.LED_DRILL_DOWN_START + 10, {
            "action": "clear_trail"
        })

        self.tree_data = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "root_nodes": []
        }

        self._save_trail()

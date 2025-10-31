"""
Agent 2: Demographics Analyst

Extracts demographic profiles from product reviews and discussions.
Validates via triangulation across multiple sources.

LED Range: 2500-2599
"""

from agents.agent_2.config import Agent2Config
from agents.agent_2.demographics_extractor import DemographicsExtractor, DemographicProfile
from agents.agent_2.aggregator import DemographicsAggregator, DemographicCluster
from agents.agent_2.confidence_calculator import ConfidenceCalculator
from agents.agent_2.checkpoint import CheckpointGate
from agents.agent_2.scraper import DataScraper

__all__ = [
    'Agent2Config',
    'DemographicsExtractor',
    'DemographicProfile',
    'DemographicsAggregator',
    'DemographicCluster',
    'ConfidenceCalculator',
    'CheckpointGate',
    'DataScraper'
]

"""
Agent 0 Playwright CSV Parser
Parses downloaded Google Trends CSVs into PyTrends-compatible format

LED Breadcrumb Range: 580-589 (CSV parsing operations)
- 580: Parser initialization
- 581: Interest Over Time parsing
- 582: Related Queries parsing
- 583: Related Topics parsing
- 584: Interest By Region parsing
- 585: Data transformation
- 586: DataFrame creation
- 587: Validation
- 588: Error handling
- 589: Completion
"""

import csv
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd
from datetime import datetime

from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class PlaywrightCSVParser:
    """
    Parses Google Trends CSV downloads into PyTrends-compatible DataFrames

    Handles all 4 CSV types:
    - Interest Over Time
    - Related Queries (TOP + RISING)
    - Related Topics (TOP + RISING)
    - Interest By Region
    """

    def __init__(self, trail: BreadcrumbTrail):
        """
        Initialize CSV parser

        Args:
            trail: LED breadcrumb trail for debugging
        """
        self.trail = trail

        self.trail.light(580, {
            "action": "parser_init"
        })

    def identify_csv_type(self, file_path: str) -> Optional[str]:
        """
        Identify which type of CSV this is based on column headers

        Args:
            file_path: Path to CSV file

        Returns:
            One of: 'interest_over_time', 'related_queries', 'related_topics', 'interest_by_region', or None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read first few lines
                lines = [f.readline().strip() for _ in range(5)]

            # Check for identifying patterns
            if lines and 'Week' in lines[0] or 'Month' in lines[0] or 'Day' in lines[0]:
                return 'interest_over_time'
            elif lines and 'TOP' in '\n'.join(lines):
                # Check if it's queries or topics
                if 'query' in lines[0].lower():
                    return 'related_queries'
                else:
                    return 'related_topics'
            elif lines and 'Region' in lines[0]:
                return 'interest_by_region'

            return None

        except Exception as e:
            self.trail.light(588, {
                "action": "identify_csv_type_error",
                "file_path": file_path,
                "error": str(e)[:200]
            })
            return None

    def parse_interest_over_time(self, file_path: str, keyword: str) -> Optional[pd.DataFrame]:
        """
        Parse Interest Over Time CSV to PyTrends format

        PyTrends format:
        - Index: datetime
        - Column: keyword (values 0-100)
        - Column: isPartial (boolean)

        CSV format:
        Week,[keyword]
        2004-01-04 - 2004-01-10,45
        2004-01-11 - 2004-01-17,47

        Args:
            file_path: Path to CSV file
            keyword: Search keyword

        Returns:
            DataFrame with datetime index and keyword column, or None on error
        """
        self.trail.light(581, {
            "action": "parse_interest_over_time_start",
            "file_path": file_path,
            "keyword": keyword
        })

        try:
            # Read CSV
            df = pd.read_csv(file_path, skiprows=0)

            # Get time column name (Week, Month, or Day)
            time_col = None
            for col in df.columns:
                if col in ['Week', 'Month', 'Day', 'Date']:
                    time_col = col
                    break

            if not time_col:
                self.trail.light(588, {
                    "action": "parse_interest_over_time_no_time_column",
                    "columns": list(df.columns)
                })
                return None

            # Extract start date from range (e.g., "2004-01-04 - 2004-01-10" → "2004-01-04")
            df['date'] = df[time_col].str.split(' - ').str[0]
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            # Set as index
            df = df.set_index('date')

            # Drop the original time column
            df = df.drop(columns=[time_col])

            # Rename keyword column if needed
            if keyword in df.columns:
                df = df[[keyword]]  # Keep only keyword column
            else:
                # If column name doesn't match keyword, assume it's the first data column
                data_cols = [col for col in df.columns if col not in ['isPartial']]
                if data_cols:
                    df = df.rename(columns={data_cols[0]: keyword})
                    df = df[[keyword]]

            # Add isPartial column (last row is usually partial)
            df['isPartial'] = False
            if len(df) > 0:
                df.iloc[-1, df.columns.get_loc('isPartial')] = True

            # Convert to numeric
            df[keyword] = pd.to_numeric(df[keyword], errors='coerce').fillna(0).astype(int)

            self.trail.light(581, {
                "action": "parse_interest_over_time_complete",
                "rows": len(df),
                "columns": list(df.columns)
            })

            return df

        except Exception as e:
            self.trail.fail(588, e)
            return None

    def parse_related_queries_or_topics(self, file_path: str) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Parse Related Queries or Topics CSV to PyTrends format

        PyTrends format:
        {
            'top': DataFrame with columns [query/topic, value],
            'rising': DataFrame with columns [query/topic, value]
        }

        CSV format:
        TOP,value
        corona,100
        coronavirus symptoms,97

        RISING,value
        coronavirus vaccine,Breakout
        covid-19 test,+5000%

        Args:
            file_path: Path to CSV file

        Returns:
            Dict with 'top' and 'rising' DataFrames, or None on error
        """
        csv_type = self.identify_csv_type(file_path)
        led_num = 582 if csv_type == 'related_queries' else 583

        self.trail.light(led_num, {
            "action": f"parse_{csv_type}_start",
            "file_path": file_path
        })

        try:
            # Read entire CSV
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find TOP and RISING sections
            top_start = None
            rising_start = None

            for i, line in enumerate(lines):
                if line.strip().startswith('TOP'):
                    top_start = i
                elif line.strip().startswith('RISING'):
                    rising_start = i

            result = {}

            # Parse TOP section
            if top_start is not None:
                top_end = rising_start if rising_start else len(lines)
                top_lines = lines[top_start:top_end]

                # Parse as CSV
                top_data = []
                for line in top_lines[1:]:  # Skip header
                    line = line.strip()
                    if line and ',' in line:
                        parts = line.split(',', 1)
                        if len(parts) == 2:
                            query, value = parts
                            # Convert value (handle "100", "Breakout", "+5000%")
                            if value == 'Breakout':
                                value_num = 'Breakout'
                            elif value.endswith('%'):
                                value_num = value
                            else:
                                try:
                                    value_num = int(value)
                                except:
                                    value_num = value

                            top_data.append({'query': query.strip(), 'value': value_num})

                if top_data:
                    result['top'] = pd.DataFrame(top_data)

            # Parse RISING section
            if rising_start is not None:
                rising_lines = lines[rising_start:]

                rising_data = []
                for line in rising_lines[1:]:  # Skip header
                    line = line.strip()
                    if line and ',' in line:
                        parts = line.split(',', 1)
                        if len(parts) == 2:
                            query, value = parts
                            # Convert value
                            if value == 'Breakout':
                                value_num = 'Breakout'
                            elif value.endswith('%'):
                                value_num = value
                            else:
                                try:
                                    value_num = int(value)
                                except:
                                    value_num = value

                            rising_data.append({'query': query.strip(), 'value': value_num})

                if rising_data:
                    result['rising'] = pd.DataFrame(rising_data)

            self.trail.light(led_num, {
                "action": f"parse_{csv_type}_complete",
                "top_rows": len(result.get('top', [])),
                "rising_rows": len(result.get('rising', []))
            })

            return result if result else None

        except Exception as e:
            self.trail.fail(588, e)
            return None

    def parse_interest_by_region(self, file_path: str, keyword: str) -> Optional[pd.DataFrame]:
        """
        Parse Interest By Region CSV to PyTrends format

        PyTrends format:
        - Index: region name
        - Column: keyword (values 0-100)

        CSV format:
        Region,[keyword]
        California,100
        Texas,87

        Args:
            file_path: Path to CSV file
            keyword: Search keyword

        Returns:
            DataFrame with region index and keyword column, or None on error
        """
        self.trail.light(584, {
            "action": "parse_interest_by_region_start",
            "file_path": file_path,
            "keyword": keyword
        })

        try:
            # Read CSV
            df = pd.read_csv(file_path, skiprows=0)

            # Set region as index
            if 'Region' in df.columns:
                df = df.set_index('Region')

            # Rename keyword column if needed
            if keyword not in df.columns and len(df.columns) > 0:
                # Assume first column is keyword
                df = df.rename(columns={df.columns[0]: keyword})

            # Convert to numeric
            if keyword in df.columns:
                df[keyword] = pd.to_numeric(df[keyword], errors='coerce').fillna(0).astype(int)

            self.trail.light(584, {
                "action": "parse_interest_by_region_complete",
                "rows": len(df),
                "columns": list(df.columns)
            })

            return df

        except Exception as e:
            self.trail.fail(588, e)
            return None

    def parse_all_csvs(self, csv_files: List[str], keyword: str) -> Dict[str, any]:
        """
        Parse all CSV files for a keyword into PyTrends-compatible format

        Args:
            csv_files: List of CSV file paths downloaded for this keyword
            keyword: Search keyword

        Returns:
            Dict with keys matching PyTrends methods:
            - 'interest_over_time': DataFrame
            - 'related_queries': Dict[str, DataFrame] (top/rising)
            - 'related_topics': Dict[str, DataFrame] (top/rising)
            - 'interest_by_region': DataFrame
        """
        self.trail.light(580, {
            "action": "parse_all_csvs_start",
            "keyword": keyword,
            "csv_count": len(csv_files)
        })

        result = {}

        for csv_file in csv_files:
            csv_type = self.identify_csv_type(csv_file)

            if not csv_type:
                self.trail.light(588, {
                    "action": "unknown_csv_type",
                    "file_path": csv_file
                })
                continue

            if csv_type == 'interest_over_time':
                result['interest_over_time'] = self.parse_interest_over_time(csv_file, keyword)

            elif csv_type == 'related_queries':
                result['related_queries'] = self.parse_related_queries_or_topics(csv_file)

            elif csv_type == 'related_topics':
                result['related_topics'] = self.parse_related_queries_or_topics(csv_file)

            elif csv_type == 'interest_by_region':
                result['interest_by_region'] = self.parse_interest_by_region(csv_file, keyword)

        self.trail.light(589, {
            "action": "parse_all_csvs_complete",
            "keyword": keyword,
            "parsed_types": list(result.keys())
        })

        return result

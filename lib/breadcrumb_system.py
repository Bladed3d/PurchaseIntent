"""
Purchase Intent System - LED Breadcrumb System
Python implementation for autonomous debugging and monitoring

Based on VoiceCoach V2 breadcrumb-system.ts pattern
Optimized for CLI Python agents with JSON Lines logging

SECURITY: Auto-sanitizes API keys, tokens, and secrets before logging
"""

import json
import time
import traceback
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from datetime import datetime


@dataclass
class Breadcrumb:
    """Individual LED breadcrumb record"""
    id: int
    name: str
    component: str
    timestamp: float
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    stack: Optional[str] = None


@dataclass
class VerificationResult:
    """Verification data for lightWithVerification"""
    expect: Any
    actual: Any
    validator: Optional[Callable[[Any], bool]] = None


# SECURITY: Patterns that indicate sensitive data
SENSITIVE_KEY_PATTERNS = [
    'api_key', 'apikey', 'api-key', 'key',
    'secret', 'password', 'token', 'auth',
    'credential', 'authorization', 'bearer',
    'client_secret', 'client_id', 'access_token',
    'refresh_token', 'session', 'cookie'
]

# SECURITY: Regex patterns for detecting API keys in strings
SECRET_VALUE_PATTERNS = [
    r'AIza[0-9A-Za-z_-]{35}',  # Google API keys
    r'sk-[0-9A-Za-z]{48}',  # OpenAI API keys
    r'Bearer\s+[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+',  # JWT tokens
    r'[A-Za-z0-9]{40}',  # Generic 40-char tokens (GitHub, AWS)
    r'xox[baprs]-[0-9A-Za-z\-]+',  # Slack tokens
    r'ghp_[0-9A-Za-z]{36}',  # GitHub personal access tokens
    r'AKIA[0-9A-Z]{16}',  # AWS access keys
]


class BreadcrumbTrail:
    """
    LED breadcrumb trail for Python CLI agents

    Features:
    - JSON Lines logging for easy grep/parsing
    - Console output with emojis for human readability
    - Global trail aggregation across all agents
    - Failure tracking for autonomous debugging
    - Verification and checkpoint support

    Usage:
        trail = BreadcrumbTrail("Agent0_TopicResearch")
        trail.light(500, {"action": "Starting Google Trends query"})
        trail.light(501, {"topics_found": 15})
        if error:
            trail.fail(502, Exception("API rate limit exceeded"))
    """

    # Class-level storage for global trail
    _global_trail: List[Breadcrumb] = []
    _global_failures: List[Breadcrumb] = []
    _component_trails: Dict[str, 'BreadcrumbTrail'] = {}
    _log_file: Optional[Path] = None

    def __init__(self, component_name: str, log_file: Optional[str] = None):
        """
        Initialize breadcrumb trail for a component

        Args:
            component_name: Name of component/agent (e.g., "Agent0_TopicResearch")
            log_file: Optional path to JSON Lines log file (default: logs/breadcrumbs.jsonl)
        """
        self.component_name = component_name
        self.sequence: List[Breadcrumb] = []
        self.assertions: List[Dict[str, Any]] = []

        # Register this trail globally
        BreadcrumbTrail._component_trails[component_name] = self

        # Set up logging
        if log_file:
            BreadcrumbTrail._log_file = Path(log_file)
        elif BreadcrumbTrail._log_file is None:
            # Default log location
            log_dir = Path(__file__).parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            BreadcrumbTrail._log_file = log_dir / "breadcrumbs.jsonl"

    def light(self, led_id: int, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Light an LED breadcrumb (success)

        Args:
            led_id: LED number (500-4599 for Purchase Intent agents)
            data: Optional data dictionary to attach
        """
        breadcrumb = Breadcrumb(
            id=led_id,
            name=self._get_led_name(led_id),
            component=self.component_name,
            timestamp=time.time(),
            success=True,
            data=data
        )

        self.sequence.append(breadcrumb)
        BreadcrumbTrail._global_trail.append(breadcrumb)

        # Console output with emoji (safe encoding)
        data_str = json.dumps(data or {})
        try:
            print(f"🎵 LED {led_id}: {breadcrumb.name} - {data_str} {self.component_name}_{led_id}")
        except UnicodeEncodeError:
            # Fallback for Windows console without emoji support
            print(f"[OK] LED {led_id}: {breadcrumb.name} - {data_str} {self.component_name}_{led_id}")

        # Write to JSON Lines log
        self._write_log(breadcrumb)

    def light_with_verification(
        self,
        led_id: int,
        data: Any,
        verification: Optional[VerificationResult] = None
    ) -> bool:
        """
        Light LED with optional verification check

        Args:
            led_id: LED number
            data: Data to attach
            verification: Optional verification to perform

        Returns:
            True if verification passed (or no verification), False otherwise
        """
        # Standard LED lighting
        self.light(led_id, data if isinstance(data, dict) else {"value": data})

        # Verification step
        if verification:
            if verification.validator:
                passed = verification.validator(verification.actual)
            else:
                passed = verification.expect == verification.actual

            if not passed:
                error_msg = (
                    f"Verification failed: Expected {verification.expect}, "
                    f"got {verification.actual}"
                )
                self.fail(led_id, Exception(error_msg))
                return False

            self.assertions.append({
                "led_id": led_id,
                "passed": passed,
                "expect": verification.expect,
                "actual": verification.actual,
                "timestamp": time.time()
            })

        return True

    def checkpoint(
        self,
        led_id: int,
        checkpoint_name: str,
        validation_fn: Callable[[], bool],
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a validation checkpoint

        Args:
            led_id: LED number
            checkpoint_name: Name of checkpoint
            validation_fn: Function that returns True if checkpoint passes
            data: Optional additional data

        Returns:
            True if checkpoint passed, False otherwise
        """
        passed = validation_fn()

        checkpoint_data = {
            "checkpoint": checkpoint_name,
            "status": "PASSED" if passed else "FAILED",
            **(data or {})
        }

        if passed:
            self.light(led_id, checkpoint_data)
        else:
            self.fail(led_id, Exception(f"Checkpoint failed: {checkpoint_name}"))

        return passed

    def fail(self, led_id: int, error: Exception) -> None:
        """
        Record a failed LED breadcrumb

        Args:
            led_id: LED number
            error: Exception that caused the failure
        """
        breadcrumb = Breadcrumb(
            id=led_id,
            name=self._get_led_name(led_id),
            component=self.component_name,
            timestamp=time.time(),
            success=False,
            error=str(error),
            stack=traceback.format_exc()
        )

        self.sequence.append(breadcrumb)
        BreadcrumbTrail._global_trail.append(breadcrumb)
        BreadcrumbTrail._global_failures.append(breadcrumb)

        # Console error output (safe encoding)
        try:
            print(f"❌ LED {led_id} FAILED [{self.component_name}]: {breadcrumb.name} {error}")
        except UnicodeEncodeError:
            # Fallback for Windows console without emoji support
            print(f"[FAIL] LED {led_id} FAILED [{self.component_name}]: {breadcrumb.name} {error}")

        # Write to JSON Lines log
        self._write_log(breadcrumb)

    def get_verification_summary(self) -> Dict[str, Any]:
        """
        Get summary of all verifications and failures

        Returns:
            Dictionary with verification statistics
        """
        failures = [b for b in self.sequence if not b.success]

        return {
            "total_leds": len(self.sequence),
            "failures": len(failures),
            "assertions_passed": sum(1 for a in self.assertions if a["passed"]),
            "assertions_failed": sum(1 for a in self.assertions if not a["passed"]),
            "failure_rate": len(failures) / max(len(self.sequence), 1),
            "critical_failures": [f for f in failures if 8000 <= f.id < 9000],
            "verification_passed": len(failures) == 0 and all(a["passed"] for a in self.assertions)
        }

    def _get_led_name(self, led_id: int) -> str:
        """
        Get descriptive name for LED based on range

        Purchase Intent System ranges:
        - 500-599: Agent 0 - Topic Research
        - 1500-1599: Agent 1 - Product Research
        - 2500-2599: Agent 2 - Demographics Analysis
        - 3500-3599: Agent 3 - Persona Generation
        - 4500-4599: Agent 4 - ParaThinker Intent Simulation
        - 5000-9099: General Application (if needed)
        """
        if 500 <= led_id < 600:
            return "AGENT0_TOPIC_RESEARCH"
        elif 1500 <= led_id < 1600:
            return "AGENT1_PRODUCT_RESEARCH"
        elif 2500 <= led_id < 2600:
            return "AGENT2_DEMOGRAPHICS"
        elif 3500 <= led_id < 3600:
            return "AGENT3_PERSONA_GENERATION"
        elif 4500 <= led_id < 4600:
            return "AGENT4_INTENT_SIMULATION"
        elif 5000 <= led_id < 6000:
            return "ANALYTICS_REPORTING"
        elif 6000 <= led_id < 7000:
            return "API_INTEGRATION"
        elif 7000 <= led_id < 8000:
            return "UI_INTERACTIONS"
        elif 8000 <= led_id < 9000:
            return "ERROR_HANDLING"
        elif 9000 <= led_id < 10000:
            return "TESTING_VALIDATION"
        else:
            return f"LED_{led_id}"

    def _sanitize_value(self, value: Any) -> Any:
        """
        Sanitize a single value (recursive for nested structures)

        SECURITY: Redacts API keys, tokens, passwords, secrets
        """
        if value is None:
            return value

        if isinstance(value, dict):
            return self._sanitize_data(value)

        if isinstance(value, list):
            return [self._sanitize_value(item) for item in value]

        if isinstance(value, str):
            # Check if value looks like a secret (matches known patterns)
            for pattern in SECRET_VALUE_PATTERNS:
                if re.search(pattern, value):
                    return "***REDACTED_SECRET***"

            # Redact very long strings that might be tokens (>50 chars with no spaces)
            if len(value) > 50 and ' ' not in value:
                return "***REDACTED_LONG_STRING***"

        return value

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive data before logging

        SECURITY: Auto-detects and redacts:
        - API keys (by key name: api_key, token, secret, etc.)
        - Credential values (Google API keys AIza..., OpenAI sk-..., etc.)
        - Long tokens and bearer strings
        """
        if not data:
            return data

        sanitized = {}
        for key, value in data.items():
            # Normalize key for comparison (lowercase, no separators)
            key_normalized = key.lower().replace('_', '').replace('-', '').replace(' ', '')

            # Check if key name indicates sensitive data
            is_sensitive_key = any(pattern in key_normalized for pattern in SENSITIVE_KEY_PATTERNS)

            if is_sensitive_key:
                sanitized[key] = "***REDACTED_API_KEY***"
            else:
                sanitized[key] = self._sanitize_value(value)

        return sanitized

    def _sanitize_string(self, text: str) -> str:
        """
        Sanitize a string (for error messages, stack traces)

        SECURITY: Redacts secrets that might appear in URLs, error messages, etc.
        """
        if not text:
            return text

        sanitized = text
        for pattern in SECRET_VALUE_PATTERNS:
            sanitized = re.sub(pattern, '***REDACTED_SECRET***', sanitized)

        return sanitized

    def _write_log(self, breadcrumb: Breadcrumb) -> None:
        """
        Write breadcrumb to JSON Lines log file

        SECURITY: Automatically sanitizes sensitive data before writing
        """
        if BreadcrumbTrail._log_file:
            try:
                with open(BreadcrumbTrail._log_file, 'a', encoding='utf-8') as f:
                    log_entry = asdict(breadcrumb)

                    # SECURITY: Sanitize data field
                    if log_entry.get('data'):
                        log_entry['data'] = self._sanitize_data(log_entry['data'])

                    # SECURITY: Sanitize error messages (might contain URLs with tokens)
                    if log_entry.get('error'):
                        log_entry['error'] = self._sanitize_string(log_entry['error'])

                    # SECURITY: Sanitize stack traces
                    if log_entry.get('stack'):
                        log_entry['stack'] = self._sanitize_string(log_entry['stack'])

                    log_entry['iso_timestamp'] = datetime.fromtimestamp(
                        breadcrumb.timestamp
                    ).isoformat()
                    f.write(json.dumps(log_entry) + '\n')
            except Exception as e:
                # Don't fail the application if logging fails
                print(f"⚠️  Failed to write breadcrumb log: {e}")

    @classmethod
    def get_all(cls) -> List[Breadcrumb]:
        """Get all breadcrumbs across all components"""
        return cls._global_trail

    @classmethod
    def get_range(cls, start: int, end: int) -> List[Breadcrumb]:
        """Get breadcrumbs within a specific LED range"""
        return [b for b in cls._global_trail if start <= b.id <= end]

    @classmethod
    def get_failures(cls) -> List[Breadcrumb]:
        """Get all failed breadcrumbs"""
        return cls._global_failures

    @classmethod
    def get_component(cls, name: str) -> Optional[List[Breadcrumb]]:
        """Get breadcrumbs for a specific component"""
        trail = cls._component_trails.get(name)
        return trail.sequence if trail else None

    @classmethod
    def clear(cls) -> None:
        """Clear all breadcrumb trails (useful for testing)"""
        cls._global_trail.clear()
        cls._global_failures.clear()
        for trail in cls._component_trails.values():
            trail.sequence.clear()
            trail.assertions.clear()

    @classmethod
    def check_range(cls, start: int, end: int) -> Dict[str, Any]:
        """
        Check if all LEDs in a range fired successfully

        Returns:
            Dictionary with passed status, missing LEDs, and failed LEDs
        """
        leds = cls.get_range(start, end)
        failed = [b.id for b in leds if not b.success]
        existing = [b.id for b in leds]
        expected = list(range(start, end + 1))
        missing = [led_id for led_id in expected if led_id not in existing]

        return {
            "passed": len(failed) == 0 and len(missing) == 0,
            "missing": missing,
            "failed": failed
        }

    @classmethod
    def get_quality_score(cls) -> float:
        """
        Calculate quality score (0-100) based on failure rate

        Returns:
            Percentage of successful breadcrumbs
        """
        total = len(cls._global_trail)
        failures = len(cls._global_failures)
        if total == 0:
            return 0.0
        return round(((total - failures) / total) * 100, 2)


# Convenience function for quick LED lighting without creating a trail object
def light_led(led_id: int, component: str, data: Optional[Dict[str, Any]] = None) -> None:
    """
    Quick LED lighting without managing a BreadcrumbTrail object

    Args:
        led_id: LED number
        component: Component name
        data: Optional data dictionary
    """
    trail = BreadcrumbTrail._component_trails.get(component)
    if not trail:
        trail = BreadcrumbTrail(component)
    trail.light(led_id, data)

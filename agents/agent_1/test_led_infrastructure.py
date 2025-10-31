"""
Agent 1 LED Infrastructure Verification Test
Tests that all LED breadcrumbs fire correctly and integrate with breadcrumb_system.py

Run with: python agents/agent_1/test_led_infrastructure.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_1.config import Agent1Config as Config


def test_led_ranges():
    """Test that all LED constants are within the 1500-1599 range"""
    print("Testing LED range assignments...")

    led_constants = {
        "LED_INIT": Config.LED_INIT,
        "LED_AMAZON_START": Config.LED_AMAZON_START,
        "LED_REDDIT_START": Config.LED_REDDIT_START,
        "LED_YOUTUBE_START": Config.LED_YOUTUBE_START,
        "LED_GOODREADS_START": Config.LED_GOODREADS_START,
        "LED_COMPARABLES_START": Config.LED_COMPARABLES_START,
        "LED_OVERLAP_START": Config.LED_OVERLAP_START,
        "LED_CHECKPOINT_START": Config.LED_CHECKPOINT_START,
        "LED_OUTPUT_START": Config.LED_OUTPUT_START,
        "LED_ERROR_START": Config.LED_ERROR_START,
    }

    all_valid = True
    for name, led_id in led_constants.items():
        if not (1500 <= led_id < 1600):
            print(f"  ❌ {name} = {led_id} (OUT OF RANGE)")
            all_valid = False
        else:
            print(f"  ✅ {name} = {led_id}")

    return all_valid


def test_led_firing():
    """Test that LEDs fire correctly and are tracked"""
    print("\nTesting LED firing and tracking...")

    # Clear any existing breadcrumbs
    BreadcrumbTrail.clear()

    # Create trail
    trail = BreadcrumbTrail("Agent1_Test")

    # Fire some test LEDs
    trail.light(Config.LED_INIT, {"action": "test_init"})
    trail.light(Config.LED_AMAZON_START, {"action": "test_amazon_start"})
    trail.light(Config.LED_AMAZON_START + 1, {"action": "test_amazon_complete"})

    # Check they were recorded
    all_leds = BreadcrumbTrail.get_all()
    agent1_leds = [b for b in all_leds if 1500 <= b.id < 1600]

    if len(agent1_leds) == 3:
        print(f"  ✅ All 3 test LEDs fired correctly")
        return True
    else:
        print(f"  ❌ Expected 3 LEDs, got {len(agent1_leds)}")
        return False


def test_error_tracking():
    """Test that error LEDs are tracked correctly"""
    print("\nTesting error tracking...")

    # Clear any existing breadcrumbs
    BreadcrumbTrail.clear()

    # Create trail
    trail = BreadcrumbTrail("Agent1_ErrorTest")

    # Fire a test error
    test_error = Exception("Test error for LED verification")
    trail.fail(Config.LED_ERROR_START, test_error)

    # Check error was recorded
    failures = BreadcrumbTrail.get_failures()

    if len(failures) == 1 and failures[0].id == Config.LED_ERROR_START:
        print(f"  ✅ Error LED tracked correctly")
        print(f"     LED {failures[0].id}: {failures[0].error}")
        return True
    else:
        print(f"  ❌ Error tracking failed")
        return False


def test_verification():
    """Test verification functionality"""
    print("\nTesting verification functionality...")

    # Clear any existing breadcrumbs
    BreadcrumbTrail.clear()

    # Create trail
    trail = BreadcrumbTrail("Agent1_VerificationTest")

    # Test passing verification
    from lib.breadcrumb_system import VerificationResult
    result = trail.light_with_verification(
        Config.LED_COMPARABLES_START,
        {"comparables": 10},
        verification=VerificationResult(
            expect=">=5 comparables",
            actual=10,
            validator=lambda x: x >= 5
        )
    )

    if result:
        print(f"  ✅ Verification passed correctly")
        return True
    else:
        print(f"  ❌ Verification failed unexpectedly")
        return False


def test_checkpoint():
    """Test checkpoint functionality"""
    print("\nTesting checkpoint functionality...")

    # Clear any existing breadcrumbs
    BreadcrumbTrail.clear()

    # Create trail
    trail = BreadcrumbTrail("Agent1_CheckpointTest")

    # Test checkpoint that passes
    result = trail.checkpoint(
        Config.LED_CHECKPOINT_START,
        "test_checkpoint",
        lambda: True,  # Validation passes
        {"test_data": "sample"}
    )

    if result:
        print(f"  ✅ Checkpoint passed correctly")
        return True
    else:
        print(f"  ❌ Checkpoint failed unexpectedly")
        return False


def test_led_naming():
    """Test LED naming convention"""
    print("\nTesting LED naming...")

    # Clear any existing breadcrumbs
    BreadcrumbTrail.clear()

    # Create trail
    trail = BreadcrumbTrail("Agent1_NamingTest")

    # Fire LED and check name
    trail.light(Config.LED_INIT, {"test": "naming"})

    all_leds = BreadcrumbTrail.get_all()
    if all_leds and all_leds[0].name == "AGENT1_PRODUCT_RESEARCH":
        print(f"  ✅ LED naming correct: {all_leds[0].name}")
        return True
    else:
        print(f"  ❌ LED naming incorrect")
        return False


def test_quality_score():
    """Test quality score calculation"""
    print("\nTesting quality score calculation...")

    # Clear any existing breadcrumbs
    BreadcrumbTrail.clear()

    # Create trail
    trail = BreadcrumbTrail("Agent1_QualityTest")

    # Fire 8 successful LEDs
    for i in range(8):
        trail.light(1500 + i, {"test": i})

    # Fire 2 failed LEDs
    for i in range(2):
        trail.fail(1590 + i, Exception(f"Test error {i}"))

    # Calculate quality score
    score = BreadcrumbTrail.get_quality_score()
    expected_score = 80.0  # 8/10 = 80%

    if score == expected_score:
        print(f"  ✅ Quality score correct: {score}%")
        return True
    else:
        print(f"  ❌ Quality score incorrect: {score}% (expected {expected_score}%)")
        return False


def main():
    """Run all LED infrastructure tests"""
    print("=" * 80)
    print("AGENT 1 LED INFRASTRUCTURE VERIFICATION TEST")
    print("=" * 80)
    print()

    tests = [
        ("LED Range Assignment", test_led_ranges),
        ("LED Firing", test_led_firing),
        ("Error Tracking", test_error_tracking),
        ("Verification", test_verification),
        ("Checkpoint", test_checkpoint),
        ("LED Naming", test_led_naming),
        ("Quality Score", test_quality_score),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - LED infrastructure is production ready!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review LED implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())

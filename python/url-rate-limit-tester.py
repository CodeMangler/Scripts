import requests
import time
import random
from urllib.parse import urlparse
import argparse
from datetime import datetime


class RequestRateLimitTester:
    def __init__(self, url, min_delay=0, max_delay=30, steps=10, requests_per_step=5):
        self.url = url
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.steps = steps
        self.requests_per_step = requests_per_step
        self.domain = urlparse(url).netloc
        self.session = self.create_session()
        self.results = {}

    def create_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return session

    def generate_delays(self):
        return [self.min_delay + i * (self.max_delay - self.min_delay) / (self.steps - 1)
                for i in range(self.steps)]

    def print_header(self):
        print(f"\nTesting rate limits for {self.domain}")
        print(f"Testing delays from {self.min_delay} to {self.max_delay} seconds in {self.steps} steps")
        print("-" * 60)
        print("| Delay (s) | Success | Status | Time (ms) | Notes       |")
        print("|-----------|---------|--------|-----------|-------------|")

    def make_request(self, delay, request_index):
        # Add a small random variation to the delay to make it look more natural
        actual_delay = delay * (1 + random.uniform(-0.1, 0.1))
        if request_index > 0:  # Don't delay before the first request of each step
            time.sleep(actual_delay)

        try:
            start_time = time.time()
            response = self.session.get(self.url, timeout=30)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000
            success = 200 <= response.status_code < 300

            return success, response_time, response.status_code, None

        except requests.exceptions.RequestException as e:
            return False, 0, 0, str(e)[:10]

    def test_with_delay(self, delay):
        successes = 0
        response_times = []
        status_codes = []

        for i in range(self.requests_per_step):
            success, response_time, status_code, error_msg = self.make_request(delay, i)

            if success:
                successes += 1

            if status_code in [429, 503]:
                print(f"| {delay:9.1f} | {successes:7d} | {status_code:6d} | {response_time:9.1f} | Rate limited |")
                break

            if error_msg:
                print(f"| {delay:9.1f} | {successes:7d} | ERROR   | ---       | {error_msg}  |")
                break

            response_times.append(response_time)
            status_codes.append(status_code)

        success_rate = successes / self.requests_per_step if self.requests_per_step > 0 else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        dominant_status = max(set(status_codes), key=status_codes.count) if status_codes else "N/A"

        print(
            f"| {delay:9.1f} | {success_rate * 100:6.1f}% | {dominant_status:6} | {avg_response_time:9.1f} | {self.requests_per_step} requests |")

        return {
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'dominant_status': dominant_status
        }

    def print_recommendations(self):
        successful_delays = {d: r for d, r in self.results.items()
                             if r['success_rate'] == 1.0 and
                             isinstance(r['dominant_status'], int) and
                             200 <= r['dominant_status'] < 300}

        if successful_delays:
            recommended_delay = min(successful_delays.keys())
            buffer_factor = 1.5  # Add safety buffer
            final_recommendation = recommended_delay * buffer_factor

            print("\nRECOMMENDATION:")
            print(f"Minimum successful delay: {recommended_delay:.1f} seconds")
            print(f"Recommended delay with safety buffer: {final_recommendation:.1f} seconds")
        else:
            print("\nNo completely successful delay found. Consider:")
            print("1. Increasing the maximum delay")
            print("2. Checking if the site is blocking automated requests")
            print("3. Using more sophisticated request patterns")

        print(f"\nTest completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def run_test(self):
        self.print_header()

        for delay in self.generate_delays():
            self.results[delay] = self.test_with_delay(delay)

        self.print_recommendations()
        return self.results


def test_rate_limits(url, min_delay=0, max_delay=30, steps=10, requests_per_step=5):
    """
    Test a URL for rate limiting by gradually increasing the delay between requests.

    Args:
        url: The URL to test
        min_delay: Starting delay in seconds
        max_delay: Maximum delay in seconds
        steps: Number of different delay values to test
        requests_per_step: Number of requests to make for each delay value

    Returns:
        dict: Test results for each delay
    """
    tester = RequestRateLimitTester(url, min_delay, max_delay, steps, requests_per_step)
    return tester.run_test()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test URL rate limits')
    parser.add_argument('url', help='URL to test')
    parser.add_argument('--min', type=float, default=5, help='Minimum delay in seconds')
    parser.add_argument('--max', type=float, default=30, help='Maximum delay in seconds')
    parser.add_argument('--steps', type=int, default=6, help='Number of delay steps to test')
    parser.add_argument('--requests', type=int, default=5, help='Requests per step')

    args = parser.parse_args()

    test_rate_limits(
        args.url,
        min_delay=args.min,
        max_delay=args.max,
        steps=args.steps,
        requests_per_step=args.requests
    )

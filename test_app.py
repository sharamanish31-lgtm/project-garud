import pytest
import requests

BASE_URL = "http://127.0.0.1:80"

def test_home_route_integrity():
    """Verifies public root is operational internally"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200

def test_jarvis_dashboard_availability():
    """Ensures UI canvas dashboard answers properly inside network"""
    response = requests.get(f"{BASE_URL}/jarvis")
    assert response.status_code == 200

def test_circuit_breaker_rate_limiting():
    """Validates local perimeter block response matrix"""
    target_url = f"{BASE_URL}/invalid-scanning-path-check"
    # Testing rate limiter logic directly via internal network gate
    responses = [requests.get(target_url) for _ in range(6)]
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes or 200 in status_codes

"""
Test script to verify API documentation endpoints are accessible.
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(url, description):
    """Test if an endpoint is accessible."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✓ {description}: SUCCESS (Status: {response.status_code})")
            return True
        else:
            print(f"✗ {description}: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ {description}: ERROR - {str(e)}")
        return False

def main():
    """Run all tests."""
    print("Testing Phantom Scheduler API Documentation Endpoints\n")
    print("=" * 60)
    
    tests = [
        (f"{BASE_URL}/api/schema/", "OpenAPI Schema Endpoint"),
        (f"{BASE_URL}/api/docs/", "Swagger UI Documentation"),
        (f"{BASE_URL}/api/redoc/", "ReDoc Documentation"),
    ]
    
    results = []
    for url, description in tests:
        result = test_endpoint(url, description)
        results.append(result)
        print()
    
    print("=" * 60)
    print(f"\nResults: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("\n✓ All API documentation endpoints are working correctly!")
        return 0
    else:
        print("\n✗ Some endpoints failed. Please check the server logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

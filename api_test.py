#!/usr/bin/env python3
"""
API Test Script for Smart Ticketing System
This script tests the ESP32 API endpoints to ensure they work correctly
"""

import requests
import json
import secrets
import time
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:5000"  # Change to your server URL
DEVICE_ID = "ESP32_TEST_001"

def test_device_status():
    """Test the device status endpoint"""
    print("Testing device status endpoint...")
    
    url = f"{SERVER_URL}/api/device_status"
    data = {
        "device_id": DEVICE_ID,
        "status": "online",
        "door_open": False,
        "wifi_strength": -45,
        "uptime": 12345
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_qr_validation():
    """Test QR validation with invalid QR code"""
    print("\nTesting QR validation with invalid code...")
    
    url = f"{SERVER_URL}/api/validate_qr"
    data = {
        "qr_code": "INVALID_QR_CODE_12345",
        "device_id": DEVICE_ID
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 404
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_valid_qr_validation(qr_code):
    """Test QR validation with a valid QR code"""
    print(f"\nTesting QR validation with valid code: {qr_code}")
    
    url = f"{SERVER_URL}/api/validate_qr"
    data = {
        "qr_code": qr_code,
        "device_id": DEVICE_ID
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [200, 403, 404]  # Any valid response
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_test_user():
    """Create a test user account"""
    print("\nCreating test user...")
    
    url = f"{SERVER_URL}/register"
    data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "phone": "+250788123456",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            print("Test user created successfully")
            return data
        else:
            print(f"Response: {response.json()}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def login_user(username, password):
    """Login and get session"""
    print(f"\nLogging in user: {username}")
    
    url = f"{SERVER_URL}/login"
    data = {
        "username": username,
        "password": password
    }
    
    session = requests.Session()
    
    try:
        response = session.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Login successful")
            return session
        else:
            print(f"Response: {response.json()}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_missing_qr_parameter():
    """Test QR validation endpoint without QR code parameter"""
    print("\nTesting QR validation without QR code parameter...")
    
    url = f"{SERVER_URL}/api/validate_qr"
    data = {
        "device_id": DEVICE_ID
        # Missing qr_code parameter
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def simulate_esp32_requests():
    """Simulate a series of ESP32 requests"""
    print("\n" + "="*50)
    print("SIMULATING ESP32 REQUESTS")
    print("="*50)
    
    # Test scenarios
    test_cases = [
        ("Empty QR code", ""),
        ("Short invalid QR", "123"),
        ("Random QR code", secrets.token_urlsafe(32)),
        ("Another random QR", secrets.token_urlsafe(16)),
    ]
    
    for description, qr_code in test_cases:
        print(f"\n--- {description} ---")
        test_valid_qr_validation(qr_code)
        time.sleep(1)  # Small delay between requests

def run_comprehensive_test():
    """Run comprehensive API testing"""
    print("="*60)
    print("SMART TICKETING SYSTEM - API TESTING")
    print("="*60)
    print(f"Server URL: {SERVER_URL}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Test started at: {datetime.now()}")
    
    results = []
    
    # Test 1: Device Status
    results.append(("Device Status", test_device_status()))
    
    # Test 2: Missing QR Parameter
    results.append(("Missing QR Parameter", test_missing_qr_parameter()))
    
    # Test 3: Invalid QR Code
    results.append(("Invalid QR Code", test_invalid_qr_validation()))
    
    # Test 4: Simulate ESP32 requests
    simulate_esp32_requests()
    
    # Print results summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:<25}: {status}")
    
    passed_count = sum(results)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("✅ All tests passed! ESP32 API is working correctly.")
    else:
        print("❌ Some tests failed. Check the Flask server and configuration.")

def test_server_connectivity():
    """Test basic server connectivity"""
    print("Testing server connectivity...")
    
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is accessible")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is the Flask app running?")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

if __name__ == "__main__":
    print("Smart Ticketing System - ESP32 API Test")
    print("Make sure the Flask server is running before starting tests.\n")
    
    # Check server connectivity first
    if not test_server_connectivity():
        print("\nPlease start the Flask server with:")
        print("python app.py")
        exit(1)
    
    # Run comprehensive tests
    run_comprehensive_test()
    
    print(f"\nTest completed at: {datetime.now()}")
    print("\nTo test with actual valid QR codes:")
    print("1. Start the Flask app")
    print("2. Register a user and purchase a ticket")
    print("3. Use the QR code from the ticket in this test script")
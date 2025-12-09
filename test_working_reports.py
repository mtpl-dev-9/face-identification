"""Test script to verify Working Reports API works with your database"""
import requests

# Test with user ID 1 (has data from 2025-11-27)
print("Testing Working Reports API...")
print("-" * 50)

# Test 1: Get last 7 days for user 1
print("\nTest 1: User 1 - Last 7 days")
response = requests.get("http://127.0.0.1:5000/api/working-reports?user_id=1")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Success: {data.get('success')}")
if data.get('success'):
    print(f"Records found: {len(data.get('records', []))}")
    for record in data.get('records', []):
        print(f"  - {record.get('date')}: {record.get('clock_in_time')} to {record.get('clock_out_time')}")
else:
    print(f"Error: {data.get('error')}")

# Test 2: Get specific date for user 1
print("\nTest 2: User 1 - Date 27, Month 11, Year 2025")
response = requests.get("http://127.0.0.1:5000/api/working-reports?user_id=1&date=27&month=11&year=2025")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Success: {data.get('success')}")
if data.get('success'):
    print(f"Records found: {len(data.get('records', []))}")
    for record in data.get('records', []):
        print(f"  - {record.get('date')}: {record.get('clock_in_time')} to {record.get('clock_out_time')}")
        print(f"    Worked: {record.get('worked_hours')} hrs, Diff: {record.get('total_hours_difference')} hrs")
else:
    print(f"Error: {data.get('error')}")

# Test 3: Get last 7 days for user 5
print("\nTest 3: User 5 - Last 7 days")
response = requests.get("http://127.0.0.1:5000/api/working-reports?user_id=5")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Success: {data.get('success')}")
if data.get('success'):
    print(f"Records found: {len(data.get('records', []))}")
    for record in data.get('records', []):
        print(f"  - {record.get('date')}: {record.get('clock_in_time')} to {record.get('clock_out_time')}")
else:
    print(f"Error: {data.get('error')}")

print("\n" + "-" * 50)
print("Test complete!")

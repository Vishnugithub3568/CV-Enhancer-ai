import requests

# Test all Day 4 endpoints
print("=" * 60)
print("Testing Day 4 — Resume Generator Endpoints")
print("=" * 60)

# Test Parse Resume
print("\n1. Testing /parse-resume/")
try:
    response = requests.get('http://127.0.0.1:8003/parse-resume/')
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Has raw_text: {'raw_text' in data}")
    print(f"   Has parsed_data: {'parsed_data' in data}")
    if 'parsed_data' in data:
        print(f"   Parsed keys: {list(data['parsed_data'].keys())}")
except Exception as e:
    print(f"   Error: {e}")

# Test Enhance Resume
print("\n2. Testing /enhance-resume/")
try:
    response = requests.get('http://127.0.0.1:8003/enhance-resume/')
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Has parsed_data: {'parsed_data' in data}")
    print(f"   Has enhanced_resume: {'enhanced_resume' in data}")
except Exception as e:
    print(f"   Error: {e}")

# Test Generate Resume
print("\n3. Testing /generate-resume/ (Day 4)")
try:
    response = requests.get('http://127.0.0.1:8003/generate-resume/')
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {data}")
    if 'file_path' in data:
        print(f"   Generated file: {data['file_path']}")
        import os
        if os.path.exists(data['file_path']):
            print(f"   ✓ File verified to exist!")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("Day 4 Testing Complete!")
print("=" * 60)

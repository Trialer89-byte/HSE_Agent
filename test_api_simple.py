import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TENANT_DOMAIN = "demo.hse-system.com"

print("=== HSE Multi-Tenant API Test ===\n")

# 1. Login
print("1. LOGIN TEST")
login_data = {
    "username": "superadmin",
    "password": "SuperAdmin123!"
}

response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
if response.status_code == 200:
    auth_data = response.json()
    token = auth_data["access_token"]
    print(f"✓ Login successful!")
    print(f"  User: {auth_data['user']['username']}")
    print(f"  Role: {auth_data['user']['role']}")
else:
    print(f"✗ Login failed: {response.text}")
    exit(1)

# 2. Create Work Permit
print("\n2. CREATE WORK PERMIT")
headers = {
    "Authorization": f"Bearer {token}",
    "X-Tenant-Domain": TENANT_DOMAIN,
    "Content-Type": "application/json"
}

permit_data = {
    "title": "Manutenzione Serbatoio A1",
    "description": "Pulizia interna e ispezione",
    "work_type": "confined_space",
    "location": "Area Stoccaggio",
    "duration_hours": 4,
    "priority_level": "high",
    "dpi_required": ["respiratore", "imbracatura", "rilevatore_gas"]
}

response = requests.post(
    f"{BASE_URL}/api/v1/permits",
    headers=headers,
    json=permit_data
)

if response.status_code in [200, 201]:
    permit = response.json()
    print(f"✓ Work permit created!")
    print(f"  ID: {permit.get('id', 'N/A')}")
    print(f"  Title: {permit.get('title', 'N/A')}")
else:
    print(f"✗ Failed to create permit: {response.text}")

# 3. List Permits
print("\n3. LIST WORK PERMITS")
response = requests.get(
    f"{BASE_URL}/api/v1/permits",
    headers=headers
)

if response.status_code == 200:
    permits = response.json()
    print(f"✓ Found {len(permits)} permits:")
    for permit in permits:
        print(f"  - {permit['title']} (ID: {permit['id']})")
else:
    print(f"✗ Failed to list permits: {response.text}")

print("\n=== Test Complete ===")
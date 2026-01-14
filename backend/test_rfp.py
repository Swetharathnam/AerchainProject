import requests

# Test RFP creation
rfp_data = {
    "title": "Test RFP",
    "description": "I need 20 laptops",
    "budget": 50000,
    "currency": "USD",
    "status": "DRAFT"
}

response = requests.post("http://localhost:8000/rfps/", json=rfp_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

import requests
import json

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API endpoint
API_URL = "http://localhost:8000/analyze/simple"

# Your credentials - Set these in environment variables or .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-proj-YOUR_OPENAI_KEY_HERE")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC_YOUR_TWILIO_SID_HERE")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "YOUR_TWILIO_TOKEN_HERE")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+91_YOUR_PHONE_HERE")

# Test inventory with LOW COST items to trigger AUTO_APPROVE
test_request = {
    "inventory": [
        {
            "id": 1,
            "name": "Pens",
            "stock": 2,
            "reorderPoint": 10,
            "price": 2.50,  # Low price = AUTO_APPROVE
            "vendor": "Office Supplies",
            "vendorEmail": "orders@office.com",
            "vendorPhone": "+91 9876543210",
            "lastOrder": "2026-01-01",
            "salesPerDay": 1.5
        },
        {
            "id": 2,
            "name": "Notebooks",
            "stock": 5,
            "reorderPoint": 20,
            "price": 3.00,  # Low price = AUTO_APPROVE
            "vendor": "Stationery Hub",
            "vendorEmail": "sales@stationery.com",
            "vendorPhone": "+91 9876543211",
            "lastOrder": "2026-01-02",
            "salesPerDay": 2.0
        }
    ],
    "openai_api_key": OPENAI_API_KEY,
    "resend_api_key": None,
    "user_email": "shop@yourstore.com",
    "twilio_account_sid": TWILIO_ACCOUNT_SID,
    "twilio_auth_token": TWILIO_AUTH_TOKEN,
    "twilio_phone_number": TWILIO_PHONE_NUMBER,
    "send_sms": True
}

print("=" * 70)
print("AUTONOMOS SMS TEST - AUTO_APPROVE Items")
print("=" * 70)
print(f"\n📱 Testing SMS sending to vendor phones...")
print(f"📲 Twilio Phone: {TWILIO_PHONE_NUMBER}")
print(f"\nSending request to: {API_URL}\n")

try:
    response = requests.post(API_URL, json=test_request)
    response.raise_for_status()
    
    result = response.json()
    
    print("✅ Request successful!\n")
    print("Response Summary:")
    print(json.dumps(result, indent=2))
    
    # Check SMS status for each decision
    if "decisions" in result:
        print("\n" + "=" * 70)
        print("SMS STATUS DETAILS")
        print("=" * 70)
        for decision in result["decisions"]:
            print(f"\nItem: {decision['item']}")
            print(f"Decision: {decision['decision']}")
            print(f"Cost: ${decision['cost']}")
            print(f"Urgency: {decision['urgency']}")
            
            if "smsStatus" in decision:
                sms = decision["smsStatus"]
                print(f"SMS Success: {sms['success']}")
                if sms['success']:
                    if sms.get('simulated'):
                        print("⚠️  SMS simulated (Twilio not properly configured)")
                    else:
                        print(f"✅ SMS ID: {sms.get('sms_id')}")
                        print(f"📊 Status: {sms.get('status')}")
                        print(f"Message: {sms.get('message')}")
                else:
                    print(f"❌ Error: {sms.get('error')}")
            else:
                print("⏭️  SMS not sent (decision not auto-approved or phone missing)")
    
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to backend!")
    print("   Make sure the server is running:")
    print("   uvicorn autonomos_backend:app --reload --port 8000")
except requests.exceptions.RequestException as e:
    print(f"❌ Request error: {e}")
    print(f"\nResponse: {response.text if 'response' in locals() else 'No response'}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

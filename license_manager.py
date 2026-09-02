###############################################################
# LICENSE MANAGER
# AI Linux Command Assistant
###############################################################

import os
import json
import hashlib
import platform
import requests

# ── YOUR GUMROAD PRODUCT ID ───────────────────────────────
# Get this from Gumroad Dashboard after creating product
GUMROAD_PRODUCT_ID = "YOUR_PRODUCT_ID_HERE"

LICENSE_FILE = os.path.join(
    os.path.expanduser("~"),
    ".ai_assistant",
    "license.json"
)

###############################################################
def get_machine_id():
    """Generate unique ID for this PC"""
    raw = (
        platform.node() +
        platform.machine() +
        platform.processor()
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

###############################################################
def save_license(key, email):
    """Save verified license to disk"""
    os.makedirs(os.path.dirname(LICENSE_FILE), exist_ok=True)
    data = {
        "key":        key,
        "email":      email,
        "machine_id": get_machine_id()
    }
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

###############################################################
def load_license():
    """Load saved license from disk"""
    try:
        with open(LICENSE_FILE, "r") as f:
            return json.load(f)
    except:
        return None

###############################################################
def verify_license_gumroad(license_key, email):
    """
    Verify license key with Gumroad API
    Returns: (True/False, message)
    """
    try:
        url = "https://api.gumroad.com/v2/licenses/verify"
        response = requests.post(url, data={
            "product_id":  GUMROAD_PRODUCT_ID,
            "license_key": license_key,
            "email":       email
        }, timeout=10)

        data = response.json()

        if data.get("success"):
            return True, "License verified!"
        else:
            return False, data.get(
                "message", "Invalid license key"
            )

    except requests.exceptions.ConnectionError:
        # No internet — fallback to saved license
        saved = load_license()
        if saved and saved.get("key") == license_key:
            return True, "License verified (offline mode)"
        return False, "No internet connection to verify license"

    except Exception as e:
        return False, f"Verification error: {str(e)}"

###############################################################
def check_license():
    """
    Check if this machine has a valid license
    Returns: (True/False, license_data)
    """
    saved = load_license()
    if not saved:
        return False, None

    # Verify machine ID matches
    if saved.get("machine_id") != get_machine_id():
        return False, None

    return True, saved

###############################################################
def activate_license(key, email):
    """
    Activate and save a new license key
    Returns: (True/False, message)
    """
    valid, message = verify_license_gumroad(key, email)
    if valid:
        save_license(key, email)
    return valid, message

###############################################################
def deactivate_license():
    """Remove saved license from this machine"""
    try:
        if os.path.exists(LICENSE_FILE):
            os.remove(LICENSE_FILE)
        return True
    except:
        return False

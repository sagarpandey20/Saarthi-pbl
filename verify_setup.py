
import sys

def check_import(module_name):
    try:
        __import__(module_name)
        print(f"[OK] {module_name} imported successfully.")
        return True
    except ImportError as e:
        print(f"[FAIL] Could not import {module_name}: {e}")
        return False

print("Verifying System Setup...")
print(f"Python Version: {sys.version}")

checks = [
    "flask",
    "speech_recognition",
    "gtts",
    "deep_translator"
]

all_pass = True
for module in checks:
    if not check_import(module):
        all_pass = False

import os
if not os.path.exists('static'):
    try:
        os.makedirs('static')
        print("[OK] 'static' directory created.")
    except Exception as e:
        print(f"[FAIL] Could not create 'static' directory: {e}")
        all_pass = False
else:
    print("[OK] 'static' directory exists.")

if all_pass:
    print("\nSUCCESS: All dependencies appear to be installed correctly.")
    print("You can run the app using: python app.py")
else:
    print("\nERROR: Some dependencies are missing. Please run: pip install -r requirements.txt")

"""encode_service_account.py — Run this ONCE locally to encode the service 
account JSON as base64. Copy the output into Railway as SERVICE_ACCOUNT_JSON.

Usage:
  python encode_service_account.py service_account.json
"""

import base64
import sys
import os


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "service_account.json"
    if not os.path.exists(path):
        print(f"❌  File not found: {path}")
        sys.exit(1)

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    print("\n" + "=" * 64)
    print("  Copy this value into Railway → SERVICE_ACCOUNT_JSON")
    print("=" * 64)
    print(f"\nSERVICE_ACCOUNT_JSON={encoded}\n")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    main()

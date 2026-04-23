"""encode_cv.py — Run this ONCE locally to encode Vincent's CV as base64.
Copy the output string into Railway as the CV_BASE64 environment variable.

Usage:
  python encode_cv.py CV_Vincent_Oppong.pdf
"""

import base64
import sys
import os


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "CV_Vincent_Oppong.pdf"
    if not os.path.exists(path):
        print(f"❌  Fichier introuvable : {path}")
        sys.exit(1)

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    print("\n" + "=" * 64)
    print("  Copie cette valeur dans Railway → CV_BASE64")
    print("=" * 64)
    print(f"\nCV_BASE64={encoded}\n")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    main()

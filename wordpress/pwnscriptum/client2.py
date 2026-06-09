#!/usr/bin/env python3
"""
WordPress Normal User Client
----------------------------
A benign client to verify WordPress site connectivity and browse the site like
a normal visitor (home page, login page, static assets and RSS feed).
"""

import argparse
import sys
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    try:
        r = requests.get(f"{target}/", timeout=10, verify=False)
        print(f"[+] Connected to WordPress server (HTTP {r.status_code})")
        if "wordpress" in r.text.lower() or "wp-content" in r.text.lower():
            print("[+] WordPress signature detected in response body")
        else:
            print("[*] Target reachable, but WordPress signature was not found")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection failed: {e}")
        return False


def simulate_active(target):
    try:
        r1 = requests.get(f"{target}/wp-login.php", timeout=10, verify=False)
        print(f"[+] Visited login page (HTTP {r1.status_code})")

        r2 = requests.get(f"{target}/wp-includes/js/jquery/jquery.js", timeout=10, verify=False)
        print(f"[+] Fetched jQuery static asset (HTTP {r2.status_code})")

        r3 = requests.get(f"{target}/?feed=rss2", timeout=10, verify=False)
        print(f"[+] Fetched RSS feed (HTTP {r3.status_code})")
    except Exception as e:
        print(f"[-] Active simulation failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="WordPress Normal User Client")
    parser.add_argument("target", help="Target WordPress URL, e.g. http://localhost:8081")
    parser.add_argument("--mode", choices=["check", "active"], default="check", help="Simulation mode")
    args = parser.parse_args()

    target = args.target.rstrip("/")

    print(f"[*] Target: {target}")
    if args.mode == "check":
        if not check_target(target):
            sys.exit(1)
    elif args.mode == "active":
        simulate_active(target)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
WordPress Normal User Client
----------------------------
A benign client to verify WordPress site connectivity and retrieve posts/users via REST API.
"""

import argparse
import sys
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    try:
        r = requests.get(f"{target}/", timeout=10, verify=False)
        print(f"[+] Connected to WordPress server (HTTP {r.status_code})")

        # Query public REST API
        api_url = f"{target}/wp-json/"
        r_api = requests.get(api_url, timeout=10, verify=False)
        if r_api.status_code == 200:
            print("[+] WordPress REST API is active")
            try:
                data = r_api.json()
                name = data.get("name", "WordPress Site")
                print(f"[+] Site Name: {name}")
            except ValueError:
                pass
        else:
            print(f"[*] REST API response status: HTTP {r_api.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection failed: {e}")
        return False


def simulate_active(target):
    try:
        r1 = requests.get(f"{target}/wp-json/wp/v2/posts", timeout=10, verify=False)
        print(f"[+] Fetched blog posts via WordPress REST API (HTTP {r1.status_code})")
        if r1.status_code == 200:
            print(f"[+] Found {len(r1.json())} published posts")
            
        r2 = requests.get(f"{target}/wp-json/wp/v2/users", timeout=10, verify=False)
        print(f"[+] Fetched users list via WordPress REST API (HTTP {r2.status_code})")
        if r2.status_code == 200:
            print(f"[+] Found {len(r2.json())} public user accounts")
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

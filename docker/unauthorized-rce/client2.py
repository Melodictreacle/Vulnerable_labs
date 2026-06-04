#!/usr/bin/env python3
"""
Docker Status Checker
---------------------
A benign client to connect to an exposed Docker daemon API and display version details and simulate container operations.
"""

import argparse
import sys
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    try:
        r = requests.get(f"{target}/version", timeout=10, verify=False)
        print(f"[+] Connected to Docker Daemon (HTTP {r.status_code})")
        if r.status_code == 200:
            data = r.json()
            print(f"[+] Docker Version: {data.get('Version', 'Unknown')}")
            print(f"[+] API Version: {data.get('ApiVersion', 'Unknown')}")
            return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection failed: {e}")
        return False


def simulate_active(target):
    try:
        r1 = requests.get(f"{target}/containers/json?all=1", timeout=10, verify=False)
        print(f"[+] Listed containers (HTTP {r1.status_code})")
        if r1.status_code == 200:
            containers = r1.json()
            print(f"[+] Total containers: {len(containers)}")
            
        r2 = requests.get(f"{target}/images/json", timeout=10, verify=False)
        print(f"[+] Listed images (HTTP {r2.status_code})")
        if r2.status_code == 200:
            images = r2.json()
            print(f"[+] Total images: {len(images)}")
    except Exception as e:
        print(f"[-] Active simulation failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Docker Status Checker")
    parser.add_argument("target", help="Target Docker API URL, e.g. http://localhost:2375")
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

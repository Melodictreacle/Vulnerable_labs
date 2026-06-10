#!/usr/bin/env python3
"""
Struts2 Normal User Client
--------------------------
A benign client to connect to the Struts2 endpoint using normal HTTP requests and submit benign forms.
"""

import argparse
import sys
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    try:
        # Send a normal GET request
        r = requests.get(f"{target}/", timeout=10, verify=False)
        print(f"[+] Connected to Struts2 application (HTTP {r.status_code})\n[+] Response Body:\n{r.text[:250]}...\n")
        # Send a normal POST request
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r_post = requests.post(f"{target}/", headers=headers, data="", timeout=10, verify=False)
        print(f"[+] Normal POST request returned HTTP {r_post.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection failed: {e}")
        return False


def simulate_active(target):
    try:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"name": "testuser", "email": "test@example.com", "message": "hello struts2"}
        r = requests.post(f"{target}/", headers=headers, data=data, timeout=10, verify=False)
        print(f"[+] Submitted form POST request to main action (HTTP {r.status_code})\n[+] Response Body:\n{r.text[:250]}...\n")
        r_get = requests.get(f"{target}/", timeout=10, verify=False)
        print(f"[+] Sent GET request to main action (HTTP {r_get.status_code})\n[+] Response Body:\n{r_get.text[:250]}...\n")
        r_put = requests.put(f"{target}/benign-note.txt", data="benign normal user content", timeout=10, verify=False)
        print(f"[+] Sent PUT request for a benign text resource (HTTP {r_put.status_code})\n[+] Response Body:\n{r_put.text[:250]}...\n")
    except Exception as e:
        print(f"[-] Active simulation failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Struts2 Normal User Client")
    parser.add_argument("target", help="Target Struts2 URL, e.g. http://localhost:8080")
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

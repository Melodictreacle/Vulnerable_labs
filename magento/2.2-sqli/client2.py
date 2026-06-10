#!/usr/bin/env python3
"""
Magento Status Checker
----------------------
A benign client to connect to a Magento storefront and verify its availability and search Catalog.
"""

import argparse
import sys
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    try:
        r = requests.get(f"{target}/", timeout=10, verify=False)
        print(f"[+] Connected to Magento server (HTTP {r.status_code})\n[+] Response Body:\n{r.text[:250]}...\n")
        if r.status_code == 200 and "magento" in r.text.lower():
            print("[+] Magento storefront is accessible.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[-] Connection failed: {e}")
        return False


def simulate_active(target):
    try:
        r = requests.get(f"{target}/catalogsearch/result/?q=test", timeout=10, verify=False)
        print(f"[+] Performed catalog search (HTTP {r.status_code})\n[+] Response Body:\n{r.text[:250]}...\n")
        r_post = requests.post(f"{target}/catalogsearch/result/", data={"q": "test"}, timeout=10, verify=False)
        print(f"[+] Sent POST catalog search request (HTTP {r_post.status_code})\n[+] Response Body:\n{r_post.text[:250]}...\n")
        r_put = requests.put(f"{target}/benign-note.txt", data="benign normal user content", timeout=10, verify=False)
        print(f"[+] Sent PUT request for a benign text resource (HTTP {r_put.status_code})\n[+] Response Body:\n{r_put.text[:250]}...\n")
    except Exception as e:
        print(f"[-] Active simulation failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Magento Status Checker")
    parser.add_argument("target", help="Target Magento URL, e.g. http://localhost:8081")
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

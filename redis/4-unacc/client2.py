#!/usr/bin/env python3
"""
Redis Normal User Client
------------------------
A benign client to connect to a Redis database using standard socket protocol,
and retrieve basic status information and set/get test keys.
"""

import argparse
import socket
import sys


def check_target(host, port):
    try:
        s = socket.create_connection((host, port), timeout=10)
        print(f"[+] Connected to Redis server at {host}:{port}")

        # Send PING
        s.sendall(b"*1\r\n$4\r\nPING\r\n")
        resp = s.recv(1024).decode()
        if "PONG" in resp:
            print("[+] Redis PING response: PONG")

        # Send INFO
        s.sendall(b"*1\r\n$4\r\nINFO\r\n")
        info_resp = s.recv(4096).decode()
        for line in info_resp.split("\r\n"):
            if line.startswith("redis_version:") or line.startswith("os:"):
                print(f"[+] {line}")

        s.close()
        return True
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return False


def simulate_active(host, port):
    try:
        s = socket.create_connection((host, port), timeout=10)
        s.sendall(b"*3\r\n$3\r\nSET\r\n$8\r\ntest_key\r\n$10\r\ntest_value\r\n")
        resp1 = s.recv(1024)
        print(f"[+] Redis SET test_key: {resp1.decode().strip()}")
        
        s.sendall(b"*2\r\n$3\r\nGET\r\n$8\r\ntest_key\r\n")
        resp2 = s.recv(1024)
        print(f"[+] Redis GET test_key: {resp2.decode().strip()}")
        
        s.sendall(b"*2\r\n$3\r\nDEL\r\n$8\r\ntest_key\r\n")
        resp3 = s.recv(1024)
        print(f"[+] Redis DEL test_key: {resp3.decode().strip()}")
        s.close()
    except Exception as e:
        print(f"[-] Active simulation failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Redis Normal User Client")
    parser.add_argument("target", help="Target Redis host (IP or hostname)")
    parser.add_argument("--port", type=int, default=6379, help="Target Redis port (default: 6379)")
    parser.add_argument("--mode", choices=["check", "active"], default="check", help="Simulation mode")
    args = parser.parse_args()

    host = args.target
    port = args.port
    
    print(f"[*] Target: {host}:{port}")
    if args.mode == "check":
        if not check_target(host, port):
            sys.exit(1)
    elif args.mode == "active":
        simulate_active(host, port)


if __name__ == "__main__":
    main()

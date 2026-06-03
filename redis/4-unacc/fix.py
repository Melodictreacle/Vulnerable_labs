path = '/home/shuvadip/Vulnerable_labs/redis/4-unacc/n0b0dyCN-redis-rogue-server/redis-rogue-server.py'
with open(path, 'r') as f:
    lines = f.readlines()
lines[54] = '    return msg.decode("utf-8", errors="ignore")\n'
with open(path, 'w') as f:
    f.writelines(lines)

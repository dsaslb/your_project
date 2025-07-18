import re

failed_files = set()
with open('black_failed_files.txt', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if '.py' in line:
            print(line.strip())

with open('failed_files.txt', 'w', encoding='utf-8') as f:
    for path in sorted(failed_files):
        f.write(path + '\n') 
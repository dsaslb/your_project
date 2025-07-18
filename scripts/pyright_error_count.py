import re
from collections import Counter

# pyright 로그 파일 경로
log_path = 'pyright.log'

# 오류 유형 추출용 정규표현식
pattern = re.compile(r'report\w+')

error_types = []

try:
    with open(log_path, encoding='utf-8') as f:
        for line in f:
            matches = pattern.findall(line)
            error_types.extend(matches)
except UnicodeDecodeError:
    try:
        with open(log_path, encoding='cp949') as f:
            for line in f:
                matches = pattern.findall(line)
                error_types.extend(matches)
    except UnicodeDecodeError:
        with open(log_path, encoding='latin1') as f:
            for line in f:
                matches = pattern.findall(line)
                error_types.extend(matches)

counter = Counter(error_types)

print('pyright 오류 유형별 개수 (많은 순):')
for error_type, count in counter.most_common():
    print(f'{error_type}: {count}') 
from collections import Counter

error_lines = []
with open("pyright_output_head.txt", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        print(f"{i+1}: {repr(line)}")
        if i >= 19:
            break

print(f"오류 라인 총 개수: {len(error_lines)}")
counter = Counter(error_lines)
print("가장 많이 발생한 오류 유형 Top 10:")
for err, cnt in counter.most_common(10):
    print(f"{err}: {cnt}회")

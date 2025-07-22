import requests
import threading
import time

def load_test(endpoint, num_requests=100, concurrency=10):
    results = []
    def worker():
        for _ in range(num_requests // concurrency):
            start = time.time()
            try:
                r = requests.get(endpoint)
                elapsed = time.time() - start
                results.append((r.status_code, elapsed))
            except Exception:
                results.append(('fail', 0))
    threads = [threading.Thread(target=worker) for _ in range(concurrency)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results

if __name__ == '__main__':
    endpoint = 'http://localhost:5000/api/admin/brands'
    num_requests = 100
    concurrency = 10
    print(f'부하 테스트: {endpoint} ({num_requests}회, 동시 {concurrency}개)')
    results = load_test(endpoint, num_requests, concurrency)
    success = sum(1 for code, _ in results if code == 200)
    fails = sum(1 for code, _ in results if code != 200)
    avg_time = sum(t for _, t in results) / len(results)
    print(f'성공: {success}, 실패: {fails}, 평균 응답시간: {avg_time:.3f}s') 
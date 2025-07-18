import logging
from datetime import datetime
import random
import time

logging.basicConfig(filename="ci_cd_pipeline.log", level=logging.INFO)


class CICDPipeline:
    def __init__(self):
        self.release_history = []

    def build(self):
        logging.info(f"[{datetime.now()}] 빌드 시작")
        time.sleep(1)
        logging.info(f"[{datetime.now()}] 빌드 완료")

    def test(self):
        logging.info(f"[{datetime.now()}] 테스트 시작")
        time.sleep(1)
        result = random.choice(["성공", "실패"])
        logging.info(f"[{datetime.now()}] 테스트 결과: {result}")
        return result == "성공"

    def deploy(self):
        logging.info(f"[{datetime.now()}] 배포 시작")
        time.sleep(1)
        logging.info(f"[{datetime.now()}] 배포 완료")

    def record_release(self, version):
        entry = {"version": version, "timestamp": datetime.now()}
        self.release_history.append(entry)
        logging.info(f"[{datetime.now()}] 릴리즈 기록: {entry}")

    def run_pipeline(self, version):
        self.build()
        if self.test():
            self.deploy()
            self.record_release(version)
        else:
            logging.error(f"[{datetime.now()}] 파이프라인 실패: 테스트 불합격")


if __name__ == "__main__":
    pipeline = CICDPipeline()
    for v in range(1, 4):
        pipeline.run_pipeline(f"v1.0.{v}")
        time.sleep(2)

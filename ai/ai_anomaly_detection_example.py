import pandas as pd
from sklearn.ensemble import IsolationForest

# AI/머신러닝 기반 이상 탐지 예시 코드
# 운영 로그/이벤트/알림 데이터에서 이상(Anomaly) 자동 탐지


def detect_anomalies(log_data):
    # log_data: pandas DataFrame (예: ['timestamp', 'event_type', 'value'])
    model = IsolationForest(contamination=0.05, random_state=42)  # pyright: ignore
    # 예시: value 컬럼만 사용
    X = log_data[["value"]]
    log_data["anomaly"] = model.fit_predict(X)
    # -1: 이상, 1: 정상
    anomalies = log_data[log_data["anomaly"] == -1]
    return anomalies


if __name__ == "__main__":
    # 예시 데이터 생성
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=100, freq="H"),
            "event_type": ["normal"] * 95 + ["error"] * 5,
            "value": list(range(95)) + [200, 210, 220, 230, 240],
        }
    )
    anomalies = detect_anomalies(df)
    print("[AI 이상 탐지 결과]")
    print(anomalies)

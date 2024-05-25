import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Параметры генерации данных
models = ["Prophet", "Isolation Forest"]
metrics = ["Web Response", "Throughput", "Apdex", "Error"]
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 1, 2)
date_range = pd.date_range(start_date, end_date, freq='H')

data = []

for model in models:
    for metric in metrics:
        for timestamp in date_range:
            is_anomaly = np.random.choice([True, False], p=[0.1, 0.9])
            value = np.random.random()
            data.append([model, metric, timestamp, value, is_anomaly])

# Создаем композитную модель
composite_data = []
for metric in metrics:
    metric_data = [d for d in data if d[1] == metric]
    for timestamp in date_range:
        timestamp_data = [d for d in metric_data if d[2] == timestamp]
        is_anomaly = any([d[4] for d in timestamp_data])
        value = np.mean([d[3] for d in timestamp_data])
        composite_data.append(["Composite", metric, timestamp, value, is_anomaly])

# Объединяем данные
data.extend(composite_data)

# Создаем DataFrame
df = pd.DataFrame(data, columns=["Модель", "Метрика", "timestamp", "value", "is_anomaly"])
df.to_csv("fake_anomalies.csv", index=False)

print("Fake data generated and saved to 'fake_anomalies.csv'.")

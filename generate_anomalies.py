import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import os

# Генерация случайных данных
np.random.seed(42)
timestamps = pd.date_range(start='2024-01-01', periods=10000, freq='H')
metrics = ['web_response', 'throughput', 'apdex', 'error']

data = pd.DataFrame({
    'timestamp': timestamps,
    'web_response': np.random.normal(200, 20, size=len(timestamps)),  # Время ответа сервиса
    'throughput': np.random.normal(300, 30, size=len(timestamps)),    # Пропускная способность
    'apdex': np.random.normal(0.8, 0.05, size=len(timestamps)),       # Apdex
    'error': np.random.normal(0.01, 0.005, size=len(timestamps))      # Процент ошибок
})

# Введение аномалий в данные
data.loc[100:110, 'web_response'] += 100
data.loc[200:210, 'throughput'] -= 50
data.loc[300:310, 'apdex'] -= 0.3
data.loc[400:410, 'error'] += 0.05

# Создание директории для сохранения результатов
os.makedirs('anomalies', exist_ok=True)

# Функции для обнаружения аномалий
def detect_anomalies_prophet(df, metric):
    df = df.rename(columns={metric: 'y'})
    df['ds'] = df['timestamp']
    m = Prophet()
    m.fit(df[['ds', 'y']])
    future = m.make_future_dataframe(periods=0)
    forecast = m.predict(future)
    df['yhat'] = forecast['yhat']
    df['yhat_lower'] = forecast['yhat_lower']
    df['yhat_upper'] = forecast['yhat_upper']
    df['anomaly'] = (df['y'] > df['yhat_upper']) | (df['y'] < df['yhat_lower'])
    df = df.rename(columns={'y': 'metric'})
    return df[['timestamp', 'metric', 'yhat', 'yhat_lower', 'yhat_upper', 'anomaly']]

def detect_anomalies_isolation_forest(df, metric):
    df = df.rename(columns={metric: 'metric'})
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[['metric']])
    model = IsolationForest(contamination=0.01)
    df['anomaly'] = model.fit_predict(scaled_data)
    df['anomaly'] = df['anomaly'] == -1
    return df[['timestamp', 'metric', 'anomaly']]

# Обнаружение аномалий и сохранение результатов
for metric in metrics:
    df_metric = data[['timestamp', metric]].copy()
    anomalies_prophet = detect_anomalies_prophet(df_metric, metric)
    anomalies_iforest = detect_anomalies_isolation_forest(df_metric, metric)
    
    anomalies_prophet.to_csv(f'anomalies/{metric}_prophet.csv', index=False)
    anomalies_iforest.to_csv(f'anomalies/{metric}_iforest.csv', index=False)

print("Аномалии обнаружены и сохранены.")

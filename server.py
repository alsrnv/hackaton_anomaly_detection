from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Загрузка всех файлов с аномалиями
anomalies = {}
for file in os.listdir('anomalies'):
    if file.endswith('.csv'):
        key = file.replace('.csv', '')
        anomalies[key] = pd.read_csv(f'anomalies/{file}')

# Функция для поиска временного окна в данных
def get_time_window(data, start_timestamp, end_timestamp):
    mask = (data['timestamp'] >= start_timestamp) & (data['timestamp'] <= end_timestamp)
    return data.loc[mask]

@app.route('/check_anomalies', methods=['POST'])
def check_anomalies():
    try:
        req_data = request.get_json()
        start_timestamp = req_data['start_timestamp']
        end_timestamp = req_data['end_timestamp']

        response_data = {}

        for key, df in anomalies.items():
            time_window = get_time_window(df, start_timestamp, end_timestamp)
            if time_window.empty:
                continue

            anomaly_points = time_window[time_window['anomaly'] == True]
            response_data[key] = {
                'has_anomaly': not anomaly_points.empty,
                'anomaly_timestamps': anomaly_points['timestamp'].tolist()
            }

        print("Response data:", response_data)
        return jsonify(response_data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)

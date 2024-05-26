import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, time

st.set_page_config(page_title="Обнаружение Аномалий во Временных Рядах", layout="wide")

# Подключение CSS-стилей
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Обнаружение Аномалий во Временных Рядах")

# Загрузка данных
df = pd.read_csv("metrics.csv")

# Преобразование столбца timestamp в формат datetime с обработкой разных форматов
try:
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
except ValueError:
    st.error("Ошибка преобразования столбца временных меток. Проверьте формат данных.")

# Определение минимальной и максимальной даты в данных
min_date = df['timestamp'].min()
max_date = df['timestamp'].max()

# Ввод временного окна с помощью календаря с минимальными и максимальными датами
start_date = st.date_input("Дата начала", value=min_date)
start_time = st.time_input("Время начала", value=pd.to_datetime(min_date).time())
end_date = st.date_input("Дата окончания", value=max_date)
end_time = st.time_input("Время окончания", value=pd.to_datetime(max_date).time())

start_timestamp = datetime.combine(start_date, start_time).strftime('%Y-%m-%d %H:%M:%S')
end_timestamp = datetime.combine(end_date, end_time).strftime('%Y-%m-%d %H:%M:%S')

if st.button("Рассчитать"):
    st.write(f"Временная метка начала: {start_timestamp}")
    st.write(f"Временная метка окончания: {end_timestamp}")

    # Фильтрация данных по временным меткам
    filtered_df = df[(df['timestamp'] >= start_timestamp) & (df['timestamp'] <= end_timestamp)]

    # Получение уникальных значений метрик для создания вкладок
    unique_metrics = filtered_df["Метрика"].unique().tolist()
    
    tabs = st.tabs(unique_metrics)

    # Функция для отображения аномалий
    def display_anomalies(tab, metric):
        with tab:
            st.header(metric)

            # Фильтрация данных по метрике
            metric_data = filtered_df[filtered_df["Метрика"] == metric]

            # Prophet
            st.subheader("Модель Prophet")
            process_anomalies(metric_data, "Prophet")

            # Isolation Forest
            st.subheader("Модель Isolation Forest")
            process_anomalies(metric_data, "Isolation Forest")

            # Композитная модель
            st.subheader("Общая модель (Композитная)")
            process_anomalies(metric_data, "Composite")

    def process_anomalies(data, model_key):
        model_data = data[data["Модель"] == model_key]

        if not model_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=model_data['timestamp'], y=model_data['value'], mode='lines', name='Metric'))
            fig.add_trace(go.Scatter(x=model_data['timestamp'][model_data['is_anomaly']], y=model_data['value'][model_data['is_anomaly']], mode='markers', name='Anomaly', marker=dict(color='red')))
            fig.update_layout(xaxis_range=[start_timestamp, end_timestamp])  # Установка диапазона оси X
            st.plotly_chart(fig)

            st.subheader("Данные")
            st.write(model_data[["timestamp", "value", "is_anomaly"]])
        else:
            st.write(f"Нет данных за выбранный период для модели {model_key}.")

    # Отображение аномалий для каждой метрики
    for i, metric in enumerate(unique_metrics):
        display_anomalies(tabs[i], metric)

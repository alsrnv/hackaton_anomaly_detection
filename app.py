import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, time

st.set_page_config(page_title="Обнаружение Аномалий во Временных Рядах", layout="wide")

# Подключение CSS-стилей
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Обнаружение Аномалий во Временных Рядах")

# Ввод временного окна с помощью календаря
start_date = st.date_input("Дата начала", value=pd.to_datetime("2024-01-01"))
start_time = st.time_input("Время начала", value=time(0, 0))
end_date = st.date_input("Дата окончания", value=pd.to_datetime("2024-01-02"))
end_time = st.time_input("Время окончания", value=time(0, 0))

start_timestamp = datetime.combine(start_date, start_time).strftime('%Y-%m-%d %H:%M:%S')
end_timestamp = datetime.combine(end_date, end_time).strftime('%Y-%m-%d %H:%M:%S')

if st.button("Рассчитать"):
    st.write(f"Временная метка начала: {start_timestamp}")
    st.write(f"Временная метка окончания: {end_timestamp}")

    # Загрузка данных
    df = pd.read_csv("metrics.csv")

    # Получение уникальных значений метрик для создания вкладок
    unique_metrics = df["Метрика"].unique().tolist()
    
    tabs = st.tabs(unique_metrics)

    # Функция для отображения аномалий
    def display_anomalies(tab, metric):
        with tab:
            st.header(metric)

            # Фильтрация данных по метрике
            metric_data = df[df["Метрика"] == metric]

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

        time_window = model_data[(model_data['timestamp'] >= start_timestamp) & (model_data['timestamp'] <= end_timestamp)]

        if not time_window.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time_window['timestamp'], y=time_window['value'], mode='lines', name='Metric'))
            fig.add_trace(go.Scatter(x=time_window['timestamp'][time_window['is_anomaly']], y=time_window['value'][time_window['is_anomaly']], mode='markers', name='Anomaly', marker=dict(color='red')))
            st.plotly_chart(fig)

            st.subheader("Данные")
            st.write(time_window[["timestamp", "value", "is_anomaly"]])
        else:
            st.write(f"Нет данных за выбранный период для модели {model_key}.")

    # Отображение аномалий для каждой метрики
    for i, metric in enumerate(unique_metrics):
        display_anomalies(tabs[i], metric)

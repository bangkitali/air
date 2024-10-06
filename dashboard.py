import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

def load_data():
    data = pd.read_csv('main.csv')
    data['datetime'] = pd.to_datetime(data['datetime'])
    data['date'] = data['datetime'].dt.date
    data['hour'] = data['datetime'].dt.hour
    return data

data = load_data()

st.title("Analisis Kualitas Udara di Huairou")


selected_date = st.date_input("Pilih tanggal", min_value=data['date'].min(), max_value=data['date'].max())
filtered_data = data[data['date'] == selected_date]

if not filtered_data.empty:
    st.subheader(f"Data untuk {selected_date}")
    st.write(filtered_data[['datetime', 'PM2.5', 'PM10', 'TEMP', 'PRES']])

    
    def create_plots(data, column, row, title, ylabel, y_range=None):
        
        histogram = go.Bar(
            x=data['hour'],
            y=data[column],
            name=f'Histogram {title}'
        )

        
        time_series = go.Scatter(
            x=data['datetime'],
            y=data[column],
            mode='lines+markers',
            name=f'Time Series {title}'
        )

        return histogram, time_series, y_range

    
    fig = make_subplots(rows=4, cols=2, 
                        subplot_titles=('PM2.5 per Jam', 'PM2.5 Time Series',
                                        'PM10 per Jam', 'PM10 Time Series',
                                        'Suhu per Jam', 'Suhu Time Series',
                                        'Tekanan Atmosfer per Jam', 'Tekanan Atmosfer Time Series'))

    
    metrics = [
        ('PM2.5', 'Nilai PM2.5 (µg/m³)', None),
        ('PM10', 'Nilai PM10 (µg/m³)', None),
        ('TEMP', 'Suhu (°C)', None),
        ('PRES', 'Tekanan (hPa)', [1000, None]) 
    ]

    for i, (column, ylabel, y_range) in enumerate(metrics, start=1):
        histogram, time_series, y_range = create_plots(filtered_data, column, i, column, ylabel, y_range)
        fig.add_trace(histogram, row=i, col=1)
        fig.add_trace(time_series, row=i, col=2)

        
        fig.update_yaxes(title_text=ylabel, row=i, col=1, range=y_range)
        fig.update_yaxes(title_text=ylabel, row=i, col=2, range=y_range)

    
    for i in range(1, 5):
        fig.update_xaxes(title_text='Jam', row=i, col=1)
        fig.update_xaxes(title_text='Waktu', row=i, col=2)

    
    fig.update_layout(height=1600, width=1000, title_text="Analisis Kualitas Udara")
    st.plotly_chart(fig)

else:
    st.write("Tidak ada data untuk tanggal yang dipilih.")

st.subheader("Analisis Rentang Waktu dan Rekomendasi Waktu Kunjungan")

start_date = st.date_input("Pilih tanggal mulai", min_value=data['date'].min(), max_value=data['date'].max())
end_date = st.date_input("Pilih tanggal akhir", min_value=start_date, max_value=data['date'].max())

if start_date <= end_date:
    date_range_data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]

    if not date_range_data.empty:
        st.write(f"Analisis untuk rentang waktu: {start_date} hingga {end_date}")

        def calculate_aqi(pm25, pm10):
            aqi_pm25 = pm25 * 2  
            aqi_pm10 = pm10
            return max(aqi_pm25, aqi_pm10)

        date_range_data['AQI'] = date_range_data.apply(lambda row: calculate_aqi(row['PM2.5'], row['PM10']), axis=1)

        best_pm25 = date_range_data.loc[date_range_data['PM2.5'].idxmin()]
        best_pm10 = date_range_data.loc[date_range_data['PM10'].idxmin()]
        best_aqi = date_range_data.loc[date_range_data['AQI'].idxmin()]
        
        
        pressure_stability = date_range_data.groupby('date')['PRES'].std()
        most_stable_date = pressure_stability.idxmin()
        most_stable_data = date_range_data[date_range_data['date'] == most_stable_date]
        
        st.subheader("Rekomendasi Waktu Kunjungan:")
        st.write(f"1. Berdasarkan PM2.5 Terendah: {best_pm25['datetime']} (PM2.5: {best_pm25['PM2.5']:.2f} µg/m³)")
        st.write(f"2. Berdasarkan PM10 Terendah: {best_pm10['datetime']} (PM10: {best_pm10['PM10']:.2f} µg/m³)")
        st.write(f"3. Berdasarkan Kualitas Udara Terbaik (AQI Terendah): {best_aqi['datetime']} (AQI: {best_aqi['AQI']:.2f})")
        st.write(f"4. Berdasarkan Tekanan Atmosfer Paling Stabil: {most_stable_date} (Standar Deviasi: {pressure_stability.min():.2f} hPa)")

        st.subheader("Visualisasi Data untuk Rentang Waktu yang Dipilih")
        
        fig = make_subplots(rows=5, cols=1, subplot_titles=('PM2.5', 'PM10', 'AQI', 'Suhu', 'Tekanan Atmosfer'))

        fig.add_trace(go.Scatter(x=date_range_data['datetime'], y=date_range_data['PM2.5'], mode='lines', name='PM2.5'), row=1, col=1)
        fig.add_trace(go.Scatter(x=date_range_data['datetime'], y=date_range_data['PM10'], mode='lines', name='PM10'), row=2, col=1)
        fig.add_trace(go.Scatter(x=date_range_data['datetime'], y=date_range_data['AQI'], mode='lines', name='AQI'), row=3, col=1)
        fig.add_trace(go.Scatter(x=date_range_data['datetime'], y=date_range_data['TEMP'], mode='lines', name='Suhu'), row=4, col=1)
        fig.add_trace(go.Scatter(x=date_range_data['datetime'], y=date_range_data['PRES'], mode='lines', name='Tekanan'), row=5, col=1)

        fig.update_layout(height=1200, width=800, title_text="Trend Kualitas Udara dan Kondisi Atmosfer")
        st.plotly_chart(fig)

        st.subheader("Tren pada Hari Terbaik (Berdasarkan AQI Terendah)")
        
        best_day = best_aqi['date']
        best_day_data = data[data['date'] == best_day]
        
        fig_best_day = make_subplots(rows=4, cols=1, 
                                     subplot_titles=('PM2.5', 'PM10', 'Suhu', 'Tekanan Atmosfer'),
                                     shared_xaxes=True)
        
        fig_best_day.add_trace(go.Scatter(x=best_day_data['hour'], y=best_day_data['PM2.5'], mode='lines+markers', name='PM2.5'), row=1, col=1)
        fig_best_day.add_trace(go.Scatter(x=best_day_data['hour'], y=best_day_data['PM10'], mode='lines+markers', name='PM10'), row=2, col=1)
        fig_best_day.add_trace(go.Scatter(x=best_day_data['hour'], y=best_day_data['TEMP'], mode='lines+markers', name='Suhu'), row=3, col=1)
        fig_best_day.add_trace(go.Scatter(x=best_day_data['hour'], y=best_day_data['PRES'], mode='lines+markers', name='Tekanan'), row=4, col=1)
        
        fig_best_day.update_layout(height=1000, width=800, title_text=f"Tren pada {best_day} (Hari dengan AQI Terendah)")
        fig_best_day.update_xaxes(title_text="Jam", row=4, col=1)
        fig_best_day.update_yaxes(title_text="µg/m³", row=1, col=1)
        fig_best_day.update_yaxes(title_text="µg/m³", row=2, col=1)
        fig_best_day.update_yaxes(title_text="°C", row=3, col=1)
        fig_best_day.update_yaxes(title_text="hPa", row=4, col=1)
        
        st.plotly_chart(fig_best_day)

    else:
        st.write("Tidak ada data untuk rentang waktu yang dipilih.")
else:
    st.write("Tanggal akhir harus setelah tanggal mulai.")

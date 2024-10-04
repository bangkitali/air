import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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

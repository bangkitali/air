import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

    fig, axs = plt.subplots(4, 2, figsize=(16, 20))

    def create_plots(data, column, row, title, ylabel):
        
        sns.barplot(x='hour', y=column, data=data, ax=axs[row, 0], estimator=lambda x: x.iloc[0])
        axs[row, 0].set_title(f'Histogram {title} per Jam')
        axs[row, 0].set_xlabel('Jam')
        axs[row, 0].set_ylabel(ylabel)
        axs[row, 0].set_xticks(range(0, 24, 2))

        sns.lineplot(x='datetime', y=column, data=data, ax=axs[row, 1], marker='o')
        axs[row, 1].set_title(f'Time Series {title}')
        axs[row, 1].set_xlabel('Waktu')
        axs[row, 1].set_ylabel(ylabel)
        axs[row, 1].tick_params(axis='x', rotation=45)

    create_plots(filtered_data, 'PM2.5', 0, 'PM2.5', 'Nilai PM2.5 (µg/m³)')
    create_plots(filtered_data, 'PM10', 1, 'PM10', 'Nilai PM10 (µg/m³)')
    create_plots(filtered_data, 'TEMP', 2, 'Suhu', 'Suhu (°C)')
    create_plots(filtered_data, 'PRES', 3, 'Tekanan Atmosfer', 'Tekanan (hPa)')

    
    plt.tight_layout()
    st.pyplot(fig)  
else:
    st.write("Tidak ada data untuk tanggal yang dipilih.")
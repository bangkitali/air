import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('main.csv')
    df['DATE'] = pd.to_datetime(df['DATE'])
    return df

df = load_data()

# Set up Streamlit title and description
st.title("Dashboard Analisis Kualitas Udara dan Cuaca Kota Huairou")
st.markdown("""
    Dashboard ini menampilkan visualisasi dari analisis mengenai waktu terbaik untuk membuka pariwisata berdasarkan tingkat polusi dan suhu yang ideal di kota Huairou.
""")

# Date range selection
min_date = df['DATE'].min().date()
max_date = df['DATE'].max().date()
start_date = st.date_input("Pilih tanggal mulai", min_date, min_value=min_date, max_value=max_date)
end_date = st.date_input("Pilih tanggal akhir", max_date, min_value=min_date, max_value=max_date)

# Filter data based on selected date range
mask = (df['DATE'].dt.date >= start_date) & (df['DATE'].dt.date <= end_date)
filtered_df = df.loc[mask]

# Define ideal conditions
def is_ideal_pm25(value):
    return value <= 35

def is_ideal_pm10(value):
    return value <= 50

def is_ideal_temp(value):
    return 0 <= value <= 25

def is_ideal_pres(value):
    return 1000 <= value <= 1020

filtered_df['Ideal_PM25'] = filtered_df['PM2.5'].apply(is_ideal_pm25)
filtered_df['Ideal_PM10'] = filtered_df['PM10'].apply(is_ideal_pm10)
filtered_df['Ideal_TEMP'] = filtered_df['TEMP'].apply(is_ideal_temp)
filtered_df['Ideal_PRES'] = filtered_df['PRES'].apply(is_ideal_pres)

filtered_df['Month'] = filtered_df['DATE'].dt.month
monthly_ideal = filtered_df.groupby('Month').agg({
    'Ideal_PM25': 'mean',
    'Ideal_PM10': 'mean',
    'Ideal_TEMP': 'mean',
    'Ideal_PRES': 'mean'
})

for col in ['Ideal_PM25', 'Ideal_PM10', 'Ideal_TEMP', 'Ideal_PRES']:
    monthly_ideal[col] = monthly_ideal[col] * 100

st.header("Persentase Hari Ideal per Bulan")

fig, axs = plt.subplots(2, 2, figsize=(20, 15))
fig.suptitle("Persentase Hari Ideal per Bulan untuk Berbagai Parameter", fontsize=16)

params = ['PM25', 'PM10', 'TEMP', 'PRES']
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_names = [month_names[i - 1] for i in monthly_ideal.index]

# Perulangan visualisasi
for i, param in enumerate(params):
    ax = axs[i // 2, i % 2]
    sns.barplot(x=month_names, y=f'Ideal_{param}', data=monthly_ideal.reset_index(), ax=ax)
    ax.set_title(f"Hari Ideal - {param}")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Persentase Hari Ideal")
    ax.set_ylim(0, 100)
    
    for j, v in enumerate(monthly_ideal[f'Ideal_{param}']):
        ax.text(j, v, f'{v:.1f}%', ha='center', va='bottom')

plt.tight_layout()
st.pyplot(fig)

# Buat dictionary best_months dengan pengecekan panjang indeks
best_months = {}
for key, col in zip(['PM2.5', 'PM10', 'TEMP', 'PRES'], ['Ideal_PM25', 'Ideal_PM10', 'Ideal_TEMP', 'Ideal_PRES']):
    max_idx = monthly_ideal[col].idxmax() - 1  # Adjust for zero-based index
    # Pastikan indeks ada dalam rentang yang valid
    if 0 <= max_idx < len(month_names):
        best_months[key] = month_names[max_idx]
    else:
        best_months[key] = "Data tidak mencakup bulan ini"

st.markdown("### Kesimpulan")
st.markdown(f"""
    Berdasarkan data dari {start_date} hingga {end_date}:
    - **PM2.5:** Bulan dengan persentase hari ideal tertinggi adalah {best_months['PM2.5']}
    - **PM10:** Bulan dengan persentase hari ideal tertinggi adalah {best_months['PM10']}
    - **Suhu:** Bulan dengan persentase hari ideal tertinggi adalah {best_months['TEMP']}
    - **Tekanan:** Bulan dengan persentase hari ideal tertinggi adalah {best_months['PRES']}
""")

st.markdown("""
    Berdasarkan analisis di atas, waktu terbaik untuk membuka pariwisata dapat ditentukan dengan mempertimbangkan bulan-bulan yang memiliki persentase hari ideal tertinggi untuk setiap parameter.
    Perlu diperhatikan bahwa mungkin ada trade-off antara parameter-parameter tersebut, sehingga pemilihan waktu terbaik harus mempertimbangkan prioritas dari masing-masing faktor.
""")

import os
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import json

def get_csv_files(folder_path):
    """
    ค้นหาไฟล์ CSV ในโฟลเดอร์ที่ระบุ
    """
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.csv')]

def load_csv_file(file_path):
    """
    โหลดไฟล์ CSV และตรวจสอบคอลัมน์ที่จำเป็น
    """
    try:
        data = pd.read_csv(file_path, skiprows=4)
        if not {'Time', 'Ampl'}.issubset(data.columns):
            print(f"File {file_path} does not contain 'Time' and 'Ampl' columns. Skipping...")
            return None
        return data[['Time', 'Ampl']].dropna()
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def load_files(folder_path):
    """
    โหลดไฟล์ CSV ทั้งหมดในโฟลเดอร์ที่ระบุ
    """
    csv_files = get_csv_files(folder_path)

    if not csv_files:
        raise ValueError("No CSV files found in the specified folder.")

    file_data = []
    for file_path in tqdm(csv_files, desc="Loading files", unit="file"):
        data = load_csv_file(file_path)
        if data is not None:
            file_data.append(data)

    return file_data

def validate_data(file_data):
    """
    ตรวจสอบความสอดคล้องของข้อมูล
    """
    row_counts = [len(data) for data in file_data]
    if len(set(row_counts)) != 1:
        raise ValueError("All files must have the same number of rows.")

def process_files(file_data):
    """
    ประมวลผลข้อมูลจากไฟล์ CSV
    """
    validate_data(file_data)

    combined_data = pd.concat(file_data).groupby(level=0).median()

    c = 3e8
    combined_data = combined_data[combined_data['Time'] > 10e-6]
    combined_data['Time'] = combined_data['Time'] - 10e-6
    combined_data['Ampl'] = -combined_data['Ampl']
    combined_data['Distance (m)'] = (combined_data['Time'] * c) / 2
    combined_data['Digitizer Signal (v * m²)'] = combined_data['Ampl'] * (combined_data['Distance (m)'] ** 2)

    return combined_data

def extract_date_from_folder(folder_path):
    """
    ดึงวันที่และเวลาออกจากชื่อโฟลเดอร์
    """
    folder_name = os.path.basename(folder_path)
    parts = folder_name.split('-')
    day, month, year, hour, minute = parts[1], parts[2], parts[3], parts[5], parts[6]
    return f"{day}/{month}/{year} {hour}:{minute}"

def plot_lidar_data(data, oc_cal, oc_dis, folder_path):
    """
    แสดงกราฟข้อมูล LIDAR
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # ax.plot(oc_cal, oc_dis, color='green', linewidth=1, label="old software")
    ax.plot(data['Digitizer Signal (v * m²)'], data['Distance (m)'], color='red', linewidth=1, label="new software")

    ax.set_xlabel("Digitizer Signal (v * m²)", fontsize=12)
    ax.set_ylabel("Distance (m)", fontsize=12)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    date_str = extract_date_from_folder(folder_path)
    chart_title = f"LIDAR Signal Analyzer {date_str}"
    fig.suptitle(chart_title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1, 1))

    plt.show()

def load_json_data(json_file_path):
    """
    โหลดข้อมูล JSON
    """
    with open(json_file_path, 'r') as f:
        return json.load(f)

def main():
    """
    ฟังก์ชันหลักสำหรับวิเคราะห์ข้อมูล LIDAR
    """
    print("Welcome to LIDAR Signal Analyzer!")

    json_file_path = 'ALiN_202404032035.json'
    json_data = load_json_data(json_file_path)

    oc_cal = json_data[0]['OC_cal']
    oc_dis = json_data[0]['dis']

    folder_path = "../excample-file/csv-28-11-2024-tmp4-19-25"

    if os.path.isdir(folder_path):
        try:
            file_data = load_files(folder_path)
            data = process_files(file_data)
            if not data.empty:
                plot_lidar_data(data, oc_cal, oc_dis, folder_path)
            else:
                print("No valid data to plot.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("The specified folder path does not exist.")

if __name__ == "__main__":
    main()

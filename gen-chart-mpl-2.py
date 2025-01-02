import pandas as pd
from tkinter import Tk, filedialog
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ฟังก์ชันสำหรับดึงข้อมูลจากไฟล์ CSV
def load_copol_data(csv_file):
    try:
        # อ่านข้อมูลจากไฟล์ CSV
        data = pd.read_csv(csv_file)

        # ตรวจสอบว่ามีคอลัมน์ copol_raw และ copol_nrb หรือไม่
        if 'copol_raw' not in data.columns or 'range_raw' not in data.columns  or 'copol_background' not in data.columns:
            raise ValueError("ไฟล์ CSV ไม่มีคอลัมน์ที่ต้องการ: copol_raw หรือ copol_nrb")

        # ดึงข้อมูลมาเก็บในตัวแปร
        copol_raw = data['copol_raw'].tolist()  # แปลงเป็น List
        range_raw = data['range_raw'].tolist()  # แปลงเป็น List
        copol_background = data['copol_background'].tolist()  # แปลงเป็น List

        return copol_raw, copol_background, range_raw 
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None, None

# ฟังก์ชันสำหรับเลือกไฟล์ด้วย UI
def browse_file():
    root = Tk()
    root.withdraw()  # ซ่อนหน้าต่างหลักของ Tkinter
    file_path = filedialog.askopenfilename(title="เลือกไฟล์ CSV", filetypes=[("CSV Files", "*.csv")])
    return file_path

# ฟังก์ชันสำหรับคำนวณ Distance
def calculate_distance(time):
    Distance = [ 2/  x * 3e8  for x in time]
    return Distance

def calculate_Digitizer_signal(copol_raw, copol_background, range_raw):
    R_squared = [(copol_raw[i] - copol_background) * (range_raw[i] ** 2) for i in range(len(copol_raw))]
    return R_squared

# เลือกไฟล์ CSV ผ่าน UI
csv_file = browse_file()
if csv_file:
    copol_raw, copol_background, range_raw  = load_copol_data(csv_file)

    # แสดงผลข้อมูลที่ดึงมา
    if copol_raw is not None and copol_background is not None and range_raw is not None :
        # print("copol_raw:", copol_raw[:5])  # แสดงตัวอย่างข้อมูล 5 ตัวแรก
        # print("copol_nrb:", copol_nrb[:5])  # แสดงตัวอย่างข้อมูล 5 ตัวแรก


        # ตรวจสอบความยาวของรายการ
        min_length = min(len(copol_raw), len(range_raw))
        copol_raw = copol_raw[:min_length]
        range_raw = range_raw[:min_length]

        copol_background = copol_background[0]  # สมมติว่า copol_background มีเพียงค่าเดียว

        Distance = range_raw
        R_squared = calculate_Digitizer_signal(copol_raw, copol_background, Distance)
        # ดึงชื่อไฟล์จากเส้นทาง
        file_name = os.path.basename(csv_file)
        
        # ดึงส่วนที่เป็นเวลาออกจากชื่อไฟล์
        timestamp_str = file_name.split('_')[2].split('.')[0]
        # แปลงเป็น datetime object
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M")
        # แปลงเป็นรูปแบบที่ต้องการ
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")

        plt.figure(figsize=(10, 6))
        plt.plot(R_squared, range_raw, color='blue', linewidth=2, label='Digitizer Signal vs Distance')
        # ตั้งค่าชื่อกราฟและแกน
        plt.title(f"Distance vs Digitizer Signal - {formatted_timestamp}")
        plt.xlabel("Digitizer Signal (Digitizer_signal1)")
        plt.ylabel("Distance (Distance1)")
        plt.grid(True)
        plt.legend()
        plt.show()
        
else:
    print("ไม่มีการเลือกไฟล์")

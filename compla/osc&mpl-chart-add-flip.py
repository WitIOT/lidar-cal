import pandas as pd
from tkinter import Tk, filedialog
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ฟังก์ชันสำหรับดึงข้อมูลจากไฟล์ CSV
def mplfile(csv_file):
    try:
        data = pd.read_csv(csv_file)
        required_columns = {'copol_raw', 'range_raw', 'copol_background'}
        if not required_columns.issubset(data.columns):
            raise ValueError(f"ไฟล์ CSV ต้องมีคอลัมน์: {required_columns}")
        return data['copol_raw'].tolist(), data['copol_background'].tolist(), data['range_raw'].tolist()
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None, None, None

def oscfile(folder_path):
    try:
        csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
        if not csv_files:
            raise ValueError("ไม่มีไฟล์ CSV ในโฟลเดอร์ที่ระบุ")
        all_data = [pd.read_csv(f, skiprows=4) for f in csv_files]
        combined_data = pd.concat(all_data)
        combined_data = combined_data.groupby(level=0).median()
        return combined_data
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None

def range_mpl(range_raw):
    return [x * 1000 for x in range_raw]

def R_squared_mpl(copol_raw, copol_background, Distance):
    return [(copol_raw[i] - copol_background) * (Distance[i] ** 2) for i in range(len(copol_raw))]

def cal_osc(combined_data):
    try:
        c = 3e8  # ความเร็วแสงในหน่วย m/s
        
        # ตรวจสอบว่าคอลัมน์ที่ต้องการมีอยู่ใน DataFrame
        required_columns = {'time', 'ampl'}
        if not required_columns.issubset(combined_data.columns.str.lower()):
            raise ValueError(f"DataFrame ต้องมีคอลัมน์: {required_columns}")
        
        # เปลี่ยนชื่อคอลัมน์เป็นตัวพิมพ์เล็กทั้งหมดเพื่อป้องกันปัญหา case-sensitive
        combined_data.columns = combined_data.columns.str.lower()

        # กรองข้อมูล: เลือกเฉพาะเวลาที่มากกว่า 10e-6
        combined_data = combined_data[combined_data['time'] > 10e-6].copy()
        
        # ปรับค่า 'Time'
        combined_data['time'] = combined_data['time'] - 10e-6
        
        # กลับค่า 'Ampl' ให้เป็นค่าติดลบ
        combined_data['ampl'] = -combined_data['ampl']
        
        # คำนวณระยะทางในหน่วยเมตร
        combined_data['distance (m)'] = (combined_data['time'] * c) / 2
        
        # คำนวณค่า Digitizer Signal
        combined_data['digitizer signal (v * m²)'] = combined_data['ampl'] * (combined_data['distance (m)'] ** 2)
        
        # เพิ่มระยะทางในหน่วยกิโลเมตร
        combined_data['distance (km)'] = combined_data['distance (m)'] / 1000
        
        range_osc = combined_data['distance (m)']
        R_sq_osc = combined_data['digitizer signal (v * m²)']

        return range_osc, R_sq_osc
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการประมวลผลข้อมูล OSC: {e}")
        return None, None

def browse_file():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="เลือกไฟล์ CSV", filetypes=[("CSV Files", "*.csv")])

def debug(copol_raw, copol_background, range_raw, combined_data):
    print("rang_raw:", range_raw[:5])
    print("copol_raw:", copol_raw[:5])
    print("copol_background:", copol_background[:1])
    print("median_data[Time]:", combined_data['Ampl'][:5])
    print("median_data[Ampl]:", combined_data['Time'][:5])
    return range_raw, copol_raw, copol_background, combined_data

def plot_data(R_sq_mpl, distance_mpl, range_osc, R_sq_osc, formatted_timestamp):
    """
    ฟังก์ชันวาดกราฟ MPL และ OSC โดยปรับป้ายชื่อให้อยู่ในตำแหน่งเดียวกัน
    """
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # MPL Plot (แกน Y ด้านซ้าย)
    mpl_line, = ax1.plot(R_sq_mpl, 
                         distance_mpl, 
                         color='blue', 
                         linewidth=2, 
                         label='MPL')
    ax1.set_xlabel("Digitizer Signal (v * m²)", fontsize=12)
    ax1.set_ylabel("Distance (m)", fontsize=12, color='blue')
    ax1.set_xlim(0)
    ax1.set_ylim(0, 5000)
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True)

    # OSC Plot (แกน Y ด้านบน)
    ax2 = ax1.twiny()  # สร้างแกน X รอง
    osc_line, = ax2.plot(R_sq_osc, 
                         range_osc, 
                         color='red', 
                         linewidth=2, 
                         label='OSC')
    ax2.set_ylabel("Range OSC (m)", fontsize=12, color='red')
    ax2.set_xlim(0)
    ax2.set_ylim(0, 5000)
    ax2.tick_params(axis='y', labelcolor='red')

    # รวมป้ายชื่อ MPL และ OSC ในกรอบเดียว
    ax1.legend(handles=[mpl_line, osc_line], loc='upper right', bbox_to_anchor=(1, 1))

    # Title
    fig.suptitle(f"ALIN : {formatted_timestamp}", fontsize=16, fontweight='bold')

    plt.show()


def main():
    csv_file = browse_file()
    if not csv_file:
        print("ไม่มีการเลือกไฟล์")
        return

    copol_raw, copol_background, range_raw = mplfile(csv_file)
    osc_path = "../excample-file/csv-03-04-2024-tmp4-20-00"
    d1 = oscfile(osc_path)
    
    if d1 is not None:
        print("Columns in combined_data:", d1.columns)  # ตรวจสอบคอลัมน์
    else:
        print("ไม่สามารถโหลดข้อมูล OSC ได้")
        return

    debug(copol_raw, copol_background, range_raw, d1)

    if copol_raw is not None and copol_background is not None and range_raw is not None and d1 is not None:
        range_osc, R_sq_osc = cal_osc(d1)
        if range_osc is None or R_sq_osc is None:
            print("การคำนวณ OSC ล้มเหลว")
            return

        copol_background = copol_background[0]
        distance_mpl = range_mpl(range_raw)
        R_sq_mpl = R_squared_mpl(copol_raw, copol_background, distance_mpl)

        file_name = os.path.basename(csv_file)
        timestamp_str = file_name.split('_')[2].split('.')[0]
        timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M")
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")

        # เรียกใช้ฟังก์ชันวาดกราฟ
        plot_data(R_sq_mpl, distance_mpl, range_osc, R_sq_osc, formatted_timestamp)
    else:
        print("ข้อมูลไม่สมบูรณ์หรือไม่มีข้อมูล OSC")

if __name__ == "__main__":
    main()

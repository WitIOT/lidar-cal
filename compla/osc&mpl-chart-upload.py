import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os
import json
import matplotlib.pyplot as plt


# ฟังก์ชันสำหรับอ่านข้อมูลจากไฟล์ MPL
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


# ฟังก์ชันสำหรับอ่านข้อมูล OSC
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


# ฟังก์ชันแปลงช่วง MPL เป็นเมตร
def range_mpl(range_raw):
    return [x * 1000 for x in range_raw]


# ฟังก์ชันคำนวณ Digitizer Signal MPL
def R_squared_mpl(copol_raw, copol_background, Distance):
    return [(copol_raw[i] - copol_background) * (Distance[i] ** 2) for i in range(len(copol_raw))]


# ฟังก์ชันคำนวณ OSC
def cal_osc(combined_data):
    try:
        c = 3e8  # ความเร็วแสงในหน่วย m/s
        required_columns = {'time', 'ampl'}
        if not required_columns.issubset(combined_data.columns.str.lower()):
            raise ValueError(f"DataFrame ต้องมีคอลัมน์: {required_columns}")

        combined_data.columns = combined_data.columns.str.lower()
        combined_data = combined_data[combined_data['time'] > 10e-6].copy()
        combined_data['time'] = combined_data['time'] - 10e-6
        combined_data['ampl'] = -combined_data['ampl']
        combined_data['distance (m)'] = (combined_data['time'] * c) / 2
        combined_data['digitizer signal (v * m²)'] = combined_data['ampl'] * (combined_data['distance (m)'] ** 2)

        distance_osc = combined_data['distance (m)']
        R_sq_osc = combined_data['digitizer signal (v * m²)']

        return distance_osc.tolist(), R_sq_osc.tolist()
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการประมวลผลข้อมูล OSC: {e}")
        return None, None


# ฟังก์ชันสร้างข้อมูล JSON
def generate_json_data(R_sq_mpl, distance_mpl, distance_osc, R_sq_osc):
    try:
        data = {
            "R_sq_mpl": R_sq_mpl,
            "distance_mpl": distance_mpl,
            "R_sq_osc": R_sq_osc,
            "distance_osc": distance_osc
        }
        return data
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการสร้าง JSON: {e}")
        return None


# ฟังก์ชันอัปโหลด JSON ไปยัง MongoDB
def upload_to_mongo_data(json_data, db_url, db_name, collection_name):
    try:
        client = MongoClient(db_url)
        db = client[db_name]
        collection = db[collection_name]
        result = collection.insert_one(json_data)
        print(f"ข้อมูลถูกอัปโหลดไปยัง MongoDB ใน Collection '{collection_name}' เรียบร้อยแล้ว ID: {result.inserted_id}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอัพโหลดข้อมูลไปยัง MongoDB: {e}")


# ฟังก์ชันหลัก
def main():
    mpl_path = "../excample-file/mpl/20241128/MPL_5038_202411281855.csv"
    osc_path = "../excample-file/osc/csv-28-11-2024-tmp4-18-55"

    copol_raw, copol_background, range_raw = mplfile(mpl_path)
    d1 = oscfile(osc_path)

    if d1 is not None:
        print("Columns in combined_data:", d1.columns)
    else:
        print("ไม่สามารถโหลดข้อมูล OSC ได้")
        return

    if copol_raw is not None and copol_background is not None and range_raw is not None and d1 is not None:
        distance_osc, R_sq_osc = cal_osc(d1)
        if distance_osc is None or R_sq_osc is None:
            print("การคำนวณ OSC ล้มเหลว")
            return

        copol_background = copol_background[0]
        distance_mpl = range_mpl(range_raw)
        R_sq_mpl = R_squared_mpl(copol_raw, copol_background, distance_mpl)

        # ตั้งชื่อ Collection ตามชื่อไฟล์
        file_name = os.path.basename(mpl_path)
        timestamp_str = file_name.split('_')[2].split('.')[0]
        collection_name = f"ALiN_{timestamp_str}"

        # สร้าง JSON และอัปโหลดไปยัง MongoDB
        json_data = generate_json_data(R_sq_mpl, distance_mpl, distance_osc, R_sq_osc)
        if json_data:
            # upload_to_mongo_data(
            #     json_data=json_data,
            #     db_url="mongodb://192.168.2.190:27017/",
            #     db_name="ALiN",
            #     collection_name=collection_name
            # )

            print(f"ข้อมูลถูกจัดเก็บใน Collection: {collection_name}")
    else:
        print("ข้อมูลไม่สมบูรณ์หรือไม่มีข้อมูล OSC")


if __name__ == "__main__":
    main()

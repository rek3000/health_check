from datetime import datetime
import mysql.connector
import os
from rekdoc import tools


def create_connection():
    try:
        conn = mysql.connector.connect(
                host='127.0.0.1',
                port=3306,
                user='rek',
                password='thuanlp123',
                database='log_mps'
                )

        if conn.is_connected():
            db_Info = conn.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
    except Exception as e:
        print("Error while connecting to MySQL", e)
    return conn

def insert_data(data, cursor):
    for idMachine, info in data.items():
    # Lấy thời gian hiện tại
        now = datetime.now()
        initTime = now.strftime("%Y-%m-%d %H:%M:%S")

        fault = info.get("fault", None)
        inlet = info.get("inlet", None)
        exhaust = info.get("exhaust", None)
        firmware = info.get("firmware", None)
        image = info.get("image", None)
        vol_avail = info.get("vol_avail", None)
        raid_stat = info.get("raid_stat", None)
        bonding = info.get("bonding", None)
        cpu_util = info.get("cpu_util", None)

        load = info.get("load", None)
        load_avg = load.get("load_avg", None)
        load_vcpu = load.get("vcpu", None)
        load_avg_per = load.get("load_avg_per", None)

        mem_util = info.get("mem_util", None)
        swap_util = info.get("swap_util", None)
    
        cursor.execute("INSERT INTO Clusters (idCluster) VALUES (%s)", (idMachine,))

        cursor.execute("INSERT INTO Details (idMachine, initTime, fault, inlet, exhaust, firmware, image, vol_avail, raid_stat, bonding, cpu_util, load_avg, load_vcpu, load_avg_per, mem_util, swap_util) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)", (idMachine, initTime, fault, inlet, exhaust, firmware, image, vol_avail, raid_stat, bonding, cpu_util, load_avg, load_vcpu, load_avg_per, mem_util, swap_util))


def run(file):
    conn = create_connection()
    data = tools.read_json(file)
    cursor = conn.cursor()
    insert_data(data, cursor)
    conn.commit()
    conn.close()
if __name__ == "__main__":
    run('./output/test.json')



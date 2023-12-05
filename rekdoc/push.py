from datetime import datetime
import mysql.connector
import os
from rekdoc import tools
from dotenv import load_dotenv


def create_connection():
    # default_host = "127.0.0.1"
    # default_database = "logs"
    # default_username = "rekdoc"
    # default_password = "welcome1"
    # default_port = 3306
    # dotenv_path = os.path.join(, '.env')
    load_dotenv('.env')

    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")
    database = os.environ.get("DB_DATABASE")

    # host = os.environ.get("DB_HOST", default_host)
    # port = os.environ.get("DB_PORT", default_port)
    # username = os.environ.get("DB_USERNAME", default_username)
    # password = os.environ.get("DB_PASSWORD", default_password)
    # database = os.environ.get("DB_DATABASE", default_database)
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )

        if conn.is_connected():
            db_Info = conn.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            return conn
    except Exception as e:
        print("Error while connecting to MySQL", e)


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

        # cursor.execute("INSERT INTO Clusters (idCluster)
        # VALUES (%s)", (idMachine,))

        cursor.execute(
            """
            INSERT INTO Details (idMachine, initTime, fault, inlet, exhaust,
            firmware, image, vol_avail, raid_stat, bonding, cpu_util, load_avg,
            load_vcpu, load_avg_per, mem_util, swap_util)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)
            """,
            (
                idMachine,
                initTime,
                fault,
                inlet,
                exhaust,
                firmware,
                image,
                vol_avail,
                raid_stat,
                bonding,
                cpu_util,
                load_avg,
                load_vcpu,
                load_avg_per,
                mem_util,
                swap_util,
            ),
        )


def run(file):
    conn = create_connection()
    data = tools.read_json(file)
    cursor = conn.cursor()
    insert_data(data, cursor)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # run("./output/test.json")
    pass

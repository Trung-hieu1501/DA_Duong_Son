import pandas as pd
import requests
import psycopg2
from psycopg2 import OperationalError, Error
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging


def crawl_financial_ratios():
    symbols = ['VIC', 'A32', 'AAA']
    financial_ratios = []
    for symbol in symbols:
        try:
            response = requests.get(f"https://s.cafef.vn/Ajax/PageNew/FinanceData/fi.ashx?symbol={symbol}")
            response.raise_for_status()
            records = response.json()
            for record in records:
                financial_ratios.append({
                    'symbol': record.get("Symbol"),
                    'year': int(record.get('Year')) if record.get('Year') else None,
                    'eps': float(record.get('EPS')) if record.get('EPS') else None,
                    'pe': float(record.get('PE')) if record.get('PE') else None,
                })
            logging.info(f"Crawl xong {symbol}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Request error với symbol {symbol}: {e}")
            raise

    df = pd.DataFrame(financial_ratios)
    #df = df.whre(df.notnull(df),None)
    logging.info(f"Số lượng bản ghi thu được: {df.shape[0]} bản ghi")
    if df.empty:
        logging.warning("DataFrame rỗng, không có dữ liệu để insert.")
        return

    conn = None
    try:
        # Cấu hình connection kết nối với DB 
        conn = psycopg2.connect(
            host='host.docker.internal',
            port=5433,                      
            user='hust_2024',               # User tương ứng với user postgres
            password='admin123',            # Pass tương ứng với pass postgres
            database='hust_2024'            # Db cần dùng
        )
        cursor = conn.cursor()
        logging.info('Kết nối Postgresql thành công')
        cursor.execute(""" SELECT *
                            FROM financial_ratios """)
        inserted_count = 0
        for _, row in df.iterrows():
            try:
                # Câu lệnh insert dữ liệu vào bảng (Sửa lại tên bảng, các cột của bảng)
                cursor.execute("""
                    INSERT INTO financial_ratios (symbol, year, eps, pe)    
                    VALUES (%s, %s, %s, %s)
                """, (row['symbol'], row['year'], row['eps'], row['pe']))       # Dữ liệu tương ứng với các cột insert
                inserted_count += 1
            except Error as e:
                logging.error(f"SQL lỗi khi insert {row['symbol']} - {row['year']}: {e}")

        conn.commit()
        logging.info(f'Insert dữ liệu thành công {inserted_count} bản ghi')
    except Error as e:
        logging.error(f"Lỗi kết nối hoặc thao tác MySQL: {e}")
        raise
    finally:
        if conn:
            if cursor:
                cursor.close()
            conn.close()


default_args = {
    'owner': 'HieuVDT',                         # Owner của Dags (có thể sửa)
    'depends_on_past': False,                   # Ko sửa
    'start_date': datetime(2025, 5, 15),        # Ngày bắt đầu chạy luồng (nếu luồng chạy daily thì để ngày hiện tại - 1)
    'retries': 3,                               # Số lần retry để xử lý lỗi (có thể sửa)
    'retry_delay': timedelta(minutes=1),        # Thời gian delay giữa các lần retry (có thể sửa)
    'retry_exponential_backoff': True,          # Ko sửa
    'max_retry_delay': timedelta(minutes=5),    # Thời gian chờ task thực thi (có thể sửa)
}

with DAG(
    dag_id="test_crawl",                        # Id của Dags (có thể sửa)
    default_args=default_args,                  
    schedule_interval=None,                     # Lập lịch cho job chạy (None: ko lập lịch, '@hourly': chạy hàng giờ, '@daily': chạy hàng ngày, '* * * * *': Tương ứng với  'phút giờ ngày_tháng tháng ngày_tuần')
    catchup=False,                              # Ko sửa
) as dag:
    crawl_financial_ratios_task = PythonOperator(    # Định nghĩa tên Task, id và hàm thực thi Task 
        task_id='crawl_financial_ratios',            # Id của Task
        python_callable=crawl_financial_ratios,      # Gọi đến hàm thực thi logic của task
    )

    # Chu trình thực hiện của các Task trong Dags
    crawl_financial_ratios_task
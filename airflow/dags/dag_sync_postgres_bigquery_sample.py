from airflow import DAG
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.state import DagRunState
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta
import logging
import pandas as pd

import psycopg2
from psycopg2 import Error

from google.cloud import bigquery
from google.oauth2 import service_account



def get_data(**kwargs):
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
        
        # Câu lệnh query trong postgres (có thể chạy các lệnh xử lý dữ liệu luôn)
        cursor.execute(""" SELECT *
                        FROM mart.financial_ratios__fa """)
        
        rows = cursor.fetchall()                                    # Lấy dữ liệu trả về
        columns = [desc[0] for desc in cursor.description]          # Lấy các cột trong câu query
        data = [dict(zip(columns, row)) for row in rows]            # Lưu dữ liệu vào dicts
        logging.info(f"Push {len(data)} records vào XCom")
        kwargs['ti'].xcom_push(key='financial_data', value=data)    # Push dữ liệu lên XCom

        conn.commit()
        logging.info(f'Query thành công')
    except Error as e:
        logging.error(f"Lỗi kết nối hoặc thao tác Postgres: {e}")
        raise
    finally:
        if conn:
            if cursor:
                cursor.close()
            conn.close()


def sync_data(**kwargs):
    try:
        data = kwargs['ti'].xcom_pull(task_ids='dag_get_data_postgres', key='financial_data')
        if not data:
            logging.warning("Không có dữ liệu từ XCom")
            return

        # Chuyển list dict thành DataFrame
        df = pd.DataFrame(data)

        client = bigquery.Client()
        table_id = "project2-441416.stock_dataa.financial_ratios"

        # Dùng load_table_from_dataframe để load dữ liệu lên BigQuery
        job = client.load_table_from_dataframe(df, table_id)
        job.result()  # đợi load xong

        logging.info("Insert thành công")

    except Exception as e:
        logging.error(f"Lỗi khi xử lý BigQuery: {e}")
        raise



default_args = {
    'owner': 'HieuVDT',                         # Owner của Dags (có thể sửa)
    'depends_on_past': False,                   # Ko sửa
    'start_date': datetime(2025, 5, 17),        # Ngày bắt đầu chạy luồng (nếu luồng chạy daily thì để ngày hiện tại - 1)
    'retries': 3,                               # Số lần retry để xử lý lỗi (có thể sửa)
    'retry_delay': timedelta(minutes=1),        # Thời gian delay giữa các lần retry (có thể sửa)
    'retry_exponential_backoff': True,          # Ko sửa
    'max_retry_delay': timedelta(minutes=5),    # Thời gian chờ task thực thi (có thể sửa)
}
with DAG(
    dag_id="sync_dag_sample",                   # Id của Dags (có thể sửa)
    default_args=default_args,                  
    schedule_interval='@daily',                     # Lập lịch cho job chạy (None: ko lập lịch, '@hourly': chạy hàng giờ, '@daily': chạy hàng ngày, '* * * * *': Tương ứng với  'phút giờ ngày_tháng tháng ngày_tuần')
    catchup=False,                              # Ko sửa
)as dag:
    # Task chờ Dags crawl dữ liệu chạy xong
    wait_for_other_dag = ExternalTaskSensor(
        task_id='wait_for_other_dag',
        external_dag_id='test_crawl',             # DAG cần kiểm tra
        external_task_id=None,        
        allowed_states=[DagRunState.SUCCESS],
        failed_states=[DagRunState.FAILED],
        mode='reschedule',
        timeout=43200,                          # timeout nếu DAG kia không xong (đơn vị là giây)
        poke_interval=1800,                     # mỗi 30m kiểm tra 1 lần
    )

    # Task transform dữ liệu trên postgres
    dag_get_data = PythonOperator(
        task_id='dag_get_data_postgres',
        python_callable=get_data,
        op_kwargs={},
    )

    # Task đồng bộ dữ liệu đã transform vào bigquery
    dag_sync_data_bqr = PythonOperator (
        task_id='sync_data_bigquery',
        python_callable=sync_data,
        op_kwargs={},
    )

    wait_for_other_dag >> dag_get_data >> dag_sync_data_bqr

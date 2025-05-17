from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Hàm cấu hình logic thực thi cho các Task
def say_hello():
    print("Hello world")

def say_hi():
    print('hi')

def say_ok():
    print('ok')

default_args = {
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),     # Ngày bắt đầu chạy luồng (nếu luồng chạy daily thì để ngày hiện tại - 1)
    'retries': 3,                           # Số lần retry để xử lý lỗi (có thể sửa)
    'retry_delay': timedelta(minutes=5),    # Thời gian delay giữa các lần retry (có thể sửa)
    'retry_exponential_backoff': True,      # Ko sửa
    'max_retry_delay': timedelta(minutes=60) # Thời gian chờ task thực thi (có thể sửa)

}

with DAG(
    dag_id="test_dag",              # Id của Dags (có thể sửa)
    default_args=default_args,      
    schedule_interval=None,         # Lập lịch cho job chạy (None: ko lập lịch, '@hourly': chạy hàng giờ, '@daily': chạy hàng ngày, '* * * * *': Tương ứng với  'phút giờ ngày_tháng tháng ngày_tuần')
    catchup=False,                  # Ko sửa
) as dag:
    task_hello = PythonOperator(    # Định nghĩa tên Task, id và hàm thực thi Task 
        task_id="say_hello",        # Id của Task (có thể sửa) 
        python_callable=say_hello,  # Gọi đến hàm thực thi logic của task
    )
    task_hi = PythonOperator(
        task_id="say_hi",           # Id của Task (có thể sửa)
        python_callable=say_hi,     # Gọi đến hàm thực thi logic của task
    )
    task_ok = PythonOperator(
        task_id="say_ok",
        python_callable=say_ok,
    )

    # Chu trình thực hiện của các Task 
    task_ok >> task_hi >> task_hello
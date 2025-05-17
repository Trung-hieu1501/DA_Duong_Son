FROM apache/airflow:2.10.3-python3.10

USER root

# Cập nhật pip và cài các thư viện cần thiết
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

USER airflow



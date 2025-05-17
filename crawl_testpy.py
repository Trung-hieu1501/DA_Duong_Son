import pandas as pd
import requests
import time
import random
import concurrent.futures

def header_param_products( cateId, cateTex, cateUrl, numpage=1):
    headers ={
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    # fix
    'Referer': f'https://tiki.vn{cateUrl}',
    'x-guest-token': '81n0c5t7OCxfZSRNe69uDWGpE3MJrVPd',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
    }

    params = {
    'limit': '40',
    'include': 'advertisement',
    'aggregations': '2',
    'trackity_id': 'c5464b70-2f56-0421-5dcc-93cc46c3dd2f',
    'category': f'{cateId}',
    'page': f'{numpage}',
    'urlKey': f'{cateTex}'
    }

    return headers, params

def process_product_by_link(info: dict):
    df_pro = pd.DataFrame()
    sleep_duration = random.uniform(1, 3) 
    time.sleep(sleep_duration)
    n=1
    for i in range(0,50):
        headers, params = header_param_products(cateId=info['query_value'], cateTex=info['url_key'], cateUrl=info['url_path'], numpage=i)
        response = requests.get('https://tiki.vn/api/personalish/v1/blocks/listings',headers=headers, params=params)
        if(response.status_code==200):
            print(f'kết nối thành công reponse thứ {n}')
            n+=1

def parallel_get_product(df_link):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_product_by_link, df_link.to_dict('records'))

if __name__ == "__main__":
    df_link = pd.read_csv("link_category.csv")
    for i in range(0,10):
        print(f'lần {i}')
        parallel_get_product(df_link)
        time.sleep(30)
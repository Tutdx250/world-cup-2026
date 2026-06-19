import json
import requests
from pprint import pprint

base = 'https://worldcup26.ir'
urls = [
    base + '/get/games',
    base + '/get/groups',
    base + '/get/teams'
]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

for url in urls:
    print('\n=== URL:', url, '===')
    try:
        r = requests.get(url, headers=headers, timeout=30, verify=False)
        print('status:', r.status_code)
        print('content-type:', r.headers.get('content-type'))
        print(r.text[:6000])
        try:
            data = r.json()
            print('\nJSON top-level type:', type(data).__name__)
            if isinstance(data, list):
                print('list len:', len(data))
                if data:
                    pprint(data[0])
            elif isinstance(data, dict):
                print('keys:', list(data.keys())[:20])
                for k, v in list(data.items())[:5]:
                    print(f'key={k} type={type(v).__name__} sample={str(v)[:200]}')
        except Exception as e:
            print('json parse error:', e)
    except Exception as e:
        print('request error:', e)

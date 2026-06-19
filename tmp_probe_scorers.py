import json, re, requests
from collections import Counter

url='http://worldcup26.ir:3050/get/games'
resp=requests.get(url, timeout=60)
data=resp.json()['games']

for item in data:
    if item.get('home_scorers') or item.get('away_scorers'):
        for side in ('home','away'):
            raw=item.get(f'{side}_scorers')
            if raw and raw not in ('null', None):
                text = raw.replace('“', '"').replace('”', '"')
                text = text.replace('{', '[').replace('}', ']')
                print('RAW:', raw)
                print('TEXT:', text)
                try:
                    parsed = json.loads(text)
                    print('PARSED_JSON:', parsed)
                except Exception as e:
                    print('JSON_ERR:', e)
                    # fallback regex
                    matches = re.findall(r'([A-Za-zÀ-ÿ\-\.\' ]+)\s+(\d+(?:\+\d+)?[\'’]?)', text)
                    print('REGEX:', matches)
                print('---')
        break

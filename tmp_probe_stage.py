import requests
from collections import Counter

url = 'http://worldcup26.ir:3050/get/games'
response = requests.get(url, timeout=60)
response.raise_for_status()
data = response.json()['games']

print('count=', len(data))
print('types=', Counter(item.get('type') for item in data))

for item in data:
    if item.get('type') in ('r32', 'r16', 'qf', 'sf', 'third', 'final'):
        print(f"\nID={item.get('id')} TYPE={item.get('type')} GROUP={item.get('group')} DATE={item.get('local_date')} FINISHED={item.get('finished')}")
        print('home_team_id=', item.get('home_team_id'), 'away_team_id=', item.get('away_team_id'))
        print('home_team_name_en=', item.get('home_team_name_en'))
        print('away_team_name_en=', item.get('away_team_name_en'))
        print('home_score=', item.get('home_score'), 'away_score=', item.get('away_score'))
        print('home_scorers=', item.get('home_scorers'))
        print('away_scorers=', item.get('away_scorers'))

'''CWA Weather SDK 
'''

print(f'my __name__ is {__name__}')

import requests

URLS = ['https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001',
        'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001']

_sites = {}
_coors = {}


def cwa(site: str | tuple, key: str) -> dict:
    '''get weather info from CWA
    site   - site name or coordinates
    key    - applid from CWA
    return - weather info in dcit, ex:
             {'S': '苗栗',
              'C': (24.564569, 120.824575),
              'O': '2025-11-18T11:00:00',
              'T': 20.4,
              'H': 0.71,
              'R': 0.0}
    '''

    global _sites, _coors

    # parameter validation
    if not site or type(site) not in (str, tuple):
        return {}
    if not key or type(key) != str:
        return {}

    # confirm sites map
    if not _sites:
        _sites, _coors = _load_sites(key)
        print('_load_sites() done', flush=True)

    # coor to name
    if type(site) == tuple:
        site = _nearest(site)

    return _cwa(url, site, key) if (url := _sites.get(site)) else {}

def _cwa(url: str, site: str, key: str) -> dict:
    params = {'Authorization': key,
              'StationName': site}

    r = requests.get(url, params=params)
    if r.status_code != 200:
        return {}

    station = r.json().get('records', {}).get('Station', [])
    if not station:
        return {}
    
    a = station[0]
    c = float(a['GeoInfo']['Coordinates'][1]['StationLatitude']), float(a['GeoInfo']['Coordinates'][1]['StationLongitude'])
    o = a['ObsTime']['DateTime'].replace('+08:00', '')
    t = float(a['WeatherElement']['AirTemperature'])
    h = float(a['WeatherElement']['RelativeHumidity']) / 100
    r = float(a['WeatherElement']['Now']['Precipitation'])
    return {'S': site, 'C': c, 'O': o, 'T': t, 'H': h, 'R': r}

def _nearest(site: tuple[float, float]):
    dist_map = []
    for n, (x, y) in _coors.items():
        dist = (x - site[0]) ** 2 + (y - site[1]) ** 2
        dist_map.append((dist, n))
    return min(dist_map)[1]

def _load_sites(key: str) -> tuple[dict, dict]:
    params = {'Authorization': key}
    sites, coors = {}, {}
    for url in URLS[::-1]:
        r = requests.get(url, params=params)
        if r.status_code != 200:
            continue
        
        station = r.json().get('records', {}).get('Station', [])
        if not station:
            continue
        
        for s in station:
            sites[s['StationName']] = url
            c = (float(s['GeoInfo']['Coordinates'][1]['StationLatitude']),
                 float(s['GeoInfo']['Coordinates'][1]['StationLongitude']))
            coors[s['StationName']] = c

    return sites, coors

def tostr(info: dict, sep: str = ', ') -> str:
    '''convert weather info from dict to str
    info   - weather info in dict
    sep    - sepertor of weather element
    return - weather info description
    '''
    if not info or type(info) != dict:
        return '無此站'
    if not sep or type(sep) != str:
        return 'bad sep'
    
    buf = []
    
    s = info.get('S')
    if s and type(s) == str:
        buf.append(f'測站: {s}')

    s = info.get('C')
    if s and type(s) == tuple and len(s) == 2:
        buf.append(f'座標: {s}')

    s = info.get('O')
    if s and type(s) == str:
        buf.append(f'時間: {s}')

    s = info.get('T')
    if s and type(s) == float:
        buf.append(f'溫度: {s}度')

    s = info.get('H')
    if s and type(s) == float:
        buf.append(f'濕度: {s:.0%}')

    s = info.get('R')
    if s and type(s) == float:
        buf.append(f'雨量: {s:.1f}mm')
    
    return sep.join(buf)

if __name__ == '__main__':
    info = {
        'S': '苗栗',
        'C': (24.564569, 120.824575),
        'O': '2025-11-18T11:00:00',
        'T': 20.4,
        'H': 0.71,
        'R': 0.0
    }
    print(tostr(info))

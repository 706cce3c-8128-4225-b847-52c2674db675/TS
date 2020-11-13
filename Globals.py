from pathlib import Path
import pandas as pd
from datetime import datetime
import json

data_root = Path('./csv')
data_weather_path = data_root.joinpath('weather')
data_activity_path = data_root.joinpath('activity')
info_df  = pd.read_csv('csv/info.csv')

region_keys =  info_df['keys'].values
region_friendly_name =dict(zip(info_df['keys'].values, info_df['name'].values)) #{

region_friendly_name_inv = {y:x for x,y in region_friendly_name.items()}
region_population = dict(zip(info_df['name'].values, info_df['population'].values))

def get_covid_region_data(region_name):
    if region_name[:2] == 'RU':
        data = pd.read_csv(data_root.joinpath(region_name + '.csv'))
    else:
        data = pd.read_csv(data_root.joinpath(region_friendly_name_inv[region_name] + '.csv'))

    data['date']  = pd.to_datetime(data['date']).tolist()
    return data


def get_weather_region_data(region_key):
    if not region_key[:2] == 'RU':
        region_key = region_friendly_name_inv[region_key]

    info = pd.read_csv(data_weather_path.joinpath('info.csv'))
    id_ = info[info['region_key']==region_key]['id'].to_list()
    assert len(id_) == 1
    id_ = str(id_[0])
    data = pd.read_csv(data_weather_path.joinpath(id_ + '.csv'))

    data['date'] = pd.to_datetime(data['timestamp'].map(lambda x: datetime.utcfromtimestamp(x).date())) # strftime('%Y-%m-%d'))
    data['time'] = data['timestamp'].map(lambda x: datetime.utcfromtimestamp(x).strftime('%H:%M'))
    return data


def get_region_activity_data(region_key):
    if not region_key[:2] == 'RU':
        region_key = region_friendly_name_inv[region_key]

    info = pd.read_csv(str(data_activity_path.joinpath('info.csv')), index_col=0)
    json_key = info['json_key'][region_key == info['region_key']].values

    if len(json_key) == 0:
        raise NameError('There is no such region in dataset')

    with open(data_activity_path.joinpath('yandex_activity_index.json'), encoding='utf8') as f:
        activity = json.load(f)

    df = pd.DataFrame(activity[json_key[0]])
    df.rename(columns={'value': 'activity_rate'}, inplace=True)
    return df[['date', 'activity_rate']]

def get_regions_with_activity_check():
    info = pd.read_csv(str(data_activity_path.joinpath('info.csv')), index_col=0)
    return info['region_key'].values
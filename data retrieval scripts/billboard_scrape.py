import billboard
import pandas as pd
from datetime import datetime, timedelta
import sys

'''
    This script scrapes the tracks from billboard from today back to
    a certain number of weeks as specified by the user (commnad line args)
'''
def get_songs(n_weeks):
    #n_weeks = int(sys.argv[1])
    days = 0
    today = datetime.today()
    now = datetime(today.year, today.month, today.day)

    df_final = pd.DataFrame()

    for i in range(n_weeks):
        
        curr_date = (now - timedelta(days = days)).date().__str__()
        
        days += 7
            
        chart = billboard.ChartData('rock-songs', curr_date, fetch = True, timeout = 25)
        
        df_t = pd.DataFrame()
        
        for i in chart:
            a = pd.Series()
            a['title'] = i.title
            a['artist'] = i.artist
            a['weeks'] = i.weeks
            df_t = df_t.append(a, ignore_index = True)
            
        df_final = df_final.append(df_t, ignore_index = True)

    df_agg = df_final.groupby(['artist', 'title']).max()
    return df_agg.reset_index()
    #df_agg.reset_index().to_csv('billboard_tracks.csv')

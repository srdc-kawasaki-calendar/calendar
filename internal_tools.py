import json
from datetime import datetime,time,timedelta
def read_log():
    with open('calendar_storage/log.txt','r',encoding='utf8') as f:
        return json.loads(f.read())

def before(hours,minutes): # X時X分まで待つ -> X時X分にXをする
    given_time = time(hours, minutes)
    now = datetime.now()
    future_exec = datetime.combine(now, given_time)
    if (future_exec - now).days < 0: 
        future_exec = datetime.combine(now + timedelta(days=1), given_time)
    return (future_exec - now).total_seconds()

def duration_calc(start_date,start_time,endtime_or_duration): #終了時間を計算する
    start_month,start_day= (int(each) for each in start_date.split('-'))
    start_hour,start_minute=(int(each) for each in start_time.split(':'))
    now=datetime.now()
    start_year=now.year
    end_time=None
    if 'h' in endtime_or_duration:
        hour,minute=(int(each) for each in endtime_or_duration.split('h'))
        if start_month<now.month: start_year+=1
        start=datetime(start_year,start_month,start_day,start_hour,start_minute)
        end_time=start+timedelta(hours=hour,minutes=minute)
    else:
        hour,minute=(int(each) for each in endtime_or_duration.split(':'))
        end_time=datetime(now.year,now.month,now.day,hour,minute)
    e_time=end_time.strftime("%H:%M")
    e_year=end_time.year
    r={"s_year":start_year,"e_year":e_year,"e_time":e_time,"time_log":now.strftime("%Y-%m-%d %H:%M:%S")}
    e_date=end_time.strftime("%m-%d")
    start_date=datetime.strptime(start_date,"%m-%d").strftime("%m-%d")
    if e_date!=start_date:
        r["e_date"]=e_date
        r['summary']=f"{start_time} ~ ({e_date}){e_time}"
    else:
        r["e_date"]=start_date
        r['summary']=f"{start_time} ~ {e_time}"
    return r

def days_between(d1, d2):  # 三日立った予約を自動的に削除するための日付の計算
    d1 = datetime.strptime(d1, "%m-%d")
    d2 = datetime.strptime(d2, "%m-%d")
    return abs((d2 - d1).days)
from datetime import datetime

class CalendarData():
    summary:str
    description:str
    s_year:int
    s_month:int
    s_day:int
    s_hour:int
    s_minute:int
    e_year:int
    e_month:int
    e_day:int
    e_hour:int
    e_minute:int

class discordCalendarData():
    author:str
    s_date:str
    s_time:str
    e_date:str
    e_time:str
    comment:str

def createInsertData(data:CalendarData):
    return {
        'summary':data.summary,
        'description': data.description,
        'start':{
            'dateTime': datetime(data.s_year, data.s_month, data.s_day, data.s_hour, data.s_minute).isoformat(),
            'timeZone': 'Japan'
        },
        'end': {
            'dateTime': datetime(data.e_year, data.e_month, data.e_day, data.e_hour, data.e_minute).isoformat(),
            'timeZone': 'Japan'
        },
    }
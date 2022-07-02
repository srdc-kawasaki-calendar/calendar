import  git,models
from datetime import datetime,timezone,timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account

TZ=timezone(timedelta(hours=+9),'JST')
NC_CONVERTER={"makoto":"マコト","minimakoto":"ミニマコト","takumi":"匠",
            "ookuro":"大きい黒いやつ","kuroiyatsu":"黒いやつ","tetsunoomo":"鉄のおもちゃ",}
wh={"id":"da739ec0-1d64-43af-bc1d-9c970f32a5b6","type":"webhook","address":"https://discord.com/api/webhooks/992493738523893814/gQpPazv2ymi9-5X5dTwTy36b1c3GJ40idvBZa5oAfmCstRxYoOtpm26NdF3ILVeSrklf"}
class GitHub():
    def __init__(self,url) -> None:
        self.local_repo=git.Repo.clone_from(url,'./calendar_storage')

    def commit_push(self,message="commit",log=None):
        if log:
            with open('calendar_storage/log.txt','a',encoding='utf-8') as f:
                print(log,file=f)
            # with open('calendar_storage/log.txt','a+',encoding='utf8') as f:
            #     json.dump(log+'\n',f,ensure_ascii=False)
        self.local_repo.git.add(all=True)
        self.local_repo.index.commit(message)
        self.local_repo.remote(name='origin').push()

class GoogleCalendar():
    def __init__(self,SERVICE_ACCOUNT,nc_calendar_list:dict) -> None:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT, scopes=SCOPES)
        self.service = build('calendar', 'v3', credentials=creds)
        self.nc_list=nc_calendar_list

    def sync(self,calendarId,syncToken=None,pageToken=None):
        if not syncToken:
            return self.service.events().list(calendarId=calendarId,singleEvents=True,maxResults=50).execute()["nextSyncToken"]
        result=None
        if pageToken:
            result=self.service.events().list(calendarId=calendarId,singleEvents=True,maxResults=10,syncToken=syncToken,pageToken=pageToken).execute()
        else: result=self.service.events().list(calendarId=calendarId,singleEvents=True,maxResults=10,syncToken=syncToken).execute()
        if "error" in result: self.sync(calendarId)
        eventIds=result["items"]
        if "nextPageToken" in result: return {"page":result["nextPageToken"],"eventIds":eventIds}
        return {"sync":result["nextSyncToken"],"eventIds":eventIds}
    def gcupload(self,nc_name,data:dict):
        calData = models.CalendarData()
        calData.s_year,calData.s_month,calData.s_day=(int(each) for each in data["s_date"].split('-'))
        calData.s_hour,calData.s_minute=(int(each) for each in data["s_time"].split(':'))
        calData.e_year,calData.e_month,calData.e_day=(int(each) for each in data["e_date"].split('-'))
        calData.e_hour,calData.e_minute=(int(each) for each in data["e_time"].split(':'))
        calData.summary=data['author']
        calData.description=NC_CONVERTER[nc_name]
        if data["comment"]: calData.description+=f"\n{data['comment']}"
        body=models.createInsertData(calData)
        return self.service.events().insert(calendarId=self.nc_list[nc_name.upper()], body=body).execute()["id"]

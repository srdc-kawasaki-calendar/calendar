from calendar import calendar
import os,os.path,json,asyncio
from discord.ext import commands,tasks
from datetime import date
from dotenv import load_dotenv,find_dotenv
from external_tools import GitHub,GoogleCalendar
from internal_tools import read_log,before,duration_calc,days_between

# 事前準備
dotenv_path=find_dotenv()
load_dotenv(dotenv_path)

#githubとgoogle calendar
pusher=GitHub(url=os.environ["GITHUB_URL"])
nc_calendarid_list={"MAKOTO":os.environ['MAKOTO'],"MINIMAKOTO":os.environ['MINIMAKOTO'],
                "TAKUMI":os.environ['TAKUMI'],"OOKURO":os.environ['OOKURO'],
                "KUROIYATSU":os.environ['KUROIYATSU'],"TETSUNOOMO":os.environ['TETSUNOOMO'],}
calendar_token_list={"MAKOTO":None,"MINIMAKOTO":None,"TAKUMI":None,"OOKURO":None,"KUROIYATSU":None,"TETSUNOOMO":None}
gc_calendar=GoogleCalendar(os.environ['SERVICE_ACCOUNT'],nc_calendarid_list)
nc_list=['マコト','ミニマコト','匠','大きい黒いやつ','黒いやつ','鉄のおもちゃ']
recognition_list={
    'makoto':['m','M','makoto'],
    'minimakoto':['mm','MM','minimakoto'],
    'takumi':['t','T','takumi'],
    'ookuro':['ok','OK','ookuro','ookiikuroiyatsu'],
    'kuroiyatsu':['k','K','kuro','kuroiyatsu'],
    'tetsunoomo':['to','TO','tetsunoomo']
}

class NC(commands.Cog):
    def rwcalendar(self,log_content=None,option='w'):  # calendar.txt を読み込む・書き込む
        with open('calendar_storage/calendar.txt','r+',encoding='utf8') as f:
            if option=='r': return json.loads(f.read())
            json.dump(self.calendar,f,ensure_ascii=False)
        pusher.commit_push(log=log_content)
            
    def rwconfig(self,option='w'):
        with open('calendar_storage/config.txt','r+',encoding='utf8') as f:
            if option=='r': return json.loads(f.read())
            json.dump(self.config,f,ensure_ascii=False)
        pusher.commit_push()

    def announce(self):  # Announce_channelにアナウンスする
        text=""
        for i,(_,value) in enumerate(self.calendar.items()):
            text+=f"**{nc_list[i]}**\n```\n"
            if value:
                for date,schedule in value.items():
                    text+=f"//{date}//\n"
                    for applicant, detail in schedule.items():
                        for each in detail:
                            text+=f"{each['summary']} {applicant}\n"
                            if each["comment"]: text+=f"{each['comment']}\n"
                text+="```"
            else:
                text+="なし\n```"
            if i==2 or i==5:
                self.bot.loop.create_task(self.bot.get_channel(self.announce_channel_id).send(text))
                text=""
        
    def __init__(self,bot): # 初期化（事前準備）
        self.bot = bot
        self.command_channel_id=int(os.environ['COMMAND_CHANNEL_ID'])
        self.announce_channel_id=int(os.environ['ANNOUNCE_CHANNEL_ID'])
        self.calendar=self.rwcalendar(option='r')
        self.config=self.rwconfig(option='r')
        for nc_name in calendar_token_list:
            calendar_token_list[nc_name]=gc_calendar.sync(nc_calendarid_list[nc_name],None,None)
        self.AutoDelete.start() # Autodeleteの計算を開始する
        self.retrieve_new.start()
    
    @tasks.loop() #リピートするコマンド
    async def AutoDelete(self):
        await asyncio.sleep(before(0,1))
        now=date.today().strftime("%m-%d")
        # 削除したかにかかわらず，カレンダーを更新する。そしてアナウンスする
        for _,value in self.calendar.items():
            if value:
                for d in value:
                    if days_between(d,now)>=3:
                        del value[d]
        self.rwcalendar()
        self.announce()
    
    @tasks.loop()
    async def retrieve_new(self):
        await asyncio.sleep(10)
        new_events={"MAKOTO":[],"MINIMAKOTO":[],"TAKUMI":[],"OOKURO":[],"KUROIYATSU":[],"TETSUNOOMO":[]}
        for nc_name in calendar_token_list:
            result=None
            if type(calendar_token_list[nc_name]) is list:
                result=gc_calendar.sync(nc_calendarid_list[nc_name],calendar_token_list[nc_name][0],calendar_token_list[nc_name][1])
            else: result=gc_calendar.sync(nc_calendarid_list[nc_name],calendar_token_list[nc_name])
            if "page" in result:
                calendar_token_list[nc_name]=[calendar_token_list[nc_name][0],result["page"]]
            else: calendar_token_list[nc_name]=result["sync"]
            for each in result["eventIds"]:
                new_events[nc_name].append(each["id"])
        print(new_events)
        
    @commands.command(aliases=['Nc','NC'])
    async def nc(self,ctx:commands.Context,name,date,start_time,end_or_duration,*args):
        #ex) nc 06-18 17:00 7h30 いじめはよくない
        if ctx.message.channel.id == self.command_channel_id:
            await ctx.message.add_reaction("\N{Anticlockwise Downwards and Upwards Open Circle Arrows}")
            try:
                author=None
                id=ctx.message.author.id
                if str(id) not in self.config:
                    author=ctx.message.author.display_name
                    self.config[id]=ctx.message.author.display_name
                    self.rwconfig()
                else: author=self.config[str(id)]
                comment=' '.join(args)
                time_info=duration_calc(date,start_time,end_or_duration)
                log=f"{time_info['time_log']} NEW {author} {date} {time_info['summary']} {comment}"
                dc_data={"start_time":start_time,"comment":comment,"summary":time_info['summary']}
                for key,value in recognition_list.items():
                    if name in value:
                        if date not in self.calendar[key]:self.calendar[key][date]={author:[dc_data]}
                        elif date in self.calendar[key] and author not in self.calendar[key][date]:
                            self.calendar[key][date][author]=[dc_data]
                        else:
                            self.calendar[key][date][author].append(dc_data)
                        self.calendar[key][date][author][-1]['eventId']=gc_calendar.gcupload(nc_name=key,data={"s_date":f"{time_info['e_year']}-{date}",
                        "s_time":start_time,"e_date":f"{time_info['e_year']}-{time_info['e_date']}","e_time":time_info['e_time'],
                        "author":author,"comment":comment if comment else None})
                        self.rwcalendar(log_content=log)
                        await ctx.message.add_reaction("\N{Heavy Large Circle}")
                        self.announce()
                        return
                await ctx.send("このNCは存在していません")
            except Exception as e:
                await ctx.message.add_reaction("\N{CROSS MARK}")
                await ctx.send(f"入力したパラメータに誤りがある\nError: {e}")

    @commands.command(aliases=['Delete','del','Del'])
    async def delete(self,ctx:commands.Context,name=None,date=None,start_time=None):
        author=self.config[ctx.message.author.id]
        log:str
        if not name:
            for key,value in self.calendar.items():
                if value:
                    for d,t in value.items():
                        if author in t: del t[author]
            log="ユーザのすべての記録"
        else:
            for key,value in recognition_list.items():
                if name in value:
                    name=key
                    break
            if not date:
                for d,t in self.calendar[name].items():
                    if author in t: del self.calendar[name][d][author]
                log=f"{name}のすべての記録"
            else:
                if not start_time:
                    if author in self.calendar[name][date]: del self.calendar[name][date][author]
                    log=f"{name} {date}のすべての記録"
                else:
                    start_time_ls=[each[0] for each in self.calendar[name][date][author]]
                    del self.calendar[name][date][author][start_time_ls.index(start_time)]
                    log=f"{name} {date} {start_time}"
        for key,value in self.calendar.items():
            if value:
                for d,t in value.items():
                    if not t: 
                        del self.calendar[key][d]
                        break
                break
        self.rwcalendar(log_content=[author,log])
        await ctx.send("削除できました")
        self.announce()

    @commands.command(aliases=['name','username'])
    async def nickname(self,ctx:commands.Context,*new_name):
        new_name=new_name[0]
        old_name=self.config[ctx.message.author.id]
        self.config[ctx.message.author.id]=new_name
        self.rwconfig()
        for key,value in self.calendar.items():
            if value:
                for d,t in value.items():
                    if old_name in t: t[new_name]=t.pop(old_name)
        self.rwcalendar(log_content=[f"username {old_name} changed to {new_name}"])
        await ctx.send(f"{old_name}->{new_name}に変更しました")
        self.announce()

    @commands.command(aliases=['Update'])
    async def update(self,ctx:commands.Context):
        pusher.commit_push()
    
    @commands.command(aliases=['Check'])
    async def check(self,ctx:commands.Context):
        self.announce()

def setup(bot: commands.Bot):
    bot.add_cog(NC(bot))

if __name__=='__main__':
    pusher.commit_push("update")

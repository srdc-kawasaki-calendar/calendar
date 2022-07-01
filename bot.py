import os
from dotenv import load_dotenv,find_dotenv
from discord.ext import commands

dotenv_path=find_dotenv()
load_dotenv(dotenv_path)

def main():
    client=commands.Bot(command_prefix="k! ")
    client.load_extension("cog")
    client.run(os.environ["DISCORD_TOKEN"])
    
if __name__ == '__main__':
    main()
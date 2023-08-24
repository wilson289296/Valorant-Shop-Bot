import discord
from discord import app_commands
from discord.ext import commands, tasks
from shopss import login, continue_otp
import json
import os
import asyncio
import base64
# import time
# import asyncio

# ===================================== Generic funcs ====================================

def loadCredStore():
    if os.path.exists(os.getcwd()+"/creds.json"):
        with open("creds.json", "r") as f:
            creds = json.load(f)
        print("Credential store loaded.")
    else:
        creds = json.loads('{}')
    return creds

def saveCredStore(creds):
    with open("creds.json", "w") as f:
        json.dump(creds, f, indent=4)
    print("Credential store saved.")

def b64enc(str):
    return str
    # return base64.b64encode(str.encode("ascii")).decode("ascii")

def b64dec(str):
    return str
    # return base64.b64decode(str.encode("ascii")).decode("ascii")

# ===================================== /Generic funcs ===================================

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is up and ready, creating or loading credentials object...")
    process_queue.start()
    creds = loadCredStore()
    saveCredStore(creds)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="addaccount")
@app_commands.describe(username = "Riot account username",
                       password = "Riot account password")
async def addaccount(interaction: discord.Interaction, username: str, password: str):
    creds = loadCredStore()
    creds[interaction.user.id] = {
        "username": username,
        "password": b64enc(password)
    }
    saveCredStore(creds)
    await interaction.response.send_message(f"Successfully added user {interaction.user.nick}", ephemeral=True)

@bot.tree.command(name="shop")
async def get_shop(interaction: discord.Interaction):
    global response_time_total
    global jobs
    creds = loadCredStore()
    if str(interaction.user.id) in creds.keys():
        user = creds[str(interaction.user.id)]["username"]
        pw = b64dec(creds[str(interaction.user.id)]["password"])
        task_queue.append({
            "discuser": interaction.user.id,
            "user": user,
            "pw": pw,
            "channel": interaction.channel_id
        })
        place = len(task_queue)
        global working
        if working:
            place += 1
        try:
            est_time = response_time_total/jobs
        except:
            est_time = 50
        await interaction.response.send_message(f"Request queued. You are #{place} in line (est completion in ~{est_time:.2f}s).")
    else:
        await interaction.response.send_message(f"User not found, try adding yourself first with `/addaccount`.")

task_queue = []
working = False
response_time_total = 0
jobs = 0

@tasks.loop(seconds=0.5)
async def process_queue():
    global task_queue
    global working
    global jobs
    global response_time_total
    # print(f"Number of jobs in queue: {len(task_queue)}")
    if len(task_queue) != 0 and not working:
        print(f"{len(task_queue)} jobs in queue, starting work...")
        working = True
        task = task_queue.pop(0)
        channel = bot.get_channel(task["channel"])
        elap, result = await login(task["user"], task["pw"])
        if result == "done":
            print("ss taken, sending photo")
            with open("ss.png", 'rb') as f:
                picture = discord.File(f)
                await channel.send(content=f"<@{task['discuser']}>\n*(time elapsed = {elap:.2f}s)*", file=picture)
            jobs += 1
            response_time_total += elap
            print(f"completed task for {task['user']}")
        elif result == "otp":
            print("Encountered OTP. Prompting user.")
            # set flag that user has OTP enabled
            def check(message: discord.Message):
                return message.channel.id == channel.id and message.author.id == task['discuser'] and len(message.content) == 6
            try:
                await channel.send(content=f"<@{task['discuser']}> login requires OTP - reply to this message with 6 digit OTP within 120 seconds.")
                message = await bot.wait_for('message', check=check, timeout=120.0)
            except asyncio.TimeoutError:
                print("User did not respond in time, cancelling job.")
                await channel.send(content=f"<@{task['discuser']}> did not respond with OTP in time. Login aborted.")
            else:
                elap2, result = await continue_otp(message.content)
                if result == "done":
                    print("ss taken, sending photo")
                    with open("ss.png", 'rb') as f:
                        picture = discord.File(f)
                        await channel.send(content=f"<@{task['discuser']}>\n*(time elapsed = {elap + elap2:.2f}s)*", file=picture)
                    jobs += 1
                    response_time_total += elap + elap2
                    print(f"completed task for {task['user']}")
                else:
                    print("User submitted invalid OTP, cancelling job.")
                    await channel.send(content=f"<@{task['discuser']}> submitted invalid OTP. Login aborted.")
        elif result == "error":
            print("Process errored out or timed out, requeueing task to try again.")
            await channel.send(content=f"I farted, brb")
            task_queue.insert(0, task)
        await asyncio.sleep(5)
        working = False

    

with open('token.key') as f:
    token = f.readline()

bot.run(token)



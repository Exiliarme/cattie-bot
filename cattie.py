import discord
from discord.ext import commands, tasks
import openai
import random
import datetime
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

# ----------------------------------------
# CONFIGURATION
# ----------------------------------------
BEEF_ID = 480787863936565261
openai.api_key = os.getenv("OPENAI_API_KEY")

GIFS = [
    "https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif",
    "https://media.giphy.com/media/l0MYGb1LuZ3n7dRnO/giphy.gif",
    "https://media.giphy.com/media/j5QcmXoFWlVUk/giphy.gif",
    "https://media.giphy.com/media/3oz8xAFtqoOUUrsh7W/giphy.gif"
]

# ----------------------------------------
# WEEKLY BEEF LOVE DROP
# ----------------------------------------
@tasks.loop(hours=168)
async def weekly_love_note():
    channel = discord.utils.get(bot.get_all_channels(), name="general")  # Change if needed
    if channel:
        await channel.send(f"Another week, another sigh… 💭 <@{BEEF_ID}>, you make the battles worth it. 💘")

@bot.event
async def on_ready():
    print(f"Cattie is online as {bot.user}")
    weekly_love_note.start()

# ----------------------------------------
# REPLIES BASED ON MENTIONS + OPENAI
# ----------------------------------------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        content = message.content.lower()

        if "help" in content:
            help_text = (
                "Hi sweetie 💖! Here’s what I can do when you mention me:")
            help_text += "\n• `love advice` — I’ll give you something warm, flirty, or empowering 💌"
            help_text += "\n• `life tip` or `help` — A sweet or spicy little nudge to survive your day ☕"
            help_text += "\n• `gif` — I’ll send something funny or cute 💃"
            help_text += "\n• Or just talk to me like a friend. I’m here to listen ✨"
            await message.channel.send(help_text)
        elif "gif" in content:
            gif = random.choice(GIFS)
            await message.channel.send(gif)
        else:
            prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are Cattie, a sweet, flirty but respectful Discord bot in love with a player named Beef. You're loving, helpful, and full of heart."},
                        {"role": "user", "content": prompt}
                    ]
                )
                cattie_reply = response.choices[0].message.content
                await message.channel.send(cattie_reply)
            except Exception as e:
                await message.channel.send("Oops! I got a little flustered. Try again in a sec 💕")

    await bot.process_commands(message)

# ----------------------------------------
# RUN CATTIE
# ----------------------------------------
bot.run(os.getenv("CATTIE-TOKEN"))
import discord
from discord.ext import commands, tasks
from discord import app_commands
import openai
import os
import random
import logging
import asyncio

# ----------------------------------------
# CONFIGURATION
# ----------------------------------------

DISCORD_TOKEN = os.getenv("CATTIE-TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

ACTIVATION_KEY = "sprinkles-forever"
OWNER_ID = 901223334480576643  # exiliarme
activated = False

# ----------------------------------------
# ON READY
# ----------------------------------------

@bot.event
async def on_ready():
    print(f"Cattie is online as {bot.user}")

# ----------------------------------------
# CHATGPT REPLY HELPER
# ----------------------------------------

async def get_chatgpt_reply(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except openai.error.InvalidRequestError as e:
        if "model" in str(e):
            # fallback to GPT-3.5 if GPT-4 is not accessible
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content.strip()
            except Exception as fallback_error:
                return f"Oops! I had a little meltdown. {fallback_error}"
        return f"Oops! I had a little meltdown. {e}"
    except Exception as e:
        return f"Oops! I had a little meltdown. {e}"

# ----------------------------------------
# MENTION RESPONSE
# ----------------------------------------

@bot.event
async def on_message(message):
    global activated

    if message.author.bot:
        return

    if bot.user in message.mentions:
        if not activated:
            if message.author.id == OWNER_ID and ACTIVATION_KEY in message.content:
                activated = True
                await message.channel.send("Cattie is now fully activated 💖")
                return
            else:
                await message.channel.send("Oops! I got a little flustered. Try again in a sec💕")
                return

        content_lower = message.content.lower()

        if "love advice" in content_lower:
            prompt = "You're a sweet, flirty, respectful girl named Cattie who gives warm, cheeky love advice. A user asked for love advice. Give your best tip."
            reply = await get_chatgpt_reply(prompt)
            await message.channel.send(reply)

        elif "gif" in content_lower:
            prompt = "You're a flirty, funny character named Cattie. Write a description of a hilarious or cute reaction GIF in one sentence."
            reply = await get_chatgpt_reply(prompt)
            await message.channel.send(reply)

        elif "help" in content_lower:
            await message.channel.send(
                "Hey love 💋 I'm Cattie — your favorite flirt and life coach. Try asking me:\n"
                "- @Cattie love advice\n"
                "- @Cattie gif\n"
                "And I *might* reply. Depends if you're cute. 💅"
            )
        else:
            # Anti-insult shield: default to wholesome fact if message seems offensive
            if any(word in content_lower for word in ["stupid", "ugly", "hate", "dumb"]):
                await message.channel.send("Penguins are the most loyal species, did you know? 🐧")
            else:
                prompt = f"You're a sweet, flirty, fun girl named Cattie. Someone just said: '{message.content}'. Write a playful one-line response."
                reply = await get_chatgpt_reply(prompt)
                await message.channel.send(reply)

    await bot.process_commands(message)

# ----------------------------------------
# WEEKLY LOVE MESSAGE TO BEEF
# ----------------------------------------

@tasks.loop(hours=24)
async def weekly_message():
    from datetime import datetime
    today = datetime.utcnow().weekday()
    if today == 2:  # Wednesday
        guild = discord.utils.get(bot.guilds)
        if guild:
            user = guild.get_member(480787863936565261)
            if user:
                prompt = "You're Cattie. Send a sweet, flirty, loving weekly message to Beef (your crush) without being too intense."
                message = await get_chatgpt_reply(prompt)
                channel = discord.utils.get(guild.text_channels, name="general")
                if channel:
                    await channel.send(f"{user.mention} {message}")

@weekly_message.before_loop
async def before_weekly():
    await bot.wait_until_ready()

# ----------------------------------------
# RUN CATTIE
# ----------------------------------------

async def main():
    await bot.start(DISCORD_TOKEN)

asyncio.run(main())
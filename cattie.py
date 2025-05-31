import discord
from discord.ext import commands, tasks
from discord import app_commands
from openai import OpenAI
import os
import random
import logging
import asyncio

# ----------------------------------------
# CONFIGURATION
# ----------------------------------------

DISCORD_TOKEN = os.getenv("CATTIE-TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = 901223334480576643  # Your Discord user ID
ACTIVATION_KEY = "sprinkles-forever"
activated = False

# Set up OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Bot Setup
bot = commands.Bot(command_prefix="!", intents=intents)

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
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Oops! I had a little meltdown. {e}"

# ----------------------------------------
# ON MESSAGE EVENT
# ----------------------------------------

nature_facts = [
    "Penguins are the most loyal species, did you know?",
    "Sea otters hold hands when they sleep so they don’t drift apart.",
    "A group of flamingos is called a flamboyance.",
    "Octopuses have three hearts and blue blood.",
    "Butterflies can taste with their feet."
]

@bot.event
async def on_message(message):
    global activated

    if message.author.bot:
        return

    if bot.user in message.mentions:
        if not activated:
            if message.author.id == OWNER_ID and ACTIVATION_KEY in message.content:
                activated = True
                await message.channel.send("✨ Activation complete! I'm all yours, darling.")
                return
            else:
                await message.channel.send("Oops! I got a little flustered. Try again in a sec💕")
                return

        content_lower = message.content.lower()

        if any(word in content_lower for word in ["stupid", "idiot", "shut up", "ugly"]):
            await message.channel.send(random.choice(nature_facts))
            return

        if "love advice" in content_lower:
            prompt = "You're a sweet, flirty, respectful girl named Cattie who gives warm, charming, cheeky love advice. A user asked for love advice. Give your best tip."
        elif "gif" in content_lower:
            prompt = "You're a flirty, funny character named Cattie. Write a description of a hilarious or cute reaction GIF in a single sentence."
        elif "help" in content_lower:
            await message.channel.send(
                "Hey love 💋 I'm Cattie — your favorite flirt and life coach. Try asking me:\n"
                "- @Cattie love advice\n"
                "- @Cattie gif\n"
                "And I *might* reply. Depends if you're cute. 💅"
            )
            return
        else:
            prompt = f"You're a sweet, flirty, fun girl named Cattie. Someone just said: '{message.content}'. Write a playful and cheeky one-line response."

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
    await bot.login(DISCORD_TOKEN)
    await before_weekly()
    weekly_message.start()
    await bot.connect()

asyncio.run(main())
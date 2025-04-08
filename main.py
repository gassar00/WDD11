import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

voice_clients = {}
yt_dl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'force-ipv4': True,
    'extract_flat': 'in_playlist',
    'default_search': 'ytsearch'
}
ytdl = yt_dlp.YoutubeDL(yt_dl_format_options)

ffmpeg_options = {
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands.")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

@bot.tree.command(name="play", description="🎵 شغل أغنية من يوتيوب")
@app_commands.describe(url="رابط الفيديو من اليوتيوب")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()
    vc = interaction.user.voice
    if not vc or not vc.channel:
        await interaction.followup.send("❗ لازم تكون في روم صوتي.")
        return

    try:
        info = ytdl.extract_info(url, download=False)
        if "entries" in info:
            info = info["entries"][0]
        URL = info["url"]
        title = info.get("title", "Unknown Title")

        voice_client = await vc.channel.connect()
        voice_clients[interaction.guild.id] = voice_client

        source = discord.FFmpegPCMAudio(URL, **ffmpeg_options)
        voice_client.play(source)
        await interaction.followup.send(f"🎶 الآن يتم تشغيل: **{title}**")
    except Exception as e:
        await interaction.followup.send("⚠️ صار خطأ أثناء التشغيل، جرب رابط ثاني.")
        print(f"❌ Error: {e}")

@bot.tree.command(name="stop", description="⛔ أوقف الأغنية واطلع من الروم")
async def stop(interaction: discord.Interaction):
    if interaction.guild.id in voice_clients:
        await voice_clients[interaction.guild.id].disconnect()
        del voice_clients[interaction.guild.id]
        await interaction.response.send_message("⏹️ تم الإيقاف والخروج من الروم.")
    else:
        await interaction.response.send_message("❌ البوت مو في أي روم.")

bot.run(os.getenv("YOUR_BOT_TOKEN"))

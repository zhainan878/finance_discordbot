import os
import discord
import feedparser
import asyncio

# 🔑 從 Render 環境變數讀取（安全）
TOKEN = os.environ["TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

# 🤖 Discord 設定
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 📰 抓新聞
def get_news():
    rss_url = "https://news.google.com/rss/search?q=股市&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    feed = feedparser.parse(rss_url)

    news_list = []
    for entry in feed.entries[:5]:
        news_list.append(f"{entry.title}\n{entry.link}")

    return news_list

# 🔁 定時發送新聞
async def send_news_loop():
    await client.wait_until_ready()
    channel = await client.fetch_channel(CHANNEL_ID)

    while not client.is_closed():
        print("📡 發送新聞中...")

        news = get_news()
        for item in news:
            await channel.send(item)
            await asyncio.sleep(1)

        print("⏰ 等待 30 分鐘...")
        await asyncio.sleep(1800)  # 30分鐘

# 🚀 Bot 啟動
@client.event
async def on_ready():
    print(f"✅ 已登入：{client.user}")
    client.loop.create_task(send_news_loop())

# ▶️ 啟動 Bot
client.run(TOKEN)

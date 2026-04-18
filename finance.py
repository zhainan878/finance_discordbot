import os
import discord
import feedparser
import asyncio

TOKEN = os.environ["TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 🧠 記錄已發過的新聞（避免重複）
sent_links = set()

# 🌍 可切換市場
MARKET = "TW"  # TW / US / JP

def get_rss():
    if MARKET == "US":
        return "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US"
    elif MARKET == "JP":
        return "https://news.google.com/rss/search?q=株式市場&hl=ja&gl=JP&ceid=JP:ja"
    else:
        return "https://news.google.com/rss/search?q=股市&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

def get_news():
    feed = feedparser.parse(get_rss())
    news_list = []

    for entry in feed.entries[:10]:
        if entry.link in sent_links:
            continue

        sent_links.add(entry.link)

        title = entry.title

        # 🧠 超簡單摘要（先不用AI）
        if "上漲" in title or "up" in title.lower():
            summary = "📈 可能利多消息"
        elif "下跌" in title or "fall" in title.lower():
            summary = "📉 可能利空消息"
        else:
            summary = "📰 財經新聞"

        news_list.append(f"{summary}\n{title}\n{entry.link}")

    return news_list

async def loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        news = get_news()

        if channel and news:
            for n in news:
                await channel.send(n)
                await asyncio.sleep(1)

        await asyncio.sleep(900)  # 15分鐘更新一次

@client.event
async def on_ready():
    print("🟢 Bot online:", client.user)
    client.loop.create_task(loop())

client.run(TOKEN)

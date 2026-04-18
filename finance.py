import os
import discord
import feedparser
import asyncio

TOKEN = os.environ["TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

intents = discord.Intents.default()
client = discord.Client(intents=intents)

RSS_FEEDS = {
    "TW": "https://news.google.com/rss/search?q=股市&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
    "US": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US",
    "JP": "https://news.google.com/rss/search?q=株式市場&hl=ja&gl=JP&ceid=JP:ja"
}

IMPORTANT_KEYWORDS = [
    "崩盤", "暴跌", "暴漲", "利率", "升息", "降息",
    "crash", "surge", "interest rate", "Fed", "recession"
]

sent_links = set()

def is_important(title):
    return any(k.lower() in title.lower() for k in IMPORTANT_KEYWORDS)

def get_news():
    news_list = []

    for country, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            if entry.link in sent_links:
                continue

            sent_links.add(entry.link)

            title = entry.title
            important = is_important(title)

            tag = "🔴【重大新聞】" if important else "📰"

            news_list.append(
                f"{tag} [{country}]\n{title}\n{entry.link}"
            )

    return news_list

async def loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        news = get_news()

        for n in news:
            await channel.send(n)
            await asyncio.sleep(1)

        await asyncio.sleep(900)  # 15分鐘

@client.event
async def on_ready():
    print("🟢 Bot online:", client.user)
    client.loop.create_task(loop())

client.run(TOKEN)

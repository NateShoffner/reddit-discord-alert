import os
from dotenv import load_dotenv
import praw
import asyncio
import logging

from discord_handler import DiscordHandler
from monitor import SubredditMonitor

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO
)


async def main():
    load_dotenv()

    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_ID"),
        client_secret=os.getenv("REDDIT_SECRET"),
        user_agent="Discord Webhook Bot (by /u/syntack)",
    )

    handler = DiscordHandler(os.getenv("WEBHOOK_URL"))
    monitor = SubredditMonitor(reddit, os.getenv("SUBREDDIT"), handler)

    # hack to allow nested asyncio loops
    import nest_asyncio

    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    task = loop.create_task(monitor.poll(os.getenv("UPDATE_INTERVAL")))

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        task.cancel()


if __name__ == "__main__":
    asyncio.run(main())

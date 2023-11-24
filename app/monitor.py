import cachetools
import asyncpraw

import asyncio
import logging

from discord_handler import DiscordHandler


class SubredditMonitor:
    def __init__(
        self, reddit: asyncpraw.Reddit, subreddit: str, discord_handler: DiscordHandler
    ):
        self.reddit = reddit
        self.subreddit_name = subreddit
        self.discord_handler = discord_handler
        self.logger = logging.getLogger(self.__class__.__name__)
        self.post_cache = cachetools.TTLCache(maxsize=256, ttl=604800)
        # TODO persist cache to disk so we don't have to re-share posts on restart

    async def poll(self, interval):
        while True:
            self.logger.info("Polling...")
            try:
                await self.get_new_posts()
            except Exception as e:
                self.logger.error(f"Error polling: {e}")
            await asyncio.sleep(interval)

    async def get_new_posts(self):
        subreddit = await self.reddit.subreddit(self.subreddit_name)
        async for submission in subreddit.new(limit=5):
            if submission.id in self.post_cache:
                self.logger.info(f"Skipping {submission.id}")
                continue

            self.logger.info(f"Found new post: {submission.title}")

            share_result = await self.discord_handler.share_post(submission)
            self.post_cache[submission.id] = share_result

from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from asyncpraw.models import Submission


class DiscordHandler:
    def __init__(self, webhook: str) -> None:
        self.webhook = webhook

    async def share_post(self, submission: Submission) -> None:
        embed = DiscordEmbed(
            title=submission.title,
            description=f"{submission.selftext}",
            url=submission.url,
            color="FF0000",
            author={
                "name": f"New post on /r/{submission.subreddit.display_name}",
                "url": submission.url,
            },
        )

        nsfw = submission.over_18 or submission.spoiler
        if hasattr(submission, "preview") and not nsfw:
            high_res = submission.preview["images"][0]["source"]["url"]
            embed.set_image(url=high_res)

        embed.add_embed_field(name="Post Author", value=f"/u/{submission.author}")
        embed.add_embed_field(name="Content Warning", value="NSFW" if nsfw else "None")

        result = await AsyncDiscordWebhook(url=self.webhook, embeds=[embed]).execute()
        return result

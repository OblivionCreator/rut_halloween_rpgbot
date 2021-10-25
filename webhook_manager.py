if __name__ == '__main__':
    raise ImportError('This file is meant to be imported!')

import json
import discord
from discord import Webhook, AsyncWebhookAdapter
import aiohttp

c_webhooks = []

async def send(name, message, custom_img=None):

    with open('webhook_url') as file:
        url = file.readline()

    await sendWH(name=name, img=custom_img, message=message, url=url)

async def sendWH(name, img, message, url):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))

        embed = discord.Embed(title="**KRIS WHERE THE FUCK ARE WE?** approaches!",
                              description="<:susieSlap:890360533566492712>", color=0xff0000)
        embed.add_field(name="ENEMY HP", value="100/100", inline=True)
        embed.add_field(name="TEAM HP", value="100/100", inline=True)
        embed.add_field(name="ACTIONS", value="What do you do?", inline=False)
        embed.add_field(name="TRICK", value="* Commit Tax Fraud", inline=True)
        embed.add_field(name="TREAT", value="* Commit Tax Fraud But Nicely", inline=True)
        await webhook.send(message, username=name, avatar_url=img, embed=embed)
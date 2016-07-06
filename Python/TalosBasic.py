import discord
import logging

logging.basicConfig(level=logging.INFO)

client = discord.Client()

@client.event
async def on_ready():
	print(await client.get_server(199731669140373504))

client.run('MTk5OTY1NjEyNjkxMjkyMTYw.Cl2X_Q.SWyFAXsMeDG87vW6WERSLljDQIQ')
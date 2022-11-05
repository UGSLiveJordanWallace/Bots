## Written by Jordan Wallace
import discord
from discord.ext import commands
from translate import Translator

client = discord.Client()
intents = discord.Intents(messages=True, members = True, guilds=True)
client = commands.Bot(command_prefix = '!',intents = intents)

# Client Event runs on awake
@client.event
async def on_ready():
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for !tr"))

async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('What?! :rolling_eyes:.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have all the requirements stupid! :angry:")

# Client Commands
@client.command()
async def tr_sp(ctx, *, msg):
	translator = Translator(to_lang="es", email="jjbosscore@gmail.com")
	translation = translator.translate(msg)
	await ctx.send("Message Translated: " + translation)

@client.command()
async def tr_en(ctx, *, msg):
	translator = Translator(to_lang="en", from_lang="es", email="jjbosscore@gmail.com")
	translation = translator.translate(msg)
	await ctx.send("Message Translated: " + translation)

@client.command()
async def cu_tr(ctx, tr, fr, *, msg):
	translator = Translator(to_lang=f"{tr}", from_lang=f"{fr}")
	translation = translator.translate(msg)
	await ctx.send("Message Translated: " + translation)

@client.command()
async def tr_help(ctx):
	await ctx.send("AESO is a python powered translator that was built for high speed communications purposes.")
	await ctx.send("If you would like to get a more detailed description of each of the following commands, just type !tr_help_c <command>")
	await ctx.send("tr_sp")
	await ctx.send("tr_en")
	await ctx.send("cu_tr")

@client.command()
async def tr_help_c(ctx, *, command):
	if command == "tr_sp":
		await ctx.send("Translates English to Spanish")
		await ctx.send("!tr_sp <msg>")
	if command == "tr_en":
		await ctx.send("Translates Spanish to English")
		await ctx.send("!tr_en <msg>")
	if command == "cu_tr":
		await ctx.send("Translates Autodetected language to custom language")
		await ctx.send("!cu_tr <translation to> <translation from> <msg>")

client.run('OTMxNDA1ODQ2MDc0NzczNTA0.YeD9Sg.KhfKA2tTsSrhoPkW58idq3eccR4')
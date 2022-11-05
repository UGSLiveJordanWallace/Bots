import discord
import random as r
from discord.ext import commands

def startGame(ctx):
	global user
	global user_score
	global computer_choice
	global user_choice
	global computer_score
	global game_on

	user_score=0
	computer_score=0
	user_choice=0
	computer_choice=0

	author_split = str(ctx.author).split("#")
	user = author_split[0]

	game_on = True

async def won_game(ctx):
	global game_on

	game_on = False
	await ctx.send("> **Game Won!!**")

async def lost_game(ctx):
	global game_on

	game_on = False
	await ctx.send("> **Game Over!!**")

async def processInput(ctx):
	global user_choice
	global user
	global computer_choice
	global computer_score
	global user_score

	if user_choice == "User Choice Not Found!!":
		await ctx.send(f"> **Game Corrupted!!** *__{user_choice}__*")
		return

	if user_choice == computer_choice:
		await ctx.send("> **Computer Draw**")
		return	

	if user_choice == 0 and computer_choice == 1:
		computer_score += 1
	elif user_choice == 1 and computer_choice == 0:
		user_score += 1

	if user_choice == 0 and computer_choice == 2:
		user_score += 1
	elif user_choice == 2 and computer_choice == 0:
		computer_score += 1

	if user_choice == 1 and computer_choice == 2:
		computer_score += 1
	elif user_choice == 2 and computer_choice == 1:
		user_score += 1

	embed = discord.Embed(
		title="Game Results",
		color=discord.Color.green())

	if user_score == 3:
		await won_game(ctx)
		embed.add_field(name=f"{user}", value=" **Won!** :smiley:", inline=False)
		await ctx.send(embed=embed)
		return True

	if computer_score == 3:
		await lost_game(ctx)
		embed.add_field(name=f"BottleBop WON!!", value="**Lose!** :sweat_smile:", inline=False)
		await ctx.send(embed=embed)
		return True

def get_move(uc):
	global play_types
	for c in play_types:
		if uc == c:
			return play_types.index(c)

	return "User Choice Not Found!!"

user_score = 0
computer_score = 0
user_choice = ""
computer_choice = ""

play_types = ["rock", "paper", "scissors"]
game_on = False

client = discord.Client()
intents = discord.Intents(messages=True, members = True, guilds=True)
client = commands.Bot(command_prefix = "/", intents = intents)


@client.event
async def on_ready():
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you :smirk:"))

@client.command()
async def b_play(ctx):
	startGame(ctx)

	embed = discord.Embed(
		title="**Game Started**",
		description="If you would like to choose **rock** **paper** or **scissors**, ```/b_p <rock, paper, or scissors>```",
		color=discord.Color.green())

	await ctx.send(embed=embed)

@client.command()
async def b_p(ctx, choice):
	global user_choice
	global user_score
	global computer_choice
	global computer_score
	global play_types
	global game_on

	embed = discord.Embed(
		title="Game Run-Time",
		description="The Current Points, User Choice, And Copmuter Choice of the Game",
		color=discord.Color.green())

	if not game_on:
		embed.add_field(name = "**Game Not Started**", value="To Start A New Game `/b_help`", inline = False)
		await ctx.send(embed=embed)
		return

	user_choice = get_move(choice)
	computer_choice = r.randint(0, 2)

	input_process = await processInput(ctx)

	if input_process:
		return

	embed.add_field(name = f"{user}", value=f"You chose: **{play_types[user_choice]}** || Current Points: **{user_score}**", inline=False)
	embed.add_field(name = "BottleBop", value=f"Computer Chose: **{play_types[computer_choice]}** || Current Points: **{computer_score}**", inline=False)
	await ctx.send(embed=embed)

@client.command()
async def close(ctx):
	global game_on

	if game_on:
		game_on = False
		await ctx.send("> **Game Ended**")
	else:
		await ctx.send("> **Game Has Not Started**")
		return 
	
@client.command()
async def b_help(ctx):
	embed = discord.Embed(
		title="BottleBop Help List",
		description="BottleBop List of Commands:",
		color=discord.Color.green())

	
	embed.add_field(name="**Start Game Run-time**", value="`/b_play` starts a ***new game***", inline=False)
	embed.add_field(name="**Play Rock Paper Scissors**", value="`/b_p` allows the player to play ***rock paper scissors*** during ***game run-time***", inline=False)

	await ctx.send(embed=embed)

client.run('OTMxNzY3NDQzMzgxMTc4MzY4.YeJODQ.cOajIkCpyaSy_7Xv1fg7YTFuVUk')
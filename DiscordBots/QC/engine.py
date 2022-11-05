import discord
from discord import *
from discord.ext import commands
from discord.utils import get
from bs4 import BeautifulSoup
from decouple import config
import requests
import asyncio
import yt_dlp
import json
import re
import os
import glob


def query(s):
    qry = f"https://www.youtube.com/results?search_query={s}"

    response = requests.get(qry).text
    soup = BeautifulSoup(response, 'lxml')
    script = soup.find_all('script')[34]
    json_text = re.search('var ytInitialData = (.+)[,;]{1}', str(script)).group(1)
    json_data = json.loads(json_text)

    content_stream = (
        json_data
        ['contents']['twoColumnSearchResultsRenderer']['primaryContents']
        ['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    )

    for key in content_stream:
        if "videoRenderer" in key:
            video_id = key['videoRenderer']['videoId']
            video_thumbnail = key['videoRenderer']['thumbnail']['thumbnails'][0]['url']
            video_title = key['videoRenderer']['title']['runs'][0]['text']
            return {"link": f"https://www.youtube.com/watch?v={video_id}", "title": video_title, "img": video_thumbnail, "id": video_id}
            break


def handle_music(error):
    global queue
    global isQueue
    global queue_index

    if (isQueue == True):
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients)
        if (queue_index >= len(queue)):
            voice_client.stop()
            discord.AudioSource().cleanup()
            files = glob.glob("./music/*")
            for f in files:
                os.remove(f)
            return
        audio_source = discord.FFmpegPCMAudio(source=queue[queue_index]['file'])
        queue_index += 1
        voice_client.play(audio_source, after= lambda e : handle_music(e))   
    else:
        return


async def handle_play(voice, yt_opts, channel, user):
    global result
    global isQueue

    # Getting Song From Thy YOUTUBE
    await channel.send("> Getting Song From Youtube")
    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        os.chdir("./music")
        ydl.download([f'{result["link"]}'])
        os.chdir("../")

    # Renaming File 
    temp_title = ""
    for l in result['title']:
        temp_title = result['title'].replace("|", "_")

    if voice and voice.is_connected():
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients)
        if voice_client.is_playing():
            embed = discord.Embed(
                title=f"Queuing {result['title']}",
                description=f"From Link = {result['link']}",
                color=discord.Color.green()
                )
            embed.set_thumbnail(url=result['img'])

            queue.append({"title": f"{result['title']}", "img": f"{result['img']}", "link": f"{result['link']}", "file": f"./music/{temp_title} [{result['id']}].mp3"})
            isQueue = True

            return await channel.send(embed=embed)

    # DOING THE REST
    embed = discord.Embed(
        title=f"Playing Song {result['title']}",
        description=f"From Link = {result['link']}",
        color=discord.Color.red()
        )
    embed.set_thumbnail(url=result['img'])
    
    await channel.send("> Music Succefully loaded and Ready!")
    audio_source = discord.FFmpegPCMAudio(source=f"./music/{temp_title} [{result['id']}].mp3")

    if voice and voice.is_connected():
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients)
        if not voice_client.is_playing():
            voice_client.play(audio_source, after= lambda e : handle_music(e))
    else:
        await user.voice.channel.connect()
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients)
        if not voice_client.is_playing():
            voice_client.play(audio_source, after= lambda e : handle_music(e))
    return await channel.send(embed=embed)


client = commands.Bot(command_prefix="`")
result = {}
current_size = 0
queue = []
isQueue = False
queue_index = 0

@client.event
async def on_ready():
    await client.change_presence(activity = discord.Activity(type=discord.ActivityType.watching, name="for `h"))


@client.event
async def on_reaction_add(reaction, user):
    #Globals
    global result

    #Inits
    voice = get(client.voice_clients)

    members = 0

    yt_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    channel = reaction.message.channel
    if user.bot:
        return

    if reaction.emoji == "👍":
        vc_channel = client.get_channel(user.voice.channel.id)

        if not voice:
            folder = './music'
            for song in os.listdir(folder):
                file_path = os.path.join(folder, song)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason %s' % (file_path, e))

        # Getting Member Count
        member_ids = vc_channel.voice_states.keys()
        current_member_count = 0
        if voice and voice.is_connected():
            current_member_count = len(member_ids) - 1
        else:
            current_member_count = len(member_ids)

        #Regular Play
        return await handle_play(voice, yt_opts, channel, user)

        #Uncomment for Voting
        # # Less than 3 users will trigger single selection trigger
        # if current_member_count > 0 and current_member_count < 3:
        #     return await handle_play(voice, yt_opts, channel, user)

        # # If two or more users are in a voice channel, this will enable voting trigger
        # voting_minimum = int(current_member_count / 2) + 1

        # if reaction.count - 1 >= voting_minimum:
        #     return await handle_play(voice, yt_opts, channel, user)

    elif reaction.emoji == "👎":
        vc_channel = client.get_channel(user.voice.channel.id)

        member_ids = vc_channel.voice_states.keys()
        current_member_count = 0

        if voice and voice.is_connected():
            current_member_count = len(member_ids) - 1
        else:
            current_member_count = len(member_ids)

        voting_minimum = int(current_member_count / 2) + 1

        if current_member_count > 0 and current_member_count < 3:
            return await channel.send(f"> Sorry, enter `\`play` <song>` ***and be more specific!!***")

        if (reaction.count - 1) >= voting_minimum:
            return await channel.send("> Voting has canceled this song!!")


@client.command()
async def play(ctx, *, song):
    global result
    global current_size

    current_size = 0

    voice_state = ctx.author.voice
    if voice_state is None:
        return await ctx.send('> You need to be in a **voice channel** to use `play`')

    await ctx.send("> looking for song...")
    # Youtube Query
    result = query(song)

    voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients)
    if not voice_client or not voice_client.is_playing():
        folder = './music'
        for song in os.listdir(folder):
            file_path = os.path.join(folder, song)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason %s' % (file_path, e))

    embed=discord.Embed(
        title=result['title'],
        description="Is this the correct song you wanted to play?",
        color=discord.Color.red(),
        )
    embed.set_image(url=result['img'])

    emojis = ["👎", "👍"]

    message = await ctx.send(embed=embed)

    for emoji in emojis:
        await message.add_reaction(emoji)


@client.command()
async def h(ctx):
    embed = discord.Embed(
        title="Quad Core Help",
        description="List of commands needed to use the bot",
        color=discord.Color.red())
    embed.add_field(name="**Select Preview Song**", value="To Select a song, react with the emoji :thumbsup:", inline=False)
    embed.add_field(name="**Play Music**", value="To play music, enter ``play`", inline=False)
    embed.add_field(name="**Stop Music**", value="To stop music, enter ``stop`", inline=False)
    embed.add_field(name="**Disconnect**", value="To disconnect Quad Core from the channel, enter ``disconnect`", inline=False)
    await ctx.send(embed=embed)


@client.command()
async def stop(ctx):
    global result
    global current_size
    global isQueue

    current_size = 0

    voice_clients: discord.VoiceClient() = get(ctx.bot.voice_clients, guild=ctx.guild)

    # Check if Bot is in vc
    if voice_clients is None:
        return await ctx.send("Voice not configured!")

    # Check if user is on the vc
    voice_state = ctx.author.voice
    if voice_state is None:
        return await ctx.send('> You need to be in a **voice channel** to use `play`')
    
    if voice_clients:
        # Stop Music
        voice_clients.stop()
        discord.AudioSource().cleanup()

        embed = discord.Embed(
            title=f"Discord Bot Stopped: {result['title']}",
            description="Brodie, Discord bot has been Closed Fr!!",
            color=discord.Color.red())

        embed.set_thumbnail(url=result['img'])

        isQueue = False
        return await ctx.send(embed=embed)


@client.command()
async def disconnect(ctx):
    global result
    global current_size
    global isQueue

    current_size = 0

    voice_clients: discord.VoiceClient() = get(ctx.bot.voice_clients, guild=ctx.guild)

    # Check if Bot is in vc
    if voice_clients is None:
        return await ctx.send("Voice not configured!")

    # Check if user is on the vc
    voice_state = ctx.author.voice
    if voice_state is None:
        return await ctx.send('> You need to be in a **voice channel** to use `play`')
    
    if voice_clients:
        isQueue = False

        # Stop Music
        voice_clients.stop()
        discord.AudioSource().cleanup()
        await voice_clients.disconnect()

        embed = discord.Embed(
            title=f"Discord Bot Disconnected: {result['title']}",
            description="Ayo! Quad Core bot has left the chat FrFr!!",
            color=discord.Color.red())

        embed.set_thumbnail(url=result['img'])
        return await ctx.send(embed=embed)

client.run("OTMzODk0OTE3MzM4NTcwNzUy.YeoLaw.T0EG_dP2KMWaci27TzO4VeIrxZY")
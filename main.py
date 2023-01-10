import os
import discord
from discord.ext import commands
from youtubeHandler import search
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
TOKEN = os.environ.get("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

vc = None
playChannelInfo = {}
soung_queue = []
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

def play_next():
	if len(soung_queue) >= 1:
		source = soung_queue.pop(0)[1]
		vc.play(discord.FFmpegPCMAudio(source, **FFMPEG_OPTS), after = lambda e: play_next())

@bot.command()
async def play(ctx, url):
	global vc
	vChannel = ctx.message.author.voice
	channel = None
	if vChannel:
		channel = vChannel.channel
		if not ctx.voice_client:
			vc = await channel.connect()
		try:
			song_info, source = search(url)
			embed = discord.Embed()
			if not vc.is_playing():
				vc.play(discord.FFmpegPCMAudio(source, **FFMPEG_OPTS), after = lambda e: play_next()) 
				embed.title='Сейчас играет:'
			else:
				soung_queue.append([song_info['title'],source, url])
				embed.title='Добавлено в очередь: '
			embed.color=0xbd91e4
			embed.add_field(
				name=song_info['title'],
				value=url,
				inline=False
			)
		except:
			await ctx.send('Произошла ошибка, попробуйте еще раз!')
		await ctx.send(embed=embed)
	else: await ctx.send(f'{ctx.message.author.mention}, зайдите в гс канал!')

@bot.command()
async def skip(ctx):
	if ctx.voice_client:
		if len(soung_queue) >= 1:
			next_song = soung_queue[0]
			embed = discord.Embed(
				title='Сейчас играет:',
				color=0xbd91e4
			)
			embed.add_field(
				name=next_song[0],
				value=next_song[2],
				inline=False
			)
			await ctx.send(embed=embed)	
		else: await ctx.send('Это последняя песня, дальше ничего играть не будет')
		vc.stop()
	else:
		await ctx.send(f'{ctx.message.author.mention}, я не подключен ни к одному из каналов!')

@bot.command()
async def leave(ctx):
	if ctx.voice_client:
		await ctx.guild.voice_client.disconnect()
		await ctx.send('Я вышел с канала')
	else:
		await ctx.send(f'{ctx.message.author.mention}, я не подключен ни к одному из каналов!')

@bot.command()
async def pause(ctx):
	if ctx.voice_client:
		if ctx.voice_client.is_playing():
			ctx.voice_client.pause()
			await ctx.send('Иду сидеть на паузе')
		else: await ctx.send('Я итак на паузе!')
	else:
		await ctx.send(f'{ctx.message.author.mention}, я не подключен ни к одному из каналов!')

@bot.command()
async def resume(ctx):
	if ctx.voice_client:
		if ctx.voice_client.is_paused():
			ctx.voice_client.resume()
			await ctx.send('Продолжаю петь')
		else: await ctx.send('Я итак пою!')
	else:
		await ctx.send(f'{ctx.message.author.mention}, я не подключен ни к одному из каналов!')

bot.run(TOKEN)


import os 
import discord
from discord import app_commands
from discord.ext import commands
from YoutubeHandler import search
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
TOKEN = os.environ.get("BOT_TOKEN")

playChannelInfo = {}
soung_queue = []
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
	print('Im has been started')
	try:
		synced = await bot.tree.sync()
		print(f'Synced {len(synced)} command(s)')
	except Exception as e:
		print(e)

def calibration_duration(sec):
	minutes = str(sec//60)
	seconds = str(sec%60)
	if int(seconds) >= 0 and int(seconds) < 10:
		seconds = '0'+seconds
	return f'{minutes}:{seconds}'

def play_next(vc):
	if len(soung_queue) >= 1:
		source = soung_queue.pop(0)[1]
		vc.play(discord.FFmpegPCMAudio(source, **FFMPEG_OPTS), after = lambda e: play_next(vc))

@bot.tree.command(name='play', description='Играет/добавляет в очередь трек')
@app_commands.describe(link='Ссылка на трек')
async def play(interaction: discord.Interaction, link:str):
	channel = interaction.user.voice
	if channel:
		await interaction.response.defer()
		if not interaction.client.voice_clients:
			await channel.channel.connect()
		vc = interaction.guild.voice_client
		try:
			try:
				song_info, source = search(link)
			except:
				await interaction.followup.send('Ошибка загруски, попробуйте еще раз!')
				return
			embed = discord.Embed()
			if not vc.is_playing():
				vc.play(discord.FFmpegPCMAudio(source, **FFMPEG_OPTS), after = lambda e: play_next(vc)) 
				embed.title='Сейчас играет:'
			else:
				soung_queue.append([song_info['title'],source, link, song_info['duration']])
				embed.title='Добавлено в очередь: '
			embed.color=0xbd91e4
			embed.add_field(
				name=song_info['title'],
				value=link+"\n\n"+f"**Длительность**: (`{calibration_duration(song_info['duration'])}`)",
				inline=False,
			)
		except: 
			await interaction.followup.send('Произошла ошибка, попробуйте еще раз!')
			return
		await interaction.followup.send(embed=embed)
	else: await interaction.response.send_message(f'{interaction.user.mention}, для начала зайдите в голосовой канал!', ephemeral=True)


@bot.tree.command(name='skip', description='Пропускает текущий трек')
async def skip(interaction: discord.Interaction):
	vc = interaction.guild.voice_client
	if vc:
		if len(soung_queue) >= 1:
			next_song = soung_queue[0]
			embed = discord.Embed(
				title='Сейчас играет:',
				color=0xbd91e4
			)
			embed.add_field(
				name=next_song[0],
				value=next_song[2]+"\n\n"+f"**Длительность:** (`{calibration_duration(next_song[3])}`)",
				inline=False
			)
			embed.add_field(
				value=calibration_duration(next_song[3])
			)
			await interaction.response.send_message(embed=embed)	
		else: await interaction.response.send_message('Это была последняя песня, дальше ничего играть не будет')
		vc.stop()
	else:
		await interaction.response.send_message(f'{interaction.user.mention}, я не подключен ни к одному из каналов!', ephemeral=True)

@bot.tree.command(name='leave', description='Выход из голосового канала')
async def leave(interaction: discord.Interaction):
	if interaction.client.voice_clients:
		await interaction.guild.voice_client.disconnect
		await interaction.response.send_message('Я вышел с канала')
	else:
		await interaction.response.send_message(f'{interaction.user.mention}, я не подключен ни к одному из каналов!', ephemeral=True)

@bot.tree.command(name='pause', description='Остановить текущий трек')
async def pause(interaction: discord.Interaction):
	vc = interaction.guild.voice_client
	if vc:
		if vc.is_playing():
			vc.pause()
			await interaction.response.send_message('Иду сидеть на паузе')
		else: await interaction.response.send_message('Я итак на паузе!')
	else:
		await interaction.response.send_message(f'{interaction.user.mention}, я не подключен ни к одному из каналов!', ephemeral=True)

@bot.tree.command(name='resume', description='Продолжить проигрывание текущего трека')
async def resume(interaction: discord.Interaction):
	vc = interaction.guild.voice_client
	if vc:
		if vc.is_paused():
			vc.resume()
			await interaction.response.send_message('Продолжаю петь')
		else: await interaction.response.send_message('Я итак пою!')
	else:
		await interaction.response.send_message(f'{interaction.user.mention}, я не подключен ни к одному из каналов!', ephemeral=True)

bot.run(TOKEN)




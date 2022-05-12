import discord
from discord.ext import commands
import asyncio
import yt_dlp
from sys_info import *
from youtubesearchpython import VideosSearch as _search
import json

def stripes(n):
  stripe = ""
  for i in range(0,n):
    stripe += "_"
  return stripe

def format_selector(ctx):
  # formats are already sorted worst to best
  formats = ctx.get('formats')[::-1]

  # acodec='none' means there is no audio
  best_video = next(f for f in formats
    if f['vcodec'] != 'none' and f['acodec'] == 'none')

  # find compatible audio extension
  audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
  # vcodec='none' means there is no video
  best_audio = next(f for f in formats if (
    f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

  yield {
    # These are the minimum required fields for a merged format
    'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
    'ext': best_video['ext'],
    'requested_formats': [best_video, best_audio],
    # Must be + seperated list of protocols
    'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
  }

def play_next(self, ctx, voice_client, source, playlist):
    if len(source) > 1:
      voice_client.stop()
      del self._queue[0]
      del self._queue2[0]
      voice_client.play(self._queue[0], after = lambda e: play_next(self, ctx, voice_client, source, playlist))
    else:
      print("Done")

class music(commands.Cog):
  
  def __init__(self, client, bot=None):
    self.client = client
    self._queue = []
    self._queue2 = []

  @commands.command()
  # Command Play
  async def p(self,ctx, *, inp):
    # Check if author is in a Voice Channel
    if ctx.author.voice is None:
      await ctx.send("**Terjadi kesalahan, anda tidak berada di dalam voice channel** 🚫")

    # Gets voice channel
    voice_channel = ctx.author.voice.channel

    # Move to author's Voice channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
    
    voice_client = ctx.voice_client

    try:
      # Searches youtube for input
      video_search = _search(inp, limit=1)
      search_result = video_search.result()
      # URL
      url2 = search_result['result'][0]['link']
      # Embed
      judul = search_result['result'][0]['title']
      thumbnail = search_result['result'][0]['thumbnails'][0]['url']
      username = search_result['result'][0]['channel']['name']
      pfp = search_result['result'][0]['channel']['thumbnails'][0]['url']
      
      embed = discord.Embed(title=judul, url=url2, description="Request dari {}".format(ctx.author.display_name), color=0xebd234)
      embed.set_author(name=username, icon_url=pfp)
      embed.set_image(url=thumbnail)
      await ctx.send(embed=embed)

      # Download
      FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 3', 'options': '-vn'}

      YDL_OPTIONS = {'format': format_selector }

      with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url2, download=False)
        info = ydl.sanitize_info(info)
        #urls = [format['url'] for format in info['formats']][0] -> youtube-dl
        for fmt in info['formats']:
          if fmt['format_id'] == '251':
            urls = fmt['url']
        # for fmt in info['formats']:
        #   if fmt['acodec'] != 'none':
        #     urls = fmt['url']
        source = await discord.FFmpegOpusAudio.from_probe(urls ,**FFMPEG_OPTIONS)
        self._queue.append(source)
        self._queue2.append(search_result)                  
        if not voice_client.is_playing():
          voice_client.play(self._queue[0], after = lambda e: play_next(self, ctx, voice_client, self._queue, self._queue2))
          voice_client.is_playing()
        else:
          await ctx.send("**Ditambahkan ke dalam queue!** 📝")
        
    except:
      await ctx.send("**Terjadi kesalahan, mohon request kembali.** 🚫")

  @commands.command()
  async def pause(self, ctx):
    ctx.voice_client.pause()
    await ctx.send("**Pause** ⏸️")

  @commands.command()
  async def resume(self, ctx):
    ctx.voice_client.resume()
    await ctx.send("**Resume** ▶️")
    
  @commands.command()
  async def stop(self,ctx):
    self._queue = []
    ctx.voice_client.stop()
    await ctx.send("**Menghentikan lagu** ⏹️")

  # @commands.command()
  # async def clear(self,ctx):
  #   self.queue = [None]
  #   self.count = 0
  #   await ctx.send("**Membersihkan queue** 📝")

  @commands.command()
  async def skip(self, ctx):
    ctx.voice_client.stop()
    await ctx.send("**Memutar lagu selanjutnya!** ⏯️")
    
  # @commands.command()
  # async def loop(self, ctx):
  #   if self.loop_is == False:
  #     self.loop_is = True
  #     await ctx.send("**Loop is now enabled!**")
  #   else:
  #     self.loop_is = False
  #     await ctx.send("**Loop is now disabled!**")


  @commands.command()
  async def playlist(self, ctx):
    embed=discord.Embed(title="Current Playlist", description="Playlist yang sedang dimainkan.", color=0xebd234)
    
    # iterates through playlist
    for position, entry in enumerate(self._queue2, 1):
      title = entry['result'][0]['title']
      link = entry['result'][0]['link']
      #pl_entry = str(position + '. ' +  title + ' ' + link)
      embed.add_field(name=f"Position - {position}", value=f"[{title}](link)", inline=False)
      
    await ctx.send(embed=embed)
  
  @commands.command()
  async def leave(self,ctx):
    try:
      ctx.voice_client.stop()
      await ctx.voice_client.disconnect()
      await ctx.send("**Dadah** 👋🏻")
    except:
      await ctx.send("**Terjadi kesalahan, bot tidak berada di dalam voice channel** 🚫")

  @commands.command()
  async def stats(self, ctx):
    embed=discord.Embed(title="Status Bot", description="Monitoring resource, versi API, dll.", color=0xebd234)
    embed.add_field(name=stripes(50), value='\u200b', inline=False)
    embed.add_field(name="CPU", value=f"```{cpu_model}```", inline=False)
    embed.add_field(name=stripes(50), value='\u200b', inline=False)
    embed.add_field(name="Speed", value=cpu_speed[0:4] + " GHz", inline=True)
    embed.add_field(name="Cores", value=thread_count, inline=True)
    embed.add_field(name="CPU Usage", value=cpu_usage, inline=True)
    embed.add_field(name="Architecture", value=arch, inline=True)
    embed.add_field(name="RAM", value=mem_total, inline=True)
    embed.add_field(name="RAM Usage", value=mem_usage, inline=True)
    embed.add_field(name=stripes(50), value='\u200b', inline=False)
    embed.add_field(name="Discord.py", value=discord_py, inline=True)
    embed.add_field(name="Python ", value=ver, inline=True)
    embed.add_field(name="OS", value=os, inline=True)
    await ctx.send(embed=embed)
    
  @commands.command()
  async def help(self,ctx):
    embed=discord.Embed(title="Help Page", description="Menjelaskan penggunaan command pada bot.", color=0xebd234)
    embed.add_field(name="Prefix Bot", value="```> ```", inline=False)
    embed.add_field(name='Search', value="```>p [YT]```", inline=True)
    embed.add_field(name='Pause', value="```>pause```", inline=True)    
    embed.add_field(name='Resume', value="```>resume```", inline=True)
    embed.add_field(name='Stop', value="```>stop```", inline=True)
    embed.add_field(name='Skip', value="```>skip```", inline=True)
    embed.add_field(name='Leave', value="```>leave```", inline=True)         
    embed.add_field(name='Help', value="```>help```", inline=True)
    embed.add_field(name='Stats', value="```>stats```", inline=True)  
    embed.add_field(name='Wish Simulator', value="```>wish [Character]```", inline=False)
    embed.add_field(name='Wish Inventory', value="```>wish inventory```", inline=False)
    embed.add_field(name='Genshin Wiki', value="```>g [Weapon Name]```", inline=False)  
    await ctx.send(embed=embed)

  @commands.Cog.listener()
  async def on_voice_state_update(self, member, before, after):
    try:
      voice = after.channel.guild.voice_client
      while voice.is_playing(): 
        await asyncio.sleep(1) 
      else:
        await asyncio.sleep(300) 
        while voice.is_playing(): 
          break
        else:
          await voice.disconnect()
    except Exception:
      pass

def setup(client):
  client.add_cog(music(client))
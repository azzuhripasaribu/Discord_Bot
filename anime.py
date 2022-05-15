import discord
import datetime, pytz, re
from discord.ext import commands
from AnilistPython import Anilist
from encrypt import load, save

# Misc
cleanr = re.compile('<.*?>') 
tz = pytz.timezone("Asia/Jakarta")

# Truncate a long string
def truncate(data, length, suffix='..'):
  return (' '.join(data[:length+1].split(' ')[0:-1]) + suffix) if len(data) > length else data

# Html tags cleaner
def clean_tags(data):
  return re.sub(cleanr, '', data)

# Dictionary cleaner
def clean_dict(dict):
  return { k: ('-' if v == None or v == "null" else v) for k, v in dict.items() }

# Date format checker
def check_date(date, format):
  try:
    datetime.datetime.strptime(date, format)
    return date
  except ValueError:
    return "-"
  

class anime (commands.Cog):
  def __init__(self, client, anilist):
    self.client = client
    self.anilist = anilist
    self.userDict = {}
    self.yellow = 0xebd234
  
  @commands.command(name="test")
  async def testCommand(self, ctx, *, inp):
    # Send Messages
    await ctx.send(f"{inp} dari cog anime")
    
  @commands.command(name="search")
  @commands.cooldown(12,300,commands.BucketType.user)
  async def animeSearch(self, ctx, *, inp):
    # First Embed
    embed_search = discord.Embed(
      title=f"Searching \"{inp}\", please wait!", 
      color=self.yellow
    )
    embed_search.set_author(name="Anime List")
    message = await ctx.send(ctx.author.mention, embed=embed_search)
    
    try:
      # Searching
      aniDict = clean_dict(self.anilist.get_anime(inp))
      
      # Processing Information
      name_romaji = aniDict['name_romaji']
      name_english = aniDict['name_english']
      if name_english != "-":
        name = name_english
      else:
        name = name_romaji
      desc = truncate(clean_tags(aniDict['desc']), 125)
      score = aniDict['average_score']
      score = round(int(score)/10, 2) if score != "-" else "-"
      thumb = aniDict['cover_image']
      banner = aniDict['banner_image']
      eps = aniDict['airing_episodes']
      status = aniDict['airing_status'].lower().capitalize().replace("_", " ")
      genre = aniDict['genres']
      next_ep = aniDict['next_airing_ep']
      date = check_date(aniDict['starting_time'], '%m/%d/%Y')
      season = aniDict['season']
      type = ""
      if season in [None, "null", "-",] or date in [None, "null", "-"]:
        type = "-"
      elif date in [None, "null", "-"]:
        type = f"{season.lower().capitalize()}"
      else:
        type = f"{season.lower().capitalize()} {date.split('/')[-1]}"
  
      # Editted Embed
      embed = discord.Embed(
        title=name, 
        description=desc, 
        color=self.yellow
      )
      embed.set_author(name="Anime List")
      if thumb != "-":
        embed.set_thumbnail(url=thumb)
      if banner != "-":
        embed.set_image(url=banner)
      embed.add_field(name="Season", value=type, inline=True)
      embed.add_field(name="Score", value=f"{score}/10", inline=True)
      embed.add_field(name="Episodes", value=eps, inline=True)
      embed.add_field(name="Genre", value=', '.join(genre), inline=False)
      embed.add_field(name="Status", value=status, inline=True)
      if next_ep != "-":
        embed.add_field(
          name="Next Episode", 
          value=f"Episode {next_ep['episode']}\n{datetime.datetime.fromtimestamp(int(next_ep['airingAt']), tz = tz).strftime('%d/%m/%Y - %I:%M %p')}",
        inline=False
        )
      await message.edit(embed=embed)
      
    # Error Exceptions
    except Exception as e:
      # Editted Embed
      embed_fail = discord.Embed(
        title=f"An Error Occured, {e}.", 
        color=self.yellow
      )
      embed_fail.set_author(name="Anime List")
      await message.edit(embed=embed_fail)
      print(e)
      

# Cog Setup
def setup(client):
  client.add_cog(anime(client, Anilist()))

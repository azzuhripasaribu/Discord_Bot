from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
import discord
from discord.ext import commands
import time 
import os
import lxml
import cchardet
import asyncio
from gacha import gacha
from inventory import inv
import json
from encrypt import load, save

def stripes(n):
  stripe = ""
  for i in range(0,n):
    stripe += "_"
  return stripe

class genshin_fun(commands.Cog):
  def __init__(self, client):
    self.client = client

  #Gets genshin page
  @commands.command()
  async def g(self, ctx, *, inp):
    img = "https://cdn.discordapp.com/attachments/902414074720178216/905114368574894100/footer.png"
    start_time = time.time()
    search = inp.replace(" ", "+")
    
    try:
      # embeds waiting message
      embed = discord.Embed(title=f"Searching \"{inp}\", please wait!", color=0xebd234)
      embed.set_author(name="Genshin Wiki")
      embed.set_image(url=img)
      message = await ctx.send(embed=embed)

      # creates session
      html = f"https://genshin-impact.fandom.com/wiki/Special:Search?query={search}"
      session = HTMLSession()
      response = session.get(html, headers={"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
      
      #parse HTML
      html_text = bs(response.content, "lxml")
      data = html_text.find('h1', class_="unified-search__result__header")
      url = data.find('a').get("href")
      #print("--- %s seconds ---" % (time.time() - start_time))

      # Creates second session
      response = session.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})

      # Parse HTML and build discord response
      html_text = bs(response.content, "lxml")
      title = html_text.find('h2', class_="pi-item pi-item-spacing pi-title pi-secondary-background").text
      desc = html_text.find('div', class_="standard-border").find('i').text
      thumb = html_text.find('figure', class_="pi-item pi-image").find('a').get("href")
      types = html_text.find('div', attrs={'data-source' : "type"}).find('a').get("title")
      rarity = html_text.find('div', attrs={'data-source' : "rarity"}).find('img').get("title")[0:1]
      rarities = ["★", "★★", "★★★", "★★★★", "★★★★★"]
      rarity = rarities[int(rarity)-1]
      obtain = html_text.find('div', attrs={'data-source' : "obtain"}).find('div', class_="pi-data-value pi-font").find('a').text
      stats = html_text.find_all('div', class_="pi-smart-data-value pi-data-value pi-font pi-item-spacing pi-border-color")
      stats_arr = []
      for x in range(0,3):
        try:
          stats_arr.append(stats[x].text)
        except:
          stats_arr.append("None")
      title_passive = html_text.find('th', class_="pi-horizontal-group-item pi-data-label pi-secondary-font pi-border-color pi-item-spacing").text
      passive = html_text.find('td', class_="pi-horizontal-group-item pi-data-value pi-font pi-border-color pi-item-spacing").text
      if len(passive) > 200:
        passive = passive[0:200] + "..."
      #print("--- %s seconds ---" % (time.time() - start_time))

      # Build response embed
      embed1 = discord.Embed(title=title, url=url, description=desc , color=0xebd234)
      embed1.set_author(name="Genshin Wiki")
      embed1.set_thumbnail(url=thumb)
      embed1.set_image(url=img)
      embed1.add_field(name="Weapon Type", value=types, inline=True)
      embed1.add_field(name="Rarity", value=rarity, inline=True)
      embed1.add_field(name="How to Obtain", value=obtain, inline=True)
      embed1.add_field(name="Base ATK\n(Lv. 1 - 90)", value=stats_arr[0], inline=True)
      embed1.add_field(name="2nd Stat Type", value=stats_arr[1], inline=True)
      embed1.add_field(name="2nd Stat\n(Lv. 1 - 90)", value=stats_arr[2], inline=True)
      embed1.add_field(name=title_passive, value=passive, inline=False)
      
      #sends response      
      await message.edit(embed=embed1)
    
    except Exception as err:
      print(err)
      await ctx.send("**Item does not exists! Try again.**")  
    print("--- %s seconds ---" % (time.time() - start_time))

  @commands.command()
  @commands.cooldown(15,90,commands.BucketType.user)
  async def wish(self, ctx, *, inp):
    limited_char =  [character.split('.')[0] for character in os.listdir('img/card_5s/') if os.path.isfile(os.path.join('img/card_5s/', character))]
    inp.lower()
    limited_char.sort()
    thumb = 'https://cdn.discordapp.com/attachments/880704270838669325/907214236294475876/256.png'
    path = ["img/mug_shot/5s", "img/mug_shot/4s"]
    char_5s = [filename.split('.')[0] for filename in os.listdir(path[0])]
    char_4s = [filename.split('.')[0] for filename in os.listdir(path[1])]
    root = load('db.json')
    db = root['user'] 
    uid = str(ctx.author.id)
    if uid not in db:
      db[uid] = {
        '5s': {},
        '4s': {},
      }
    if inp == 'list':
      embed2 = discord.Embed(title="Character List", description=', '.join(limited_char), color=0xebd234)
      embed2.set_author(name="Genshin Wish Simulator")
      embed2.set_thumbnail(url=thumb)
      await ctx.send(ctx.author.mention, embed=embed2)
    elif inp == 'inventory':
      embed2 = discord.Embed(title=f"Genshin Wish Simulator", color=0xebd234)
      try:
        inv(db[uid])
        embed2.add_field(name=f"★ Wish Inventory ★", value=f"{ctx.author.display_name}'s Inventory", inline=False)
        embed2.add_field(name=stripes(50), value='\u200b', inline=False)
        embed2.set_thumbnail(url=thumb)
        file = discord.File("invtmp.png", filename="image.png")
        embed2.set_image(url="attachment://image.png")
        await ctx.send(ctx.author.mention, file=file, embed=embed2)
      except ValueError as err:
        embed2.add_field(name=f"★ Wish Inventory ★", value=f"<!>{ctx.author.display_name}'s {err}<!>", inline=False)
        embed2.add_field(name=stripes(50), value='\u200b', inline=False)
        embed2.set_thumbnail(url=thumb)
        await ctx.send(ctx.author.mention, embed=embed2)
    elif inp in limited_char:
      pull = gacha(inp)
      
      for item in pull:
        item = item.replace('\\', '/').split('/')[-1].split('.')[0]
        if item in char_5s:
          if item not in db[uid]['5s']:
            db[uid]['5s'][item] = 0
          db[uid]['5s'][item] += 1
        elif item in char_4s:
          if item not in db[uid]['4s']:
            db[uid]['4s'][item] = 0
          db[uid]['4s'][item] += 1

      embed2 = discord.Embed(title=f"Genshin Wish Simulator", color=0xebd234)
      embed2.add_field(name=f"★ {inp.capitalize()} ★", value="Wishing 10 Pull", inline=False)
      embed2.add_field(name=stripes(50), value='\u200b', inline=False)
      embed2.set_thumbnail(url=thumb)
      file = discord.File("test.png", filename="image.png")
      embed2.set_image(url="attachment://image.png")
      await ctx.send(ctx.author.mention, file=file, embed=embed2)
    else:
      embed2 = discord.Embed(title="Character not found!", description="Please check for the full character list by doing `[>wish list]`, you could also check your inventory by doing `[>wish inventory]`", color=0xebd234)
      embed2.set_author(name="Genshin Wish Simulator")
      embed2.set_thumbnail(url=thumb)
      await ctx.send(ctx.author.mention, embed=embed2)

    save('db.json', root)
    
def setup(client):
  client.add_cog(genshin_fun(client))
  
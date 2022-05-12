import os
import discord
from discord.ext import commands, tasks
import music, genshin_fun, genshin_stats
import keep_alive
from itertools import cycle

cogs = [music, genshin_fun, genshin_stats]
client = commands.Bot(
  command_prefix='>',
  intents=discord.Intents.all(),
  help_command=None
)
stat = cycle([
  'Python',
  'Music Player',
  'Wish Simulator',
  'Wish Inventory',
  'Genshin Wiki',
  'Genshin Stats'
])

@tasks.loop(seconds=10)
async def change_status():
  await client.change_presence(activity=discord.Game(next(stat)), status=discord.Status.idle)

@client.event
async def on_ready():
  change_status.start()
  print("Your bot is ready")
  for i in range(len(cogs)):
    cogs[i].setup(client)

@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    msg = '**Still on cooldown, please try again in {:.2f}s**'.format(error.retry_after)
    await ctx.send(msg)
  else:
    print(error)

repl_link = 'https://DiscordBot.fadilhisyam.repl.co'
keep_alive.awake(repl_link, True)
my_secret = os.environ['TOKEN']
try:
  client.run(my_secret)
except:
  os.system("kill 1")

import os
import discord
import psycopg2
import asyncio
from discord.ext import commands
from discord_components import DiscordComponents

from botCommands.voteCommand import VoteCommand
from botCommands.mailCommand import MailCommand
from botCommands.warnCommand import WarnCommand
from botCommands.mailHandler import isMailInteraction, handleMailInteraction
from botCommands.voteHandler import isVoteInteraction, handleVoteInteraction
from botCommands.infoHandler import isInfoInteraction, handleInfoInteraction

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)
DiscordComponents(client)

votingLock = asyncio.Lock()

@client.command(name='vote')
async def vote(ctx, *args):
  print(f'vote Command invoked by author={ctx.author.display_name} me={ctx.me.display_name}')
  voteCtx = VoteCommand(client, ctx, args)
  await voteCtx.execute()

@client.command(name='mail')
async def mail(ctx, *, arg):
  print(f'mail Command invoked by author={ctx.author.display_name} me={ctx.me.display_name}')
  mailCmd = MailCommand(client, ctx, arg)
  await mailCmd.execute()

@client.command(name='warn')
async def warn(ctx, target):
  print(f'vote Command invoked by author={ctx.author.display_name} me={ctx.me.display_name}')
  voteCtx = WarnCommand(client, ctx, target)
  await voteCtx.execute()

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_button_click(interaction):
  print(f'on_button_click - Receiving interaction for {interaction.custom_id}')
  async with votingLock:
    if isVoteInteraction(client, interaction):
      await handleVoteInteraction(client, interaction)
      return
    elif isInfoInteraction(client, interaction):
      await handleInfoInteraction(client, interaction)
      return
    elif isMailInteraction(client, interaction):
      await handleMailInteraction(client, interaction)
      return

  #not handled, send error message
  await interaction.send(f'No handler for the button {interaction.custom_id} was found!')

client.run(os.environ['TOKEN'])

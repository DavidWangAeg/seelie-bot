import os
import discord
from discord_components import Button, ActionRow
from database.application import createNewApplication, getActiveApplication
from .voteConstants import VoteButtonId, VoteType, InfoType, InfoButtonId, HelpCategoryMap

VOTE_ROLE_ID = int(os.environ['VOTE_COMMAND_ROLE_ID'])

voteButtons = ActionRow(
  [
    Button(label="🌟Vouch", custom_id=VoteButtonId[VoteType.Vouch], style=3),
    Button(label="✅Yes", custom_id=VoteButtonId[VoteType.Yes], style=1),
    Button(label="❌No", custom_id=VoteButtonId[VoteType.No], style=2),
    Button(label="☠️Ban", custom_id=VoteButtonId[VoteType.Ban], style=4)
  ]
)

infoButtons = ActionRow(
  [
    Button(label="🗳️Toggle Votes", custom_id=InfoButtonId[InfoType.Toggle], style=1),
    Button(label="🔒Close Vote", custom_id=InfoButtonId[InfoType.Close], style=4),
    Button(label="❌Quit", custom_id=InfoButtonId[InfoType.Quit], style=2),
  ]
)

class VoteCommand:
  def __init__(self, client, context, args):
    self.client = client
    self.context = context
    self.args = args
  
  async def execute(self):
    if not any(role.id == VOTE_ROLE_ID for role in self.context.author.roles):
      embed = discord.Embed(title='Error', description='You do not have permission to use that command!', colour=discord.Color.red())
      await self.context.send(embed=embed)
      return

    if len(self.args) == 0:
      embed = discord.Embed(title='Error', description='`!vote` requires at least one input!', colour=discord.Color.red())
      await self.context.send(embed=embed)
      return

    match self.args[0]:
      case 'new' | 'create':
        await self.__createNewVote()
      case 'find' | 'info' | 'show':
        await self.__findVote()

  async def __createNewVote(self):
    # Fetch user
    discordId = int(self.args[1])
    user = await self.__tryGetUser(discordId)
    if user is None:
      embed = discord.Embed(title='Error', description=f'User <@{discordId}> not found.', colour=discord.Color.red())
      await self.context.send(embed=embed)
      return

    # Check for an existing active application
    existingApp = getActiveApplication(discordId)
    if existingApp is not None:
      embed = discord.Embed(title='Error', description=f'There is already an active vote for <@{discordId}>!', colour=discord.Color.red())
      await self.context.send(embed=embed)
      return

    # Fetch channel
    channelId = self.args[2]

    # Extract channelId if needed from full format
    if channelId.startswith('<#'):
      end = len(channelId) - 1
      channelId = channelId[2:end]
    
    channel = None
    try:
      channel = self.client.get_channel(int(channelId))
    except Exception as e:
      print(e)
      
    if channel is None:
      embed = discord.Embed(title='Error', description=f'Channel <#{channelId}> not found.', colour=discord.Color.red())
      await self.context.send(embed=embed)
      return
    
    tag = user.name + '#' + user.discriminator
    application = createNewApplication(discordId, self.args[3], tag, HelpCategoryMap[self.args[4]], self.args[5])
    application.voteList = [[], [], [], []]

    # Build the embed
    embed = application.buildVoteEmbed()
    embed.set_thumbnail(url=user.avatar_url)
    voteMsg = await channel.send(embed=embed,components=voteButtons)
    
    application.messageid = voteMsg.id
    application.channelid = voteMsg.channel.id
    application.save()

    successEmbed = discord.Embed(title='Success!', description=f'Created vote for user <@{discordId}> in <#{channelId}>.\n[>> Jump to message <<]({voteMsg.jump_url})', colour=discord.Color.green())
    await self.context.send(embed=successEmbed)

  async def __findVote(self):
    # Find user
    discordId = self.args[1]
    user = await self.__tryGetUser(discordId)
    if user is None:
      embed = discord.Embed(title='Error', description=f'User <@{discordId}> not found.', colour=discord.Color.red())
      await self.context.send(embed=embed)
      return

    # Find active vote
    app = getActiveApplication(discordId)
    if app is None:
      embed = discord.Embed(title='Error', description=f'No active vote found for <@{discordId}>.', colour=discord.Color.red())
      await self.context.send(embed=embed)
      return

    embed = app.buildVoteEmbed()
    embed.set_thumbnail(url=user.avatar_url)
    await self.context.send(embed=embed,components=infoButtons)

  async def __tryGetUser(self, discordId):
    user = None
    try:
      user = await self.client.fetch_user(discordId)
    except Exception as e:
      print('vote.__tryGetUser()', e.message)
    return user

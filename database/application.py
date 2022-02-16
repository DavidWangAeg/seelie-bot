import os
import discord
from time import time
from .dbCommands import databaseReadOne, databaseWrite
from botCommands.voteConstants import HelpCategories, VoteIcons, VoteType
from .dbVote import getAllVotes

# Environment variable to store the name of the table in database that contains applications
APPLICATIONS_TABLE = os.environ['DATABASE_TABLE_APPLICATIONS']

ApplicationCache = {}

def createNewApplication(user, nickname, tag, category, messages):
  app = Application(user, nickname, tag, category, messages, True, 0, 0, 0, 0, int(time()), 0, 0, 0, 0)
  app.voteList = [[], [], [], []]
  return app

def createFromSqlResponse(row):
  app = Application(int(row[1]), row[2], row[3], HelpCategories[row[4]], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], int(row[14]), int(row[15]))
  app.id = row[0]
  app.getVoteList()
  return app

def getActiveApplication(userId):
  # search cache first
  if userId in ApplicationCache:
    print(f'getActiveApplication - Found active application for {userId} in cache')
    return ApplicationCache[userId]
  else:
    row = databaseReadOne(f"SELECT * FROM {APPLICATIONS_TABLE} WHERE discord_user='{userId}' AND application_active")
    if row is None:
      print(f'getActiveApplication - No active application found for {userId}')
      return None
    app = createFromSqlResponse(row)
    ApplicationCache[userId] = app
    return app

def removeApplication(userId):
  ApplicationCache.pop(userId, None)

class Application:
  def __init__(self, user, nickname, tag, category, messages, active, unweighted_yscore, unweighted_nscore, weighted_yscore, weighted_nscore, createdOn, vouches, bans, channelid, messageid):
    self.id = None
    self.user = user
    self.nickname = nickname
    self.tag = tag
    self.category = category
    self.messages = messages
    self.active = active
    self.unweighted_yscore = unweighted_yscore
    self.unweighted_nscore = unweighted_nscore
    self.weighted_yscore = weighted_yscore
    self.weighted_nscore = weighted_nscore
    self.createdOn = createdOn
    self.vouches = vouches
    self.bans = bans
    self.channelid = channelid
    self.messageid = messageid
    self.voteList = None

  def save(self):
    if self.id is None:
      databaseWrite(self.toSQLInsertQuery())
    else:
      databaseWrite(self.toSQLUpdateQuery())

  def toSQLInsertQuery(self):
    return f"""INSERT INTO {APPLICATIONS_TABLE} (discord_user, discord_nickname, discord_tag, application_categoryId, application_messages, application_active, application_unweighted_yscore, application_unweighted_nscore, application_weighted_yscore, application_weighted_nscore, application_createdOn, application_vouches, application_bans, application_channelid, application_messageid)
    VALUES ('{str(self.user)}', '{self.nickname}', '{self.tag}',{self.category.id}, '{self.messages}', {self.active}, {self.unweighted_yscore}, {self.unweighted_nscore}, {self.weighted_yscore}, {self.weighted_nscore}, {self.createdOn}, {self.vouches}, {self.bans}, '{str(self.channelid)}', '{str(self.messageid)}');"""
  
  def toSQLUpdateQuery(self):
    return f"""UPDATE {APPLICATIONS_TABLE} SET application_active={self.active}, application_unweighted_yscore={self.unweighted_yscore}, application_unweighted_nscore={self.unweighted_nscore}, application_weighted_yscore={self.weighted_yscore}, application_weighted_nscore={self.weighted_nscore}, application_vouches={self.vouches}, application_bans={self.bans}
    WHERE application_id={self.id};"""

  def getVoteList(self):
    if self.voteList is not None:
      return

    votes = getAllVotes(self.id)
    self.voteList = [[], [], [], []]
    for v in votes:
      self.voteList[v.type].append(v)

  def buildVoteEmbed(self):
    embed = discord.Embed(title=self.tag)
    embed.set_author(name=str(self.user))
    embed.color = 0x12d8d8
    # Field 0
    embed.add_field(name="Nickname", value=f"{self.nickname}\n<@{self.user}>", inline=True)

    # Field 1
    embed.add_field(name="Category", value=self.category.displayName, inline=True)
    
    # Field 2
    embed.add_field(name="Messages", value=self.messages, inline=True)

    self.updateStatusString(embed)
    self.updateScoreString(embed)
    self.updateVouchBan(embed)
    return embed

  def updateStatusString(self, embed):
    statusString = ''
    if self.active:
      statusString = f'Active - Created <t:{self.createdOn}:R>'
    else:
      statusString = 'Closed'
    if len(embed.fields) == 3:
      embed.add_field(name="Status", value=statusString, inline=False)
    else:
      embed.set_field_at(3, name="Status", value=statusString, inline=False)

  def updateScoreString(self, embed):
    if len(embed.fields) == 4:
      print(f'updateScoreString - adding new score field score')
      embed.add_field(name="Scores", value=self.getScoreString(), inline=False)
    else:
      print(f'updateScoreString - adjusting score')
      embed.set_field_at(4, name="Scores", value=self.getScoreString(), inline=False)

  def getScoreString(self):
    return f'✅ - **{min(4, self.unweighted_yscore) + self.weighted_yscore}** ({self.unweighted_yscore + self.weighted_yscore})\n❌ - **{min(4, self.unweighted_nscore) + self.weighted_nscore}** ({self.unweighted_nscore + self.weighted_nscore})'

  def updateVouchBan(self, embed):
    if len(embed.fields) == 5:
      print(f'updateVouchBan - adding new vouch/ban field')
      embed.add_field(name=f"=={VoteIcons[VoteType.Vouch]} Vouch==", value=self.getVoteListString(VoteType.Vouch), inline=True)
      embed.add_field(name=f"=={VoteIcons[VoteType.Ban]} Ban==", value=self.getVoteListString(VoteType.Ban), inline=True)
    else:
      print(f'updateVouchBan - aadjusting scores')
      embed.set_field_at(5, name=f"=={VoteIcons[VoteType.Vouch]} Vouch==", value=self.getVoteListString(VoteType.Vouch), inline=True)
      embed.set_field_at(6, name=f"=={VoteIcons[VoteType.Ban]} Ban==", value=self.getVoteListString(VoteType.Ban), inline=True)

  def getVoteListString(self, type):
    if len(self.voteList[type]) == 0:
      print(f'getVoteListString - {type} - None')
      return "None"
    print(f'getVoteListString - {type} - {self.voteList[type]}')
    return "\n".join(map(lambda vote: vote.toDisplayString(), self.voteList[type]))

  def toggleVotes(self, embed):
    if len(embed.fields) == 9:
      embed.remove_field(8)
      embed.remove_field(7)
    else:
      embed.add_field(name=f"=={VoteIcons[VoteType.Yes]} Yes==", value=self.getVoteListString(VoteType.Yes), inline=True)
      embed.add_field(name=f"=={VoteIcons[VoteType.No]} No==", value=self.getVoteListString(VoteType.No), inline=True)
  
  def setVotes(self, embed, visible):
    if len(embed.fields) == 9 and not visible:
      self.toggleVotes(embed)
    elif len(embed.fields) == 7 and visible:
      self.toggleVotes(embed)

  def __str__(self):
    return str(self.__class__) + " : " + str(self.__dict__)

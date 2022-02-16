import os
from database.application import getActiveApplication
from database.dbVote import getVote, createNewVote, getAllVotes
from .voteConstants import VoteButtonId, VoteType

DEFAULT_WEIGHT = int(os.environ['VOTE_WEIGHT_DEFAULT'])
LEAD_WEIGHT = int(os.environ['VOTE_WEIGHT_LEAD'])
MOD_WEIGHT = int(os.environ['VOTE_WEIGHT_MOD'])
CATEGORY_WEIGHT = int(os.environ['VOTE_WEIGHT_CATEGORY'])

def isVoteInteraction(client, interaction):
  isVote = interaction.custom_id in VoteButtonId
  print(f'isVoteInteraction - {isVote}')
  if interaction.custom_id in VoteButtonId:
    return True
  return False

async def handleVoteInteraction(client, interaction):
  print(f'handleVoteInteraction')
  msg = interaction.message
  embed = msg.embeds[0]

  # Find the application
  applicationUserId = embed.author.name
  app = getActiveApplication(applicationUserId)
  if app is None:
     print(f'handleVoteInteraction - Unable to find active vote for user {applicationUserId}')
     return True

  await updateVote(interaction, app)

  # Update the application
  app.save()

  # Update the message
  app.updateScoreString(embed)
  app.updateVouchBan(embed)
  await msg.edit(embed=embed)

async def updateVote(interaction, app):
  userId = interaction.user.id
  type = VoteButtonId.index(interaction.custom_id)
  # Find any existing votes
  vote = getVote(userId, app.id)

  if vote is not None:
    #undo existing vote
    adjustScore(app, vote.type, vote.weight, False)
    adjustVote(app, vote, False)

    if vote.type is type:
      #check if it's the same type - if so, remove vote and end early
      print(f'handleVoteInteraction - undoing vote')
      vote.delete()
      await interaction.send('Your vote has been removed.')
      return

    #update type
    vote.type = type
  else:
    weight = calculateWeight(interaction.user, app.category)
    vote = createNewVote(app.id, userId, type, weight)
  
  # apply new score
  adjustScore(app, vote.type, vote.weight, True)
  adjustVote(app, vote, True)

  # Save the vote
  vote.save()
  await interaction.send('Your vote has been registered!')

def adjustVote(app, vote, isAdd):
  print(f'adjustVote - add: {isAdd} List: {app.voteList[vote.type]} Vote: {vote}')
  if isAdd:
    app.voteList[vote.type].append(vote)
  else:
    filtered = []
    for v in app.voteList[vote.type]:
      print(f'handleVoteInteraction - comparing {v} to {vote}')
      if v.user != vote.user:
        filtered.append(v)

    print(f'handleVoteInteraction - {len(app.voteList[vote.type] )}->{len(filtered)}')
    app.voteList[vote.type] = filtered

def adjustScore(app, voteType, weight, isAdd):
  scalar = 1 if isAdd else -1
  print(f'adjustScore - voteType={voteType} weight={weight} isAdd={isAdd}')

  if voteType is VoteType.Vouch:
    app.vouches += scalar
  elif voteType is VoteType.Ban:
    app.bans += scalar

  if voteType is VoteType.Vouch or voteType is VoteType.Yes:
    if weight > 1:
      print(f'adjustScore - weighted y')
      app.weighted_yscore += scalar * weight
    else:
      print(f'adjustScore - unweighted y')
      app.unweighted_yscore += scalar
  elif voteType is VoteType.Ban or voteType is VoteType.No:
    if weight > 1:
      print(f'adjustScore - weighted n')
      app.weighted_nscore += scalar * weight
    else:
      print(f'adjustScore - unweighted n')
      app.unweighted_nscore += scalar

def calculateWeight(member, category):
  # check for a match to the category
  isCategory = False
  isMod = False
  isLead = False

  for role in member.roles:
    if role.name == category.leadRoleName:
      isCategory = True
    elif role.name == "Moderator":
      isMod = True
    elif role.name == "Lead":
      isLead = True

  # Category takes precedence
  if isCategory:
    print(f'calculateWeight - Category lead vote {category.leadRoleName}')
    return CATEGORY_WEIGHT
  if isMod:
    print(f'calculateWeight - Moderator vote')
    return MOD_WEIGHT
  if isLead:
    print(f'calculateWeight - Lead vote')
    return LEAD_WEIGHT

  print(f'calculateWeight - Default vote')
  return DEFAULT_WEIGHT

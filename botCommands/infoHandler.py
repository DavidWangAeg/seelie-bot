from database.application import getActiveApplication, removeApplication
from database.dbVote import deleteAllVotes
from .voteConstants import InfoButtonId, InfoType, VoteType, VoteIcons

def isInfoInteraction(client, interaction):
  if interaction.custom_id in InfoButtonId:
    return True
  return False

async def handleInfoInteraction(client, interaction):
  type = InfoButtonId.index(interaction.custom_id)  
  print(f'handleInfoInteraction - type {type}')

  match type:
    case InfoType.Toggle:
      await handleToggle(client, interaction)
    case InfoType.Close:
      await handleClose(client, interaction)
    case InfoType.Quit:
      await handleQuit(client, interaction)

async def handleToggle(client, interaction):
  print(f'handleToggle')
  msg = interaction.message
  embed = msg.embeds[0]
  applicationUserId = embed.author.name  
  app = getActiveApplication(applicationUserId)
  print(f'handleToggle - found embed')
  
  app.toggleVotes(embed)

  await interaction.respond(type=7, embed=embed)

async def handleClose(client, interaction):
  msg = interaction.message
  embed = msg.embeds[0]
  applicationUserId = embed.author.name  
  app = getActiveApplication(applicationUserId)

  if app is None:
    print(f'handleClose - Unable to find active vote for user {applicationUserId}')
    return
  
  app.active = False
  app.updateStatusString(embed)
  app.save()
  removeApplication(applicationUserId)
  
  #turn on votes before closing
  app.setVotes(embed, True)

  await msg.edit(embed=embed, components=[])

  #turn off votes to close main vote
  app.toggleVotes(embed)

  if app.channelid != 0 and app.messageid != 0:
    try:
      channel = client.get_channel(app.channelid)
      voteMsg = await channel.fetch_message(app.messageid)
      await voteMsg.edit(embed=embed, components=[])

      print(f'handleClose - Successfully closed vote message')
    except Exception as e:
      print(e)

  deleteAllVotes(app.id)

  await interaction.send("Vote has been closed.")
  
  return

async def handleQuit(client, interaction):
  msg = interaction.message
  await msg.delete()
  await interaction.send("Quitting")

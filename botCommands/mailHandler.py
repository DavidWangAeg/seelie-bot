import os
from database.application import getActiveApplication, removeApplication
from database.dbVote import deleteAllVotes
from .mailConstants import MailType, MailButtonId
from database.dbMail import logMessage

MAIL_TARGET_CHANNEL_ID = int(os.environ['MAIL_TARGET_CHANNEL_ID'])

def isMailInteraction(client, interaction):
  if interaction.custom_id in MailButtonId:
    return True
  return False

async def handleMailInteraction(client, interaction):
  type = MailButtonId.index(interaction.custom_id)  
  print(f'handleMailInteraction - type {type}')
  match type:
    case MailType.SendAnon:
      await handleSend(client, interaction, True)
    case MailType.SendUser:
      await handleSend(client, interaction, False)
    case MailType.Cancel:
      await handleCancel(client, interaction)

async def handleSend(client, interaction, isAnonymous):
  msg = interaction.message
  channel = client.get_channel(int(MAIL_TARGET_CHANNEL_ID))

  authorName = "Anonymous" if isAnonymous else f'Sent by user {interaction.user.id}'

  embed = msg.embeds[0]
  embed.title = 'New Mail!'
  embed.set_footer(text='')
  embed.set_author(name=authorName)
  sentMessage = await channel.send(embed=embed, files=[await attch.to_file() for attch in msg.attachments])

  logMessage(interaction.user.id, sentMessage.id)

  await msg.edit(components=[])
  await interaction.send("Your message has been sent!")

async def handleCancel(client, interaction):  
  msg = interaction.message
  await msg.delete()
  await interaction.send("Cancelled.")
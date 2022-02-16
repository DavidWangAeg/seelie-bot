import os
import discord
from discord_components import Button, ActionRow
from .mailConstants import MailType, MailButtonId, EmbedColor

mailButtons = ActionRow(
  [
    Button(label="📮Send (Anonymous)", custom_id=MailButtonId[MailType.SendAnon], style=3),
    Button(label="✉️Send (Named)", custom_id=MailButtonId[MailType.SendUser], style=1),
    Button(label="❌Cancel", custom_id=MailButtonId[MailType.Cancel], style=2),
  ]
)

class MailCommand:
  def __init__(self, client, context, args):
    self.client = client
    self.context = context
    self.args = args
  
  async def execute(self):
    # mail can only be used in DMs
    if self.context.channel.type is not discord.ChannelType.private:
      embed = discord.Embed(title='Warning', description='The `mail` command should be used via DMs only!', colour=discord.Color.orange)
      await self.context.send(embed=embed)
      return

    if len(self.args) == 0:
      embed = discord.Embed(title='Error', description='`!mail` requires at least one input!', colour=discord.Color.red())
      await self.context.send(embed=embed)
      return

    embed = discord.Embed(title='Preview - would you like to send this message?', description=self.args, color=EmbedColor)
    embed.set_footer(text='Mails can be sent anonymously with `Send (Anonymous)`, or with your user revealed with `Send (Named)`. Make sure you pick the right one! If you are found to be misusing mail, your username can be looked up for anonymous mails.')
    await self.context.send(embed=embed, components=mailButtons, files=[await attch.to_file() for attch in self.context.message.attachments])

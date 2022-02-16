import os
import discord

VOTE_ROLE_ID = int(os.environ['VOTE_COMMAND_ROLE_ID'])

warnText = """Hello Seelie Guide,

We've noticed that your activity for the previous month is somewhat low. Due to the reward system, we do require a minimum level of activity to maintain Seelie Guide status and be eligible for rewards in order to be fair to the others who remain active.

If you're not able to dedicate more time in the help channels in the next month, then we may revoke your status. Do remember to prioritize yourself regarding the Seelie Guide program, and if you're finding you have less time and/or interest in being a Seelie Guide, you should consider giving up the role. We are happy to welcome you back once you have more time, and we still hope you will continue to help in our channels when convenient for you, even without the role.

If you have any questions/concerns over this assessment, please feel to reach out to via <#881797138277859338> or the `!mail` command via this bot."""

class WarnCommand:
  def __init__(self, client, context, target):
    self.client = client
    self.context = context
    self.target = int(target)

  async def execute(self):
    if not any(role.id == VOTE_ROLE_ID for role in self.context.author.roles):
      embed = discord.Embed(title='Error', description='You do not have permission to use that command!', colour=discord.Color.red())
      await self.context.send(embed=embed)
      return

    try:
      user = await self.client.fetch_user(self.target)

      embed = discord.Embed(title='Inactivity Warning', description=warnText, color=discord.Color.orange())
      await user.send(embed=embed)
      successEmbed = discord.Embed(title='Success!', description=f'Successfully sent warning to <@{self.target}>.', colour=discord.Color.green())
      await self.context.send(embed=successEmbed)
    except Exception as e:
      errorEmbed = discord.Embed(title='Error', description=e, colour=discord.Color.red())
      await self.context.send(embed=errorEmbed)

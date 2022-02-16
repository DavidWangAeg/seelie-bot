import os
from .dbCommands import databaseReadOne, databaseWrite, databaseReadMany
from botCommands.voteConstants import VoteIcons

MAIL_TABLE = os.environ['DATABASE_TABLE_MAIL']

def logMessage(userId, messageid):
  mail = Mail(userId, messageid)
  mail.save()

class Mail:
  def __init__(self, user, messageid):
    self.user = user
    self.messageid = messageid
  
  def save(self):
    print('Mail.save - performing save')
    databaseWrite(self.toSQLInsertQuery())

  def toSQLInsertQuery(self):
    return f"""INSERT INTO {MAIL_TABLE} (discord_user, mail_messageid)
    VALUES ('{self.user}', '{self.messageid}');"""

  def __str__(self):
    return str(self.__class__) + " : " + str(self.__dict__)
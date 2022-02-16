import os
from .dbCommands import databaseReadOne, databaseWrite, databaseReadMany
from botCommands.voteConstants import VoteIcons

VOTES_TABLE = os.environ['DATABASE_TABLE_VOTES']

def createNewVote(applicationId, user, type, weight):
  return Vote(applicationId, user, type, weight)

def createFromSqlResponse(row):
  app = Vote(int(row[1]), int(row[2]), row[3], row[4])
  app.id = row[0]
  return app

def getVote(userId, applicationId):
  row = databaseReadOne(f"SELECT * FROM {VOTES_TABLE} WHERE discord_user='{userId}' AND application_id={applicationId}")
  if row is None:
    print(f'getVote - No active vote found for user {userId} / application {applicationId}')
    return None
  
  return createFromSqlResponse(row)

def getAllVotes(applicationId):
  rows = databaseReadMany(f"SELECT * FROM {VOTES_TABLE} WHERE application_id={applicationId}")
  if rows is None:
    print(f'getAllVotes - No active votes found for application {applicationId}')
    return None
  return map(createFromSqlResponse, rows)

def deleteAllVotes(applicationId):
  databaseWrite(f"DELETE FROM {VOTES_TABLE} WHERE application_id={applicationId}")

class Vote:
  def __init__(self, applicationId, user, type, weight):
    self.id = None
    self.applicationId = applicationId
    self.user = user
    self.type = type
    self.weight = weight
  
  def save(self):
    print('Vote.save - performing save')
    if self.id is None:
      print('Vote.save - Creating new Vote: ', self)
      databaseWrite(self.toSQLInsertQuery())
    else:
      print('Vote.save - Update vote: ', self)
      databaseWrite(self.toSQLUpdateQuery())

  def delete(self):
    if self.id is not None:
      databaseWrite(self.toSQLDeleteQuery())

  def toSQLInsertQuery(self):
    return f"""INSERT INTO {VOTES_TABLE} (application_id, discord_user, vote_type, vote_weight)
    VALUES ({self.applicationId}, '{str(self.user)}', {self.type}, {self.weight});"""

  def toSQLUpdateQuery(self):
    return f"""UPDATE {VOTES_TABLE} SET vote_type={self.type}, vote_weight={self.weight}
    WHERE vote_id={self.id};"""

  def toSQLDeleteQuery(self):
    return f"""DELETE FROM {VOTES_TABLE} WHERE vote_id={self.id}"""

  def toDisplayString(self):
    return f"[{self.weight}]<@{self.user}>"

  def __str__(self):
    return str(self.__class__) + " : " + str(self.__dict__)
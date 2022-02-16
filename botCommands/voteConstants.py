class VoteType:
  Vouch = 0
  Yes = 1
  No = 2
  Ban = 3

VoteButtonId = ["voteVouch", "voteYes", "voteNo", "voteBan"]
VoteIcons = ['🌟', '✅', '❌', '☠️']

class InfoType:
  Toggle = 0
  Close = 1
  Quit = 2

InfoButtonId = ["infoToggle", "infoClose", "infoQuit"]

class HelpCategory:
  def __init__(self, id, displayName, leadRoleName):
    self.id = id
    self.displayName = displayName
    self.leadRoleName = leadRoleName

HelpCategories = [
  HelpCategory(0, 'General', 'Lead-Gen'),
  HelpCategory(1, 'Exploration', 'Lead-Explo'),
  HelpCategory(2, 'Strategy', 'Lead-Strat'),
  HelpCategory(3, 'Abyss', 'Lead-Abyss'),
  HelpCategory(4, 'Party', 'Lead-Party'),
  HelpCategory(5, 'Technical', 'Lead-Tech'),
  HelpCategory(6, 'Lore', 'Lead-Lore'),
  HelpCategory(7, 'Spanish', 'Lead-ESP'),
  HelpCategory(8, 'French', 'Lead-FR'),
  HelpCategory(9, 'German', 'Lead-DE'),
  HelpCategory(10, 'Portuguese', 'Lead-PTBR'),
  HelpCategory(11, 'Russian', 'Lead-RU')
]

HelpCategoryMap = {}

for category in HelpCategories:
  HelpCategoryMap[category.displayName] = category
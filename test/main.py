import sys, os

sys.path.insert(0, os.path.dirname('D:\pyfiles\project_automator\src'))

from src.Bot import *

jarvis = Bot(name="jarvis", gender="male")

jarvis.add_extension('extentions.Wish')
jarvis.add_extension('extentions.Open_app')
jarvis.run()
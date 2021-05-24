from .src.Bot import *
import parsedatetime
from datetime import datetime
from .src.Setup import debug, log


async def parsediff(tstr):
    calender = parsedatetime.Calendar()
    time_struct, parse_status = calender.parse(tstr)
    return datetime(*time_struct[:6]) - datetime.now()

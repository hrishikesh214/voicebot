# Voicebot

### Voice Assistant `Ezz Pzz`

### Installation

`Clone this dir in your root directory`

### Creating Instance

#### `main.py`

```py
import voicebot as vb
bot = vb.Bot(name="jarvis", gender="male",
             match="jarvis|jar|jalvis", min_energy=2000, show_beat=True, show_task=True)

bot.run()
```

### Adding Bot Extentions

`for example we have an greeting extention`
`Greet.py` in root dir

```py
import voicebot

# make your class
class Greetings:
    def __init__(self, bot):
        # required
        self.bot = bot
        self.name = 'Greetings'

    # define each command like this
    @voicebot.match("?* greet me ?* || ?* good morning|afternoon|evening|night ?*")
    async def greet(self, vars):
        self.bot.say('greetings!')

     @voicebot.match('quit || shutdown || sleep || shut down')
    async def end(self, vars):
        self.bot.say(f'Good Bye')
        self.bot.stop()

# attach function is required
def attach(bot):
    bot.attach_extention(Greetings(bot))
```

Now finnaly attach extention to `main.py` file

```py
bot.add_extention('.Greet')
```

### Vars

whenever there is `?*` in match string bot engine will break user voice and adds whatever comes in place of ?_ to a list of strings. This list is passed as first(after self) argument to class function so that you can get argument of author.
**`Note: ` If nothing matches with `?_`, it acts as empty string**

### Background Tasks

Yes! you can make bot run multiple background tasks
lets look at an example!
suppose you have `Common.py` Extention

```py
import voicebot
import asyncio

class Common:
    def __init__(self, bot):
        # required
        self.bot = bot
        self.name = 'Common'

    # define each command like this
    @voicebot.match("?* remind ?* that ?*")
    async def remind(self, vars):
        diff = await voicebot.parsediff(vars[1])
        nounce: str = vars[2]
        replacer = [
            ['i', 'you'],
            ['we', 'your'],
            ['my', 'your']
        ]
        for thing in replacer:
            nounce = nounce.replace(thing[0], thing[1])

        # create task will add 1st argument(function and rest all args) as background task
        await self.bot.create_task(set_reminder, self.bot, diff.seconds, nounce)
        self.bot.say(f"reminder set!")

async def set_reminder(bot, t, doWhat):
    try:
        t = int(t)
        await asyncio.sleep(t)
        nonce = f"sir, its reminder that {doWhat}"
        log(nonce)
        bot.say(nonce)
    except Exception as e:
        print(e)

# attach function is required
def attach(bot):
    bot.attach_extention(Common(bot))
```

#### Made with ❤️ by Hrishikesh

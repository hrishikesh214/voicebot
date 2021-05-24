

class Wish:
    def __init__(self, bot):
        self.name = "wish"
        self.bot = bot
        self.routes = {
            'wish ?':'wish',
            'say bye': 'bye',
            'who are you': 'whoareyou'
        }
    
    def wish(self, l1):
        whom = l1[0]
        if whom == 'me':
            whom = 'you'
        self.bot.say(f'good morning to {whom}')
    
    def bye(self, l1):
        print(l1)
        self.bot.say("Good Bye")
    
    def whoareyou(self, l1):
        print(l1)
        self.bot.say(f'i am {self.bot.name}')

def attach(bot):
    bot.attach_extension(Wish(bot))
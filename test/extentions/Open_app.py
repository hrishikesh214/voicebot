class Open_app:
    def __init__(self, bot):
        self.name = "Open_app"
        self.bot = bot
        self.routes = {
            'wish ?':'ooowish',
            'say bye': 'ooobye'
        }
    
    def ooowish(self, l1):
        self.bot.say("hello")
        return l1
    
    def ooobye(self, l1):
        return l1
    

def attach(bot):
    bot.attach_extension(Open_app(bot))
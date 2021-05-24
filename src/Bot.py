from . import Setup
from .Setup import *
from .Setup import _green, _blue, _red, _yellow, _magenta
import asyncio
import threading
import random


class Bot:
    def __init__(self, name, gender="male", match=None, min_energy=None, max_pause=None, show_beat=False, show_task=False):

        # Bot Configs
        self.name = name
        self.gender = gender
        self.match = match if match is not None else name
        self.show_beat = show_beat
        self.show_task = show_task

        # Voice Engine
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        if gender == 'male':
            gender = 0
        else:
            gender = 1
        self.engine.setProperty('voice', voices[gender].id)
        self.engine. setProperty("rate", 165)
        self.say("initialising...")

        # Voice Recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.say(f"wait lemme adjust ambient noise, it will only take 10 seconds")
        if min_energy is None:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=5)
        else:
            self.recognizer.energy_threshold = min_energy
        self.recognizer.pause_threshold = max_pause if max_pause is not None else 0.8

        self.exts = []

        self.tasks = []

        self.to_say = []

        self.main_loop = None

        self.threads = []

    def say(self, audio):
        '''
            Function makes bot say as per configured voice configurations
            ``audio`` is string for bot to say
        '''
        if self.engine._inLoop:
            try:
                self.engine.endLoop()
            # except RuntimeError as e:
            #     self.say(audio)
            except Exception as e:
                print(e)
                self.say(audio)
            return
        self.engine.say(audio)
        self.engine.runAndWait()

    async def listen(self):
        '''
            Function makes bot listen a `phrase` and return it
        '''
        command = await self.getSpeech()
        if command == "None":
            return "None"
        return command[0]

    async def getSpeech(self):
        '''
            Function actually heares phrase and conert it to text and returns it
        '''
        with self.microphone as source:
            audio = self.recognizer.listen(source)

        try:
            query = self.recognizer.recognize_google(
                audio, language='en-in', show_all=True)
            if isinstance(query, list):
                return "None"
            final_q = [x['transcript'].lower() for x in query['alternative']]

        except Exception as e:
            print(f"getSpeech: {e}")
            return "None"
        return final_q

    async def make_run(self):
        '''
        Background hearing of bot
        '''

        while True:
            if self.show_beat:
                Setup.log('< BEATING: MAIN THREAD >', _yellow)
            try:
                queries = await self.getSpeech()
                queries != "None" and print(f"queries = {queries}")
                found = False
                if queries != "None" and len(queries) > 0:
                    for query in queries:
                        check_call = match_string(f'?- {self.match} ?*', query)
                        if check_call['matched']:
                            found = True
                            break

                    if found:
                        self.say('yes sir?')
                        command = await self.getSpeech()
                        if command != 'None':
                            await self.process_query(command)
            except Exception as e:
                print(e)
                continue

    def run(self):
        '''
            Makes Bot run and hear in background
        '''
        def main_thread():
            '''
            main thread
            '''
            self.say("hello sir, i am ready!")
            runner = asyncio.new_event_loop()
            self.main_loop = runner
            Setup.log('<MAIN THREAD STARTED>', _green)
            runner.run_until_complete(self.make_run())

        def background_tasks():
            '''
            background tasks
            '''

            def task_runner(task, args):
                asyncio.run(task(*args))

            print('\n')

            async def runner():
                Setup.log('<BACKGROUND TASKS STARTED>', _green)
                while True:
                    if self.show_beat:
                        Setup.log('< BEATING: BACKGROUND TASKS >', _yellow)
                    if len(self.tasks):
                        task = self.tasks[0]
                        self.tasks.pop(0)
                        task = threading.Thread(target=task_runner, args=[
                                                task[0], task[1]])
                        if self.show_task:
                            log(f'< TASK EXPORTED : {str(task[0])} >', _yellow)
                        task.start()
                    await asyncio.sleep(2)

            asyncio.run(runner())

        def clear_says():
            async def runner():
                Setup.debug('< CLEARING SAYS >', _green)
                Setup.log('AWAITING', _blue)
                while True:
                    if self.show_beat:
                        Setup.log('< BEATING: CHECKS CYCLE >',
                                  random.choice([_yellow, _blue]))
                    try:
                        if not self.engine._inLoop and len(self.to_say):
                            to_say = self.to_say[0]
                            self.to_say.pop(0)
                            self.say(to_say)
                    except Exception as e:
                        print(e)
                    await asyncio.sleep(1)

            asyncio.run(runner())

        # gather threads
        t1 = threading.Thread(target=clear_says)
        t2 = threading.Thread(target=background_tasks)

        self.threads = [t2, t1]

        # run them all
        for t in self.threads:
            t.start()

        # now run main thread
        main_thread()

    def add_extension(self, extension):
        '''
            Function adds routes and callbacks to routes and callbacks
        '''
        try:
            ext = il.import_module(extension)
            ext.attach(self)

        except Exception as e:
            print(e)
            pass

    def attach_extension(self, ext):
        try:
            extname = ext.name.lower()
            self.exts.append(ext)
            log(f"{extname} attached", Back.MAGENTA)
        except Exception as e:
            print(e)
            self.say(f"sir, i got error while attaching extension {extname}")

    async def process_query(self, queries):
        '''
        it will choose 1st query as for now and run all bot functions asynchronously accordingly
        '''

        Setup.log(Back.MAGENTA + Fore.BLACK + "command = " + queries[0])
        try:
            for query in queries:
                async_methods = []
                for ext in self.exts:
                    methods = [func for func in dir(ext) if callable(
                        getattr(ext, func)) and not func.startswith("__")]
                    for method in methods:
                        method = getattr(ext, method)
                        if not asyncio.iscoroutinefunction(method):
                            method = asyncio.coroutine(method)
                        async_methods.append(
                            asyncio.create_task(method(_query=query)))
                await asyncio.wait(async_methods)
                break
            print(Back.MAGENTA + Fore.BLACK + "command = ", queries[0])
        except Exception as e:
            Setup.log(e, _red)
            self.say("i have an error")

    async def create_task(self, task, *args):
        '''
        This method creates task for bot as a thread
        @return bool
        '''
        try:
            # if its not coroutine then make it
            if not asyncio.iscoroutinefunction(task):
                task = asyncio.coroutine(task)

            # finnaly append it to task list
            self.tasks.append((task, args))
            return True
        except Exception as e:
            print(e)
            return False

    async def stop(self):
        '''
        This method stops the bot
        '''

        # stop all threads
        for t in self.threads:
            t.stop()

        # finnaly exit
        exit(1)

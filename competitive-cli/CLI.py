import getpass
import pathlib
import sys

from . import CLI_helper
from . import SessionAPI

websiteObject = None


class InteractiveShell:
    def __init__(self):
        self.active = False

    def __enter__(self):
        self.active = True

        while self.active:
            query = input("shell>> ")
            if query == 'q':
                self.active = False
                break
            else:
                parse(query)

        return self

    def __exit__(self):
        self.active = False


def submit(probID, website=None):

    pass


def download(probID):
    pass


def create(probID):
    pass


def open_question(probID):
    pass


def login(website=None):
    global websiteObject
    global acc_manager

    username = input("Enter your username: ")
    try:
        password = getpass.getpass("Enter your password: ")
    except getpass.GetPassWarning:
        print("Your system is not allowing us to disable echo. We cannot read your password")
        return

    if website is None and websiteObject is None:
        print("Website not mentioned")
        return
    if websiteObject is None:
        sessionObject = SessionAPI.SessionAPI()
        websiteObject = sessionObject.factoryMethod(website)

    websiteObject.login(username, password)

    acc_manager.insert(website, username, password)


def soln():
    pass


def debug():
    pass


def setweb():
    pass


def settpl():
    pass


def stats():
    pass


def parse(query):
    cmds = query.split(' ')
    flags = []
    new_cmds = []

    for cmd in cmds:
        if '-' in cmd:
            flags.append(cmd)
        else:
            new_cmds.append(cmd)

    commands = {

        'set':
            {
                'browser': pref_manager.update_browser, 'mode': pref_manager.update_mode, 'acc': setweb, 'tpl': settpl
            },

        'view':
            {
                'question': open_question, 'solutions': soln, 'tpl': lambda: str(tpl_manager),
                'accounts': lambda: str(acc_manager), 'stats': stats
            },

        'submit': submit,

        'download': download,

        'create':
            {
                'tpl': tpl_manager.insert, 'accounts': acc_manager.insert, 'file': create
            },

        'delete':
            {
                'tpl': tpl_manager.delete, 'accounts': acc_manager.delete
            },

        'login': login,

        'update':
            {
                'account': acc_manager.update
            },

        'debug': debug
    }

    iterative_commands = commands[new_cmds[0]]
    new_cmds = new_cmds[1:]
    arguments = []

    for command in new_cmds:
        if isinstance(iterative_commands, dict):
            try:
                iterative_commands = iterative_commands[command]
            except KeyError:
                return "Invalid Command"
        else:
            arguments.append(command)

    # iterative_commands(*arguments)

    return iterative_commands, arguments, flags


# query = sys.argv[2:]
query = input()

pathlib.Path(pathlib.Path.home() / "competitive-cli").mkdir(parents=True, exist_ok=True)

with CLI_helper.PreferenceManager() as pref_manager, CLI_helper.TemplateManager() as tpl_manager, CLI_helper.AccountManager() as acc_manager:
    print(parse(query))

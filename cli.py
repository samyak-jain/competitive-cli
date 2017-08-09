import cli_helper
import pathlib
import SessionAPI
import sys


class InteractiveShell:
    def __init__(self, pref, tpl, acc):
        self.active = False
        self.pref = pref
        self.tpl = tpl
        self.acc = acc

    def __enter__(self):
        self.active = True

        while self.active:
            query = input("shell>> ")
            if query == 'q':
                self.active = False
                break
            else:
                parse(query, self.pref, self.tpl, self.acc)

        return self

    def __exit__(self):
        self.active = False


def submit(probID):
    pass


def download(probID):
    pass


def create(probID):
    pass


def open_question(probID):
    pass


def login():
    pass


def soln():
    pass


def debug():
    pass

def parse(query, pref, tpl, acc):
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
                'browser': pref.update_browser, 'mode': pref.update_mode
            },

        'view':
            {
                'question': open_question, 'solutions': soln, 'tpl': lambda: str(tpl_manager),
                'accounts': lambda: str(acc_manager)
            },

        'submit': submit,

        'download': download,

        'create':
            {
                'tpl': tpl.insert, 'accounts': acc.insert, 'file': create
            },
        'delete':
            {
                'tpl': tpl.delete, 'accounts': acc.delete
            },

        'login': login,

        'update':
            {
                'account': acc.update
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

    return iterative_commands, arguments, flags


query = sys.argv[2:]
# query = input()

pathlib.Path(pathlib.Path.home() / "competitive-cli").mkdir(parents=True, exist_ok=True)

with cli_helper.PreferenceManager() as pref_manager, cli_helper.TemplateManager() as tpl_manager, cli_helper.AccountManager() as acc_manager:
    print(parse(query, pref_manager, tpl_manager, acc_manager))

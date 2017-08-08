import cli_helper
import pathlib
import SessionAPI
import sys


class InteractiveShell:
    def __init__(self):
        self.active = False

    def __enter__(self):
        self.active = True

        while self.active:
            query = input("shell>> ")
            if query == 'q':
                self.__exit__()
            else:
                parse(query)

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


def parse(query, pref_manager, tpl_manager, acc_manager):
    cmds = query.split(' ')
    flags = []
    new_cmds = []

    for cmd in cmds:
        if '-' in cmd:
            flags.append(cmd)
        else:
            new_cmds.append(cmd)

    commands = {
        'set': dict(browser=pref_manager.update_browser, mode=pref_manager.update_mode),
        'view': dict(question=open_question, answers=1, tpl=lambda: str(tpl_manager),
                     accounts=lambda: str(acc_manager)),
        'submit': submit,
        'download': download,
        'create': dict(tpl=tpl_manager.insert, accounts=acc_manager.insert),
        'delete': dict(tpl=tpl_manager.delete, accounts=acc_manager.delete),
        'login': 6,
        'update': dict(accounts=0)
    }

    iterative_commands = commands

    for command in new_cmds:
        iterative_commands = iterative_commands[command]


query = sys.argv[2:]

pathlib.Path(pathlib.Path.home() / "competitive-cli").mkdir(parents=True, exist_ok=True)

with cli_helper.PreferenceManager(), cli_helper.TemplateManager(), cli_helper.AccountManager() as [pref_manager,
                                                                                                   tpl_manager,
                                                                                                   acc_manager]:
    parse(query, pref_manager, tpl_manager, acc_manager)
    pass

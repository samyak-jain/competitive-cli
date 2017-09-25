import getpass
import pathlib
import prettytable
import requests
import sys
import webbrowser

import CLI_helper
import SessionAPI

websiteObject = None

pref_manager = CLI_helper.PreferenceManager()
acc_manager = CLI_helper.AccountManager()
tpl_manager = CLI_helper.TemplateManager()

class InteractiveShell:
    def __init__(self):
        self.active = False

    def start(self):
        self.active = True

        while self.active:
            query = input("shell>> ")
            if query == 'q':
                self.active = False
                break
            else:
                parse(query.split(' '))

        return self

    def stop(self):
        self.active = False


def submit(probID, path=None, language=None, website=None):
    global websiteObject
    # login(website)
    result = websiteObject.submit(probID, path, language)

    if result is None:
        print("Error submitting")
        return

    table = prettytable.PrettyTable(result[0])
    for row in result[1:]:
        table.add_row(row)

    print(str(table))


def download(probID, path=pathlib.Path().cwd(), website=None):
    global websiteObject
    login(website)

    path = pathlib.Path(path)
    url = websiteObject.get_question(probID)
    html = requests.get(url).text
    question_file = open(path / (probID + ".html"), 'w')
    question_file.write(html)
    question_file.close()


def create(probID, language, path=None, tpl_index=None):
    global tpl_manager

    if tpl_index is None:
        tpl_index = tpl_manager.template

    if path is None:
        path = pathlib.Path().cwd()
    else:
        path = pathlib.Path(path)

    tpl_file = tpl_manager.get_template(tpl_index)
    extension = SessionAPI.SessionAPI.find_language(language)

    path = path / (probID + extension)

    if path.is_file():
        overwrite = input("File already exists? (y/n) ")
        if overwrite == 'n': return
        file = open(path, "r+")
    else:
        file = open(path, "w+")

    with open(tpl_file) as tpl_new:
        tpl_text = tpl_new.read()

    file.write(tpl_text)

    file.close()


def open_question(probID, web=None):
    global pref_manager
    global websiteObject
    login()

    if webbrowser is None:
       web = pref_manager.get("browser")
    try:
        browser = webbrowser.get(web)
    except webbrowser.Error:
        print("Invalid browser")
        return

    browser.open(websiteObject.get_question(probID))


def login(website=None):
    global websiteObject
    global acc_manager

    if website is None and acc_manager.account is not None:
        website, username, password = acc_manager.get_account(acc_manager.account)
        websiteObject = websiteObject.factoryMethod(website)
    else:
        username = input("Enter your username: ")
        try:
            password = getpass.getpass("Enter your password: ")
        except getpass.GetPassWarning:
            print("Your system is not allowing us to disable echo. We cannot read your password")
            return

    if website is None and websiteObject is None:
        website = input("Enter website: ")
        websiteObject = SessionAPI.SessionAPI().factoryMethod(website)
    elif websiteObject is None:
        websiteObject = SessionAPI.SessionAPI().factoryMethod(website)

    websiteObject.login(username, password)

    acc_manager.insert(website, username, password)

    if websiteObject.logged_in:
        print("Successful Login")
    else:
        print("Login Failed")


def soln(website=None):
    global websiteObject
    if not websiteObject.logged_in:
        login(website)

    tab_data = websiteObject.display_sub()
    table = prettytable.PrettyTable(tab_data[0])

    for row in tab_data[1:]:
        table.add_row(row)

    print(str(table))


def debug():
    pass


def insacc():
    global acc_manager

    website = input("Enter Website: ")
    username = input("Enter username: ")
    try:
        password = getpass.getpass("Enter your password: ")
    except getpass.GetPassWarning:
        print("Your system is not allowing us to disable echo. We cannot read your password")
        return

    acc_manager.insert(website, username, password)


def instpl(path=None):
    global tpl_manager

    if path == '.':
        path = pathlib.Path().cwd()
    elif path is not None:
        path = pathlib.Path(path)
    else:
        path = input("Enter Path: ")

    tpl_manager.insert(path)


def stats(website):
    global websiteObject
    if not websiteObject.logged_in:
        login(website)

    data = websiteObject.user_stats()

    for element in data:
        print(element, data[element])


def usage():
    print(
        """
            Usage:
                ccli set browser <browser-name>
        """
    )
    pass


def parse(query):
    if len(query) == 0 or query == ["--help"] or query == ["-h"]:
        usage()
        return

    flags = []
    new_cmds = []

    for cmd in query:
        if '-' in cmd:
            flags.append(cmd)
        else:
            new_cmds.append(cmd)

    commands = {

        'set':
            {
                'browser': pref_manager.update_browser,
                'acc': acc_manager.set_default, 'tpl': tpl_manager.set_default
            },

        'view':
            {
                'question': open_question, 'solutions': soln, 'tpl': lambda: print(str(tpl_manager)),
                'accounts': lambda: print(str(acc_manager)), 'stats': stats, 'config': pref_manager.show
            },

        'submit': submit,

        'download': download,

        'create':
            {
                'tpl': instpl, 'accounts': insacc, 'file': create
            },

        'delete':
            {
                'tpl': tpl_manager.delete, 'accounts': acc_manager.delete, 'config': pref_manager.clear
            },

        'login': login,

        'update':
            {
                'account': acc_manager.update
            },

        'debug': debug
    }

    try:
        iterative_commands = commands[new_cmds[0]]
    except KeyError:
        print("Invalid command")
        usage()
        return

    new_cmds = new_cmds[1:]
    arguments = []

    for command in new_cmds:
        if isinstance(iterative_commands, dict):
            try:
                iterative_commands = iterative_commands[command]
            except KeyError:
                print("Invalid Command")
                usage()
                return
        else:
            arguments.append(command)

    iterative_commands(*arguments)
    return iterative_commands, arguments, flags

def main():
    global pref_manager
    global tpl_manager
    global acc_manager

    query = sys.argv[1:]

    pathlib.Path(pathlib.Path.home() / "competitive-cli").mkdir(parents=True, exist_ok=True)

    with pref_manager, tpl_manager, acc_manager:
        if query == ["interactive"]:
            shell = InteractiveShell()
            shell.start()
        else:
            parse(query)

if __name__ == "__main__":
    main()
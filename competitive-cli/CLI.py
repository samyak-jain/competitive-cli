import getpass
import os
import pathlib
import prettytable
import requests
import sys
import webbrowser

import CLI_helper
import SessionAPI

websiteObject = SessionAPI.SessionAPI()
manager = CLI_helper.PreferenceManager()


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
    if not websiteObject.logged_in:
        login(website)

    if path is None:
        paths = list(pathlib.Path.cwd().glob(probID + '*'))
        if len(paths)>1:
            print("Multiple matches")
            return
        if len(paths)==0:
            print("No match found")
            return
        path = paths[0]
    else:
        path = pathlib.Path(path)

    if os.stat(str(path.resolve())).st_size == 0:
        print("File is empty. Please upload a valid file")
        return

    if language is None:
        result = websiteObject.submit(probID, path)
    else:
        result = websiteObject.submit(probID, path, language)

    if result is None or result is False:
        print("Error submitting")
        return

    table = prettytable.PrettyTable(result[0])
    for row in result[1:]:
        table.add_row(row)
    print(str(table))


def download(probID, path=pathlib.Path().cwd(), website=None):
    global websiteObject

    if not websiteObject.logged_in:
        login(website)

    path = pathlib.Path(path)
    url = websiteObject.get_question(probID)
    if isinstance(websiteObject, SessionAPI.UvaSession):
        pdf = requests.get(url).content
        question_file = open(path / (probID + ".pdf"), 'wb')
        question_file.write(pdf)
    else:
        html = requests.get(url).text
        question_file = open(path / (probID + ".html"), 'w')
        question_file.write(html)

    question_file.close()


def create(probID, path=None, tpl_index=None):

    if probID is None:
        print("Missing Problem ID/filename.")
        return

    if tpl_index is None:
        tpl_index = manager.template
    if path is None:
        path = pathlib.Path().cwd()
    else:
        path = pathlib.Path(path)

    # extension = SessionAPI.SessionAPI.find_language(str(language))
    path = path / str(probID)

    if path.is_file():
        overwrite = input("File already exists? (y/n) ")
        if overwrite == 'n': return
        file = open(path, "r+")
    else:
        file = open(path, "w+")

    if tpl_index is not None:
        tpl_file = pathlib.Path(manager.get_template(tpl_index))
        with open(tpl_file) as tpl_new:
            tpl_text = tpl_new.read()

        file.write(tpl_text)

    file.close()


def open_question(probID, web=None):
    # global pref_manager
    global websiteObject
    if not websiteObject.logged_in:
        login()

    if webbrowser is None:
       web = manager.get("browser")
    try:
        browser = webbrowser.get(web)
    except webbrowser.Error:
        print("Invalid browser")
        return

    browser.open(websiteObject.get_question(probID))


def login(website=None):
    global websiteObject

    if website is None and manager.account is not None or website is not None and websiteObject is not None and manager.account is not None and website == manager.get_account(manager.account)[0]:
        website, username, password = manager.get_account(manager.account)
        websiteObject = websiteObject.factoryMethod(website)
    else:
        username = input("Enter your username: ")
        try:
            password = getpass.getpass("Enter your password: ")
        except getpass.GetPassWarning:
            print("Your system is not allowing us to disable echo. We cannot read your password")
            return

    if website is not None:
        websiteObject = SessionAPI.SessionAPI().factoryMethod(website)
    elif website is None and websiteObject is None:
        website = input("Enter website: ")
        websiteObject = SessionAPI.SessionAPI().factoryMethod(website)
    elif websiteObject is None:
        websiteObject = SessionAPI.SessionAPI().factoryMethod(website)

    websiteObject.login(username, password)

    if websiteObject.logged_in:
        print("Successful Login")
        manager.insertAccount(website, username, password)
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
    # global acc_manager

    website = input("Enter Website: ")
    username = input("Enter username: ")
    try:
        password = getpass.getpass("Enter your password: ")
    except getpass.GetPassWarning:
        print("Your system is not allowing us to disable echo. We cannot read your password")
        return

    manager.insertAccount(website, username, password)


def instpl(path):
    path = pathlib.Path(path)
    pathString = str(path.resolve())
    manager.insertTemplate(pathString)


def stats(website=None):
    global websiteObject
    if not websiteObject.logged_in:
        login(website)
    data = websiteObject.user_stats()
    for element in data:
        print(element, data[element])


def displayAccount():
    kap = manager.accountString()
    print(kap)


def displayTemplate():
    kap = manager.templateString()
    print(kap)


def clr():
    if websiteObject.logged_in:
        websiteObject.logout()
    websiteObject.logged_in = False
    manager.clear()


def usage():
    print(
        """
            Usage:
                ccli set browser <browser-name> | Set default browser
                ccli set acc <key> | Set default account to be used
                ccli set tpl <key> | Set default template to be used
                ccli view question <probID> <optional:Website Name> | View the problem in your browser
                ccli view solutions <optional:Website depends on Login> | View all your solutions 
                ccli view tpl | View all the templates you have saved
                ccli view accounts | View all the accounts you have saved
                ccli view stats <website> | Displays your stats in the website       
                ccli view config | Display your settings
                ccli submit <probID> <optional:path> <optional:language=None> <optional:website> | Submit your Solution
                ccli download <probID> <optional:path> <optional:Website Name> | Download the question in the path you specified 
                ccli create tpl <optional:Path of template> | Creates template
                ccli create account | Adds an account
                ccli create file <probID> <language> <optional:Path> <optional:Template Index> | Create a file for you in given path
                ccli delete tpl  <key of Template in Table> | deletes template
                ccli delete account <key of Account in Table> | deletes Account
                ccli delete config | Clear all settings
                ccli login <optional:Website Name> | Login to the given website
                ccli update <key of Account given> <new Password> | updates password
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
        if ' -' in cmd:
            flags.append(cmd)
        else:
            new_cmds.append(cmd)
    # pref_manager = manger
    commands = {

        'set':
            {
                'browser': manager.update_browser,
                'acc': manager.setDefaultAccount,
                'tpl': manager.setDefaultTemplate
            },

        'view':
            {
                'question': open_question, 'solutions': soln, 'tpl': displayTemplate,
                'accounts': displayAccount, 'stats': stats, 'config': manager.show
            },

        'submit': submit,

        'download': download,

        'create':
            {
                'tpl': instpl, 'account': insacc, 'file': create
            },

        'delete':
            {
                'tpl': manager.deleteTemplate, 'account': manager.deleteAccount, 'config': clr
            },

        'login': login,

        'update':
            {
                'account': manager.updateAccount
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
    query = sys.argv[1:]

    pathlib.Path(pathlib.Path.home() / "competitive-cli").mkdir(parents=True, exist_ok=True)

    with manager:
        if query == ["interactive"]:
            shell = InteractiveShell()
            shell.start()
        else:
            parse(query)


if __name__ == "__main__":
    main()
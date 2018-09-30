# Steps to run

```
git clone https://github.com/samyak-jain/competitive-cli
pip3 install pipenv
pipenv install --three
pipenv shell
```

```
python CLI.py set browser <browser-name> | Set default browser
python CLI.py set acc <key> | Set default account to be used
python CLI.py set tpl <key> | Set default template to be used
python CLI.py view question <probID> <optional:Website Name> | View the problem in your browser
python CLI.py view solutions <optional:Website depends on Login> | View all your solutions
python CLI.py view tpl | View all the templates you have saved
python CLI.py view accounts | View all the accounts you have saved
python CLI.py view stats <website> | Displays your stats in the website       
python CLI.py view config | Display your settings
python CLI.py submit <probID> <optional:path> <optional:language=None> <optional:website> | Submit your Solution
python CLI.py download <probID> <optional:path> <optional:Website Name> | Download the question in the path you specified
python CLI.py create tpl <optional:Path of template> | Creates template
python CLI.py create account | Adds an account
python CLI.py create file <probID> <language> <optional:Path> <optional:Template Index> | Create a file for you in given path
python CLI.py delete tpl  <key of Template in Table> | deletes template
python CLI.py delete account <key of Account in Table> | deletes Account
python CLI.py delete config | Clear all settings
python CLI.py login <optional:Website Name> | Login to the given website
python CLI.py update <key of Account given> <new Password> | updates password
```

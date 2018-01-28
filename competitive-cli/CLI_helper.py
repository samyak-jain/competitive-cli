import json
import keyring
import os
import pathlib
import prettytable


class PreferenceManager:
    file_path = pathlib.Path.home() / "competitive-cli" / "config.json"

    def __init__(self):
        """
        Creates file config.json if it doesn't already exist

        When creating a new config.json, it creates the following key-value pairs

        config.json
        {
            "templates": {} => List of templates
            "browser": Null => Browser Preference of the user
            "tpl": Null => Default template of the user
            "accounts": {} => List of accounts
            "acc": null => Default account of the user
        }

        Additional attributes of self.data
        - number_of_templates => Default value 0
        - template => Default template
        - account => Default account

        """

        if pathlib.Path(PreferenceManager.file_path).is_file():
            self.config_file = open(PreferenceManager.file_path, "r+")
        else:
            pathlib.Path(pathlib.Path.home() / "competitive-cli").mkdir(parents=True, exist_ok=True)
            self.config_file = open(PreferenceManager.file_path, "w+")

        self.config_file.seek(0)

        try:
            self.data = json.load(self.config_file)
        except json.decoder.JSONDecodeError:
            self.data = dict()
            self.data["templates"] = dict()
            self.data["browser"] = None
            self.data["tpl"] = None
            self.data["accounts"] = dict()
            self.data["acc"] = None
        # Templates
        if self.data["templates"] == {}:
            self.number_of_templates = 0
        else:
            self.number_of_templates = int(max(self.data["templates"].keys()))

        self.template = self.data["tpl"]

        #Account
        if self.data["accounts"] == {}:
            self.number_of_accounts = 0
        else:
            self.number_of_accounts = int(max(self.data["accounts"].keys()))

        self.account = self.data["acc"]

    def __enter__(self):
        return self

    # TODO: Handle Exceptions
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Update config.json with changes to self.data
        """
        self.config_file.seek(0)
        self.config_file.truncate()
        json.dump(self.data, self.config_file)
        self.config_file.close()

    @property
    def account(self):
        return self.__account

    @account.setter
    def account(self, account):
        self.__account = account
        self.data["acc"] = account

    def templateString(self):
        """
        Returns Table Of Templates set 
        :return: 
        """
        if len(self.data["templates"]) == 0:
            return "There are no templates set"

        table = prettytable.PrettyTable(["Index", "Path"])
        list_to_highlight = []

        for keys in self.data["templates"]:
            if int(keys) == self.template:
                list_to_highlight.append(keys)
            table.add_row([keys] +[self.data["templates"][keys]])

        table_string = table.get_string()
        table_list = table_string.split("\n")

        for keys in list_to_highlight:
            table_list[int(keys) + 2] = table_list[int(keys) + 2]

        return "\n".join(table_list)

    def accountString(self):
        """
        :return: Table of Accounts
        """
        if len(self.data["accounts"]) == 0:
            return "There are no accounts set"

        table = prettytable.PrettyTable(["Index", "Website", "Username"])
        list_to_highlight = []

        for keys in self.data["accounts"]:
            if int(keys) == self.account:
                list_to_highlight.append(keys)
            table.add_row([keys] + self.data["accounts"][keys])

        table_string = table.get_string()
        table_list = table_string.split("\n")

        for keys in list_to_highlight:
            table_list[int(keys) + 2] = table_list[int(keys) + 2]

        return "\n".join(table_list)

    def insertTemplate(self, path):
        """

        :param path: Path of the Template
        :return: index of the template stored
        """
        if path in self.data["templates"].values():
            return

        new_index = self.number_of_templates + 1
        self.template = new_index
        self.number_of_templates += 1

        self.data["templates"][str(new_index)] = path

        return new_index

    def deleteTemplate(self, key):
        """
        :param key: key of the template in tha table
        :return:
        """
        key = str(key)
        if key not in self.data["templates"]:
            print("Template with given index does not exist")
            return
        return_value = self.data["templates"].pop(key)
        template_keys = [int(indices) for indices in self.data["templates"].keys() if int(indices)>int(key)]
        for indices in template_keys:
            temp_value = self.data["templates"].pop(int(indices))
            self.data["templates"][str(indices-1)] = temp_value

            if self.template == indices: self.template -= 1

        self.number_of_templates -= 1

        if self.template == int(key): self.template = None

        return key,return_value


    def get_template(self, key):
        """
        :param key: index of the template in the table
        :return: template
        """
        key = str(key)
        return self.data["templates"][key]

    def setDefaultTemplate(self, key):
        """
        :param key: key of the template in the table
        Sets template according to key
        """
        self.template = int(key)

    @property
    def template(self):
        return self.__template

    @template.setter
    def template(self, template):
        self.__template = template
        self.data["tpl"] = template

    def get(self, key):
        return self.data[key]

    def update(self, key, value):
        self.data[key] = value

    def update_browser(self, browser):
        self.update("browser", browser)

    def delete(self, key):
        try:
            return_value = self.data[key]
        except KeyError:
            print("Value cannot be deleted because it doesn't exist")
            return
        self.update(key,None)
        return return_value

    def clear(self):
        """
        Remove and recreate config.json
        """
        try:
            self.config_file.close()
            os.remove(PreferenceManager.file_path)
        except OSError as e:
            print(e)
            print("Config file does not exist")

        self.__init__()

    def show(self):
        print(self.data)

    #  Account
    def insertAccount(self, website, username, password):
        """
        :param website: codeforces, UvA, codechef, etc
        :param username: username used on the website
        :param password: password used with the Account
        Account is added
        """
        if [website, username] in self.data["accounts"].values():
            return

        new_index = self.number_of_accounts + 1

        self.account = new_index
        self.number_of_accounts += 1
        self.data["accounts"][str(new_index)] = [website, username]
        keyring.set_password(website, username, password)

    def updateAccount(self, key, password):
        """
        :param key: key of the Account in the table
        :param password: password for checking Authenticity
        Updates password
        """
        key = str(key)
        if key not in self.data["accounts"]:
            print("Account with given index does not exist")
            return
        website, username = self.data["accounts"][key]
        keyring.delete_password(website, username)
        keyring.set_password(website, username, password)
        return

    def deleteAccount(self, key):
        """
        :param key: key of the Account in the Table
        Deletes Account
        """
        key = str(key)
        if key not in self.data["accounts"]:
            print("Account with given index does not exist")
            return
        return_value = self.data["accounts"].pop(key)
        account_keys = [int(indices) for indices in self.data["accounts"].keys() if int(indices)>int(key)]
        for indices in account_keys:
            temp_value = self.data["accounts"].pop(str(indices))
            self.data["accounts"][str(indices-1)] = temp_value

            if self.account == indices: self.account -= 1

        self.number_of_accounts -= 1

        if self.account == int(key): self.account = None
        keyring.delete_password(*return_value)

        return key,return_value

    def get_account(self, key):
        """
        :param key:
        :return: Name of the website, username, password
        """
        if key is None:
            print("Login to continue")
            return False

        key = str(key)
        website, username = self.data["accounts"][key]
        password = keyring.get_password(website, username)
        return website, username, password

    def setDefaultAccount(self, key):
        """
        :param key: Key of the Account in the table
        sets Default
        """
        self.account = int(key)
import json
import keyring
import os
import pathlib
import prettytable

from colors import color


class PreferenceManager:
    file_path = pathlib.Path.home() / "competitive-cli" / "config.json"

    def __init__(self):
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.config_file.seek(0)
        self.config_file.truncate()
        json.dump(self.data, self.config_file)
        self.config_file.close()

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
        try:
            os.remove(PreferenceManager.file_path)
        except OSError:
            print("Config file does not exist")

        self.__init__()

    def show(self):
        print(self.data)

class TemplateManager(PreferenceManager):
    def __init__(self):
        super().__init__()

        if self.data["templates"] == {}:
            self.number_of_templates = 0
        else:
            self.number_of_templates = int(max(self.data["templates"].keys()))

        self.common_template = self.data["tpl"]

    def __str__(self):
        if len(self.data["templates"]) == 0:
            return "There are no templates set"

        table = prettytable.PrettyTable(["Index", "Path"])
        list_to_highlight = []

        for keys in self.data["templates"]:
            if int(keys) == self.template:
                list_to_highlight.append(keys)
            table.add_row([keys] + self.data["templates"][keys])

        table_string = table.get_string()
        table_list = table_string.split("\n")

        for keys in list_to_highlight:
            table_list[int(keys) + 2] = color.BOLD + table_list[int(keys) + 2] + color.END

        return "\n".join(table_list)

    @property
    def template(self):
        return self.__template

    @template.setter
    def template(self, template):
        self.__template = template
        self.data["tpl"] = template

    def insert(self, path):
        if path in self.data["templates"].values():
            return

        new_index = self.number_of_templates + 1
        self.template = new_index
        self.number_of_templates += 1

        self.data["templates"][new_index] = path

        return new_index

    def delete(self, key):
        key = str(key)
        if key not in self.data["templates"]:
            print("Template with given index does not exist")
            return
        return_value = self.data["templates"].pop(key)
        template_keys = [int(indices) for indices in self.data["templates"].keys() if int(indices)>int(key)]
        for indices in template_keys:
            temp_value = self.data["templates"].pop(str(indices))
            self.data["templates"][str(indices-1)] = temp_value

            if self.template == indices: self.template -= 1

        self.number_of_templates -= 1

        if self.template == int(key): self.template = None

        return key,return_value

    def get_template(self, index):
        index = str(index)
        return self.data["templates"][index]

    def set_default(self, key):
        self.template = int(key)


class AccountManager(PreferenceManager):
    def __init__(self):
        super().__init__()

        if self.data["accounts"] == {}:
            self.number_of_accounts = 0
        else:
            self.number_of_accounts = int(max(self.data["accounts"].keys()))

        self.account = self.data["acc"]

    def __str__(self):
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
            table_list[int(keys) + 2] = color.BOLD + table_list[int(keys) + 2] + color.END

        return "\n".join(table_list)

    @property
    def account(self):
        return self.__account

    @account.setter
    def account(self, account):
        self.__account = account
        self.data["acc"] = account

    def insert(self, website, username, password):
        if [website, username] in self.data["accounts"].values():
            return

        new_index = self.number_of_accounts + 1

        self.account = new_index
        self.number_of_accounts += 1
        self.data["accounts"][new_index] = [website, username]
        print(self.data["accounts"][new_index])
        keyring.set_password(website, username, password)

    def update(self, key, password):
        key = str(key)
        if key not in self.data["accounts"]:
            print("Account with given index does not exist")
            return
        website, username = self.data["accounts"][key]
        keyring.delete_password(website, username)
        keyring.set_password(website, username, password)
        return

    def delete(self, key):
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

    def get_account(self, index):
        index = str(index)
        website, username = self.data["accounts"][index]
        password = keyring.get_password(website, username)
        return website, username, password

    def set_default(self, key):
        self.account = int(key)

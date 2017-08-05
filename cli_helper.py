import json
import keyring
import pathlib
import prettytable

from colors import color


class PreferenceManager:
    def __init__(self):
        if pathlib.Path(pathlib.Path.home() / "competitive-cli" / "config.json").is_file():
            self.config_file = open(pathlib.Path.home() / "competitive-cli" / "config.json", "r+")
        else:
            self.config_file = open(pathlib.Path.home() / "competitive-cli" / "config.json", "w+")

        self.config_file.seek(0)

        try:
            self.data = json.load(self.config_file)
        except json.decoder.JSONDecodeError:
            self.data = dict()
            self.data["templates"] = dict()
            self.data["browser"] = None
            self.data["mode"] = None
            self.data["common-tpl"] = None
            self.data["uva-tpl"] = None
            self.data["codechef-tpl"] = None
            self.data["accounts"] = dict()
            self.data["uva-acc"] = None
            self.data["codechef-acc"] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.config_file.seek(0)
        self.config_file.truncate()
        json.dump(self.data, self.config_file)
        self.config_file.close()

    def update(self, key, value):
        self.data[key] = value

    def update_browser(self, browser):
        self.update("browser", browser)

    def update_mode(self, mode):
        self.update("mode", mode)

    def delete(self, key):
        try:
            return_value = self.data[key]
        except KeyError:
            print("Value cannot be deleted because it doesn't exist")
            return
        self.update(key,None)
        return return_value


class TemplateManager(PreferenceManager):
    def __init__(self):
        super().__init__()

        if self.data["templates"] == {}:
            self.number_of_templates = 0
        else:
            self.number_of_templates = int(max(self.data["templates"].keys()))

        self.uva_template = self.data["uva-tpl"]
        self.codechef_template = self.data["codechef-tpl"]
        self.common_template = self.data["common-tpl"]

    def __str__(self):
        if len(self.data["templates"]) == 0:
            return "There are no templates set"

        table = prettytable.PrettyTable(["Index", "Website", "Path"])
        list_to_highlight = []

        for keys in self.data["templates"]:
            if int(keys) in [self.uva_template, self.codechef_template, self.common_template]:
                list_to_highlight.append(keys)
            table.add_row([keys] + self.data["templates"][keys])

        table_string = table.get_string()
        table_list = table_string.split("\n")

        for keys in list_to_highlight:
            table_list[int(keys) + 2] = color.BOLD + table_list[int(keys) + 2] + color.END

        return "\n".join(table_list)


    @property
    def uva_template(self):
        return self.__uva_template

    @property
    def codechef_template(self):
        return self.__codechef_template

    @property
    def common_template(self):
        return self.__common_template

    @uva_template.setter
    def uva_template(self, uva_template):
        self.__uva_template = uva_template
        self.data["uva-tpl"] = uva_template

    @codechef_template.setter
    def codechef_template(self, codechef_template):
        self.__codechef_template = codechef_template
        self.data["codechef-tpl"] = codechef_template

    @common_template.setter
    def common_template(self, common_template):
        self.__common_template = common_template
        self.data["common-tpl"] = common_template

    def insert(self, website, path):
        if [website, path] in self.data["templates"].values():
            return

        new_index = self.number_of_templates + 1

        if website == "uva":
            self.uva_template = new_index
        elif website == "codechef":
            self.codechef_template = new_index
        elif website == "common":
            self.common_template = new_index
        else:
            print("Website", website, "not supported")
            return

        self.number_of_templates += 1

        self.data["templates"][new_index] = [website, path]

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

            if self.uva_template == indices: self.uva_template -= 1
            if self.codechef_template == indices: self.codechef_template -= 1
            if self.common_template == indices: self.common_template -= 1

        self.number_of_templates -= 1

        if self.uva_template == int(key): self.uva_template = None
        if self.codechef_template == int(key): self.codechef_template = None
        if self.common_template == int(key): self.common_template = None

        return key,return_value

    def get_template(self, index):
        index = str(index)
        return self.data["templates"][index]

    def set_default(self, key):
        key = str(key)
        website = self.data["templates"][key][0]

        if website == "uva":
            self.uva_template = int(key)
        elif website == "codechef":
            self.codechef_template = int(key)
        elif website == "common":
            self.common_template = int(key)


class AccountManager(PreferenceManager):
    def __init__(self):
        super().__init__()

        if self.data["accounts"] == {}:
            self.number_of_accounts = 0
        else:
            self.number_of_accounts = int(max(self.data["accounts"].keys()))

        self.uva_account = self.data["uva-acc"]
        self.codechef_account = self.data["codechef-acc"]

    def __str__(self):
        if len(self.data["accounts"]) == 0:
            return "There are no accounts set"

        table = prettytable.PrettyTable(["Index", "Website", "Username"])
        list_to_highlight = []

        for keys in self.data["accounts"]:
            if int(keys) in [self.uva_account, self.codechef_account]:
                list_to_highlight.append(keys)
            table.add_row([keys] + self.data["accounts"][keys])

        table_string = table.get_string()
        table_list = table_string.split("\n")

        for keys in list_to_highlight:
            table_list[int(keys) + 2] = color.BOLD + table_list[int(keys) + 2] + color.END

        return "\n".join(table_list)



    @property
    def uva_account(self):
        return self.__uva_account

    @property
    def codechef_account(self):
        return self.__codechef_account

    @uva_account.setter
    def uva_account(self, uva_account):
        self.__uva_account = uva_account
        self.data["uva-acc"] = uva_account

    @codechef_account.setter
    def codechef_account(self, codechef_account):
        self.__codechef_account = codechef_account
        self.data["codechef-acc"] = codechef_account

    def insert(self, website, username, password):
        if [website, username] in self.data["accounts"].values():
            return

        new_index = self.number_of_accounts + 1

        if website == "uva":
            self.uva_account = new_index
        elif website == "codechef":
            self.codechef_account = new_index
        else:
            print("Website", website, "not supported")
            return

        self.number_of_accounts += 1
        self.data["accounts"][new_index] = [website, username]

        keyring.set_password(website, username, password)

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

            if self.uva_account == indices: self.uva_account -= 1
            if self.codechef_account == indices: self.codechef_account-= 1

        self.number_of_accounts -= 1

        if self.uva_account == int(key): self.uva_account = None
        if self.codechef_account == int(key): self.codechef_account = None

        return key,return_value

    def get_account(self, index):
        index = str(index)
        website, username = self.data["accounts"][index]
        password = keyring.get_password(website, username)
        return website, username, password

    def set_default(self, key):
        key = str(key)
        website = self.data["accounts"][key][0]

        if website == "uva":
            self.uva_account = int(key)
        elif website == "codechef":
            self.codechef_account = int(key)




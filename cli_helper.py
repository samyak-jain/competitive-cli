import pathlib
import json
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.config_file.seek(0)
        self.config_file.truncate()
        json.dump(self.data, self.config_file)
        self.config_file.close()

    def update(self, key, value):
        self.data[key] = value

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

    def __repr__(self):
        return f"TemplateManager(number_of_templates={self.number_of_templates!r},uva_template={self.uva_template!r}, \
        codechef_template={self.codechef_template!r},common_template={self.common_template!r})"

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
        new_index = self.number_of_templates

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
    pass

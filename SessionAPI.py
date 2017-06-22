import requests
import lxml.html
import os


class UvaSession:
    UVA_HOST = "https://uva.onlinejudge.org/"
    SUBMIT_PATH = UVA_HOST + "index.php?option=com_onlinejudge&Itemid=25&page=save_submission"
    language_handler = {
        ".c": "1", "c": "1",
        ".java": "2", "java": "2",
        ".cpp": "5", "c++": "5", "c++11": "5",
        ".pas": "4", "pascal": "4",
        ".py": "6", "python": "6",
        "C++03": "3", "C++98": "3"
    }

    def __init__(self):
        self.uva_session = requests.session()

    @staticmethod
    def find_file(filename, path):
        for root, dirs, file in os.walk(path):
            for files in file:
                if filename in files:
                    return os.path.join(root, files), files
        raise IOError("File does not exist")

    @staticmethod
    def find_language(filename):
        extension_index = filename.find(".")
        file_extension = filename[extension_index:]
        try:
            return UvaSession.language_handler[file_extension]
        except KeyError:
            print("The file extension cannot be inferred. Please manually enter the relevant language")

    def login(self, username, password):
        get_response = self.uva_session.get(UvaSession.UVA_HOST)
        login_text = lxml.html.fromstring(get_response.text)
        hidden_inputs = login_text.xpath(r'//form//input[@type="hidden"]')
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs if x.attrib['name'] not in ["cx", "ie"]}
        form["username"] = username
        form["passwd"] = password
        form["remember"] = "yes"
        return self.uva_session.post(UvaSession.UVA_HOST + "index.php?option=com_comprofiler&task=login", data=form,
                                     allow_redirects=False, headers={"referer": UvaSession.UVA_HOST})

    def submit(self, probNum, path=".", language=None):
        file_path, filename = UvaSession.find_file(probNum,path)
        probFile = open(file_path)

        if language is None:
            language_number = UvaSession.find_language(filename)
        else:
            language_number = UvaSession.language_handler[language]

        if language_number is None:
            return

        payload = {
            "localid": probNum,
            "code": probFile.read(),
            "language": language_number,
            "codeupl": "",
            "problemid": "",
            "category": "",
            "submit": "Submit"
        }

        updated_headers = {
            "Referer": UvaSession.UVA_HOST + "index.php?option=com_onlinejudge&Itemid=25",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Host": "uva.onlinejudge.org",
            "Origin": UvaSession.UVA_HOST
        }

        return self.uva_session.post(UvaSession.SUBMIT_PATH, data=payload, headers=updated_headers)








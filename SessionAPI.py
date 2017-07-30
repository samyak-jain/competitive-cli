import requests
import lxml.html
import os
from bs4 import BeautifulSoup as bs


class SessionAPI:

    @staticmethod
    def find_file(filename, path):
        for root, dirs, file in os.walk(path):
            for files in file:
                if filename in files:
                    return os.path.join(root, files), files
        raise IOError("File does not exist")

    @classmethod
    def find_language(cls, filename):
        """
            to return the language code of the question to be submitted
            :return:language code
        """
        extension_index = filename.find(".")
        file_extension = filename[extension_index:]
        try:
            return cls.language_handler[file_extension.lower()]
        except KeyError:
            print("The file extension cannot be inferred. Please manually enter the relevant language")


class UvaSession(SessionAPI):
    UVA_HOST = "https://uva.onlinejudge.org/"
    SUBMIT_PATH = UVA_HOST + "index.php?option=com_onlinejudge&Itemid=25&page=save_submission"
    language_handler = {
        ".c": "1", "c": "1",
        ".java": "2", "java": "2",
        ".cpp": "5", "c++": "5", "c++11": "5",
        ".pas": "4", "pascal": "4",
        ".py": "6", "python": "6",
        "c++03": "3", "c++98": "3"
    }

    def __init__(self):
        self.uva_session = requests.session()

    def login(self, username, password):
        get_response = self.uva_session.get(UvaSession.UVA_HOST)
        login_text = lxml.html.fromstring(get_response.text)
        hidden_inputs = login_text.xpath(r'//form//input[@type="hidden"]')
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs if x.attrib['name'] not in ["cx", "ie"]}
        form["username"] = username
        form["passwd"] = password
        form["remember"] = "yes"
        login_response = self.uva_session.post(UvaSession.UVA_HOST + "index.php?option=com_comprofiler&task=login", data=form,
                                     allow_redirects=False, headers={"referer": UvaSession.UVA_HOST})
        return login_response

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

        # TODO: Check for success


class CodechefSession(SessionAPI):
    codechef_url = "https://www.codechef.com"

    language_handler = {
        'cpp': '44',
        'c': '11',
        'c#': '27',
        'go': '114',
        'javascript': '56',
        'java': '10',
        'php': '29',
        'python3': '116',
        'python2': '4'
    }

    def __init__(self):
        self.codechef_session = requests.session()

    def login(self, username="", password=""):
        # logging in without credentials
        html_page = self.codechef_session.get(CodechefSession.codechef_url)
        soup = bs(html_page.content, 'html5lib')
        form_build_id = soup.find('input', {'name': 'form_build_id'})['value']
        payload = {
            'name': username,
            'pass': password,
            'form_build_id': form_build_id,
            'form_id': 'new_login_form',
            'op': 'Login'
        }

        # session = requests.session()
        response = self.codechef_session.post(CodechefSession.codechef_url, data=payload)

        # removing extra sessions using simple scraping and form handling
        while response.url == CodechefSession.codechef_url + '/session/limit':
            soup = bs(response.content, 'html5lib')
            value = soup.find('input', attrs={'class', 'form-radio'})['value']
            form_build_id = soup.find('input', {'name': 'form_build_id'})['value']
            form_token = soup.find('input', {'name': 'form_token'})['value']
            # print form_build_id
            payload = {
                'sid': value,
                'op': 'Disconnect session',
                'form_build_id': form_build_id,
                'form_token': form_token,
                'form_id': 'session_limit_page'
            }
            response = self.codechef_session.post(CodechefSession.codechef_url + '/session/limit', data=payload)
        return response

    def submit(self, question_code, path, language):
        file_path, file_name = CodechefSession.find_file(question_code, path)
        lang = self.find_language(language)
        html_page = self.codechef_session.get(self.codechef_url + '/submit/' + question_code )
        soup = bs(html_page.content, 'html5lib')
        # print soup

        form_build_id = soup.find('input', {'name': 'form_build_id'})['value']
        form_token = soup.find('input', {'name': 'form_token'})['value']

        payload ={
            'form_build_id': form_build_id,
            "form_token": form_token,
            'form_id': 'problem_submission',
            "files[sourcefile]": "",
            "language": lang,
            'problem_code': question_code,
            'op': "Submit"
        }

        file = {
            "files[sourcefile]": open(file_path)
        }

        response = self.codechef_session.post(CodechefSession.codechef_url + '/submit/' + question_code, data=payload, files=file, verify=False)

        return response.url.split('/')[-1]

    def check_result(self, submission_id, question_code):
        """
        returns the result of a problem submission.
        :return: result
        Responses
        - right answer
        - wrong answer
        - Compilation error
        - Runtime Error
        """
        response = self.codechef_session.get(CodechefSession.codechef_url + '/status/' + question_code)
        soup = bs(response.content,'html5lib')
        result = soup.find(text=str(submission_id)).parent.parent.find('span')['title']
        if result == "":
            return "correct answer"
        else:
            return result


    def logout(self):
        """
        logout
        :return: nothing
        """
        return self.codechef_session.get(CodechefSession.codechef_url + '/logout')






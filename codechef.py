from login import login
import os
import requests
from bs4 import BeautifulSoup as bs


class CodechefSession:
    codechef_url = "https://www.codechef.com"

    language_list = {
        'cpp': '44',
        'c': '11',
        'c#': '27',
        'java': '10',
        'php': '29',
        'python3': '116',
        'python2': '4'
    }

    def __init__(self):
        self.codechef_session = requests.session

    def login(self, username="", password=""):
        # logging in without credentials
        payload = {
            'name': username,
            'pass': password,
            'form_build_id': 'form-0k32rjFWt649_E48uCImFOjVzLRUAQmCw16nVQ_nrMM',
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
            print form_build_id
            payload = {
                'sid': value,
                'op': 'Disconnect session',
                'form_build_id': form_build_id,
                'form_token': form_token,
                'form_id': 'session_limit_page'
            }
            response = self.codechef_session.post(CodechefSession.codechef_url + '/session/limit', data=payload)

        return response

    @staticmethod
    def find_language(path):
        """
        to return the language code of the question to be submitted
        :return:language code
        """
        extension_index = path.find('.')
        lang = path[extension_index:]
        try:
            return CodechefSession.language_list[lang]
        except:
            print "The file name is invalid or cannot be retrieved .Please enter language manually"


    def submit(self, question_code, path):
        """
        This function is to submit an answer to codechef
        :param question_code: name-code of the question whose answer u have to submit
        :param path: The address of the solution in your system
        :return: String-submission id to be used for checking the result
        """
        file_open = open(path)
        code = file_open.read()
        response = self.get(CodechefSession.codechef_url + '/submit/' + question_code)
        print response


# How To use
# from codechef import CodechefSession
# session = CodechefSession()
# session.login('username','password')
# session.submit('ques_code','file_path')






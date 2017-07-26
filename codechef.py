import os
import requests
import re
from bs4 import BeautifulSoup as bs


class CodechefSession:
    codechef_url = "https://www.codechef.com"

    language_list = {
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

    @staticmethod
    def find_file(filename, path):
        for root, dirs, file in os.walk(path):
            for files in file:
                if filename in files:
                    return os.path.join(root, files), files
        raise IOError("File does not exist")

    @staticmethod
    def find_language(language):
        """
        to return the language code of the question to be submitted
        :return:language code
        """
        try:
            return CodechefSession.language_list[language.lower()]
        except:
            print "The file name is invalid or cannot be retrieved .Please enter language manually"


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


    def info_present_contests(self):
        """
        to check all present contests in codechef
        :return: list of present contests with contest name and date
        """
        contests = []
        response = self.codechef_session.get(CodechefSession.codechef_url + '/contests')
        soup = bs(response.content,'html5lib')
        table = soup.find_all('table', attrs={'class', 'dataTable'})[0]
        for tr in table.find("tbody").find_all("tr"):
            # for td in tr.find_all("td"):
            #     print td.contents
            contest_description = tr.find_all("td")
            reg = {
                'contest_name': contest_description[0].get_text(),
                'contest_type': contest_description[1].get_text(),
                'contest_date_start': contest_description[2].get_text(),
                'contest_date_end': contest_description[3].get_text()
            }
            contests.append(reg)
        return contests

    def info_future_contests(self):
        """
        to check all present contests in codechef
        :return: list of present contests with contest name and date
        """
        contests = []
        response = self.codechef_session.get(CodechefSession.codechef_url + '/contests')
        soup = bs(response.content,'html5lib')
        table = soup.find_all('table', attrs={'class', 'dataTable'})[1]
        for tr in table.find("tbody").find_all("tr"):
            contest_description = tr.find_all("td")
            reg = {
                'contest_name': contest_description[0].get_text(),
                'contest_type': contest_description[1].get_text(),
                'contest_date_start': contest_description[2].get_text(),
                'contest_date_end': contest_description[3].get_text()
            }
            contests.append(reg)
        return contests
        # print table


# How To use
# from codechef import CodechefSession
# session = CodechefSession()
# session.login('username','password')
# session.submit('ques_code','file_path')






import requests
import lxml.html
import os
from bs4 import BeautifulSoup as bs
import json


class SessionAPI:
    language_handler = {}

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
    UVA_HOST = r"https://uva.onlinejudge.org/"
    SUBMIT_PATH = UVA_HOST + r"index.php?option=com_onlinejudge&Itemid=25&page=save_submission"
    UHUNT_API = r"http://uhunt.felix-halim.net/api/p/num/"

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
        # print hidden_inputs
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs if x.attrib['name'] not in ["cx", "ie"]}
        form["username"] = username
        form["passwd"] = password
        form["remember"] = "yes"
        login_response = self.uva_session.post(UvaSession.UVA_HOST + "index.php?option=com_comprofiler&task=login",
                                               data=form,
                                               allow_redirects=False, headers={"referer": UvaSession.UVA_HOST})
        return login_response

    def submit(self, probNum, path=".", language=None):
        file_path, filename = UvaSession.find_file(probNum, path)
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

    @staticmethod
    def get_question_url(probID):
        prob_json = json.loads(
            requests.get(UvaSession.UHUNT_API + str(probID)).text
        )
        return r"https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem=" + str(prob_json["pid"])


class CodechefSession(SessionAPI):
    codechef_url = r"https://www.codechef.com"

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
        self.username = ""

    def login(self, username="", password=""):

        # logging in without credentials
        self.username = username
        response_page = self.codechef_session.get(CodechefSession.codechef_url)
        html_page = lxml.html.fromstring(response_page.text)
        hidden_inputs = html_page.xpath(
            r'//form//input[@type="hidden"]'
        )
        payload = {i.attrib["name"]: i.attrib["value"]
                   for i in hidden_inputs}
        payload['name'] = username
        payload['pass'] = password
        payload['op'] = 'Login'
        response = self.codechef_session.post(CodechefSession.codechef_url, data=payload)

        # removing extra sessions using simple scraping and form handling
        while response.url == CodechefSession.codechef_url + '/session/limit':
            html_page = lxml.html.fromstring(response.text)
            all_inputs = html_page.xpath(r'//form//input')
            payload = {i.attrib["name"]: i.attrib["value"] for i in all_inputs[::-1]}

            response = self.codechef_session.post(CodechefSession.codechef_url + '/session/limit', data=payload)
        return response

    def submit(self, question_code, path=".", language=None):
        contest = ""
        for contests in self.info_present_contests():
            for contest_ques in CodechefSession.ques_in_contest(contests['contest_name']):
                if contest_ques == question_code:
                    contest = '/' + contests['contest_name']
                    break

        file_path, file_name = CodechefSession.find_file(question_code, path)
        lang = CodechefSession.language_handler[language]
        response = self.codechef_session.get(
            self.codechef_url + contest + '/submit/' + question_code
        )

        html_page = lxml.html.fromstring(response.text)
        hidden_inputs = html_page.xpath(r'//form//input[@type="hidden"]')
        payload = {i.attrib['name']: i.attrib['value'] for i in hidden_inputs}
        payload['language'] = lang
        payload['problem_code'] = question_code
        payload['op'] = 'Submit'

        file = {
            "files[sourcefile]": open(file_path)
        }

        response = self.codechef_session.post(CodechefSession.codechef_url + contest + '/submit/' + question_code,
                                              data=payload,
                                              files=file,
                                              verify=False
                                              )

        return int(response.url.split('/')[-1])
    
    @staticmethod
    def ques_in_contest(contest_name):
        response = json.loads(
            requests.get(
                CodechefSession.codechef_url + '/api/contests/'+contest_name
            ).text
        )

        return response['problems'].keys()

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
        soup = bs(response.text,'lxml')
        result = soup.find(text=str(submission_id)).parent.parent.find('span')['title']
        if result == "":
            return "Correct Answer"
        else:
            return result

    def logout(self):
        """
        logout
        :return: logout response
        """
        return self.codechef_session.get(CodechefSession.codechef_url + '/logout')

    def info_present_contests(self):
        """
        to check all present contests in codechef
        :return: list of present contests with contest name and date
        """
        contests = []
        response = self.codechef_session.get(CodechefSession.codechef_url + '/contests')
        soup = bs(response.content, 'html5lib')
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

    def question_url(self, question_code):
        contest = ""
        for contests in self.info_present_contests():
            for contest_ques in self.ques_in_contest(contests['contest_name']):
                if contest_ques == question_code:
                    contest = '/' + contests['contest_name']
                    break

        url = self.codechef_url + contest + '/problems/' + question_code
        return url

    def display_sub(self, prob_code="", contest_code="", year="", language="All"):
        """
        To get submission status... enter the above fields for filtering
        :param prob_code: (optional) prob_code
        :param contest_code: (optional) contest_code
        :param year:  (optional)
        :param language: (optional)
        :return: list of submissions with question status
        """
        param = {
            'pcode':prob_code,
            'ccode':contest_code,
            'year':year,
            'language':language,
            'handle':self.username
        }
        response = self.codechef_session.get(self.codechef_url+'/submissions',
                                  params=param)
        soup = bs(response.content,'html5lib')
        table = soup.find('table', attrs={'class', 'dataTable'})
        stats = []
        for tr in table.find('tbody').findAll('tr'):
            td = tr.find_all('td')
            stats.append(
                {
                    'id':td[0].get_text(),
                    'date':td[1].get_text(),
                    'question':td[3].get_text(),
                    'contest':td[4].get_text(),
                    'status':td[5].find('span')['title']
                }
            )
        return stats


class CodeForce(SessionAPI):
    FORCE_HOST = r"http://codeforces.com/"
    FORCE_LOGIN = r"http://codeforces.com/enter?back=%2F"
    language = {
        'GNU GCC 5.1.0': '10',
        'GNU GCC C11 5.10': '43',
        'GNU G++ 5.1.0': '1',
        'GNU G++11 5.1.0': '42',
        'GNU G++14 6.2.0': '50',
        'Microsoft Visual C++ 2010': '2',
        'C# Mono 3.12.1.0': '9',
        'MS C# .NET 4.0.30319': '29',
        'D DMD32 v2.071.2': '28',
        'Go 1.7.3': '32',
        'Haskell GHC 7.8.3': '12',
        'Java 1.8.0_112': '36',
        'Kotlin 1.0.5-2': '48',
        'OCaml 4.02.1': '19',
        'Delphi 7': '3',
        'Free Pascal 2.6.4': '4',
        'Perl 5.20.1': '13',
        'PHP 7.0.12': '6',
        'Python 2.7.12': '7',
        'Python 3.5.2': '31',
        'PyPy 2.7.10 (2.6.1)': '40',
        'PyPy 3.2.5 (2.4.0)': '41',
        'Ruby 2.0.0p645': '8',
        'Rust 1.12.1': '49',
        'Scala 2.11.8': '20',
        'Javascript V8 4.8.0': '34'
    }

    language_handler = {'.rb': '8',
                        '.cpp': '50',
                        '.c': '50',
                        '.py': '31',
                        '.php': '6',
                        '.go': '32',
                        '.js': '34',
                        '.java': '36',
                        '.pas': '4',
                        '.rs': '49',
                        '.rslib': '49',
                        '.scala': '20',
                        '.sc': '20',
                        '.hs': '12',
                        '.lhs': '12',
                        '.cs': '29',
                        '.ml': '19',
                        '.mli': '19',
                        '.kt': '48',
                        '.kts': '48', }

    def __init__(self):
        self.code_sess = requests.session()

    def login(self, username, password):
        login = self.code_sess.get(CodeForce.FORCE_LOGIN)
        login = bs(login.text, "lxml")
        login = login.find('form', id='linkEnterForm')
        hidden = login.find_all('input')
        form = {
            'csrf_token': hidden[0]['value'],
            'action': 'enter',
            'ftaa': hidden[1]['value'],
            'bfaa': hidden[2]['value'],
            'handle': username,
            'password': password,
            '_tta': ''
        }
        header = {
            'Host': 'codeforces.com',
            'Origin': 'http://codeforces.com',
            'Referer': CodeForce.FORCE_LOGIN,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.115 Safari/537.36'
        }
        login_response = self.code_sess.post(CodeForce.FORCE_LOGIN, data=form, headers=header)
        login_soup = bs(login_response.text, 'lxml')

        return username == login_soup.find('a', href='/profile/' + username).text

    # check result of the LATEST submission made
    def check_result(self, username):
        response = self.code_sess.get(CodeForce.FORCE_HOST + "submissions/" + username)
        soup = bs(response.text, 'lxml')
        table = soup.find_all('tr')
        table_data = [["Submission Id", "When", "Who", "Problem", "Language", "Verdict", "Time", "Memory"]]
        row = list()
        for element in table[26].find_all('td'):
            row.append("".join(element.text.split()))
        table_data.append(row)
        return table_data

    # finds the csrf_token for the logout link and signs out user
    def logout(self, username):
        loginpage = self.code_sess.get(CodeForce.FORCE_HOST)
        soup = bs(loginpage.text, "lxml")
        csrf = soup.find('a', href='/profile/' + username)
        logout_link = "http://codeforces.com" + csrf.find_next_sibling('a')['href']
        self.code_sess.get(logout_link)

    def submit(self, question_id, path, username, lang=None):
        file_path, filename = CodeForce.find_file(question_id, path)
        submit_link = CodeForce.FORCE_HOST + "problemset/submit"
        sub_request = self.code_sess.get(submit_link)
        subsoup = bs(sub_request.text, 'lxml')
        hidden = subsoup.find('form', class_='submit-form')
        hidden = hidden.find_all('input')

        # uncomment this to list compiler list_compiler()
        if not lang:
            compiler = CodeForce.find_language(filename)
        else:
            compiler = CodeForce.language['lang']

        form = {
            'csrf_token': hidden[0]['value'],
            'ftaa': hidden[1]['value'],
            'bfaa': hidden[2]['value'],
            'action': 'submitSolutionFormSubmitted',
            'submittedProblemCode': question_id,
            'programTypeId': compiler,
            'source': '',
            'tabsize': hidden[6]['value'],
            'sourceFile': open(file_path),
            '_tta': ''
        }

        response = self.code_sess.post(submit_link, data=form)
        if response == CodeForce.FORCE_HOST + "problemset/status":
            return self.check_result(username)
        else:
            return "Error submitting"

    # List out all the submissions made till date
    def display_sub(self, username):
        submit_link = CodeForce.FORCE_HOST + "submissions/" + username
        submit_page = self.code_sess.get(submit_link)
        submit_soup = bs(submit_page.text, 'lxml')
        table = submit_soup.find_all('tr')
        table_data = [["Submission Id", "When", "Who", "Problem", "Language", "Verdict", "Time", "Memory"]]
        for row in range(26, len(table) - 1):
            new_row = list()
            for element in table[row].find_all('td'):
                new_row.append("".join(element.text.split()))
            table_data.append(new_row)
        return table_data

    def check_question_status(self, questionid, username):
        table_data = self.display_sub(username)
        data = list()
        for row in table_data[1:]:
            if questionid == row[3]:
                data.append(row)
        return data

    @staticmethod
    def question_url(questionid):
        question_link = CodeForce.FORCE_HOST + "problemset/problem/" + questionid[:3] + "/" + questionid[3:]
        return question_link

    def user_stats(self, username):
        info_page = self.code_sess.get(CodeForce.FORCE_HOST + "profile/" + username)
        info_soup = bs(info_page.text, 'lxml')
        info_div = info_soup.find('div', class_='info')
        user_rank = info_div.find('div', class_='user-rank').text.strip()
        li = info_div.find_all('li')
        table_data = self.display_sub(username)
        solved = 0

        for row in table_data[1:]:
            if row[5] == 'Accepted':
                solved += 1

        user_info = {
            'user_rank': user_rank,
            'Contribution': li[0].span.text,
            li[1].text.strip()[:9]: li[1].text.strip()[10:],
            'Last-Visit': li[5].span.text.strip(),
            'Registered': li[6].span.text.strip(),
            'solved-questions': solved
        }
        return user_info

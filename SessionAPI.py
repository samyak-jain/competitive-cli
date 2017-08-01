import requests
import lxml.html
import os
from bs4 import BeautifulSoup as bs


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
        print hidden_inputs
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

    def login(self, username="", password=""):
        # logging in without credentials
        response_page = self.codechef_session.get(CodechefSession.codechef_url)
        html_page = lxml.html.fromstring(response_page.text)
        hidden_inputs = html_page.xpath(r'//form//input[@type="hidden"]')
        # print hidden_inputs
        payload = {i.attrib["name"]: i.attrib["value"] for i in hidden_inputs}
        payload['name'] = username
        payload['pass'] = password
        payload['op'] = 'Login'
        response = self.codechef_session.post(CodechefSession.codechef_url, data=payload)
        #
        # removing extra sessions using simple scraping and form handling
        while response.url == CodechefSession.codechef_url + '/session/limit':
            html_page = lxml.html.fromstring(response.text)
            all_inputs = html_page.xpath(r'//form//input')
            payload = {i.attrib["name"]: i.attrib["value"] for i in all_inputs[::-1]}

            response = self.codechef_session.post(CodechefSession.codechef_url + '/session/limit', data=payload)
        return response

    def submit(self, question_code, path=".",language=None, contest=""):

        for contests in self.info_present_contests():
            if(contests['contest_name'] == contest):
                contest = contest+'/'

        # print self.info_present_contests()
        file_path, file_name = CodechefSession.find_file(question_code, path)
        lang = CodechefSession.language_handler[language]
        response = self.codechef_session.get(self.codechef_url  + '/submit/' + contest + question_code )
        html_page = lxml.html.fromstring(response.text)
        hidden_inputs = html_page.xpath(r'//form//input[@type="hidden"]')
        print hidden_inputs
        payload = {i.attrib['name']: i.attrib['value'] for i in hidden_inputs}
        if contest == "":
            payload['language'] = lang
        payload['problem_code'] = question_code
        payload['op'] = 'Submit'

        file = {
            "files[sourcefile]": open(file_path)
        }

        response = self.codechef_session.post(CodechefSession.codechef_url + '/submit/' + question_code, data=payload,
                                                files=file, verify=False)

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
        to check all future contests in codechef
        :return: list of future contests with contest name and date
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

# To-do : submit for contest just check if the contest is in present contests or not if then submit


class CodeForce(SessionAPI):
    FORCE_HOST = r"http://codeforces.com/"
    FORCE_LOGIN = r"http://codeforces.com/enter?back=%2F"
    language_handler = {
        '44': 'GNU GCC 5.1.0',
        '43': 'GNU GCC C11 5.10',
        '1': 'GNU G++ 5.1.0',
        '42': 'GNU G++11 5.1.0',
        '50': 'GNU G++14 6.2.0',
        '2': 'Microsoft Visual C++ 2010',
        '9': 'C# Mono 3.12.1.0',
        '29': 'MS C# .NET 4.0.30319',
        '28': 'D DMD32 v2.071.2',
        '32': 'Go 1.7.3',
        '12': 'Haskell GHC 7.8.3',
        '36': 'Java 1.8.0_112',
        '48': 'Kotlin 1.0.5-2',
        '19': 'OCaml 4.02.1',
        '3': 'Delphi 7',
        '4': 'Free Pascal 2.6.4',
        '13': 'Perl 5.20.1',
        '6': 'PHP 7.0.12',
        '7': 'Python 2.7.12',
        '31': 'Python 3.5.2',
        '40': 'PyPy 2.7.10 (2.6.1)',
        '41': 'PyPy 3.2.5 (2.4.0)',
        '8': 'Ruby 2.0.0p645',
        '49': 'Rust 1.12.1',
        '20': 'Scala 2.11.8',
        '34': 'Javascript V8 4.8.0'
    }

    def __init__(self):
        self.code_sess = requests.session()

    def login(self, username, password):
        login = self.code_sess.get(CodeForce.FORCE_LOGIN)
        login = bs(login.text, "lxml")
        login = login.find('form', id='linkEnterForm')
        hidden = login.find_all('input')
        form = {'csrf_token': hidden[0]['value'],
                'action': 'enter',
                'ftaa': hidden[1]['value'],
                'bfaa': hidden[2]['value'],
                'handle': username,
                'password': password,
                '_tta': ''}
        header = {'Host': 'codeforces.com',
                  'Origin': 'http://codeforces.com',
                  'Referer': CodeForce.FORCE_LOGIN,
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        return self.code_sess.post(CodeForce.FORCE_LOGIN, data=form, headers=header)

    # lists the available compiler According to the id and name
    @staticmethod
    def list_compiler():
        for i in CodeForce.language_handler:
            print(i, ' :', CodeForce.language_handler[i])

    # prompt the user to choose compiler id
    @staticmethod
    def choose_compiler(compilerid):
        if compilerid not in CodeForce.language_handler.keys():
            print("Invalid choice")
            return False
        else:
            return compilerid

    # check result of the LATEST submission made
    def check_result(self, username):
        response = self.code_sess.get(CodeForce.FORCE_HOST + "submissions/" + username)
        soup = bs(response.text, 'lxml')
        result = soup.find_all('span', class_='submissionVerdictWrapper')
        return result[0].text

    # finds the csrf_token for the logout link and signs out user
    def logout(self, username):
        loginpage = self.code_sess.get(CodeForce.FORCE_HOST)
        soup = bs(loginpage.text, "lxml")
        csrf = soup.find('a', href='/profile/'+username)
        logout_link = "http://codeforces.com"+csrf.find_next_sibling('a')['href']
        self.code_sess.get(logout_link)

    def submit(self, question_id, path):
        file_path, filename = CodeForce.find_file(question_id, path)
        submit_link = CodeForce.FORCE_HOST+"problemset/submit"
        sub_request = self.code_sess.get(submit_link)
        subsoup = bs(sub_request.text, 'lxml')
        hidden = subsoup.find('form', class_='submit-form')
        hidden = hidden.find_all('input')

        # uncomment this to list compiler list_compiler()
        compiler = input('Enter The Compiler Id according to the Compiler id list')
        if CodeForce.choose_compiler(compiler):
            form = {'csrf_token': hidden[0]['value'],
                    'ftaa': hidden[1]['value'],
                    'bfaa': hidden[2]['value'],
                    'action': 'submitSolutionFormSubmitted',
                    'submittedProblemCode': question_id,
                    'programTypeId': compiler,
                    'source': '',
                    'tabsize': hidden[6]['value'],
                    'sourceFile': open(file_path),
                    '_tta': ''}
            response = self.code_sess.post(submit_link, data=form)
            if response == CodeForce.FORCE_HOST+"problemset/status":
                print("Submitted Successfully")
            else:
                print("Error submitting")

    # List out all the submissions made till date
    def display_sub(self, username):
        submit_link = CodeForce.FORCE_HOST + "submissions/" + username
        submit_page = self.code_sess.get(submit_link)
        submit_soup = bs(submit_page.text, 'lxml')
        table = submit_soup.find_all('tr')
        table_data = [["Submission Id", "When", "Who", "Problem", "Language", "Verdict", "Time", "Memory"]]
        for row in range(26, len(table)):
            new_row = list()
            for element in table[row].find_all('td'):
                new_row.append(element.text.remove(" "))
            table_data.append(new_row)

        return table_data

    @staticmethod
    def return_question_url(questionid):
        question_link = CodeForce.FORCE_HOST + "problemset/problem/" + questionid[:3] + "/" + questionid[3:]
        return question_link


# Spot any errors? => contact me ASAP

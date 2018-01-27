import re
import requests
import lxml.html
import os
from bs4 import BeautifulSoup as bs
import json
import datetime
import difflib


class SessionAPI:
    # TODO: Improve handler
    language_handler = {
        "c++": ".cpp",
        "c": ".c",
        "python": ".py",
        "java": ".java",
        "pascal": ".pas",
        "ruby": ".rb"
    }

    def __init__(self):
        self.logged_in = False
        self.username = None

    @staticmethod
    def find_file(filename, path):
        for root, dirs, file in os.walk(path):
            for files in file:
                if filename in files:
                    return os.path.join(root, files), files
        print("File does not exist")

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

    @staticmethod
    def factoryMethod(website):
        if website == 'uva':
            return UvaSession()
        if website == 'codechef':
            return CodechefSession()
        if website == 'codeforces':
            return CodeForce()

class udebug:

    uva_link = "https://www.udebug.com/"
    translator = {
        'uva': 'UVa',
        'google-code-jam': 'GCJ',
        'dev-skill': 'DS',
        'cats-online-judge': 'CATS',
        'uri-online-judge': 'URI',
        'light-online-judge': 'LOJ',
        'acm-icpc-live-archive': 'LA',
        'facebook-hacker-cup': 'FBHC'
    }

    @staticmethod
    def phase_one(problem_id, judge):
        question_link = udebug.uva_link + udebug.translator[judge] + '/' + problem_id
        input_link = "https://www.udebug.com/udebug-custom-get-selected-input-ajax"
        problem_soup = bs(requests.get(question_link).text, 'lxml')
        input_nid = problem_soup.find('tr', class_='odd').find('a')['data-id']
        form = {
            'input_nid': input_nid
        }
        inputs = requests.post(input_link, data=form).json()['input_value']
        hidden = problem_soup.find('form', id="udebug-custom-problem-view-input-output-form").find_all('input')
        payload = {
            'problem_nid': hidden[0]['value'],
            'input_data': inputs,
            'node_nid': hidden[1]['value'],
            'op': hidden[2]['value'],
            'output_data': '',
            'user_output': '',
            'form_build_id': hidden[5]['value'],
            'form_id': hidden[-2]['value']}
        response = requests.post(question_link, data=payload)
        response_soup = bs(response.text, 'lxml')
        accepted_output = response_soup.find('textarea', id='edit-output-data').text
        try:
            file = open('logs/' + problem_id + '_Accepted.txt', 'w')
        except FileNotFoundError:
            os.makedirs('logs')
            file = open('logs/' + problem_id + '_Accepted.txt', 'w')
        file.write(accepted_output)
        file.close()
        return os.stat('logs/' + problem_id + '_Accepted.txt').st_size != 0

    @staticmethod
    def phase_two(file_path, problem_id):
        """
        checks the differences between the user output and the Accepted Output.
        it returns the additions or deletions to be done to the user output file.
        **important the addition list and subtraction list give us the lines to be added or subtracted from the
        first file respectively.**
        :return:
        if output is not identical
        dictionary containing:
        No. of additions(int),
        No. of subtractions(int),
        No. of differences between the two files(int),
        additions list(list containing additions to be made to the first file),
        subtractions list(list containing subtractions to be made to the first file_,
        details(list containing additions and subtractions together i.e. the whole diff file.)
        :else:
        :return: Success message if output is identical.
        """
        accepted = open('logs/' + problem_id + '_Accepted.txt', 'r')
        user_output = open(file_path, 'r')
        det = list()
        for line in difflib.unified_diff(user_output.readlines(), accepted.readlines(), fromfile='Your Output',
                                         tofile='Accepted Output', lineterm=''):
            if line[0] != ' ':
                det.append(line)
        accepted.close()
        user_output.close()
        if det:
            add_list = [i for i in det if i[0] == '+']
            diff_list = [j for j in det if j[0] == '-']
            details = {'additions': len(add_list) - 1,
                       'subtractions': len(diff_list) - 1,
                       'differences': len(diff_list) + len(add_list) - 2,
                       'add_list': add_list[1:],
                       'diff_list': diff_list[1:],
                       'details': det}
            return details
        return "Your Output matches the accepted Output!"
        # mark I

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

    translator = {
        '10': 'Submission error',
        '15': "Can't be judged",
        '20': 'In queue',
        '30': 'Compile error',
        '35': 'Restricted function',
        '40': 'Runtime error',
        '45': 'Output limit',
        '50': 'Time limit',
        '60': 'Memory limit',
        '70': 'Wrong answer',
        '80': 'PresentationE',
        '90': 'Accepted',
        '1': 'ANSI C',
        '2': 'Java',
        '3': 'C++',
        '4': 'Pascal',
        '5': 'C++11',
        '6': 'Python'
    }

    def __init__(self):
        super().__init__()
        self.uva_session = requests.session()

    def login(self, username, password):
        """
        logs the user in and returns a bool value
        stores the username in self.username.
        """
        get_response = self.uva_session.get(UvaSession.UVA_HOST)
        login_text = lxml.html.fromstring(get_response.text)
        hidden_inputs = login_text.xpath(r'//form//input[@type="hidden"]')
        # print hidden_inputs
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs if x.attrib['name'] not in ["cx", "ie"]}
        form["username"] = username
        form["passwd"] = password
        form["remember"] = "yes"
        login_response = self.uva_session.post(UvaSession.UVA_HOST + "index.php?option=com_comprofiler&task=login",
                                               data=form, headers={"referer": UvaSession.UVA_HOST})

        self.logged_in = login_response.url == UvaSession.UVA_HOST
        if (self.logged_in): self.username = username
        return self.logged_in

    def submit(self, probNum, path=".", language=None):
        """
        submits the problem according to the problem Number of the question.
        returns a list containing the submission details about the question.
        """
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

        resp = self.uva_session.post(UvaSession.SUBMIT_PATH, data=payload, headers=updated_headers)
        submission_id = resp.url[resp.url.find('ID')+3:]
        return self.check_result(submission_id, probNum)

    def check_result(self, submission_id, probNum):
        """
        checks the result of the latest submission and returns a list containing submission details.
        """
        username = self.username
        min_id = str(int(submission_id)-1)
        judge_id = requests.get("http://uhunt.felix-halim.net/api/uname2uid/" + username).text
        check = json.loads(requests.get('http://uhunt.felix-halim.net/api/subs-user/'+judge_id+'/'+min_id).text)
        subs = check['subs']
        translated_table = [
            ['Submission ID', 'Problem ID', 'Verdict ID', 'Runtime', 'Submission Time', 'Language', 'Rank']]
        if not subs[0]:
            return None
        else:
            while subs[0][2] in ['0', '20']:
                check = json.loads(requests.get('http://uhunt.felix-halim.net/api/subs-user/' + judge_id + '/' + min_id).text)
                subs = check['subs']
            translated_row = list(map(str, subs[0]))
            translated_row[1] = probNum
            translated_row[2] = UvaSession.translator[translated_row[2]]
            translated_row[4] = datetime.datetime.fromtimestamp(int(translated_row[4])).strftime('%Y-%m-%d %H:%M:%S')
            translated_row[5] = UvaSession.translator[translated_row[5]]
            if translated_row[6] == '-1':
                translated_row[6] = 'No Rank'
            translated_table.append(translated_row)
        return translated_table

    @staticmethod
    def display_sub(username):
        """
        returns the submission details of all the submissions made till date for the particular user.
        """
        judge_id = requests.get("http://uhunt.felix-halim.net/api/uname2uid/" + username).text
        check = json.loads(requests.get('http://uhunt.felix-halim.net/api/subs-user/' + judge_id).text)
        subs = check['subs']
        translated_table = [
            ['Submission ID', 'Problem Number', 'Verdict ID', 'Runtime', 'Submission Time', 'Language', 'Rank']]
        uhunt_num = 'http://uhunt.onlinejudge.org/api/p/id/'
        for row in subs:
            translated_row = list(map(str,row))
            translated_row[1] = json.loads(requests.get(uhunt_num + translated_row[1]).text)['num']
            translated_row[2] = UvaSession.translator[translated_row[2]]
            translated_row[4] = datetime.datetime.fromtimestamp(int(translated_row[4])).strftime('%Y-%m-%d %H:%M:%S')
            translated_row[5] = UvaSession.translator[translated_row[5]]
            if translated_row[6] == '-1':
                translated_row[6] = 'No Rank'
            translated_table.append(translated_row)
        return translated_table

    def user_stats(self, username):
        """
            Returns a Dictionary containing
            'Hits',
            'online Status',
            'Member Since',
            'Last Online',
            'submissions',
            'Tried',
            'Solved',
            'First Submission',
            'Last Submission',
            from My Statistics on the user-feed
            """
        stat = "https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=15"
        account = "https://uva.onlinejudge.org/index.php?option=com_comprofiler&Itemid=3"
        stat_page = self.uva_session.get(stat)
        stat_soup = bs(stat_page.text, 'lxml')
        stat_table = stat_soup.find_all('table')
        stats = stat_table[2].find('tr').find_all('td')
        acc = self.uva_session.get(account)
        account_soup = bs(acc.text, 'lxml')
        account_table = account_soup.find_all('table')
        td = account_table[3].find_all('td')
        data = {x.text: y.text for x, y in zip(td[0::2], td[1::2])}

        list_of_headings = ["submissions", "Tried", "Solved", "First Submission", "Last Submission"]

        for index, heading in enumerate(list_of_headings):
            data[heading] = stats[index].text

        return data

    @staticmethod
    def check_question_status(username, prob_Num):
        """
        checks the status of the given question i.e. submission details of the particular question.
        returns a list of lists containing the details.
        """
        judge_id = requests.get("http://uhunt.felix-halim.net/api/uname2uid/"+username).text
        prob_json = json.loads(
            requests.get(UvaSession.UHUNT_API + str(prob_Num)).text
        )
        pid = str(prob_json['pid'])
        subs = json.loads(requests.get("http://uhunt.felix-halim.net/api/subs-pids/" + judge_id + "/" + pid).text)
        submission_table = subs[judge_id]['subs']
        translated_table = [['Submission ID', 'Problem Number', 'Verdict ID', 'Runtime', 'Submission Time', 'Language', 'Rank']]
        for row in submission_table:
            translated_row = list(map(str,row))
            translated_row[1] = prob_Num
            translated_row[2] = UvaSession.translator[translated_row[2]]
            translated_row[4] = datetime.datetime.fromtimestamp(int(translated_row[4])).strftime('%Y-%m-%d %H:%M:%S')
            translated_row[5] = UvaSession.translator[translated_row[5]]
            if translated_row[6] == '-1':
                translated_row[6] = 'No Rank'
            translated_table.append(translated_row)
        return translated_table

    @staticmethod
    def get_question(prob_Num):
        """
        gets the problem number of the question and returns the question link.
        """
        prob_json = json.loads(
            requests.get(UvaSession.UHUNT_API + str(prob_Num)).text
        )
        url = r"https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem=" + str(
            prob_json["pid"])
        return url

    def logout(self, username):
        pass

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
        'python2': '4',
        'ada': '7',
        'assembler': '13',
        'bash': '28',
        'ocaml': '8',
        'clojure': '111',
        'clips': '14',
        'd': '20',
        'erlang': '36',
        'fortran': '5',
        'f#': '124',
        'haskell': '21',
        'icon': '16',
        'clisp': '32',
        'lua': '26',
        'nice': '25',
        'pascal': '22',
        'perl': '3',
        'perl6': '4',
        'pypy': '99',
        'scala': '39',
        'ruby': '17',
        'text': '62',
        'tcl': '38',
        'whitespace': '6'

    }

    def __init__(self):
        super().__init__()
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
        soup = bs(response.content, 'lxml')
        name = soup.find(text=username)

        self.logged_in = bool(name)
        if self.logged_in: self.username = username
        return self.logged_in


    def submit(self, question_code, path=".", language=None):
        contest = ""
        for contests in self.info_present_contests():
            for contest_ques in CodechefSession.ques_in_contest(contests['contest_name']):
                if contest_ques == question_code:
                    contest = '/' + contests['contest_name']
                    break
        file_path = path
        # file_path, file_name = CodechefSession.find_file(question_code, path)
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
                                              files=file
                                              )

        sub_id = response.url.split('/')[-1]
        return sub_id , self.check_result(sub_id, question_code)

    @staticmethod
    def ques_in_contest(contest_name):
        response = requests.get(
            CodechefSession.codechef_url + '/api/contests/' + contest_name
        )

        response = response.json()

        if response['status'] == 'error':
            return []
        ques_list = response['problems'].keys()
        return list(ques_list)

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
        table = None

        result = [['Sub-Task', 'Task', 'Score', "Result(time)"]]
        header = {
            'authority': CodechefSession.codechef_url,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36'
        }
        # unwanted_results = ['compiling..', 'running..', 'waiting..', 'running judge..']
        while table is None:
            response = self.codechef_session.get(CodechefSession.codechef_url +\
                                                 '/viewsolution/' +\
                                                 submission_id, headers=header)

            try:
                soup = bs(response.text, 'html5lib')
                table = soup.find('table', attrs={'class', 'status-table'}).find_all('tr')
            except:
                pass

        for tr in table[1:]:
            rel = []

            for td in tr.find_all('td'):
                rel.append(td.get_text())

            for k in range(4-len(rel)):
                rel.append(' ')
            result.append(rel)


        # balancing the tables
        return result

    def logout(self, username):
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

    def get_question(self, question_code):
        contest = ""
        for contests in self.info_present_contests():
            for contest_ques in CodechefSession.ques_in_contest(contests['contest_name']):
                if contest_ques == question_code:
                    contest = '/' + contests['contest_name']
                    break

        url = self.codechef_url + contest + '/problems/' + question_code
        return url

    def display_sub(self, username, prob_code="", contest_code="", year="", language="All"):
        """
        To get submission status... enter the above fields for filtering
        :param prob_code: (optional) prob_code
        :param contest_code: (optional) contest_code
        :param year:  (optional)
        :param language: (optional)
        :return: list of submissions with question status
        """
        param = {
            'pcode': prob_code,
            'ccode': contest_code,
            'year': year,
            'language': language,
            'handle': self.username
        }
        response = self.codechef_session.get(self.codechef_url + '/submissions', params=param)
        soup = bs(response.content, 'html5lib')
        table = soup.find('table', attrs={'class', 'dataTable'})
        stats = []
        for tr in table.find('tbody').findAll('tr'):
            td = tr.find_all('td')
            stats.append(
                {
                    'id': td[0].get_text(),
                    'date': td[1].get_text(),
                    'question': td[3].get_text(),
                    'contest': td[4].get_text(),
                    'status': td[5].find('span')['title']
                }
            )
        return stats

    def user_stats(self, username):
        response = requests.get(CodechefSession.codechef_url + '/users/' + self.username)
        # print(response.url)
        soup = bs(response.content, 'html5lib')
        name = soup.findAll('h2')[-1].get_text()
        username = self.username
        country = soup.find('span', attrs={'class', 'user-country-name'}).get_text()
        codechef_rating = soup.find('div', attrs={'class', 'rating-number'}).get_text()
        rank = soup.find('div', attrs={'class', 'rating-ranks'}).findAll('li')
        global_rank = rank[0].get_text().split()[0]
        country_rank = rank[1].get_text().split()[0]
        solved = soup.find('h3', text="Problems Solved").parent.findAll('h5')
        fully_solved = "".join(re.findall(r'\d+', solved[0].get_text()))
        partially_solved = "".join(re.findall(r'\d+', solved[1].get_text()))

        return({
            'name': name,
            'username': username,
            'country': country,
            'codechef-rating': codechef_rating,
            'global-rank': global_rank,
            'country-rank': country_rank,
            'completely solved questions': fully_solved,
            'partially solved question': partially_solved})


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
        super().__init__()
        self.code_sess = requests.session()
        self.username = ''

    def login(self, username, password):
        """
        logs the user in.
        :param username:
        :param password:
        :return: bool value.
        """
        self.username = username
        login = self.code_sess.get(CodeForce.FORCE_LOGIN)
        if login.status_code == 503:
            print("Server Down")
            return False
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

        try:
            self.logged_in = username == login_soup.find('a', href='/profile/' + username).text
        except AttributeError:
            return False

        if self.username: self.username = username
        return self.logged_in

    def check_result(self):
        """
        check result of the LATEST submission made
        :return: the latest submission.
        """
        response = self.code_sess.get(CodeForce.FORCE_HOST + "submissions/" + self.username)
        soup = bs(response.text, 'lxml')
        table_data = [["Submission Id", "When", "Who", "Problem", "Language", "Verdict", "Time", "Memory"]]
        row = list()
        trap = soup.find('span', class_='submissionVerdictWrapper').text.lower()
        while 'running' in trap:
            page = self.code_sess.get(CodeForce.FORCE_HOST + "submissions/" + self.username)
            soup = bs(page.text, 'lxml')
            trap = soup.find('span', class_='submissionVerdictWrapper').text.lower()
        table = soup.find_all('tr')
        for element in table[26].find_all('td'):
            row.append("".join(element.text.split()))
        table_data.append(row)
        return table_data


    def logout(self):
        """
        finds the csrf_token for the logout link and signs out user
        :param username:
        :return: the logout link.
        """
        loginpage = self.code_sess.get(CodeForce.FORCE_HOST)
        soup = bs(loginpage.text, "lxml")
        csrf = soup.find('a', href='/profile/' + self.username)
        logout_link = "http://codeforces.com" + csrf.find_next_sibling('a')['href']
        return self.code_sess.get(logout_link)

    def submit(self, question_id, path, lang=None):
        """
        gets the language from the file extension or as user input and submits the file to the website.
        :return: bool value specifying whether the function succeeded.
        """
        file_path, filename = CodeForce.find_file(question_id, path)
        submit_link = CodeForce.FORCE_HOST + "problemset/submit"
        sub_request = self.code_sess.get(submit_link)
        subsoup = bs(sub_request.text, 'lxml')
        hidden = subsoup.find('form', class_='submit-form')
        hidden = hidden.find_all('input')

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
            return self.check_result()
        else:
            return False

    def display_sub(self):
        """
        :return: list of lists containing the submission details
        """
        submit_link = CodeForce.FORCE_HOST + "submissions/" + self.username
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

    def check_question_status(self, questionid):
        """

        :return: list of lists containing the submission data of the given question id.
        """
        table_data = self.display_sub()
        data = list()
        for row in table_data[1:]:
            if questionid in row[3]:
                data.append(row)
        return data

    @staticmethod
    def get_question(questionid):
        """
        :return:  the question link.
        """
        question_link = CodeForce.FORCE_HOST + "problemset/problem/" + questionid[:3] + "/" + questionid[3:]
        return question_link

    def user_stats(self):
        """
        :return: users personal details as a dictionary.
        """
        info_page = self.code_sess.get(CodeForce.FORCE_HOST + "profile/" + self.username)
        info_soup = bs(info_page.text, 'lxml')
        info_div = info_soup.find('div', class_='info')
        user_rank = info_div.find('div', class_='user-rank').text.strip()
        li = info_div.find_all('li')
        table_data = self.display_sub()
        solved = 0

        for row in table_data[1:]:
            if row[5] == 'Accepted':
                solved += 1

        user_info = {
            'user_rank': user_rank,
            'Contribution': li[0].span.text,
            'Friend of': li[1].text.strip()[10:],
            'Last-Visit': li[5].span.text.strip(),
            'Registered': li[6].span.text.strip(),
            'solved-questions': solved
        }
        return user_info


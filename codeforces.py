import requests
import os
from bs4 import BeautifulSoup as bs


class CodeForce:
    FORCE_HOST = "http://codeforces.com/"
    FORCE_LOGIN = "http://codeforces.com/enter?back=%2F"
    language_list = {
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
        hidden = login.find_all('input', type='hidden')
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

    @staticmethod
    def find_file(filename, path):
        for root, dirs, file in os.walk(path):
            for files in file:
                if filename in files:
                    return os.path.join(root, files), files
        raise IOError('File does not exist')

    # lists the available compiler According to the id and name
    @staticmethod
    def list_compiler():
        for i in CodeForce.language_list:
            print(i, ' :', CodeForce.language_list[i])

    # prompt the user to choose compiler id
    @staticmethod
    def choose_compiler(compilerid):
        if compilerid not in CodeForce.language_list.keys():
            return "Invalid choice"
        else:
            return compilerid

    # check result of the submission made
    def check_result(self, username):
        response = self.code_sess.get(CodeForce.FORCE_LOGIN + "submissions/" + username)
        soup = bs(response.content, 'lxml')
        result = soup.find_all('span', class_='submissionVerdictWrapper')
        return result[0].text

    # finds the csrf_token for the logout link and signs out user
    def logout(self):
        loginpage = self.code_sess.get(CodeForce.FORCE_HOST)
        soup = bs(loginpage, "lxml")
        bar = bs(str(soup.find_all('div', class_='lang-chooser')))
        bar = bar.find_all('a')
        bar = bar[-1]['href']
        return self.code_sess.get(CodeForce.FORCE_HOST + bar)

        # To Do:
        # def submit():
        # qustion info

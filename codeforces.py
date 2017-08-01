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
        submit_link = CodeForce.FORCE_HOST+"submissions/"+username
        submit_page = self.code_sess.get(submit_link)
        submit_soup = bs(submit_page.text, 'lxml')
        table = submit_soup.find_all('tr')
        print('  #  ' + '    When    ' + '           Who    ' + '    Problem    ' + '      Lang    ' + '    Verdict    ' + '   Time ' + 'Memory')
        for i in range(26, len(table)):
            for j in table[i].find_all('td'):
                new = "".join(j.text.split())
                print(new, end=" ")
            print()

    # display the question according to question id
    def display_ques(self, questionid):
        question_link = CodeForce.FORCE_HOST+"problemset/problem/"+questionid[:3]+"/"+questionid[3:]
        question_response = self.code_sess.get(question_link)
        question_soup = bs(question_response.text, 'lxml')
        input_specification = question_soup.find('div', class_='input-specification')
        paragraph = input_specification.find_previous_sibling('div')
        output_specification = question_soup.find('div', class_='output-specification')
        header = question_soup.find('div', class_='header')
        question_text = ""
        for i in header.find_all('div'):
            if "".join(i['class']) != 'property-title':
                question_text += i.text
        question_text += "\n"
        for i in paragraph.find_all('p'):
            question_text += i.text
        question_text += "\nInput:"
        for i in input_specification.find_all('p'):
            question_text += i.text
        question_text += "\nOutput:"
        for i in output_specification.find_all('p'):
            question_text += i.text
        print(question_text)

# Spot any errors? => contact me ASAP

import requests
from bs4 import BeautifulSoup as bs
import difflib

uva_link = "https://www.udebug.com/UVa/"


def phase_one(problem_id):
    input_link = "https://www.udebug.com/udebug-custom-get-selected-input-ajax"
    problem_soup = bs(uva_link+problem_id, 'lxml')
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
    response = requests.post(uva_link+problem_id, data=payload)
    response_soup = bs(response.text, 'lxml')
    accepted_output = response_soup.find('textarea', id='edit-output-data').text
    file = open('/logs/Accepted.txt', 'w')
    file.write(accepted_output)


def phase_two(file_path):
    accepted = file.open('/logs/Accepted.txt', 'r')
    user_output = file.open(file_path, 'r')
    det = list()
    for line in difflib.unified_diff(user_output.readlines(), accepted.readlines(), fromfile='Your Output', tofile='Accepted Output', lineterm=''):
        if line[0] != ' ':
            det.append(line)
    if det:
        add_list = [i for i in det if i[0] == '+']
        diff_list = [j for j in det if j[0] == '-']
        details = {'additions': len(add_list)-1,
                   'subtractions': len(diff_list)-1,
                   'differences': len(diff_list)+len(add_list)-2,
                   'add_list': add_list[1:],
                   'diff_list': diff_list[1:],
                   'details': det}
        return details
    return "Your Output matches the accepted Output!"
# mark I


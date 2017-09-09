import requests
from bs4 import BeautifulSoup as bs
import difflib
import os

uva_link = "https://www.udebug.com/"
translator = {
    'uva' : 'UVa',
    'google-code-jam': 'GCJ',
    'dev-skill': 'DS',
    'cats-online-judge': 'CATS',
    'uri-online-judge': 'URI',
    'light-online-judge': 'LOJ',
    'acm-icpc-live-archive': 'LA',
    'facebook-hacker-cup': 'FBHC'
}

def phase_one(problem_id, judge):
    question_link = uva_link+translator[judge]+'/'+problem_id
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
        file = open('logs/'+ problem_id +'_Accepted.txt', 'w')
    except FileNotFoundError:
        os.makedirs('logs')
        file = open('logs/' + problem_id + '_Accepted.txt', 'w')
    file.write(accepted_output)
    file.close()


def phase_two(file_path,problem_id):
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
    accepted = open('logs/'+ problem_id +'_Accepted.txt', 'r')
    user_output = open(file_path, 'r')
    det = list()
    for line in difflib.unified_diff(user_output.readlines(), accepted.readlines(), fromfile='Your Output', tofile='Accepted Output', lineterm=''):
        if line[0] != ' ':
            det.append(line)
    accepted.close()
    user_output.close()
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


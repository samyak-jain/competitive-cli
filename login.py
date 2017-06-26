# login inside code chef with login credentials i.e username and password
# method for removing sessions- remove previous cookies by selecting radio buttons on codechef.com/session/limit

def login(username="", password=""):
    # important libraries
    import requests
    from bs4 import BeautifulSoup as bs

    # logging in without credentials
    url = "https://www.codechef.com/"
    payload = {
        'name': username,
        'pass': password,
        'form_build_id': 'form-0k32rjFWt649_E48uCImFOjVzLRUAQmCw16nVQ_nrMM',
        'form_id': 'new_login_form',
        'op': 'Login'
    }

    session = requests.session()
    response = session.post(url, data=payload)

    # removing extra sessions using simple scraping and form handling
    while response.url == 'https://www.codechef.com/session/limit':
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
        response = session.post("https://www.codechef.com/session/limit", data=payload)

    return response

# how to use
# from login import login
# browser = login(username,password)  use this for first time login
# html_page = response.content
# soup = BeautifulSoup(html_page) and then further scrapping

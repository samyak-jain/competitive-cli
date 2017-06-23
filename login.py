# login inside code chef with login credentials i.e username and password
# method for removing sessions- remove previous cookies by selecting radio buttons on codechef.com/session/limit

def login(username="", password=""):

    # important libraries
    import mechanize
    from bs4 import BeautifulSoup as bs

    br = mechanize.Browser()

    # login using login credentials
    br.set_handle_robots(False)
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)

    br.open("https://www.codechef.com")
    br.select_form(predicate=lambda frm: 'id' in frm.attrs and frm.attrs['id'] == 'new-login-form')

    br['name'] = username
    br['pass'] = password

    br.method = "POST"
    response = br.submit()
    # print response.read

    # removing extra sessions using simple scraping and form handling
    while br.geturl() == 'https://www.codechef.com/session/limit':
        br.select_form(predicate=lambda frm: 'id' in frm.attrs and frm.attrs['id'] == 'session-limit-page')
        soup = bs(response, 'html5lib')
        value = soup.find('input', attrs={'class','form-radio'})['value']
        br.form['sid'] = [value]
        br.method = "POST"
        response = br.submit()

    return br

# how to use
# from login import login
# browser = login(username,password)  use this for first time login
# html_page = browser.login("https://www.codechef.com/node")
# soup = BeautifulSoup(html_page) and then further scrapping


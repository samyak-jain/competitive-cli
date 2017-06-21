# login inside code chef with login credentials i.e username and password

# things left - if pre logged in simultaneous 2 sessions are not allowed (deleting cookies before logging in)
# method - delete previous cookies when asking for credentials.

def login(username="", password=""):

    # important libraries
    import mechanize
    import cookielib

    br = mechanize.Browser()

    # deleting previous cookies
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

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
    return br

# how to use
# from login import login
# browser = login(username,password)  use this for first time login
# html_page = browser.login("https://www.codechef.com/node")
# soup = BeautifulSoup(html_page) and then further scrapping

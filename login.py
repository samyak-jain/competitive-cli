# login inside code chef with login credentials i.e username and password

# things left - if pre logged in simultaneous 2 sessions are not allowed
# method - either delete previous cookies when asking for credentials or *still in process*

def login(username="", password=""):

    # important libraries
    import mechanize

    # login using login credentials

    br = mechanize.Browser()
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
    # print response
    return br


from codechef import CodechefSession

session = CodechefSession()
c=session.login('apuayush','**********')
p=session.submit('RGAME','F:\projects\testcli.py','python2')
print p.url
print p.content
try:
    session.logout()
except:
    print 'Not logged out'
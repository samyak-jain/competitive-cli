from codechef import CodechefSession

session = CodechefSession()
c=session.login('username','**')
p=session.submit('RGAME','F:\projects','python2')
print p
try:
    session.logout()
except:
    print 'Not logged out'
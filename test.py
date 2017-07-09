from codechef import CodechefSession
import time

session = CodechefSession()
c=session.login('username','password')
p=session.submit('RGAME','F:\projects','python2')
# sleep becomes online compiler is taking time so msg not generated so fast
time.sleep(15)
result = session.check_result(p,'RGAME')
print result
session.logout()

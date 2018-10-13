from requests_html import HTMLSession
import json
from urllib.parse import unquote
import uuid
import subprocess


def run_cpp(probNum, input):
    subUrl = f"https://www.codechef.com/status/{probNum}?sort_by=Time&sorting_order=asc&language=44&status=15&handle="
    with HTMLSession() as sess:
        resp = sess.get(subUrl)
        subID = resp.html.find("#primary-content > div > div.tablebox-section.l-float > table > tbody > "
                               "tr:nth-child(1) > td:nth-child(1)", first=True).text

        solUrl = f"https://www.codechef.com/viewsolution/{subID}"
        solResp = sess.get(solUrl)
        solution = solResp.html.find("#meta-info", first=True).text
        obj = json.loads(solution)
        code = unquote(obj['data']['plaintext'])
        randomHash = str(uuid.uuid4().hex)
        fileName = f"temp_code_{randomHash}.cpp"
        with open(fileName, "w") as temp:
            temp.write(code)

        subprocess.call(["g++", fileName, "-std=c++14"])
        run = subprocess.run(["./a.out"], stdout=subprocess.PIPE, input=input, encoding='ascii')
        output = run.stdout
        subprocess.call(["rm", fileName, 'a.out'])
        return output

import json
import os
import traceback
import tornado.httpserver
import tornado.ioloop
import tornado.web
from run_cpp import run_cpp
from tornado.options import define, options
import tornado.escape

define("port", default=8080, help="runs on the given port", type=int)


class MyAppException(tornado.web.HTTPError):
    pass


class BaseHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.write(json.dumps({
                        'status_code': status_code,
                        'message': self._reason,
                        'traceback': lines,
                }))
        else:
            self.write(json.dumps({
                    'status_code': status_code,
                    'message': self._reason,
                }))


class RunProgram(BaseHandler):
    async def get(self):
        user_input = self.get_argument("input")
        probNumber = self.get_argument("pno")
        output = run_cpp(probNumber, user_input)

        self.write(json.dumps({
            'status_Code': 200,
            'result': output
        }))


class TestHandler(BaseHandler):
    async def get(self):
        self.write(json.dumps({
            'status_code': 200,
            'message': 'success'
        }))


if __name__ == "__main__":
    options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", RunProgram),
            (r"/test", TestHandler)
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(os.environ.get("PORT", options.port))
    tornado.ioloop.IOLoop.instance().start()

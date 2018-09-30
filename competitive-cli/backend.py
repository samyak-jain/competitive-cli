import json
import os
import traceback
import tornado.httpserver
import tornado.ioloop
import tornado.web
from motor import motor_tornado
from tornado.gen import coroutine
from tornado.options import define, options
import tornado.escape

define("port", default=8080, help="runs on the given port", type=int)


class MyAppException(tornado.web.HTTPError):
    pass


class BaseHandler(tornado.web.RequestHandler):

    def db(self):
        clientz = self.settings['db_client']
        db = clientz.data
        return db

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


class PutData(BaseHandler):
    def get(self):
        data = self.get_argument("data")
        db = self.db().data
        db.insert_one({"data": data})
        self.write(json.dumps({
            'success': 200
        }))

if __name__ == "__main__":
    options.parse_command_line()
    client = motor_tornado.MotorClient("mongodb://"+os.environ['tornado_user']+":"+ os.environ['tornado_pass']
                                       +"@ds117605.mlab.com:17605/data")
    app = tornado.web.Application(
        handlers=[
            (r"/", PutData)
        ],
        db_client=client
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(os.environ.get("PORT", options.port))
    tornado.ioloop.IOLoop.instance().start()

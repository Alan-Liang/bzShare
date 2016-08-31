
import re
import tornado

from bzs import files
from bzs import const

class StaticHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'HEAD']

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        file_path = re.sub(r'^/static/', './static/', self.request.uri)

        # In case it does not exist.
        try:
            future = tornado.concurrent.Future()
            def get_file_data_async():
                file_data = files.get_static_data(file_path)
                future.set_result(file_data)
            tornado.ioloop.IOLoop.instance().add_callback(get_file_data_async)
            file_data = yield future
        except Exception:
            self.set_status(404, "Not Found")
            self._headers = tornado.httputil.HTTPHeaders()
            self.add_header('Content-Length', '0')
            self.flush()
            return None

        # File actually exists, sending data
        self.set_status(200, "OK")
        self._headers = tornado.httputil.HTTPHeaders()
        self.add_header('Cache-Control', 'max-age=0')
        self.add_header('Connection', 'close')
        self.add_header('Content-Type', files.guess_mime_type(file_path))
        self.add_header('Content-Length', str(len(file_data)))
        self.write(file_data)
        self.flush()
        self.finish()
        return self

    head=get
    pass

from flask import Flask, _request_ctx_stack
from flask.app import setupmethod
from flask import request_started, request_finished

class CustomFlask(Flask):
    def __init__(self, *args, **kw):
        super(CustomFlask, self).__init__(*args, **kw)
        self.before_response_funcs = {}

    @setupmethod
    def before_response(self, f):
        self.before_response_funcs.setdefault(None, []).append(f)

    def preprocess_response(self, rv):

        for func in self.before_response_funcs.get(None, ()):
            rv = func(rv)
        return rv

    def full_dispatch_request(self):
        """Dispatches the request and on top of that performs request
        pre and postprocessing as well as HTTP exception catching and
        error handling.

        .. versionadded:: 0.7
        """
        self.try_trigger_before_first_request_functions()
        try:
            request_started.send(self)
            rv = self.preprocess_request()
            if rv is None:
                rv = self.dispatch_request()
        except Exception as e:
            rv = self.handle_user_exception(e)
        rv = self.preprocess_response(rv)
        response = self.make_response(rv)
        response = self.process_response(response)
        request_finished.send(self, response=response)
        return response


    #def make_response(self, rv):
    #    """Overwrite Flask's make_response to support return dict and list in endpoint.

    #    :param rv: a instance(string, dict, list) or a tuple(instance, status_code, headers)

    #    `ref(1) <http://flask.pocoo.org/docs/0.11/api/#flask.Flask.make_response>`
    #    `ref(2) <https://github.com/pallets/flask/blob/0.10.1/flask/app.py#L1532>`

    #    """
    #    status = headers = None
    #    if isinstance(rv, tuple):
    #        rv, status, headers = rv + (None,) * (3 - len(rv))

    #    if isinstance(rv, (dict, list)):
    #        rv = json.dumps(rv)  # , **JSON_OPTIONS
    #        if headers is None:
    #            headers = {}
    #        headers['content-type'] = 'application/json'
    #        if "callback" in request.args:
    #            rv = "window.%s(%s);" % (request.args["callback"], rv)
    #            headers['content-type'] = 'application/javascript'
    #    rv = (rv, status, headers,)
    #    return super(CustomFlask, self).make_response(rv)

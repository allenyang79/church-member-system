import json


class InvalidError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super(InvalidError, self).__init__(message)
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        ret = {
            'success': False,
            'message': self.message
        }
        if self.payload:
            ret['payload'] = json.dumps(self.payload)
        return ret


class AccessDenyError(InvalidError):
    def __init__(self, message='access deny', status_code=403, payload=None):
        super(AccessDenyError, self).__init__(message=message,
            status_code=403,
            payload = payload
        )


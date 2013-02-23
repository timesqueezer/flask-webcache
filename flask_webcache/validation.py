from datetime import datetime
from httplib import NOT_IMPLEMENTED, NOT_MODIFIED, OK
import hashlib

from flask import request

class Validation(object):
    def can_set_etag(self, response):
        return not (
            response.is_streamed or
            'etag' in response.headers or
            response.status_code != OK
        )
    def set_etag(self, response):
        response.set_etag(hashlib.md5(response.data).hexdigest())

    def if_none_match(self, response):
        if response.status[0] != '2' and response.status_code != NOT_MODIFIED:
            return False
        etag, weak = response.get_etag()
        return etag in request.if_none_match
    def return_not_modified_response(self, response):
        if request.method not in {"GET", "HEAD"}:
            # HACK: RFC says we MUST NOT have performed this method, but it was
            #        just performed and there's nothing we can do about it.
            #       To handle this request correctly, the application logic
            #        of this app should have made the if-none-match check and
            #        abort() with 412 PRECONDITION_FAILED.
            #       Not sure what to do, I'm opting to return the 5xx status
            #        501 NOT_IMPLEMENTED. Meh.
            response.status_code = NOT_IMPLEMENTED
            return
        response.data = ''
        response.status_code = NOT_MODIFIED
    def update_last_modified(self, response):
        response.last_modified = datetime.now()

import gevent

from RequestsLibrary import RequestsLibrary

class MultithreadHttpManager(RequestsLibrary):
    ROBOT_LIBRARY_SCOPE = 'Global'

    def get_concurrency(self, alias, uri, headers=None, threads=1):
        threads = int(threads)
        greenlets = [ gevent.spawn(self.get, alias=alias,
                uri=uri,headers=headers) for x in range(threads) ]
        gevent.joinall(greenlets, raise_error=True)
        responses = [greenlet.value for greenlet in greenlets]
        return responses

    def put_concurrency(self, alias, uri, data=None, headers=None, threads=1):
        threads = int(threads)
        self.builtin.log('DATA to send: %s' % data, 'DEBUG')
        if data:
            greenlets = [ gevent.spawn(self.put, alias=alias,
                    uri=uri,data=body,headers=headers) for body in data ]
        else:
            greenlets = [ gevent.spawn(self.put, alias=alias,
                    uri=uri,headers=headers) for x in range(threads) ]
        gevent.joinall(greenlets, raise_error=True)
        responses = [greenlet.value for greenlet in greenlets]
        return responses

from .base_signer import BaseSigner

import base64
import hashlib
import hmac
import re

class V1Signer(BaseSigner):
    def __init__(self, digest):
        super(V1Signer, self).__init__(digest)

    def signable(self, request, authheaders):
        method = request.method.upper()
        md5 = hashlib.md5()
        if request.body is not None:
            md5.update(request.body)
        bodyhash = md5.hexdigest()
        ctype = request.get_header("content-type")
        date = request.get_header("date")
        cheaders = []
        cheader_first = True
        cheaders_sign = ''
        if "headers" in authheaders:
            cheaders = authheaders["headers"].split(";")
        cheaders.sort()
        for cheader in cheaders:
            if cheader_first:
                cheader_first = False
            else:
                cheaders_sign += '\n'
            cheaders_sign += '{0}: {1}'.format(cheader.lower(), request.get_header(cheader))
        requri = request.url.request_uri()

        return '{0}\n{1}\n{2}\n{3}\n{4}\n{5}'.format(method, bodyhash, ctype, date, cheaders_sign, requri)

    def sign(self, request, authheaders, secret):
        mac = hmac.HMAC(secret.encode('utf-8'), digestmod=self.digest)
        mac.update(self.signable(request, authheaders).encode('utf-8'))
        digest = mac.digest()
        return base64.b64encode(digest).decode('utf-8')

    def matches(self, header):
        if re.match(r'(?i)^\s*Acquia\s*[^:]+\s*:\s*[0-9a-zA-Z\\+/=]+\s*$', header) is not None:
            return True
        return False
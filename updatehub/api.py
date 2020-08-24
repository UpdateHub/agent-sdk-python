# Copyright (C) 2018 O.S. Systems Software LTDA.
"""
Use this package to get information and logs, and to execute actions on the
agent, like probing for new updates and aborting updates currently under way.
"""

try:
    from urllib2 import HTTPError
    from urllib2 import Request
    from urllib2 import urlopen
    from urlparse import urlparse
except ImportError:
    from urllib.error import HTTPError
    from urllib.parse import urlparse
    from urllib.request import Request
    from urllib.request import urlopen

import json


class Api:
    """
    Api class used to access the agent API. Must be executed on the host that
    is running the agent.
    """
    ABORT_PATH = "/update/download/abort"
    """
    Path to abort a download.
    """
    INFO_PATH = "/info"
    """
    Path to get information about the host, the system and the agent.
    """
    LOG_PATH = "/log"
    """
    Path to get logs about the agent execution.
    """
    PROBE_PATH = "/probe"
    """
    Path to trigger a new probe for updates.
    """
    LOCAL_INSTALL_PATH = "/local_install"
    """
    Path to trigger the installation of a local package.
    """
    REMOTE_INSTALL_PATH = "/remote_install"
    """
    Path to trigger the installation of a package from a direct URL.
    """
    SERVER_URL = "http://localhost:8080"
    """
    URL to the agent API.
    """

    def set_url(self, url):
        """
        Set a different URL than default.
        """
        p_url = urlparse(url)
        if not p_url.netloc:
            p_url = urlparse('http://'+url)
        self.__class__.SERVER_URL = "{scheme}://{hostname}:{port}"\
            .format(scheme=p_url.scheme,
                    hostname=p_url.hostname,
                    port=p_url.port)

    def abort_download(self):
        """
        Abort a currently executing download.
        """
        return self._request('POST', self.__class__.ABORT_PATH)

    def get_info(self):
        """
        Get information about the system.
        """
        return self._request('GET', self.__class__.INFO_PATH)

    def get_log(self):
        """
        Get logs of the agent.
        """
        return self._request('GET', self.__class__.LOG_PATH)

    def probe(self, host=None):
        """
        Initiate a probe looking for a new update.
        """
        data = None
        if host is not None:
            data = {"custom_server": host}
        return self._request('POST', self.__class__.PROBE_PATH, data)

    def local_install(self, path):
        """
        Requests the agent to install a local package.
        """
        data = {"file": path}
        return self._request('POST', self.__class__.LOCAL_INSTALL_PATH, data)

    def remote_install(self, url):
        """
        Requests the agent to install a local package.
        """
        data = {"url": url}
        return self._request('POST', self.__class__.REMOTE_INSTALL_PATH, data)

    def _get_uri(self, path):
        uri = urlparse(self.__class__.SERVER_URL)
        uri = uri._replace(path=path)
        return uri.geturl()

    def _request(self, method, path, data=None):
        uri = self._get_uri(path)
        headers = {}
        if data is not None:
            data = json.dumps(data)
            try:
                data = data.encode('utf-8')
            except TypeError:
                pass
            headers = {"Content-Type": "application/json"}

        request = Request(uri, data=data, method=method, headers=headers)
        try:
            response = urlopen(request)
        except HTTPError as exception:
            response = exception

        response_body = response.read()
        return_response = None
        try:
            return_response = response_body.decode("utf-8")
        except AttributeError:
            return_response = response_body

        return json.loads(return_response)

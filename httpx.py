"""Small compatibility shim for the limited HTTP client features used by this app.

It keeps the FastAPI deployment self-contained even if Vercel's Python build
cache does not install optional third-party HTTP dependencies.
"""
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class Response:
    def __init__(self, status_code, content=b""):
        self.status_code = status_code
        self.content = content

    @property
    def text(self):
        return self.content.decode("utf-8", errors="replace")


class Client:
    def __init__(self, timeout=60.0, **kwargs):
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def _request(self, method, url, headers=None, content=None):
        request = Request(url, data=content, headers=headers or {}, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return Response(response.status, response.read())
        except HTTPError as exc:
            return Response(exc.code, exc.read())
        except URLError as exc:
            raise RuntimeError(f"HTTP request failed: {exc}") from exc

    def get(self, url, headers=None, **kwargs):
        return self._request("GET", url, headers=headers)

    def post(self, url, headers=None, content=None, **kwargs):
        return self._request("POST", url, headers=headers, content=content)

    def delete(self, url, headers=None, **kwargs):
        return self._request("DELETE", url, headers=headers)

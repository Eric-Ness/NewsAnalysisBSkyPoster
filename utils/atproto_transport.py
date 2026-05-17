"""Replace atproto's httpx.Client with curl_cffi to bypass BlueSky WAF TLS fingerprinting.

BlueSky's AWS WAF began rejecting Python's stdlib TLS handshake on 2026-05-16,
returning bare 403s from awselb/2.0 for every XRPC call (including unauthenticated
read endpoints). curl_cffi performs the TLS handshake the same way a real Chrome
browser does, which the WAF accepts.

Must be imported BEFORE anything that imports atproto. The bot's entry points
(main.py, youtube_poster.py) do this.
"""

from typing import Any, Dict, Optional

import atproto_client.request as _atproto_request
from curl_cffi import requests as _curl_requests

_IMPERSONATE_PROFILE = "chrome131"


class _CurlCffiResponse:
    """Adapter exposing the few httpx.Response attributes the SDK reads."""

    def __init__(self, resp: "_curl_requests.Response") -> None:
        self._resp = resp

    @property
    def content(self) -> bytes:
        return self._resp.content

    @property
    def status_code(self) -> int:
        return self._resp.status_code

    @property
    def headers(self) -> Dict[str, str]:
        return self._resp.headers


class _CurlCffiClient:
    """Drop-in replacement for httpx.Client covering the atproto SDK's usage."""

    def __init__(self, *, follow_redirects: bool = True, **_kwargs: Any) -> None:
        self._session = _curl_requests.Session(impersonate=_IMPERSONATE_PROFILE)
        self._follow_redirects = follow_redirects

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> _CurlCffiResponse:
        # httpx → curl_cffi kwarg translation
        if "content" in kwargs:
            kwargs["data"] = kwargs.pop("content")
        resp = self._session.request(
            method=method,
            url=url,
            headers=headers,
            allow_redirects=self._follow_redirects,
            **kwargs,
        )
        return _CurlCffiResponse(resp)

    def close(self) -> None:
        self._session.close()


def _patched_request_init(self: _atproto_request.Request, **kwargs: Any) -> None:
    _atproto_request.RequestBase.__init__(self)
    self._client = _CurlCffiClient(follow_redirects=True, **kwargs)


_atproto_request.Request.__init__ = _patched_request_init  # type: ignore[method-assign]

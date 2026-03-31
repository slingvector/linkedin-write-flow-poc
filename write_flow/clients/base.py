from typing import Protocol
import requests

class LinkedInClientProtocol(Protocol):
    def post(self, endpoint: str, json_data: dict) -> requests.Response:
        ...

    def get(self, endpoint: str) -> requests.Response:
        ...

    def put_binary(self, upload_url: str, binary_data: bytes) -> requests.Response:
        ...

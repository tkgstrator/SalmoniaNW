from cgitb import handler
from cmath import log
from dataclasses import asdict, dataclass
from dataclasses_json import dataclass_json
from logging import DEBUG, FileHandler, Formatter, getLogger, config
from typing import List, Type
from typing import Optional
import datetime
import requests
import re
import urllib
import json
import sys
import os
from enum import Enum


@dataclass_json
@dataclass
class ErrorNSO:
    error: str
    error_description: str


@dataclass_json
@dataclass
class Information:
    minimumOsVersion: str
    version: str
    currentVersionReleaseDate: str


@dataclass_json
@dataclass
class AppVersion:
    resultCount: int
    results: List[Information]


@dataclass_json
@dataclass
class ErrorAPP:
    status: str
    correlationId: str
    errorMessage: str


@dataclass_json
@dataclass
class SessionToken:
    code: str
    session_token: str


@dataclass_json
@dataclass
class AccessToken:
    access_token: str
    scope: List[str]
    token_type: str
    id_token: str
    expires_in: int


@dataclass_json
@dataclass
class Credential:
    accessToken: str
    expiresIn: int


@dataclass_json
@dataclass
class FriendCode:
    regenerable: bool
    regenerableAt: int
    id: str


@dataclass_json
@dataclass
class Membership:
    active: bool


@dataclass_json
@dataclass
class NintendoAccount:
    membership: Membership


@dataclass_json
@dataclass
class Links:
    nintendoAccount: NintendoAccount
    friendCode: FriendCode


@dataclass_json
@dataclass
class Permissions:
    presence: str


@dataclass_json
@dataclass
class Game:
    pass


@dataclass_json
@dataclass
class Presence:
    state: str
    updatedAt: int
    logoutAt: int
    game: Game


@dataclass_json
@dataclass
class User:
    id: int
    nsaId: str
    imageUri: str
    name: str
    supportId: str
    isChildRestricted: bool
    etag: str
    links: Links
    permissions: Permissions
    presence: Presence


@dataclass_json
@dataclass
class SplatoonTokenResult:
    user: User
    webApiServerCredential: Credential
    firebaseCredential: Credential


@dataclass_json
@dataclass
class SplatoonToken:
    status: int
    result: SplatoonTokenResult
    correlationId: str


@dataclass_json
@dataclass
class SplatoonAccessTokenResult:
    accessToken: str
    expiresIn: int


@dataclass_json
@dataclass
class SplatoonAccessToken:
    status: int
    result: SplatoonAccessTokenResult
    correlationId: str


@dataclass_json
@dataclass
class Imink:
    f: str
    timestamp: int
    request_id: str


@dataclass_json
@dataclass
class BulletToken:
    bulletToken: str
    lang: str
    is_noe_country: bool


@dataclass_json
@dataclass
class JobNum:
    local: int = 0
    splatnet2: int = 0


@dataclass_json
@dataclass
class Credential:
    nsa_id: str
    session_token: str
    bullet_token: str
    expires_in: str


session_token_code_challenge = "tYLPO5PxpK-DTcAHJXugD7ztvAZQlo0DQQp3au5ztuM"
session_token_code_verifier = "OwaTAOolhambwvY3RXSD-efxqdBEVNnQkc0bBJ7zaak"
app_ver = '3.0.0'
version = '3.0.0-0742bda0'

logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = FileHandler('logs.txt')
handler.setLevel(DEBUG)
formatter = Formatter('%(levelname)s  %(asctime)s  [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class IminkType(Enum):
    NSO = "1"
    APP = "2"


def renew_cookie(session_token: str):
    version = get_app_version()
    logger.debug(version)
    access_token = get_access_token(session_token)
    logger.debug(access_token.access_token)
    splatoon_token = get_splatoon_token(access_token, version)
    logger.debug(splatoon_token.result.webApiServerCredential.accessToken)
    splatoon_access_token = get_splatoon_access_token(splatoon_token, version)
    logger.debug(splatoon_access_token.result.accessToken)
    bullet_token = get_bullet_token(splatoon_access_token)
    logger.debug(bullet_token.bulletToken)

    credentials = {
        'nsa_id': splatoon_token.result.user.nsaId,
        'session_token': session_token,
        'bullet_token': bullet_token.bulletToken,
        'expires_in': (datetime.datetime.now() + datetime.timedelta(hours=2)).isoformat()
    }

    # Dump User Credentials
    with open('credentials.json', "w") as f:
        json.dump(credentials, f, indent=4)


def get_cookie(url_scheme: str):
    session_token = get_session_token(url_scheme)
    logger.debug(session_token.session_token)
    renew_cookie(session_token.session_token)


def get_session_token_code():
    url = "https://accounts.nintendo.com/connect/1.0.0/authorize"

    parameters = {
        "state": "V6DSwHXbqC4rspCn_ArvfkpG1WFSvtNYrhugtfqOHsF6SYyX",
        "redirect_uri": "npf71b963c1b7b6d119://auth",
        "client_id": "71b963c1b7b6d119",
        "scope": "openid user user.birthday user.mii user.screenName",
        "response_type": "session_token_code",
        "session_token_code_challenge": session_token_code_challenge,
        "session_token_code_challenge_method": "S256",
        "theme": "login_form",
    }
    headers = {
        "user-agent": f"Salmonia/{app_ver} @tkgling",
    }
    response = requests.get(url, headers=headers, params=parameters)
    return response.history[0].url


def get_session_token(url_scheme: str) -> SessionToken:
    session_token_code = re.search("de=(.*)&", url_scheme).group(1)

    url = "https://accounts.nintendo.com/connect/1.0.0/api/session_token"
    parameters = {
        "client_id": "71b963c1b7b6d119",
        "session_token_code": session_token_code,
        "session_token_code_verifier": session_token_code_verifier,
    }
    headers = {
        "user-agent": f"Salmonia/{app_ver} @tkgling",
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "content-length": str(len(urllib.parse.urlencode(parameters))),
        "host": "accounts.nintendo.com",
    }

    try:
        response = requests.post(url, headers=headers, data=parameters).text
        return SessionToken.from_json(response)
    except Exception as e:
        logger.error(response)
        response = ErrorNSO.from_json(response.text)
        print(f"TypeError: {response.error_description}")
        sys.exit(1)


def get_access_token(session_token: str) -> AccessToken:
    url = "https://accounts.nintendo.com/connect/1.0.0/api/token"
    parameters = {
        "client_id": "71b963c1b7b6d119",
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
        "session_token": session_token,
    }
    headers = {
        "Host": "accounts.nintendo.com",
        "User-Agent": f"Salmonia/{app_ver} @tkgling",
        "Accept": "application/json",
        "Content-Length": str(len(urllib.parse.urlencode(parameters))),
    }
    try:
        response = requests.post(url, headers=headers, json=parameters).text
        return AccessToken.from_json(response)
    except Exception as e:
        logger.error(response)
        response = ErrorNSO.from_json(response.text)
        print(f"TypeError: {response.error_description}")
        sys.exit(1)


def get_imink(access_token: str, type: IminkType) -> Imink:
    url = "https://api.imink.app/f"
    headers = {
        "User-Agent": f"Salmonia/{app_ver} @tkgling",
        "Accept": "application/json",
    }
    parameters = {"hash_method": type.value, "token": access_token}
    try:
        response = requests.post(url, headers=headers, json=parameters)
        return Imink.from_json(response.text)
    except Exception as e:
        logger.error(response)
        print(f"TypeError: {response.error}")
        sys.exit(1)


def get_splatoon_token(access_token: AccessToken, version: str) -> SplatoonToken:
    url = "https://api-lp1.znc.srv.nintendo.net/v3/Account/Login"
    result = get_imink(access_token.access_token, IminkType.NSO)
    parameters = {
        "parameter": {
            "f": result.f,
            "naIdToken": access_token.access_token,
            "timestamp": result.timestamp,
            "requestId": result.request_id,
            "naCountry": "JP",
            "naBirthday": "1990-01-01",
            "language": "ja-JP",
        }
    }
    headers = {
        "Host": "api-lp1.znc.srv.nintendo.net",
        "User-Agent": f"Salmonia/{app_ver} @tkgling",
        "Authorization": "Bearer",
        "X-ProductVersion": f"{version}",
        "X-Platform": "Android",
    }
    try:
        response = requests.post(url, headers=headers, json=parameters)
        return SplatoonToken.from_json(response.text)
    except Exception as e:
        logger.error(response)
        response = ErrorNSO.from_json(response.text)
        print(f"TypeError: {response.error}")


def get_splatoon_access_token(splatoon_token: SplatoonToken, version: str
                              ) -> SplatoonAccessToken:
    url = "https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken"
    access_token = splatoon_token.result.webApiServerCredential.accessToken
    result = get_imink(access_token, IminkType.APP)
    parameters = {
        "parameter": {
            "id": 4834290508791808,
            "f": result.f,
            "registrationToken": access_token,
            "timestamp": result.timestamp,
            "requestId": result.request_id,
        }
    }
    headers = {
        "Host": "api-lp1.znc.srv.nintendo.net",
        "User-Agent": f"Salmonia/{app_ver} @tkgling",
        "Authorization": f"Bearer {access_token}",
        "X-ProductVersion": f"{version}",
        "X-Platform": "Android",
    }

    try:
        response = requests.post(url, headers=headers, json=parameters)
        return SplatoonAccessToken.from_json(response.text)
    except Exception as e:
        logger.error(response)
        response = ErrorAPP.from_json(response)
        print(f"TypeError: {response.errorMessage}")


def get_bullet_token(splatoon_access_token: SplatoonAccessToken) -> BulletToken:
    url = "https://api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens"
    headers = {
        'x-web-view-ver': version,
        'x-nacountry': 'US',
        'X-GameWebToken': splatoon_access_token.result.accessToken
    }

    try:
        response = requests.post(url, headers=headers).text
        return BulletToken.from_json(response)
    except Exception as e:
        logger.error(response)
        print(f"TypeError: invalid splatoon access token")


def get_app_version() -> str:
    url = "https://itunes.apple.com/lookup?id=1234806557"
    try:
        response = requests.get(url)
        return AppVersion.from_json(response.text).results[0].version
    except:
        print(f"TypeError: invalid id")


def request(parameters: dict) -> dict:
    # WIP: Load User Credentials
    with open('credentials.json', mode='r') as f:
        credential: Credential = Credential.from_json(f.read())
        # Renew Cookie
        if datetime.datetime.now() >= datetime.datetime.fromisoformat(credential.expires_in):
            renew_cookie(credential.session_token)
            credential: Credential = Credential.from_json(f.read())
        url = 'https://api.lp1.av5ja.srv.nintendo.net/api/graphql'
        headers = {
            'x-web-view-ver': version,
            'Authorization': f'Bearer {credential.bullet_token}'
        }
        print(requests.post(url, headers=headers, json=parameters))
        return requests.post(url, headers=headers, json=parameters).json()


def get_coop_result(id: str) -> dict:
    parameters = {
        'variables': {
            'coopHistoryDetailId': id
        },
        'extensions': {
            'persistedQuery': {
                'version': 3,
                'sha256Hash': '379f0d9b78b531be53044bcac031b34b'
            }
        }
    }
    return request(parameters)


def get_coop_summary() -> dict:
    url = 'https://api.lp1.av5ja.srv.nintendo.net/api/graphql'
    parameters = {
        'variables': {},
        'extensions': {
            'persistedQuery': {
                'version': 3,
                'sha256Hash': '6e8711fa8bb803581b97519ade4ef0a3'
            }
        }
    }
    response = request(parameters)
    with open('../data/summary.json', mode='w') as f:
        json.dump(response, f, indent=2)

    nodes = response['data']['coopResult']['historyGroups']['nodes'][0]['historyDetails']['nodes']

    ids: list[str] = set(map(lambda x: x['id'], nodes)) - \
        set(map(lambda x: os.path.splitext(x)[0], os.listdir('../data/results')))
    print(f"Available results {len(ids)}")
    for id in ids:
        with open(f'../data/results/{id}.json', mode='w') as f:
            print(f"Downloading results id: {id}")
            result = get_coop_result(id)
            json.dump(result, f, indent=2)

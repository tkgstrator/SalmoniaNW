from cgitb import handler
from cmath import log
from logging import DEBUG, FileHandler, Formatter, getLogger, config
from django.http import HttpResponseBadRequest, HttpResponse
from requests import Session
import datetime
import requests
import re
import urllib
import json
import sys
import os
import base64
from type import *
from hash import *

session_token_code_challenge = "tYLPO5PxpK-DTcAHJXugD7ztvAZQlo0DQQp3au5ztuM"
session_token_code_verifier = "OwaTAOolhambwvY3RXSD-efxqdBEVNnQkc0bBJ7zaak"
app_ver = "2.0.0"

logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = FileHandler("logs.txt")
handler.setLevel(DEBUG)
formatter = Formatter("%(levelname)s  %(asctime)s  [%(name)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def _get_hash() -> str:
    url = "https://api.lp1.av5ja.srv.nintendo.net"
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    return re.search(
        'src="/static/js/main\.([a-f0-9]{8}).js"', response.text
    ).group(1)

# Get React App Version from SplatNet3
def _get_react_version() -> str:
    hash = _get_hash()
    url = f"https://api.lp1.av5ja.srv.nintendo.net/static/js/main.{hash}.js"
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    
    version =  re.search(
        '`(\d{1}\.\d{1}\.\d{1})-', response.text
    ).group(1)
    revision = re.search(
        'REACT_APP_REVISION:"([a-f0-9]{8})', response.text
    ).group(1)
    return f"{version}-{revision}"

# Renew Bullet Token from Session Token
def renew_cookie(session_token: str):
    session = Session()
    revision = _get_react_version()
    version = _get_app_version(session)
    logger.debug(revision)
    logger.debug(version)
    access_token = _get_access_token(session, session_token)
    logger.debug(access_token.access_token)
    splatoon_token = _get_splatoon_token(session, access_token, version)
    logger.debug(splatoon_token.result.webApiServerCredential.accessToken)
    splatoon_access_token = _get_splatoon_access_token(session, splatoon_token, version)
    logger.debug(splatoon_access_token.result.accessToken)
    bullet_token = _get_bullet_token(session, splatoon_access_token, revision)
    logger.debug(bullet_token.bulletToken)

    credentials = {
        "nsa_id": splatoon_token.result.user.nsaId,
        "session_token": session_token,
        "bullet_token": bullet_token.bulletToken,
        "expires_in": (
            datetime.datetime.now() + datetime.timedelta(hours=2)
        ).isoformat(),
        "version": revision
    }

    # Dump User Credentials
    with open("credentials.json", "w") as f:
        json.dump(credentials, f, indent=4)


def get_cookie(url_scheme: str):
    session = Session()
    session_token = _get_session_token(session, url_scheme)
    logger.debug(session_token.session_token)
    renew_cookie(session_token.session_token)


def get_session_token_code() -> str:
    session = Session()
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
        "user-agent": f"Salmonia+/{app_ver} @tkgling",
    }
    response = session.get(url, headers=headers, params=parameters)
    return response.history[0].url


def _get_session_token(session: Session, url_scheme: str) -> SessionToken:
    session_token_code = re.search("de=(.*)&", url_scheme).group(1)

    url = "https://accounts.nintendo.com/connect/1.0.0/api/session_token"
    parameters = {
        "client_id": "71b963c1b7b6d119",
        "session_token_code": session_token_code,
        "session_token_code_verifier": session_token_code_verifier,
    }
    headers = {
        "user-agent": f"Salmonia+/{app_ver} @tkgling",
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "content-length": str(len(urllib.parse.urlencode(parameters))),
        "host": "accounts.nintendo.com",
    }

    try:
        response = session.post(url, headers=headers, data=parameters).text
        return SessionToken.from_json(response)
    except Exception as e:
        logger.error(response)
        response = ErrorNSO.from_json(response)
        print(f"TypeError: {response.error_description}")
        sys.exit(1)


def _get_access_token(session: Session, session_token: str) -> AccessToken:
    url = "https://accounts.nintendo.com/connect/1.0.0/api/token"
    parameters = {
        "client_id": "71b963c1b7b6d119",
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
        "session_token": session_token,
    }
    headers = {
        "Host": "accounts.nintendo.com",
        "User-Agent": f"Salmonia+/{app_ver} @tkgling",
        "Accept": "application/json",
        "Content-Length": str(len(urllib.parse.urlencode(parameters))),
    }
    try:
        response = session.post(url, headers=headers, json=parameters).text
        return AccessToken.from_json(response)
    except Exception as e:
        logger.error(response)
        response = ErrorNSO.from_json(response)
        print(f"TypeError: {response.error_description}")
        sys.exit(1)


def _get_imink(session: Session, access_token: str, type: IminkType) -> Imink:
    url = "https://api.imink.app/f"
    headers = {
        "User-Agent": f"Salmonia+/{app_ver} @tkgling",
        "Accept": "application/json",
    }
    parameters = {"hash_method": type.value, "token": access_token}
    try:
        response = session.post(url, headers=headers, json=parameters)
        return Imink.from_json(response.text)
    except Exception as e:
        response = Imink.from_json(response)
        logger.error(response)
        print(f"TypeError: {response.error}")
        sys.exit(1)


def _get_splatoon_token(
    session: Session, access_token: AccessToken, version: str
) -> SplatoonToken:
    url = "https://api-lp1.znc.srv.nintendo.net/v3/Account/Login"
    result = _get_imink(session, access_token.access_token, IminkType.NSO)
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
        "User-Agent": f"Salmonia+/{app_ver} @tkgling",
        "Authorization": "Bearer",
        "X-ProductVersion": f"{version}",
        "X-Platform": "Android",
    }
    try:
        response = session.post(url, headers=headers, json=parameters)
        return SplatoonToken.from_json(response.text)
    except Exception as e:
        logger.error(response)
        response = ErrorNSO.from_json(response)
        print(f"TypeError: {response.error}")


def _get_splatoon_access_token(
    session: Session, splatoon_token: SplatoonToken, version: str
) -> SplatoonAccessToken:
    url = "https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken"
    access_token = splatoon_token.result.webApiServerCredential.accessToken
    result = _get_imink(session, access_token, IminkType.APP)
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
        "User-Agent": f"Salmonia+/{app_ver} @tkgling",
        "Authorization": f"Bearer {access_token}",
        "X-ProductVersion": f"{version}",
        "X-Platform": "Android",
    }

    try:
        response = session.post(url, headers=headers, json=parameters)
        return SplatoonAccessToken.from_json(response.text)
    except Exception as e:
        logger.error(response)
        response = ErrorAPP.from_json(response)
        print(f"TypeError: {response.errorMessage}")


def _get_bullet_token(
    session: Session, splatoon_access_token: SplatoonAccessToken, revision: str
) -> BulletToken:
    url = "https://api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens"
    headers = {
        "x-web-view-ver": revision,
        "x-nacountry": "US",
        "X-GameWebToken": splatoon_access_token.result.accessToken,
    }

    try:
        response = session.post(url, headers=headers).text
        return BulletToken.from_json(response)
    except Exception as e:
        logger.error(response)
        print(f"TypeError: invalid splatoon access token")


# Get Nintendo Switch Online App Version from App Store
def _get_app_version(session: Session) -> str:
    url = "https://itunes.apple.com/lookup?id=1234806557"
    try:
        response = session.get(url)
        return AppVersion.from_json(response.text).results[0].version
    except:
        print(f"TypeError: invalid id")

# Request with Credentials
def request(session: Session, parameters: dict) -> dict:
    # WIP: Load User Credentials
    with open("credentials.json", mode="r") as f:
        credential: Credential = Credential.from_json(f.read())
        # Renew Cookie
        if datetime.datetime.now() >= datetime.datetime.fromisoformat(
            credential.expires_in
        ):
            renew_cookie(credential.session_token)
            session = Session()
            with open("credentials.json", mode="r") as newf:
                credential: Credential = Credential.from_json(newf.read())
        url = "https://api.lp1.av5ja.srv.nintendo.net/api/graphql"
        headers = {
            "x-web-view-ver": credential.version,
            "Authorization": f"Bearer {credential.bullet_token}",
        }
        try:
            response = session.post(url, headers=headers, json=parameters).json()
        except:
            renew_cookie(credential.session_token)
            session = Session()
            with open("credentials.json", mode="r") as newf:
                credential: Credential = Credential.from_json(newf.read())
            response = session.post(url, headers=headers, json=parameters).json()
        return response

def _upload_coop_result(session: Session, result: dict):
    url = "https://api.splatnet3.com/v1/results"
    body = {
        "results": [result]
    }
    response = session.post(url, json=body)
    if response.status_code == 201:
        return
    else:
        raise HttpResponseBadRequest

def get_coop_result(session, id: str) -> dict:
    parameters = {
        "variables": {"coopHistoryDetailId": id},
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": SHA256Hash.CoopHistoryDetailQuery.value,
            }
        },
    }
    return request(session, parameters)


def get_coop_summary() -> dict:
    session = Session()
    url = "https://api.lp1.av5ja.srv.nintendo.net/api/graphql"
    parameters = {
        "variables": {},
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": SHA256Hash.CoopHistoryQuery.value,
            }
        },
    }
    response = request(session, parameters)
    with open("summary.json", mode="w") as f:
        json.dump(response, f, indent=2)

    allnodes = response["data"]["coopResult"]["historyGroups"]["nodes"]
    nodes = []
    for n in allnodes:
        nodes = nodes + n["historyDetails"]["nodes"]

    #    nodes = response['data']['coopResult']['historyGroups']['nodes'][0]['historyDetails']['nodes']

    ids: list[str] = set(map(lambda x: x["id"], nodes)) - set(
        map(
            lambda x: base64.b64encode(os.path.splitext(x)[0].encode("utf-8")).decode(
                "utf-8"
            ),
            os.listdir("results"),
        )
    )
    print(f"Available results {len(ids)}")
    for id in ids:
        fname = f"results/{base64.b64decode(id).decode('utf-8')}.json"
        with open(fname, mode="w") as f:
            print(f"Downloading results id: {id}")
            result = get_coop_result(session, id)
            _upload_coop_result(session, result)
            json.dump(result, f, indent=2)

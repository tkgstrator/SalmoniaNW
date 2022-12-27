from dataclasses import asdict, dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import List, Type
from typing import Optional


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
    version: str

class IminkType(Enum):
    NSO = "1"
    APP = "2"


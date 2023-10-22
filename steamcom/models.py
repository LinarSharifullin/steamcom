import enum
from typing import NamedTuple


class SteamUrl:
    API = 'https://api.steampowered.com'
    COMMUNITY = 'https://steamcommunity.com'
    STORE = 'https://store.steampowered.com'
    LOGIN = 'https://login.steampowered.com'


class IAuthenticationServiceEndpoint:
    SERVICE = SteamUrl.API + '/IAuthenticationService'
    GetPasswordRSAPublicKey = SERVICE + '/GetPasswordRSAPublicKey/v1'
    BeginAuthSessionViaCredentials = SERVICE +\
        '/BeginAuthSessionViaCredentials/v1'
    UpdateAuthSessionWithSteamGuardCode = SERVICE +\
        '/UpdateAuthSessionWithSteamGuardCode/v1'
    PollAuthSessionStatus = SERVICE + '/PollAuthSessionStatus/v1'


class ConfirmationTag:
    CONF = 'conf'
    DETAILS = 'details'
    ALLOW = 'allow'
    CANCEL = 'cancel'


class ConfirmationType(enum.IntEnum):
    TRADE = 2  # Send offer and accept
    CREATE_LISTING = 3
    CHANGE_PHONE_NUMBER = 5
    CONFIRM = 6  # I saw in the mail change


class Confirmation(NamedTuple):
    type: ConfirmationType
    type_name: str
    id: str
    creator_id: str
    nonce: str
    creation_time: str
    cancel: str
    accept: str
    icon: str
    multi: bool
    headline: str
    summary: dict
    warn: None

    def __str__(self) -> str:
        if not self.summary:
            if not self.headline:
                return f'Unknown {self.type.name}'
            return self.headline
        return f'Confirmation: {self.summary[0]}'

    def __repr__(self) -> str:
        if not self.summary:
            if not self.headline:
                return f'Unknown {self.type.name}'
            return self.headline
        return f'Confirmation: {self.summary[0]}'


class HistoryStatus(enum.IntEnum):
    LISTED = 1
    CANCELED = 2
    SOLD = 3
    PURCHASED = 4


class Result(enum.IntEnum):
    INVALID = 0
    OK = 1
    FAIL = 2
    NO_CONNECTION = 3
    INVALID_PASSWORD = 5
    LOGGED_IN_ELSEWHERE = 6
    INVALID_PROTOCO_VER = 7
    INVALID_PLATFORM = 8
    FILE_NOT_FOUND = 9
    BUSY = 10
    INVALID_STATE = 11
    INVALID_NAME = 12
    INVALID_EMAIL = 13
    DUPLICATE_NAME = 14
    ACCESS_DENIED = 15
    TIMEOUT = 16
    BANNED = 17
    ACCOUNT_NOT_FOUND = 18
    INVALID_STEAM_ID = 19
    SERVICE_UNAVAILABLE = 20
    NOT_LOGGED_ON = 21
    PENDING = 22
    ENCRYPTION_FAILURE = 23
    INSUFFICIENT_PRIVILEGE = 24
    LIMIT_EXCEEDED = 25
    REVOKED = 26
    EXPIRED = 27
    ALREADY_REDEEMED = 28
    DUPLICATE_REQUEST = 29
    ALREADY_OWNED = 30
    IP_NOT_FOUND = 31
    PERSIST_FAILED = 32
    LOCKING_FAILED = 33
    LOGON_SESSION_REPLACED = 34
    CONNECT_FAILED = 35
    HANDSHAKE_FAILED = 36
    IO_FAILURE = 37
    REMOTE_DISCONNECT = 38
    SHOPPING_CART_NOT_FOUND = 39
    BLOCKED = 40
    IGNORED = 41
    NOMATCH = 42
    ACCOUNT_DISABLED = 43
    SERVICE_READ_ONLY = 44
    ACCOUNT_NOT_FEATURED = 45
    ADMINISTRATOR_OK = 46
    CONTENT_VERSION = 47
    TRY_ANOTHER_CM = 48
    PASSWORD_REQUIRED_TO_KICK_SESSION = 49
    ALREADY_LOGGED_IN_ELSEWHERE = 50
    SUSPENDED = 51
    CANCELLED = 52
    DATA_CORRUPTION = 53
    DISK_FULL = 54
    REMOTE_CALL_FAILED = 55
    PASSWORD_UNSET = 56
    EXTERNAL_ACCOUNT_UNLINKED = 57
    PSN_TICKET_INVALID = 58
    EXTERNAL_ACCOUNT_ALREADY_LINKED = 59
    REMOTE_FILE_CONFLICT = 60
    ILLEGAL_PASSWORD = 61
    SAME_AS_PREVIOUS_VALUE = 62
    ACCOUNT_LOGON_DENIED = 63
    CANNOT_USE_OLD_PASSWORD = 64
    INVALID_LOGIN_AUTH_CODE = 65
    ACCOUNT_LOGON_DENIED_NO_MAIL = 66
    HARDWARE_NOT_CAPABLE_OF_IPT = 67
    IPT_INIT_ERROR = 68
    PARENTAL_CONTROL_RESTRICTED = 69
    FACEBOOK_QUERY_ERROR = 70
    EXPIRED_LOGIN_AUTH_CODE = 71
    IP_LOGIN_RESTRICTION_FAILED = 72
    ACCOUNT_LOCKED_DOWN = 73
    ACCOUNT_LOGON_DENIED_VERIFIED_EMAIL_REQUIRED = 74
    NO_MATCHING_URL = 75
    BAD_RESPONSE = 76
    REQUIRE_PASSWORD_RE_ENTRY = 77
    VALUE_OUT_OF_RANGE = 78
    UNEXPECTED_ERROR = 79
    DISABLED = 80
    INVALID_CEG_SUBMISSION = 81
    RESTRICTED_DEVICE = 82
    REGION_LOCKED = 83
    RATE_LIMIT_EXCEEDED = 84
    ACCOUNT_LOGIN_DENIED_NEED_TWO_FACTOR = 85
    ITEM_DELETED = 86
    ACCOUNT_LOGIN_DENIED_THROTTLE = 87
    TWO_FACTOR_CODE_MISMATCH = 88
    TWO_FACTOR_ACTIVATION_CODE_MISMATCH = 89
    ACCOUNT_ASSOCIATED_TO_MULTIPLE_PARTNERS = 90
    NOT_MODIFIED = 91
    NO_MOBILE_DEVICE = 92
    TIME_NOT_SYNCED = 93
    SMS_CODE_FAILED = 94
    ACCOUNT_LIMIT_EXCEEDED = 95
    ACCOUNT_ACTIVITY_LIMIT_EXCEEDED = 96
    PHONE_ACTIVITY_LIMIT_EXCEEDED = 97
    REFUND_TO_WALLET = 98
    EMAIL_SEND_FAILURE = 99
    NOT_SETTLED = 100
    NEED_CAPTCHA = 101
    GS_LT_DENIED = 102
    GS_OWNER_DENIED = 103
    INVALID_ITEM_TYPE = 104
    IP_BANNED = 105
    GS_LT_EXPIRED = 106
    INSUFFICIENT_FUNDS = 107
    TOO_MANY_PENDING = 108
    NO_SITE_LICENSES_FOUND = 109
    WG_NETWORK_SEND_EXCEEDED = 110
    ACCOUNT_NOT_FRIENDS = 111
    LIMITED_USER_ACCOUNT = 112
    CANT_REMOVE_ITEM = 113
    ACCOUNT_HAS_BEEN_DELETED = 114
    ACCOUNT_HAS_AN_EXISTING_USER_CANCELLED_LICENSE = 115
    DENIED_DUE_TO_COMMUNITY_COOLDOWN = 116
    NO_LAUNCHER_SPECIFIED = 117
    MUST_AGREE_TO_SSA = 118
    CLIENT_NO_LONGER_SUPPORTED = 119


class Currency(enum.IntEnum):
    USD = 1
    GBP = 2
    EUR = 3
    CHF = 4
    RUB = 5
    PLN = 6
    BRL = 7
    JPY = 8
    NOK = 9
    IDR = 10
    MYR = 11
    PHP = 12
    SGD = 13
    THB = 14
    VND = 15
    KRW = 16
    TRY = 17
    UAH = 18
    MXN = 19
    CAD = 20
    AUD = 21
    NZD = 22
    CNY = 23
    INR = 24
    CLP = 25
    PEN = 26
    COP = 27
    ZAR = 28
    HKD = 29
    TWD = 30
    SAR = 31
    AED = 32
    ARS = 34
    ILS = 35
    BYN = 36
    KZT = 37
    KWD = 38
    QAR = 39
    CRC = 40
    UYU = 41

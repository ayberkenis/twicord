class TwicordError(BaseException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class SpotifyAccessTokenExpired(TwicordError):
    pass


class RequestError(TwicordError):
    pass


class InvalidArgument(TwicordError):
    pass


class AccessTokenRevoked(TwicordError):
    pass


class WebserverNotRunning(TwicordError):
    pass


class InvalidAccessToken(TwicordError):
    pass


class TwitchAccessError(TwicordError):
    pass


class TwitchAPIError(TwicordError):
    pass


class SpotifySongNotFound(TwicordError):
    pass


class DiscordAccessError(TwicordError):
    pass


class DiscordAPIError(TwicordError):
    pass


class NoSuchColumn(TwicordError):
    pass

class SourceArenaApiException(BaseException):
    pass


class SourceArenaRequestException(BaseException):
    pass


class OffDayException(SourceArenaRequestException):
    pass
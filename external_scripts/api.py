from typing import Optional, Type


class ResponseCode:
    PositiveResponse = 0
    GeneralReject = 0x10
    ServiceNotSupported = 0x11
    SubFunctionNotSupported = 0x12
    IncorrectMessageLengthOrInvalidFormat = 0x13
    ResponseTooLong = 0x14
    BusyRepeatRequest = 0x21
    ConditionsNotCorrect = 0x22
    RequestSequenceError = 0x24
    NoResponseFromSubnetComponent = 0x25
    FailurePreventsExecutionOfRequestedAction = 0x26
    RequestOutOfRange = 0x31
    SecurityAccessDenied = 0x33
    AuthenticationRequired = 0x34
    InvalidKey = 0x35
    ExceedNumberOfAttempts = 0x36
    RequiredTimeDelayNotExpired = 0x37
    SecureDataTransmissionRequired = 0x38
    SecureDataTransmissionNotAllowed = 0x39
    SecureDataVerificationFailed = 0x3A
    CertificateVerificationFailed_InvalidTimePeriod = 0x50
    CertificateVerificationFailed_InvalidSignature = 0x51
    CertificateVerificationFailed_InvalidChainOfTrust = 0x52
    CertificateVerificationFailed_InvalidType = 0x53
    CertificateVerificationFailed_InvalidFormat = 0x54
    CertificateVerificationFailed_InvalidContent = 0x55
    CertificateVerificationFailed_InvalidScope = 0x56
    CertificateVerificationFailed_InvalidCertificate = 0x57
    OwnershipVerificationFailed = 0x58
    ChallengeCalculationFailed = 0x59
    SettingAccessRightsFailed = 0x5A
    SessionKeyCreationDerivationFailed = 0x5B
    ConfigurationDataUsageFailed = 0x5C
    DeAuthenticationFailed = 0x5D
    UploadDownloadNotAccepted = 0x70
    TransferDataSuspended = 0x71
    GeneralProgrammingFailure = 0x72
    WrongBlockSequenceCounter = 0x73
    RequestCorrectlyReceived_ResponsePending = 0x78
    SubFunctionNotSupportedInActiveSession = 0x7E
    ServiceNotSupportedInActiveSession = 0x7F
    RpmTooHigh = 0x81
    RpmTooLow = 0x82
    EngineIsRunning = 0x83
    EngineIsNotRunning = 0x84
    EngineRunTimeTooLow = 0x85
    TemperatureTooHigh = 0x86
    TemperatureTooLow = 0x87
    VehicleSpeedTooHigh = 0x88
    VehicleSpeedTooLow = 0x89
    ThrottlePedalTooHigh = 0x8A
    ThrottlePedalTooLow = 0x8B
    TransmissionRangeNotInNeutral = 0x8C
    TransmissionRangeNotInGear = 0x8D
    BrakeSwitchNotClosed = 0x8F
    ShifterLeverNotInPark = 0x90
    TorqueConverterClutchLocked = 0x91
    VoltageTooHigh = 0x92
    VoltageTooLow = 0x93
    ResourceTemporarilyNotAvailable = 0x94

    # Defined by ISO-15764. Offset of 0x38 is defined within UDS standard (ISO-14229)
    GeneralSecurityViolation = 0x38 + 0
    SecuredModeRequested = 0x38 + 1
    InsufficientProtection = 0x38 + 2
    TerminationWithSignatureRequested = 0x38 + 3
    AccessDenied = 0x38 + 4
    VersionNotSupported = 0x38 + 5
    SecuredLinkNotSupported = 0x38 + 6
    CertificateNotAvailable = 0x38 + 7
    AuditTrailInformationNotAvailable = 0x38 + 8


class BaseService:
    pass


class BaseResponseData:
    pass


class Request:
    """
    Represents a UDS Request.

    :param service: The service for which to make the request. This parameter must be a class that extends :class:`udsoncan.services.BaseService`
    :type service: class

    :param subfunction: The service subfunction. This value may be ignored if the given service does not supports subfunctions
    :type subfunction: int or None

    :param suppress_positive_response: Indicates that the server should not send a response if the response code is positive.
            This parameter has effect only when the given service supports subfunctions
    :type suppress_positive_response: bool

    :param data: The service data appended after service ID and payload
    :type data: bytes
    """
    service: Optional[Type[BaseService]]
    subfunction: Optional[int]
    data: Optional[bytes]
    suppress_positive_response: bool


class Response:
    """
    Represents a server Response to a client Request

    :param service: The service implied by this response.
    :type service: class

    :param code: The response code
    :type code: int

    :param data: The response data encoded after the service and response code
    :type data: bytes

    .. data:: valid

            (boolean) True if the response content is valid. Only ``invalid_reason`` is guaranteed to have a meaningful value if this value is False

    .. data:: invalid_reason

            (string) String explaining why the response is invalid.

    .. data:: service

            (class) The response target :ref:`service<Services>` class

    .. data:: positive

            (boolean) True if the response code is 0 (PositiveResponse), False otherwise

    .. data:: unexpected

            (boolean) Indicates that the response was unexpected. Set by an external source such as the :ref:`Client<Client>` object

    .. data:: code

            (int) The response code.

    .. data:: code_name

            (string) The response code name.


    .. data:: data

            (bytes) The response data. All the payload content, except the service number and the response code


    .. data:: service_data

            (object) The content of ``data`` interpreted by a service; can be any type of content.


    .. data:: original_payload

            (bytes) When the response is built with `Response.from_payload`, this property contains a copy of the payload used. None otherwise.

    .. data:: original_request

            (Request) Optional reference to the request object that generated this response.  """
    Code = ResponseCode

    service: Optional[Type[BaseService]]
    subfunction: Optional[int]
    data: Optional[bytes]
    suppress_positive_response: bool
    original_payload: Optional[bytes]
    service_data: Optional[BaseResponseData]
    original_request: Optional[Request]


class UDSClient:
    security_seed: bytes
    security_key: bytes
    def uds_send_and_wait_response(self, payload: bytes) -> Optional[Response]:
        pass


class Utils:
    def hex_str_to_bytes(self, hex_str: str) -> bytes:
        pass


class Context:
    uds_client: UDSClient
    utils: Utils

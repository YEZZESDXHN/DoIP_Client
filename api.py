class UDSClient:
    def send_payload(self, payload: bytes):
        pass


class Utils:
    def hex_str_to_bytes(self, hex_str: str) -> bytes:
        pass


class Context:
    uds_client: "UDSClient"
    utils: 'Utils'

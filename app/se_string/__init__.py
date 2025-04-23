import logging

from app.se_string.error import SeStringError
from app.se_string.payload import PayloadReader


class SeString:
    """
    Square Enix rich text format (SeString).
    """

    def __init__(self, data: bytes):
        self.data = data

    def payloads(self):
        reader = PayloadReader(self.data)
        try:
            return [payload for payload in reader]
        except SeStringError as e:
            logging.exception(e, exc_info=True)
            return "invalid SeString"
        except Exception as e:
            logging.exception(e, exc_info=True)
            return "parse error"

    def format(self) -> str:
        reader = PayloadReader(self.data)

        try:
            return "".join(str(payload) for payload in reader)
        except SeStringError as e:
            logging.exception(e, exc_info=True)

            return "invalid SeString"
        except Exception as e:
            logging.exception(e, exc_info=True)
            return "parse error"

    def __str__(self):
        return self.format()

from typing import List, Dict
from flask import jsonify


class RequestError:
    def __init__(
        self, message: str, status_code: int = 200, details: list = None
    ):
        self.message = message
        self.details = details if details else []
        self.status_code = status_code

    def to_JSON(self):
        error = {"message": self.message}
        if isinstance(self.details, list) and len(self.details) > 0:
            error["details"] = self.details
        return jsonify(error)


class KeySizeError(RequestError):
    def __init__(self):
        super().__init__(
            message="size shall be a multiple of 8", 
            status_code=400
        )


class ExtensionMandatoryUnsupportedError(RequestError):
    def __init__(self, extension_mandatory: List[Dict[str, str]]):
        super().__init__(
            message="not all extension_mandatory parameters are supported",
            status_code=400,
        )
        self.details = extension_mandatory


class ExtensionMandatoryRequirementsError(RequestError):
    def __init__(self):
        super().__init__(
            message="not all extension_mandatory request options could be met",
            status_code=400,
        )

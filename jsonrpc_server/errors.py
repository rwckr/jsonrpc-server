class JSONRPCError(Exception):
    pass


class ParseError(JSONRPCError):
    code = -32700
    message = "Parse error"

    def __dict__(self):
        return {
                "code": self.code,
                "message": self.message
                }


class InvalidRequest(JSONRPCError):
    code = -32600
    message = "Invalid request"

    def __init__(self, data: dict):
        self.data = data

    def __dict__(self):
        return {
                "code": self.code,
                "message": self.message,
                "data": self.data
                }


class MethodNotFound(JSONRPCError):
    code = -32601
    message = "Method not found"

    def __init__(self, method: str):
        self.method = method

    def __dict__(self):
        return {
                "code": self.code,
                "message": self.message,
                "data": {
                    "method": self.method
                    }
                }


class InvalidParams(JSONRPCError):
    code = -32602
    message = "Invalid params"

    def __init__(self, data: dict):
        self.data = data

    def __dict__(self):
        return {
                "code": self.code,
                "message": self.message,
                "data": self.data
                }


class InternalError(JSONRPCError):
    code = -32603
    message = "Internal error"

    def __dict__(self):
        return {
                "code": self.code,
                "message": self.message
                }

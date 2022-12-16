from typing import Sequence, Union
from json.decoder import JSONDecodeError
from marshmallow import Schema, fields, ValidationError

from jsonrpc_server.errors import (
        JSONRPCError,
        ParseError,
        InvalidRequest,
        MethodNotFound,
        InvalidParams,
        InternalError
        )

from jsonrpc_server.schemas import JSONRPCRequest

import json
import inspect
import logging
import traceback


logger = logging.getLogger("jsonrpc")


class JSONRPCServer:
    def __init__(self):
        self._methods = dict()

    def process_request(self, request: str) -> str:

        try:
            request = json.loads(request)
        except JSONDecodeError:
            response = {"jsonrpc": "2.0", "id": None}
            response["error"] = ParseError().__dict__()
            return json.dumps(response)

        if isinstance(request, list):
            response = self._process_batch(requests=request)
        else:
            response = self._process_request(request)

        return json.dumps(response)

    def _process_request(self, request: dict) -> Union[dict, None]:

        """ Process a single JSONRPC request
        """
       
        response = {"jsonrpc": "2.0"}

        try:
            try: 
                _ = JSONRPCRequest().load(request)
            except ValidationError as e:
                raise InvalidRequest(e.messages)

            try:
                method = self._methods[request["method"]]["method"]
            except KeyError:
                raise MethodNotFound(method=request["method"])

            params_schema = self._methods[request["method"]]["params_schema"]
            params = request.get("params")

            if params:
                if isinstance(params, list):

                    try:
                        _ = params_schema.load({"positional_params": params})
                    except ValidationError as e:
                        raise InvalidParams(data=e.messages)

                    response["result"] = method(*params)

                elif isinstance(params, dict):

                    try:
                        _ = params_schema.load({"named_params": params})
                    except ValidationError as e:
                        raise InvalidParams(data=e.messages)

                    response["result"] = method(**params)
            else:
                response["result"] = method()

        except JSONRPCError as e:
            response["error"] = e.__dict__()

        except Exception as e:
            response["error"] = InternalError().__dict__()
            logger.error(traceback.format_exc().rstrip())

        if request.get("id"):
            response["id"] = request["id"]
            return response

    def _process_batch(self, requests: Sequence[dict]) -> Sequence[dict]:

        """ Process multiple JSONRPC requests
        """

        responses = list()

        for request in requests:
            responses.append(self._process_request(request))

        return responses

    def method(self, func):
        self._methods[func.__name__] = {"method": func}
        
        sig = inspect.signature(func)

        _named = dict()
        _positional = list()

        for k,v in sig.parameters.items():
            if v.annotation == int:
                _positional.append(fields.Int(required=True))
                _named[k] = fields.Int(required=True)

            elif v.annotation == str:
                _positional.append(fields.Str(required=True))
                _named[k] = fields.Str(required=True)

            elif v.annotation == bool:
                _positional.append(fields.Bool(required=True))
                _named[k] = fields.Bool(required=True)

        NamedSchema = type("NamedSchema", (Schema,), _named)
        ParamsSchema = type(
                "ParamsSchema", 
                (Schema,), 
                {
                    "named_params": fields.Nested(NamedSchema, required=False),
                    "positional_params": fields.Tuple(
                        tuple(_positional), requried=False
                        )
                    }
                )

        self._methods[func.__name__]["params_schema"] = ParamsSchema()

from marshmallow import Schema, fields


class JSONRPCField(fields.Str):
    def _deserialize(self, value, attr, data, **kwargs):
        super()._deserialize(value, attr, data, **kwargs)
        if value != "2.0":
            raise ValidationError("Not an accepted value.")


class IDField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) or isinstance(value, int):
            return value
        else:
            raise ValidationError("Not a valid string or integar.")


class ParamsField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, list) or isinstance(value, dict):
            return value
        else:
            raise ValidationError("Not a valid array or object.")


class JSONRPCRequest(Schema):
    jsonrpc = JSONRPCField(required=True)
    method = fields.Str(required=True)
    params = ParamsField()
    id = IDField()

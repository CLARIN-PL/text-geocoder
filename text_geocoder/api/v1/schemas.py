import marshmallow
from marshmallow import fields, validate


class DocumentSchema(marshmallow.Schema):
    text = fields.Str(required=True, validate=validate.Length(min=10, max=1000))


document_schema = DocumentSchema()

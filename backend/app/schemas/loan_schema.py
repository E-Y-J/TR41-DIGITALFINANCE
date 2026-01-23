# =============================================================================
# Digital Finance Tracker - Loan Schema (Aligned with Category, User, Budget)
# =============================================================================

from decimal import Decimal
from typing import Dict, Any

from marshmallow import fields, validate, validates_schema, ValidationError, EXCLUDE

from app.schemas.base import BaseSchema
from app.models.enums import LoanStatus


# =============================================================================
# LOAN SCHEMAS
# =============================================================================


class LoanSchema(BaseSchema):
    """
    Schema for serializing Loan model.

    Added computed fields:
        - user_name
        - category_name
        - budget_name (optional)
        - progress_percentage
    """

    class Meta:
        ordered = True

    # Primary key
    id = fields.UUID(dump_only=True)

    # Foreign keys
    user_id = fields.UUID(dump_only=True)
    budget_id = fields.UUID(allow_none=True)
    category_id = fields.UUID(required=True)

    # Computed fields
    user_name = fields.String(dump_only=True)
    category_name = fields.String(dump_only=True)
    budget_name = fields.String(dump_only=True)

    # Loan fields
    name = fields.String(required=True)
    original_amount = fields.Decimal(
        required=True, places=2, as_string=True, validate=validate.Range(min=Decimal("0.01"))
    )
    remaining_amount = fields.Decimal(
        required=True, places=2, as_string=True, validate=validate.Range(min=Decimal("0.00"))
    )

    progress_percentage = fields.Method("get_progress", dump_only=True)
    status = fields.Method("get_status", dump_only=True)

    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Methods to serialize enum and computed fields
    def get_status(self, obj):
        if hasattr(obj.status, "value"):
            return obj.status.value
        return str(obj.status) if obj.status else None

    def get_progress(self, obj):
        if hasattr(obj, "progress_percentage"):
            return obj.progress_percentage
        return 0


class LoanCreateSchema(BaseSchema):
    """
    Schema for creating a new loan.

    Optional:
        - budget_id
        - start_date
        - end_date
        - status (defaults to 'open')
    """

    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True)
    original_amount = fields.Decimal(
        required=True, places=2, as_string=True, validate=validate.Range(min=Decimal("0.01"))
    )
    remaining_amount = fields.Decimal(
        required=True, places=2, as_string=True, validate=validate.Range(min=Decimal("0.00"))
    )
    category_id = fields.UUID(required=True)
    budget_id = fields.UUID(allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    status = fields.String(
        validate=validate.OneOf([s.value for s in LoanStatus]),
        missing=LoanStatus.OPEN.value,  # defaults to OPEN
    )


class LoanUpdateSchema(BaseSchema):
    """
    Schema for updating an existing loan.

    All fields optional.
    """

    class Meta:
        unknown = EXCLUDE

    name = fields.String()
    original_amount = fields.Decimal(places=2, as_string=True, validate=validate.Range(min=Decimal("0.01")))
    remaining_amount = fields.Decimal(places=2, as_string=True, validate=validate.Range(min=Decimal("0.00")))
    category_id = fields.UUID()
    budget_id = fields.UUID(allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    status = fields.String(validate=validate.OneOf([s.value for s in LoanStatus]))


class LoanResponseSchema(BaseSchema):
    success = fields.Boolean(dump_only=True)
    data = fields.Nested(LoanSchema, dump_only=True)
    message = fields.String(dump_only=True)


class LoanListResponseSchema(BaseSchema):
    success = fields.Boolean(dump_only=True)
    data = fields.List(fields.Nested(LoanSchema), dump_only=True)
    message = fields.String(dump_only=True)
    meta = fields.Dict(dump_only=True)


# =============================================================================
# SCHEMA INSTANCES
# =============================================================================

loan_schema = LoanSchema()
loan_create_schema = LoanCreateSchema()
loan_update_schema = LoanUpdateSchema()
loan_list_schema = LoanSchema(many=True)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "LoanSchema",
    "LoanCreateSchema",
    "LoanUpdateSchema",
    "LoanResponseSchema",
    "LoanListResponseSchema",
    "loan_schema",
    "loan_create_schema",
    "loan_update_schema",
    "loan_list_schema",
]

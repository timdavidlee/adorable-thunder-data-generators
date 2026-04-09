from enum import StrEnum
from pydantic import BaseModel, Field


# all of these should be ordered with the top state being the most common
# and then descending in frequency from there, so that the generator will more often generate the more common states
class RequestStatusStates(StrEnum):
    APPROVED = "approved"
    INITIATED = "initiated"
    PENDING = "pending"
    REJECTED = "rejected"


class PurchaseOrderStatusStates(StrEnum):
    APPROVED = "approved"
    PENDING = "pending"
    DRAFT = "draft"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class InvoiceStatusStates(StrEnum):
    PAID = "paid"
    RECEIVED = "received"
    PENDING = "pending"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"
    IN_DISPUTE = "in_dispute"


class PaymentStatusStates(StrEnum):
    PAID = "paid"
    SCHEDULED = "scheduled"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class GeneratorConfig(BaseModel):
    num_requests: int = Field(
        default=200,
        description="The number of requests to generate",
        gt=0,
    )

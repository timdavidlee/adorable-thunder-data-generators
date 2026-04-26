from typing import NamedTuple


class PaymentTerm(NamedTuple):
    code: str
    label: str
    net_days: int | None


# net_days is None for terms without a fixed calendar due date
# Ordered by frequency in enterprise procurement (most common first)
PAYMENT_TERMS: list[PaymentTerm] = [
    PaymentTerm("NET30", "Net 30", 30),
    PaymentTerm("NET45", "Net 45", 45),
    PaymentTerm("NET60", "Net 60", 60),
    PaymentTerm("2_10_NET30", "2/10 Net 30", 30),
    PaymentTerm("NET15", "Net 15", 15),
    PaymentTerm("NET90", "Net 90", 90),
    PaymentTerm("DOR", "Due on Receipt", 0),
    PaymentTerm("NET7", "Net 7", 7),
    PaymentTerm("NET120", "Net 120", 120),
    PaymentTerm("EOM", "End of Month", None),
    PaymentTerm("PREPAID", "Prepaid", 0),
    PaymentTerm("COD", "Cash on Delivery", 0),
]

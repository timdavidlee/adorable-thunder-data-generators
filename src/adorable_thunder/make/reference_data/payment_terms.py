# (code, label, net_days)
# net_days is None for terms without a fixed calendar due date
# Ordered by frequency in enterprise procurement (most common first)
PAYMENT_TERMS = [
    ("NET30", "Net 30", 30),
    ("NET45", "Net 45", 45),
    ("NET60", "Net 60", 60),
    ("2_10_NET30", "2/10 Net 30", 30),
    ("NET15", "Net 15", 15),
    ("NET90", "Net 90", 90),
    ("DOR", "Due on Receipt", 0),
    ("NET7", "Net 7", 7),
    ("NET120", "Net 120", 120),
    ("EOM", "End of Month", None),
    ("PREPAID", "Prepaid", 0),
    ("COD", "Cash on Delivery", 0),
]

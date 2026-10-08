"""UPI Guardian - Transaction Data Model and Store."""

NAMES = [
    "Rahul Sharma",
    "Meera Stores",
    "Amit Patil",
    "Pune Electricity",
    "Neha Joshi",
    "City Pharmacy",
    "Rohan Verma",
    "Fresh Basket",
]

AMOUNTS = [35000, 1240, 8500, 2180, 48000, 640, 12999, 420, 7500, 1560, 29999, 890]
RISKS = [89, 12, 54, 8, 94, 19, 72, 6, 63, 24, 81, 16]

TRANSACTIONS: list[dict] = []

for index in range(24):
    risk = RISKS[index % len(RISKS)]
    day = 29 - (index // 4)
    late = index % 5 == 0

    if risk > 85:
        status = "critical"
    elif risk > 60:
        status = "high"
    elif risk > 30:
        status = "review"
    else:
        status = "safe"

    TRANSACTIONS.append(
        {
            "id": f"TXN-UG-{928401 + index:06d}",
            "date": f"{day} Sep 2026",
            "time": (
                "11:42 PM"
                if late
                else f"{10 + (index % 8)}:{(index * 7) % 60:02d} {'AM' if index % 2 else 'PM'}"
            ),
            "payee": NAMES[index % len(NAMES)],
            "amount": AMOUNTS[index % len(AMOUNTS)],
            "location": "Pune" if index % 3 == 0 else ("Mumbai" if index % 3 == 1 else "Nashik"),
            "risk": risk,
            "status": status,
            "newPayee": risk > 60,
            "upiId": f"demo.payee{index + 1}@upi",
            "device": "New Android device" if index % 4 == 0 else "Sunita's phone",
        }
    )


def get_all_transactions(status: str | None = None, query: str | None = None) -> list[dict]:
    """Retrieve all transactions with optional status and query filtering."""
    results = list(TRANSACTIONS)
    if status and status != "all":
        results = [t for t in results if t["status"] == status]
    if query and query.strip():
        q = query.strip().lower()
        results = [t for t in results if q in t["payee"].lower() or q in t["id"].lower()]
    return results


def get_transaction_by_id(transaction_id: str) -> dict | None:
    """Retrieve a single transaction by ID."""
    for t in TRANSACTIONS:
        if t["id"].upper() == transaction_id.upper():
            return t
    return None

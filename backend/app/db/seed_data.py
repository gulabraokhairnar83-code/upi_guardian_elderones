"""UPI Guardian - Synthetic Seed Data for MongoDB Atlas Collections.

NOTE: All records here are strictly synthetic demonstration data for academic and development testing.
No real banking information or actual personally identifiable data is used.
"""

from datetime import datetime, timezone

PRIMARY_USER_ID = "usr_sunita_68"


def seed_initial_data(db):
    """Seed the 7 collections with realistic synthetic records if empty."""
    from app.utils.auth import hash_password

    default_pw_hash = hash_password("GuardianPass123!")

    # 1. USERS COLLECTION
    if db.users.count_documents({}) == 0:
        db.users.insert_many(
            [
                {
                    "_id": PRIMARY_USER_ID,
                    "user_id": PRIMARY_USER_ID,
                    "name": "Sunita Devi",
                    "age": 68,
                    "location": "Pune, Maharashtra",
                    "phone": "+91 98765 43210",
                    "email": "sunita.demo@example.com",
                    "password_hash": default_pw_hash,
                    "role": "ELDER",
                    "accountSafetyStatus": "Protected",
                    "twoFactorEnabled": True,
                    "loginAlertsEnabled": True,
                    "is_synthetic": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "_id": "usr_sunita_alias",
                    "user_id": "usr_sunita_alias",
                    "name": "Sunita Devi",
                    "age": 68,
                    "location": "Pune, Maharashtra",
                    "phone": "+91 98765 43210",
                    "email": "sunita.devi@example.com",
                    "password_hash": default_pw_hash,
                    "role": "ELDER",
                    "accountSafetyStatus": "Protected",
                    "twoFactorEnabled": True,
                    "loginAlertsEnabled": True,
                    "is_synthetic": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "_id": "usr_rohit_01",
                    "user_id": "usr_rohit_01",
                    "name": "Rohit Caregiver",
                    "age": 38,
                    "location": "Pune, Maharashtra",
                    "phone": "+91 98201 12345",
                    "email": "rohit.caregiver@example.com",
                    "password_hash": default_pw_hash,
                    "role": "CAREGIVER",
                    "accountSafetyStatus": "Protected",
                    "twoFactorEnabled": True,
                    "loginAlertsEnabled": True,
                    "is_synthetic": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            ]
        )
    else:
        # Ensure demo users have valid password hashes in case collections existed
        db.users.update_one(
            {"$or": [{"email": "sunita.demo@example.com"}, {"_id": PRIMARY_USER_ID}]},
            {"$set": {"password_hash": default_pw_hash, "role": "ELDER"}},
        )
        if not db.users.find_one({"email": "sunita.devi@example.com"}):
            db.users.insert_one(
                {
                    "_id": "usr_sunita_alias",
                    "user_id": "usr_sunita_alias",
                    "name": "Sunita Devi",
                    "age": 68,
                    "location": "Pune, Maharashtra",
                    "phone": "+91 98765 43210",
                    "email": "sunita.devi@example.com",
                    "password_hash": default_pw_hash,
                    "role": "ELDER",
                    "accountSafetyStatus": "Protected",
                    "twoFactorEnabled": True,
                    "loginAlertsEnabled": True,
                    "is_synthetic": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        if not db.users.find_one({"email": "rohit.caregiver@example.com"}):
            db.users.insert_one(
                {
                    "_id": "usr_rohit_01",
                    "user_id": "usr_rohit_01",
                    "name": "Rohit Caregiver",
                    "age": 38,
                    "location": "Pune, Maharashtra",
                    "phone": "+91 98201 12345",
                    "email": "rohit.caregiver@example.com",
                    "password_hash": default_pw_hash,
                    "role": "CAREGIVER",
                    "accountSafetyStatus": "Protected",
                    "twoFactorEnabled": True,
                    "loginAlertsEnabled": True,
                    "is_synthetic": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )

    # 2. CAREGIVERS COLLECTION
    if db.caregivers.count_documents({}) == 0:
        db.caregivers.insert_many(
            [
                {
                    "caregiver_id": "cg_rajesh_01",
                    "user_id": PRIMARY_USER_ID,
                    "name": "Rajesh Devi",
                    "relation": "Son",
                    "phone": "+91 98201 12345",
                    "isTrusted": True,
                    "is_synthetic": True,
                },
                {
                    "caregiver_id": "cg_kavita_02",
                    "user_id": PRIMARY_USER_ID,
                    "name": "Kavita Rao",
                    "relation": "Daughter",
                    "phone": "+91 98202 23456",
                    "isTrusted": True,
                    "is_synthetic": True,
                },
                {
                    "caregiver_id": "cg_mehta_03",
                    "user_id": PRIMARY_USER_ID,
                    "name": "Dr. Mehta",
                    "relation": "Trusted Contact",
                    "phone": "+91 98203 34567",
                    "isTrusted": True,
                    "is_synthetic": True,
                },
            ]
        )

    # 3. NOTIFICATION_PREFERENCES COLLECTION
    if db.notification_preferences.count_documents({}) == 0:
        db.notification_preferences.insert_one(
            {
                "user_id": PRIMARY_USER_ID,
                "profile": {
                    "name": "Sunita Devi",
                    "age": 68,
                    "phone": "+91 ••••• ••410",
                    "email": "sunita.demo@example.com",
                },
                "security": {
                    "twoFactor": True,
                    "loginActivityAlerts": True,
                },
                "alertPreferences": {
                    "highRiskTransactions": True,
                    "scamCalls": True,
                    "scamSms": True,
                    "familyNotifications": True,
                },
                "accessibility": {
                    "seniorMode": False,
                    "highContrast": False,
                    "reducedMotion": False,
                    "voiceAssistance": False,
                },
                "is_synthetic": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    # 4. TRANSACTIONS COLLECTION
    if db.transactions.count_documents({}) == 0:
        names = [
            "Rahul Sharma",
            "Meera Stores",
            "Amit Patil",
            "Pune Electricity",
            "Neha Joshi",
            "City Pharmacy",
            "Rohan Verma",
            "Fresh Basket",
        ]
        amounts = [35000, 1240, 8500, 2180, 48000, 640, 12999, 420, 7500, 1560, 29999, 890]
        risks = [89, 12, 54, 8, 94, 19, 72, 6, 63, 24, 81, 16]

        synthetic_transactions = []
        for index in range(24):
            risk = risks[index % len(risks)]
            amount = amounts[index % len(amounts)]
            payee = names[index % len(names)]
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

            is_new = risk > 60
            formatted_time = (
                "11:42 PM"
                if late
                else f"{10 + (index % 8)}:{(index * 7) % 60:02d} {'AM' if index % 2 else 'PM'}"
            )

            synthetic_transactions.append(
                {
                    "id": f"TXN-UG-{928401 + index:06d}",
                    "user_id": PRIMARY_USER_ID,
                    "amount": float(amount),
                    "timestamp": f"2026-09-{day:02d}T{23 if late else 11}:{(index * 7) % 60:02d}:00Z",
                    "payee": payee,
                    "transaction_type": "P2M" if "Stores" in payee or "Pharmacy" in payee else "P2P",
                    "is_new_payee": is_new,
                    "historical_average": 2850.0,
                    "historical_std_dev": 1120.0,
                    "behavioral_deviation": round((amount - 2850.0) / 1120.0, 2),
                    "velocity": 3 if late else 1,
                    "unusual_time": late,
                    "anomaly_score": round(risk / 100.0, 2),
                    "communication_risk": 0.91 if late else 0.10,
                    "final_risk_score": risk,
                    "risk_level": status,
                    "explanation": (
                        "Unusual late night transaction to a new recipient with elevated anomaly score."
                        if risk > 60
                        else "Routine payment within expected historical baseline."
                    ),
                    "analyzed_at": datetime.now(timezone.utc).isoformat(),
                    # Frontend contract compatibility fields
                    "date": f"{day} Sep 2026",
                    "time": formatted_time,
                    "location": "Pune" if index % 3 == 0 else ("Mumbai" if index % 3 == 1 else "Nashik"),
                    "risk": risk,
                    "status": status,
                    "newPayee": is_new,
                    "upiId": f"demo.payee{index + 1}@upi",
                    "device": "New Android device" if index % 4 == 0 else "Sunita's phone",
                    "is_synthetic": True,
                }
            )
        db.transactions.insert_many(synthetic_transactions)

    # 5. ALERTS COLLECTION
    if db.alerts.count_documents({}) == 0:
        db.alerts.insert_many(
            [
                {
                    "id": 1,
                    "user_id": PRIMARY_USER_ID,
                    "transaction_id": "TXN-UG-928404",
                    "level": "critical",
                    "amount": 48000,
                    "title": "Large payment to a new payee",
                    "detail": "Made at 11:47 PM shortly after a suspicious call.",
                    "time": "12 minutes ago",
                    "risk": 92,
                    "status": "pending",
                    "is_synthetic": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "id": 2,
                    "user_id": PRIMARY_USER_ID,
                    "transaction_id": "TXN-UG-928400",
                    "level": "high",
                    "amount": 35000,
                    "title": "Unusual late-night transaction",
                    "detail": "Amount is much higher than Sunita’s normal payments.",
                    "time": "28 minutes ago",
                    "risk": 84,
                    "status": "pending",
                    "is_synthetic": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "id": 3,
                    "user_id": PRIMARY_USER_ID,
                    "transaction_id": "TXN-UG-928402",
                    "level": "review",
                    "amount": 8500,
                    "title": "Payment frequency increased",
                    "detail": "Three transactions were made within eleven minutes.",
                    "time": "2 hours ago",
                    "risk": 56,
                    "status": "pending",
                    "is_synthetic": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            ]
        )

    # 6. RISK_EVENTS COLLECTION (Incident Timeline)
    if db.risk_events.count_documents({}) == 0:
        db.risk_events.insert_many(
            [
                {
                    "event_id": "re_01",
                    "user_id": PRIMARY_USER_ID,
                    "time": "11:15 PM",
                    "text": "Suspicious SMS received",
                    "event_type": "SMS_ALERT",
                    "risk_score": 88,
                    "is_synthetic": True,
                },
                {
                    "event_id": "re_02",
                    "user_id": PRIMARY_USER_ID,
                    "time": "11:29 PM",
                    "text": "Scam-like call detected",
                    "event_type": "CALL_ALERT",
                    "risk_score": 94,
                    "is_synthetic": True,
                },
                {
                    "event_id": "re_03",
                    "user_id": PRIMARY_USER_ID,
                    "time": "11:42 PM",
                    "text": "₹35,000 UPI transaction initiated",
                    "event_type": "TRANSACTION_ANOMALY",
                    "risk_score": 89,
                    "is_synthetic": True,
                },
                {
                    "event_id": "re_04",
                    "user_id": PRIMARY_USER_ID,
                    "time": "11:43 PM",
                    "text": "High-risk transaction detected",
                    "event_type": "FUSION_SCORE",
                    "risk_score": 92,
                    "is_synthetic": True,
                },
                {
                    "event_id": "re_05",
                    "user_id": PRIMARY_USER_ID,
                    "time": "11:44 PM",
                    "text": "Family alert generated",
                    "event_type": "FAMILY_NOTIFIED",
                    "risk_score": 92,
                    "is_synthetic": True,
                },
            ]
        )

    # 7. ANALYZED_MESSAGES COLLECTION
    if db.analyzed_messages.count_documents({}) == 0:
        db.analyzed_messages.insert_one(
            {
                "message_id": "msg_sample_01",
                "user_id": PRIMARY_USER_ID,
                "text": "URGENT: Your account will be suspended. Share OTP and verify now at secure-upi-check.example",
                "type": "sms",
                "risk_score": 88,
                "level": "critical",
                "is_suspicious": True,
                "detected_patterns": [
                    "OTP request",
                    "Urgency or threat",
                    "Account blocking claim",
                    "Confidential information request",
                    "Impersonation",
                ],
                "explanation": "Simulated initial benchmark: message contains urgency coercion pattern.",
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "is_synthetic": True,
            }
        )

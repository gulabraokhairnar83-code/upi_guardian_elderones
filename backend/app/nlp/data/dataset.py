"""UPI Guardian - NLP Scam Communication Dataset Generator.

Generates a balanced, reproducible synthetic/demonstration dataset containing:
- NORMAL messages (genuine bank alerts, bill receipts, family messages, support notes, including benign OTP warnings)
- SUSPICIOUS messages (unsolicited offers, vague urgency, promotional links)
- SCAM messages (coercive threats, OTP/PIN requests, AnyDesk installations, electricity cut threats)

Covers all 14 target scam categories:
1. OTP_REQUEST
2. UPI_PIN_REQUEST
3. KYC_THREAT
4. ACCOUNT_BLOCK_THREAT
5. URGENT_PAYMENT
6. FAKE_BANK_SUPPORT
7. FAKE_UPI_SUPPORT
8. PRIZE_REWARD_SCAM
9. IMPERSONATION
10. REMOTE_ACCESS_REQUEST
11. SUSPICIOUS_PAYMENT_LINK
12. ELECTRICITY_DISCONNECTION_SCAM
13. LOAN_OR_REFUND_SCAM
14. DELIVERY_OR_CUSTOMS_SCAM
"""

import random
import pandas as pd
from app.nlp.preprocessing.text_cleaner import TextCleaner

# 1. NORMAL SAMPLES (Include benign occurrences of words like OTP, account, verify, payment)
NORMAL_TEMPLATES = [
    # Benign OTP / Security Notices
    ("Your OTP for netbanking login is 482019. Never share your OTP with anyone, including bank staff.", "sms", "NORMAL", "BENIGN_BANKING"),
    ("Dear customer, OTP for your transaction of Rs 640 at Apollo Meds is 918234. Do not disclose to anyone.", "sms", "NORMAL", "BENIGN_BANKING"),
    ("Use OTP 581902 to verify your mobile number on Government PF portal. Valid for 10 minutes.", "sms", "NORMAL", "BENIGN_SECURITY"),
    ("Your one time password for electricity bill payment is 319482. State electricity board will never ask for your password.", "sms", "NORMAL", "BENIGN_SECURITY"),
    ("Security notice: Never share your OTP, UPI PIN, or password with callers claiming to represent the bank.", "sms", "NORMAL", "BENIGN_SECURITY"),

    # Genuine Bank Alerts & Confirmations
    ("Your A/c XX4109 is debited by Rs 1,250.00 on 28-Sep-26 at FRESH BASKET. Available balance: Rs 42,310.00.", "sms", "NORMAL", "BENIGN_TRANSACTION"),
    ("Dear Sunita, your pension payment of Rs 24,500 has been credited to your account XX4109.", "sms", "NORMAL", "BENIGN_TRANSACTION"),
    ("Rs 450.00 paid successfully to City Care Pharmacy via UPI Ref No 9284102948. Axis Bank.", "sms", "NORMAL", "BENIGN_TRANSACTION"),
    ("Dear customer, your request for cheque book dispatch has been processed. Delivery by Friday.", "sms", "NORMAL", "BENIGN_BANKING"),
    ("Your fixed deposit account XX8192 renewal advice has been sent to your registered email.", "sms", "NORMAL", "BENIGN_BANKING"),
    ("Account verification successful. Your KYC documents were reviewed at Pune Camp branch.", "sms", "NORMAL", "BENIGN_BANKING"),
    ("Thank you for updating your nominee details. Your updated bank profile is active.", "sms", "NORMAL", "BENIGN_BANKING"),

    # Routine Bills & Utilities
    ("Payment received: Rs 1,840 for MSEB electricity bill consumer number 04918201. Thank you.", "sms", "NORMAL", "BENIGN_BILL"),
    ("Your gas cylinder refill booking order 92810 has been confirmed. Delivery scheduled tomorrow.", "sms", "NORMAL", "BENIGN_BILL"),
    ("Jio prepaid recharge of Rs 399 is successful. 2GB/day data valid for 28 days.", "sms", "NORMAL", "BENIGN_BILL"),
    ("Pune Municipal Corporation: Water tax receipt for consumer 81923 issued successfully.", "sms", "NORMAL", "BENIGN_BILL"),

    # Family & Personal Messages
    ("Mummy, please send me 500 rupees for medicines when you get time. Love, Rajesh.", "sms", "NORMAL", "BENIGN_FAMILY"),
    ("Didi, doctor appointment is confirmed for tomorrow 11:30 AM at Ruby Hall clinic.", "sms", "NORMAL", "BENIGN_FAMILY"),
    ("Grandma, we reached home safely. Will call you on video call in the evening.", "sms", "NORMAL", "BENIGN_FAMILY"),
    ("Sunita ji, temple committee meeting is scheduled for Saturday 5 PM at community hall.", "sms", "NORMAL", "BENIGN_FAMILY"),

    # Normal Customer Service & Call Transcripts
    ("Hello Sunita ji, this is Dr. Mehta's assistant calling to confirm your routine checkup tomorrow at 11:00 AM.", "call_transcript", "NORMAL", "BENIGN_SERVICE"),
    ("Calling from Fresh Basket: Madam, your grocery delivery boy is downstairs at building entrance.", "call_transcript", "NORMAL", "BENIGN_SERVICE"),
    ("Namaste, I am Rajesh calling from Mumbai. Maa, how is your health today? Did you take medicines?", "call_transcript", "NORMAL", "BENIGN_FAMILY"),
    ("This is automated call from Pune electricity board informing scheduled maintenance in Kothrud area tomorrow from 10 AM to 1 PM.", "call_transcript", "NORMAL", "BENIGN_SERVICE"),
    ("Hello Sunita ma'am, calling from your bank branch. We noticed your card is expiring next month. Would you like a replacement sent to your home address?", "call_transcript", "NORMAL", "BENIGN_BANKING"),
]

# 2. SUSPICIOUS SAMPLES (Weaker warning signs, unsolicited offers, vague links, mild urgency)
SUSPICIOUS_TEMPLATES = [
    ("Dear user, you have unredeemed rewards points worth Rs 4,500. Check points at reward-points-portal.net", "sms", "SUSPICIOUS", "PRIZE_REWARD_SCAM"),
    ("Your UPI profile is eligible for an instant credit limit increase of Rs 50,000. Verify profile now.", "sms", "SUSPICIOUS", "FAKE_UPI_SUPPORT"),
    ("Special festival gift voucher is pending for your mobile number. Claim before midnight.", "sms", "SUSPICIOUS", "PRIZE_REWARD_SCAM"),
    ("Notice: Your PAN card requires profile verification to avoid banking delays. Click link to verify.", "sms", "SUSPICIOUS", "KYC_THREAT"),
    ("Pre-approved loan of Rs 2,00,000 sanctioned for your account. Minimal documentation required.", "sms", "SUSPICIOUS", "LOAN_OR_REFUND_SCAM"),
    ("Courier notice: Your parcel 94819 is held at hub due to incomplete address. Update address online.", "sms", "SUSPICIOUS", "DELIVERY_OR_CUSTOMS_SCAM"),
    ("Dear customer, please review your pending cashback transaction of Rs 850 at promo-cashback-desk.org", "sms", "SUSPICIOUS", "SUSPICIOUS_PAYMENT_LINK"),
    ("Attention user: Upgrade to senior citizen priority banking card without fees. Inquire today.", "sms", "SUSPICIOUS", "IMPERSONATION"),
    ("Caller: Hello madam, I am calling from insurance customer care regarding your pending bonus points. Please confirm your date of birth and pin code.", "call_transcript", "SUSPICIOUS", "IMPERSONATION"),
    ("Caller: Good afternoon, this is customer loyalty desk. You have an unclaimed cashback reward from your last shopping payment. May I guide you to activate it?", "call_transcript", "SUSPICIOUS", "PRIZE_REWARD_SCAM"),
    ("Caller: Calling regarding your parcel delivery. The courier boy cannot find your flat number. Please send 5 rupees verification fee online to update address.", "call_transcript", "SUSPICIOUS", "DELIVERY_OR_CUSTOMS_SCAM"),
    ("Caller: Hello, your phone number has been selected for exclusive digital payment discount scheme. Press 1 to speak with representative.", "call_transcript", "SUSPICIOUS", "PRIZE_REWARD_SCAM"),
]

# 3. SCAM SAMPLES (Explicit coercive threats, OTP/PIN extortion, remote tools, electricity cuts, fake police)
SCAM_TEMPLATES = [
    # 1. OTP_REQUEST
    ("URGENT: Your SBI account has been compromised. An officer is reversing fraudulent debit. Send OTP immediately to verify reversal.", "sms", "SCAM", "OTP_REQUEST"),
    ("Dear customer, payment of Rs 35,000 initiated. If not you, share OTP 849201 to cancel unauthorized transaction immediately.", "sms", "SCAM", "OTP_REQUEST"),
    ("Caller: Madam I am calling from bank fraud department. Your account is being hacked right now! Read me the 6 digit OTP you just received or your money will be lost!", "call_transcript", "SCAM", "OTP_REQUEST"),

    # 2. UPI_PIN_REQUEST
    ("Caller: Sir to receive your Rs 25,000 government subsidy credit, open PhonePe, scan this QR code, and enter your secret UPI PIN to receive money in your account.", "call_transcript", "SCAM", "UPI_PIN_REQUEST"),
    ("Refund of Rs 8,500 is waiting for your UPI ID. Enter UPI PIN on payment screen to accept credit into your bank account.", "sms", "SCAM", "UPI_PIN_REQUEST"),
    ("Caller: Don't worry madam, enter your 4-digit UPI PIN on the screen. UPI PIN is required to receive incoming cash into your account.", "call_transcript", "SCAM", "UPI_PIN_REQUEST"),

    # 3. KYC_THREAT
    ("IMPORTANT NOTICE: Your SBI KYC has expired today. Your bank account will be permanently blocked within 24 hours. Update KYC immediately at bit.ly/sbi-kyc-verify", "sms", "SCAM", "KYC_THREAT"),
    ("Dear user, your Paytm KYC suspended. Account freeze in 2 hours. Upload Aadhaar and PAN immediately at paytm-kyc-update.online", "sms", "SCAM", "KYC_THREAT"),
    ("Caller: I am senior manager from Reserve Bank compliance. Your bank KYC is not completed. Your account and ATM card will be blocked by 5 PM unless you complete online verification.", "call_transcript", "SCAM", "KYC_THREAT"),

    # 4. ACCOUNT_BLOCK_THREAT
    ("FINAL WARNING: Your HDFC bank account will be blocked today due to suspicious activity. Click here immediately to unfreeze your account.", "sms", "SCAM", "ACCOUNT_BLOCK_THREAT"),
    ("Your UPI account will stop working in 10 minutes. Complete verification or pay penalty of Rs 5,000.", "sms", "SCAM", "ACCOUNT_BLOCK_THREAT"),
    ("Caller: Madam your savings account is flagged for illegal transactions and will be blocked in 15 minutes. Cooperate with me right now to keep account active.", "call_transcript", "SCAM", "ACCOUNT_BLOCK_THREAT"),

    # 5. URGENT_PAYMENT
    ("Emergency: Your son Rajesh is involved in urgent police custody accident. Immediately transfer Rs 40,000 to hospital UPI id hospital.urgent@upi to release him.", "sms", "SCAM", "URGENT_PAYMENT"),
    ("Caller: Hello, I am Inspector Shinde from police station. Your relative has been arrested. Transfer 50,000 rupees to this account within 10 minutes or we will register FIR.", "call_transcript", "SCAM", "URGENT_PAYMENT"),

    # 6. FAKE_BANK_SUPPORT
    ("SBI Customer Care: Unauthorized payment of Rs 48,000 detected from your debit card. Contact helpline officer immediately at 9820192841.", "sms", "SCAM", "FAKE_BANK_SUPPORT"),
    ("Caller: Good evening, I am calling from ICICI Bank security cell. We detected a fraudulent transfer to a Pakistani account from your phone. You must verify your credentials with me.", "call_transcript", "SCAM", "FAKE_BANK_SUPPORT"),

    # 7. FAKE_UPI_SUPPORT
    ("Google Pay Support: A refund of Rs 12,000 failed to credit. Call Google Pay senior manager at 9830112345 to process instant refund.", "sms", "SCAM", "FAKE_UPI_SUPPORT"),
    ("PhonePe Alert: Your wallet is blocked. To unblock, send Rs 1 to UPI handle unblock.desk@upi for security verification.", "sms", "SCAM", "FAKE_UPI_SUPPORT"),

    # 8. PRIZE_REWARD_SCAM
    ("CONGRATULATIONS! Your mobile number won Rs 25,00,000 in KBC Jio Lucky Draw 2026. Send processing fee of Rs 3,500 on WhatsApp to claim lottery.", "sms", "SCAM", "PRIZE_REWARD_SCAM"),
    ("Caller: Sir congratulations, you are 1st prize winner of Maruti car or cash 15 lakh rupees. Pay 1% GST registration fee through Google Pay right now to dispatch cheque.", "call_transcript", "SCAM", "PRIZE_REWARD_SCAM"),

    # 9. IMPERSONATION
    ("Caller: Hello Sunita aunty, I am Amit, your son's friend. Rajesh met with an emergency in Delhi and told me to call you. He needs 30,000 rupees immediately. Please send on my UPI.", "call_transcript", "SCAM", "IMPERSONATION"),
    ("Caller: This is Telecom Regulatory Authority officer. Your SIM card will be disconnected within 2 hours because multiple illegal complaints are filed against your Aadhaar.", "call_transcript", "SCAM", "IMPERSONATION"),

    # 10. REMOTE_ACCESS_REQUEST
    ("To fix your mobile banking error, install AnyDesk application from playstore and tell the 9-digit code to bank executive.", "sms", "SCAM", "REMOTE_ACCESS_REQUEST"),
    ("Caller: Madam please open Play Store on your phone and search for TeamViewer QuickSupport. Install it and tell me the access number on your screen so I can repair your bank app remotely.", "call_transcript", "SCAM", "REMOTE_ACCESS_REQUEST"),
    ("Caller: Sir install RustDesk APK app sent on your WhatsApp to update electricity meter software directly from electricity board server.", "call_transcript", "SCAM", "REMOTE_ACCESS_REQUEST"),

    # 11. SUSPICIOUS_PAYMENT_LINK
    ("Alert: Your electricity bill payment of Rs 1,840 is pending. Pay immediately at fake-mseb-billpay.biz/pay to avoid power cut.", "sms", "SCAM", "SUSPICIOUS_PAYMENT_LINK"),
    ("Click tinyurl.com/secure-bank-login to prevent your ATM card permanent deactivation.", "sms", "SCAM", "SUSPICIOUS_PAYMENT_LINK"),

    # 12. ELECTRICITY_DISCONNECTION_SCAM
    ("Dear Consumer, Your Electricity power will be disconnected Tonight at 9.30 PM from electricity office because your previous month bill was not updated. Immediately contact our electricity officer at 9820114920.", "sms", "SCAM", "ELECTRICITY_DISCONNECTION_SCAM"),
    ("Caller: Hello, this is officer from power supply board. Your meter bill payment failed and lineman will cut power supply in 30 minutes. Pay 200 rupees update fee on UPI immediately.", "call_transcript", "SCAM", "ELECTRICITY_DISCONNECTION_SCAM"),

    # 13. LOAN_OR_REFUND_SCAM
    ("Your income tax refund of Rs 24,800 is approved by department. Submit bank account details and debit card CVV at incometax-refund-gov.in to transfer funds.", "sms", "SCAM", "LOAN_OR_REFUND_SCAM"),
    ("Caller: I am calling from insurance regulatory authority. Your lapsed policy has 1.8 lakh rupees bonus ready. Send 5,000 rupees stamp duty fee to release full amount.", "call_transcript", "SCAM", "LOAN_OR_REFUND_SCAM"),

    # 14. DELIVERY_OR_CUSTOMS_SCAM
    ("India Post Alert: Your valuable parcel consignment from abroad is stuck at customs airport. Pay customs duty Rs 6,500 immediately to release packet.", "sms", "SCAM", "DELIVERY_OR_CUSTOMS_SCAM"),
    ("Caller: Calling from international airport courier desk. A parcel containing gold jewelry and foreign currency in your name is intercepted. Pay penalty fine or police will come to your house.", "call_transcript", "SCAM", "DELIVERY_OR_CUSTOMS_SCAM"),
]


class ScamDatasetGenerator:
    """Generates an augmented, balanced synthetic communication dataset for NLP training."""

    def __init__(self, random_seed: int = 42, target_samples: int = 600):
        self.random_seed = random_seed
        self.target_samples = max(100, target_samples)
        self.rng = random.Random(random_seed)

    def generate(self) -> pd.DataFrame:
        """Generate balanced and augmented training dataset."""
        records = []

        # Base templates
        all_templates = (
            [(*t, "base") for t in NORMAL_TEMPLATES]
            + [(*t, "base") for t in SUSPICIOUS_TEMPLATES]
            + [(*t, "base") for t in SCAM_TEMPLATES]
        )

        for text, msg_type, label, category, _ in all_templates:
            records.append({
                "text": text,
                "cleaned_text": TextCleaner.clean(text),
                "message_type": msg_type,
                "label": label,
                "category": category,
            })

        # Augmentation variations (different amounts, times, bank names, urgency words)
        banks = ["SBI", "HDFC", "ICICI", "Axis Bank", "Punjab National Bank", "Bank of Baroda", "Kotak"]
        amounts = ["1,250", "4,800", "12,500", "28,000", "45,000", "75,000"]
        times = ["10 minutes", "15 minutes", "2 hours", "tonight at 9:30 PM", "within 24 hours"]

        # Synthesize variations up to target_samples while maintaining class balance
        while len(records) < self.target_samples:
            source = self.rng.choice(all_templates)
            text, msg_type, label, category, _ = source

            aug_text = text
            bank = self.rng.choice(banks)
            amt = self.rng.choice(amounts)
            t_span = self.rng.choice(times)

            for b in ["SBI", "HDFC", "ICICI", "Axis Bank", "State Bank"]:
                if b in aug_text:
                    aug_text = aug_text.replace(b, bank)
            for a in ["35,000", "40,000", "48,000", "25,000", "1,840"]:
                if a in aug_text:
                    aug_text = aug_text.replace(a, amt)
            for t in ["today", "in 10 minutes", "Tonight at 9.30 PM", "within 24 hours"]:
                if t in aug_text:
                    aug_text = aug_text.replace(t, t_span)

            records.append({
                "text": aug_text,
                "cleaned_text": TextCleaner.clean(aug_text),
                "message_type": msg_type,
                "label": label,
                "category": category,
            })

        self.rng.shuffle(records)
        df = pd.DataFrame(records)
        return df

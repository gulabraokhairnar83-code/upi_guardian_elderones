"""UPI Guardian - NLP Scam Communication Explainability Layer.

Identifies matched scam categories and suspicious phrases using deterministic
linguistic patterns, clearly distinguishing rule-based domain reasoning from
the statistical ML Logistic Regression classification.
"""

import re

# Controlled dictionary of suspicious phrases and category triggers
CATEGORY_PATTERNS: dict[str, list[re.Pattern]] = {
    "OTP_REQUEST": [
        re.compile(r"\b(?:share|send|tell|give|read|enter)\s+(?:your\s+)?otp\b", re.I),
        re.compile(r"\botp\s+(?:immediately|now|to\s+cancel|to\s+reverse|required)\b", re.I),
        re.compile(r"\b6[\s\-]digit\s+otp\b", re.I),
    ],
    "UPI_PIN_REQUEST": [
        re.compile(r"\b(?:enter|share|type)\s+(?:your\s+)?(?:secret\s+)?upi\s*pin\b", re.I),
        re.compile(r"\bupi\s*pin\s+(?:is\s+required|to\s+receive|to\s+accept)\b", re.I),
        re.compile(r"\b4[\s\-]digit\s+upi\s*pin\b", re.I),
    ],
    "KYC_THREAT": [
        re.compile(r"\bkyc\s+(?:has\s+)?(?:expired|suspended|pending|incomplete)\b", re.I),
        re.compile(r"\bupdate\s+(?:your\s+)?kyc\b", re.I),
        re.compile(r"\b(?:pan|aadhaar)\s+(?:card\s+)?(?:verification|requires\s+update)\b", re.I),
    ],
    "ACCOUNT_BLOCK_THREAT": [
        re.compile(r"\baccount\s+will\s+be\s+(?:permanently\s+)?blocked\b", re.I),
        re.compile(r"\baccount\s+(?:freeze|suspended|deactivated)\b", re.I),
        re.compile(r"\bupi\s+(?:account\s+)?will\s+stop\s+working\b", re.I),
        re.compile(r"\bfinal\s+warning\b", re.I),
    ],
    "URGENT_PAYMENT": [
        re.compile(r"\bwithin\s+(?:10|15|20|30)\s+minutes\b", re.I),
        re.compile(r"\bemergency\s+(?:transfer|hospital|police)\b", re.I),
        re.compile(r"\barrested|police\s+custody|register\s+fir\b", re.I),
    ],
    "FAKE_BANK_SUPPORT": [
        re.compile(r"\bbank\s+fraud\s+department\b", re.I),
        re.compile(r"\bbank\s+security\s+cell\b", re.I),
        re.compile(r"\baccount\s+is\s+being\s+hacked\b", re.I),
        re.compile(r"\bcontact\s+helpline\s+officer\b", re.I),
    ],
    "FAKE_UPI_SUPPORT": [
        re.compile(r"\b(?:google\s*pay|phonepe|paytm)\s+(?:support|senior\s+manager|alert)\b", re.I),
        re.compile(r"\brefund\s+(?:of\s+rs\s+)?\d+\s+failed\s+to\s+credit\b", re.I),
        re.compile(r"\bwallet\s+is\s+blocked\b", re.I),
    ],
    "PRIZE_REWARD_SCAM": [
        re.compile(r"\b(?:won|winner\s+of)\s+(?:rs|lakh|car|lottery|prize)\b", re.I),
        re.compile(r"\bkbc\s+(?:jio\s+)?lucky\s+draw\b", re.I),
        re.compile(r"\bclaim\s+(?:lottery|reward|bonus\s+points|cashback)\b", re.I),
    ],
    "IMPERSONATION": [
        re.compile(r"\b(?:calling\s+from|inspector|officer|senior\s+manager)\s+(?:police|telecom|trai|rbi|reserve\s+bank)\b", re.I),
        re.compile(r"\byour\s+son(?:'s)?\s+friend\b", re.I),
    ],
    "REMOTE_ACCESS_REQUEST": [
        re.compile(r"\b(?:install|download)\s+(?:anydesk|teamviewer|quicksupport|rustdesk)\b", re.I),
        re.compile(r"\binstall\s+(?:this\s+)?(?:apk|application|app)\b", re.I),
        re.compile(r"\btell\s+(?:the\s+)?(?:9[\s\-]digit\s+code|access\s+number)\b", re.I),
    ],
    "SUSPICIOUS_PAYMENT_LINK": [
        re.compile(r"\bbit\.ly/\S+|tinyurl\.com/\S+\b", re.I),
        re.compile(r"\bclick\s+(?:here|this\s+link|link_url)\b", re.I),
    ],
    "ELECTRICITY_DISCONNECTION_SCAM": [
        re.compile(r"\belectricity\s+(?:power\s+|connection\s+)?will\s+be\s+(?:disconnected|cut\s+off)\b", re.I),
        re.compile(r"\bpower\s+cut\b|\bcut\s+off\b", re.I),
        re.compile(r"\btonight\s+at\s+9[\.:]30\s*pm\b", re.I),
        re.compile(r"\bprevious\s+(?:month\s+)?bill\s+(?:was\s+)?not\s+updated\b", re.I),
    ],
    "LOAN_OR_REFUND_SCAM": [
        re.compile(r"\bincome\s+tax\s+refund\b", re.I),
        re.compile(r"\blapsed\s+policy\s+(?:bonus)?\b", re.I),
        re.compile(r"\bpre[\s\-]approved\s+loan\b", re.I),
    ],
    "DELIVERY_OR_CUSTOMS_SCAM": [
        re.compile(r"\b(?:parcel|consignment)\s+(?:is\s+)?stuck\s+at\s+customs\b", re.I),
        re.compile(r"\bpay\s+customs\s+duty\b", re.I),
        re.compile(r"\bforeign\s+currency|gold\s+jewelry\b", re.I),
    ],
}


class ScamExplainer:
    """Provides transparent, rule-based category detection, phrase extraction, and elder advice."""

    @classmethod
    def explain(
        cls,
        text: str,
        classification: str,
        scam_probability: float,
        risk_level: str,
    ) -> dict:
        """Derive categories, extract phrases, and formulate advice.

        Args:
            text: Original message or call transcript text.
            classification: 'NORMAL', 'SUSPICIOUS', or 'SCAM' (from ML classifier).
            scam_probability: Model scam probability estimate (0.0 to 100.0).
            risk_level: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'.

        Returns:
            dict containing categories, suspicious_phrases, explanation, recommended_action.
        """
        matched_categories = []
        matched_phrases = []

        # Evaluate deterministic pattern matching
        for category, patterns in CATEGORY_PATTERNS.items():
            for pat in patterns:
                matches = pat.findall(text)
                if matches:
                    if category not in matched_categories:
                        matched_categories.append(category)
                    for m in matches:
                        phrase_clean = str(m).strip()
                        if phrase_clean and phrase_clean not in matched_phrases:
                            matched_phrases.append(phrase_clean)

        # Build human-readable explanation
        explanation = cls._generate_explanation(
            classification=classification,
            scam_probability=scam_probability,
            categories=matched_categories,
        )

        # Build elder-friendly recommended action
        recommended_action = cls._generate_recommended_action(
            classification=classification,
            categories=matched_categories,
        )

        return {
            "categories": matched_categories,
            "suspicious_phrases": matched_phrases[:8],
            "explanation": explanation,
            "recommended_action": recommended_action,
        }

    @staticmethod
    def _generate_explanation(
        classification: str,
        scam_probability: float,
        categories: list[str],
    ) -> str:
        """Synthesize neutral, safety-oriented explanation."""
        readable_cats = [c.replace("_", " ").lower() for c in categories]

        if classification == "SCAM":
            if readable_cats:
                cat_summary = ", ".join(readable_cats[:3])
                return (
                    f"Potential scam detected (model confidence: {scam_probability:.1f}%). "
                    f"The communication exhibits high-risk coercive indicators including {cat_summary}."
                )
            return (
                f"Potential scam detected (model confidence: {scam_probability:.1f}%). "
                "The message exhibits strong linguistic patterns associated with financial fraud."
            )

        if classification == "SUSPICIOUS":
            if readable_cats:
                cat_summary = ", ".join(readable_cats[:3])
                return (
                    f"Suspicious communication detected (risk score: {scam_probability:.1f}%). "
                    f"Contains unverified signals such as {cat_summary}."
                )
            return (
                f"Suspicious communication detected (risk score: {scam_probability:.1f}%). "
                "Presents unverified promotional or urgency claims requiring caution."
            )

        return (
            f"Routine communication (risk score: {scam_probability:.1f}%). "
            "No coercive threats, unauthorized OTP demands, or scam patterns detected."
        )

    @staticmethod
    def _generate_recommended_action(classification: str, categories: list[str]) -> str:
        """Formulate actionable advice without causing panic."""
        if classification == "SCAM":
            if "OTP_REQUEST" in categories or "UPI_PIN_REQUEST" in categories:
                return (
                    "Do NOT share your OTP, UPI PIN, or passwords with anyone. "
                    "Legitimate bank officials never ask for secret PINs over calls or SMS."
                )
            if "REMOTE_ACCESS_REQUEST" in categories:
                return (
                    "Do NOT install AnyDesk, TeamViewer, or unknown APK applications. "
                    "Contact a trusted family member or visit your branch in person."
                )
            if "ELECTRICITY_DISCONNECTION_SCAM" in categories:
                return (
                    "Do NOT call the phone number in the message. Electricity boards never "
                    "cut power within minutes via SMS. Verify your bill on the official MSEB/utility portal."
                )
            return (
                "Do not respond, click links, share OTP/PIN, or transfer money. "
                "Contact your bank or service provider through its official verified customer care number."
            )

        if classification == "SUSPICIOUS":
            return (
                "Do not share personal details, OTP, or UPI PIN. "
                "Verify the sender's identity using an independent official contact method before proceeding."
            )

        return "Continue normally. Remember to never disclose your UPI PIN or banking passwords."

export type MessageAnalysisResult = {
  isSuspicious: boolean;
  riskScore: number;
  level: "safe" | "review" | "high" | "critical";
  title: string;
  detectedPatterns: string[];
  explanation: string;
  recommendations: string[];
  isDemo: boolean;
  suspiciousPhrases?: string[];
  classification?: string;
  recommendedAction?: string;
};

export const sampleSmsText =
  "URGENT: Your account will be suspended. Share OTP and verify now at secure-upi-check.example";

export const sampleCallTranscript =
  "Your bank account will be blocked today. Please share your OTP to verify your account immediately.";

export const detectedScamPatterns: readonly string[] = [
  "OTP request",
  "Urgency or threat",
  "Account blocking claim",
  "Confidential information request",
  "Impersonation",
] as const;

export const mockSmsAnalysisResult: MessageAnalysisResult = {
  isSuspicious: true,
  riskScore: 88,
  level: "critical",
  title: "SUSPICIOUS MESSAGE DETECTED",
  detectedPatterns: [...detectedScamPatterns],
  explanation:
    "This message contains multiple patterns commonly associated with financial scams. Do not share private details or open links.",
  recommendations: [
    "Never share OTP or PIN with anyone",
    "Banks never threaten immediate suspension via SMS",
    "Do not click on unverified link attachments",
  ],
  isDemo: true,
};

export const mockCallAnalysisResult: MessageAnalysisResult = {
  isSuspicious: true,
  riskScore: 94,
  level: "critical",
  title: "SCAM RISK DETECTED",
  detectedPatterns: [...detectedScamPatterns],
  explanation:
    "This conversation contains multiple patterns commonly associated with financial scams. Do not share private details or open links.",
  recommendations: [
    "Hang up immediately and contact your branch directly",
    "Call a trusted family member before taking any action",
    "Never verify account details over phone calls",
  ],
  isDemo: true,
};

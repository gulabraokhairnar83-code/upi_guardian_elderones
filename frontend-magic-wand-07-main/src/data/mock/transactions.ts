export type RiskLevel = "safe" | "review" | "high" | "critical";

export type Transaction = {
  id: string;
  date: string;
  time: string;
  payee: string;
  amount: number;
  location: string;
  risk: number;
  status: RiskLevel;
  newPayee: boolean;
  upiId: string;
  device: string;
  transaction_id?: string;
  timestamp?: string;
  transaction_type?: string;
  is_new_payee?: boolean;
  behavioral_deviation?: number;
  velocity?: number;
  anomaly_score?: number;
  risk_level?: string;
  explanation?: string;
  analyzed_at?: string;
};

export type ActivityPoint = {
  time: string;
  normal: number;
  suspicious: number;
  high: number;
};

export type ReportPoint = {
  day: string;
  volume: number;
  risk: number;
  calls: number;
  sms: number;
};

const names: readonly string[] = [
  "Rahul Sharma",
  "Meera Stores",
  "Amit Patil",
  "Pune Electricity",
  "Neha Joshi",
  "City Pharmacy",
  "Rohan Verma",
  "Fresh Basket",
];

const amounts: readonly number[] = [
  35000, 1240, 8500, 2180, 48000, 640, 12999, 420, 7500, 1560, 29999, 890,
];

const risks: readonly number[] = [
  89, 12, 54, 8, 94, 19, 72, 6, 63, 24, 81, 16,
];

export const transactions: Transaction[] = Array.from({ length: 24 }, (_, index) => {
  const risk = risks[index % risks.length] ?? 20;
  const payee = names[index % names.length] ?? "Unknown Payee";
  const amount = amounts[index % amounts.length] ?? 1000;
  const day = 29 - Math.floor(index / 4);
  const late = index % 5 === 0;

  const status: RiskLevel =
    risk > 85 ? "critical" : risk > 60 ? "high" : risk > 30 ? "review" : "safe";

  return {
    id: `TXN-UG-${String(928401 + index).padStart(6, "0")}`,
    date: `${day} Sep 2026`,
    time: late
      ? "11:42 PM"
      : `${10 + (index % 8)}:${String((index * 7) % 60).padStart(2, "0")} ${index % 2 ? "AM" : "PM"}`,
    payee,
    amount,
    location: index % 3 === 0 ? "Pune" : index % 3 === 1 ? "Mumbai" : "Nashik",
    risk,
    status,
    newPayee: risk > 60,
    upiId: `demo.payee${index + 1}@upi`,
    device: index % 4 === 0 ? "New Android device" : "Sunita's phone",
  };
});

export const activityData: ActivityPoint[] = [
  { time: "8 AM", normal: 1200, suspicious: 0, high: 0 },
  { time: "10 AM", normal: 3600, suspicious: 600, high: 0 },
  { time: "12 PM", normal: 5200, suspicious: 800, high: 0 },
  { time: "2 PM", normal: 2900, suspicious: 1100, high: 0 },
  { time: "4 PM", normal: 6100, suspicious: 500, high: 0 },
  { time: "6 PM", normal: 4200, suspicious: 2400, high: 0 },
  { time: "8 PM", normal: 3300, suspicious: 1800, high: 7500 },
  { time: "11 PM", normal: 900, suspicious: 3500, high: 48000 },
];

export const reportData: ReportPoint[] = [
  { day: "Mon", volume: 31, risk: 18, calls: 1, sms: 2 },
  { day: "Tue", volume: 42, risk: 22, calls: 0, sms: 1 },
  { day: "Wed", volume: 28, risk: 38, calls: 2, sms: 3 },
  { day: "Thu", volume: 39, risk: 29, calls: 1, sms: 1 },
  { day: "Fri", volume: 51, risk: 61, calls: 3, sms: 4 },
  { day: "Sat", volume: 34, risk: 44, calls: 1, sms: 2 },
  { day: "Sun", volume: 23, risk: 27, calls: 0, sms: 1 },
];

export const riskFactors: readonly (readonly [string, number])[] = [
  ["Behavioral Drift", 78],
  ["Transaction Velocity", 64],
  ["Amount Anomaly", 82],
  ["New Payee", 95],
  ["Unusual Time", 88],
  ["Communication Risk", 91],
] as const;

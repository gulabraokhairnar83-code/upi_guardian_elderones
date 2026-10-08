import type { RiskLevel } from "./transactions";

export type Alert = {
  id: number;
  level: RiskLevel;
  amount: number;
  title: string;
  detail: string;
  time: string;
  risk: number;
  status?: "pending" | "resolved" | "dismissed";
};

export const alerts: Alert[] = [
  {
    id: 1,
    level: "critical",
    amount: 48000,
    title: "Large payment to a new payee",
    detail: "Made at 11:47 PM shortly after a suspicious call.",
    time: "12 minutes ago",
    risk: 92,
    status: "pending",
  },
  {
    id: 2,
    level: "high",
    amount: 35000,
    title: "Unusual late-night transaction",
    detail: "Amount is much higher than Sunita’s normal payments.",
    time: "28 minutes ago",
    risk: 84,
    status: "pending",
  },
  {
    id: 3,
    level: "review",
    amount: 8500,
    title: "Payment frequency increased",
    detail: "Three transactions were made within eleven minutes.",
    time: "2 hours ago",
    risk: 56,
    status: "pending",
  },
];

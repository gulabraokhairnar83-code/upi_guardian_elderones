import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  CreditCard,
  Eye,
  IndianRupee,
  MessageSquareWarning,
  ShieldAlert,
} from "lucide-react";
import { motion } from "motion/react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { activityData, alerts, type Alert, type ActivityPoint } from "@/lib/fraud-data";
import { Button, Card, RiskBadge } from "./ui";

export function RiskGauge({
  score = 27,
  size = "large",
}: {
  score?: number;
  size?: "small" | "large";
}) {
  const r = 70;
  const c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;
  const strokeColor =
    score > 75 ? "var(--danger)" : score > 50 ? "var(--warning)" : "var(--safe)";

  return (
    <div
      className={`relative grid place-items-center ${
        size === "large" ? "h-48 w-48" : "h-32 w-32"
      }`}
    >
      <svg viewBox="0 0 180 180" className="h-full w-full -rotate-90">
        <circle cx="90" cy="90" r={r} fill="none" stroke="var(--muted)" strokeWidth="14" />
        <motion.circle
          cx="90"
          cy="90"
          r={r}
          fill="none"
          stroke={strokeColor}
          strokeLinecap="round"
          strokeWidth="14"
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1 }}
        />
      </svg>
      <div className="absolute text-center">
        <p className="font-mono text-3xl font-bold">{score}</p>
        <p className="text-xs font-semibold text-muted-foreground">OUT OF 100</p>
      </div>
    </div>
  );
}

export interface KpiItem {
  label: string;
  value: string;
  trend: string;
  tone: "info" | "safe" | "warning" | "danger" | "ai";
}

const defaultKpis: KpiItem[] = [
  { label: "Total Transactions", value: "248", trend: "+12%", tone: "info" },
  { label: "Safe Transactions", value: "221", trend: "+8%", tone: "safe" },
  { label: "Suspicious", value: "18", trend: "-3%", tone: "warning" },
  { label: "High Risk Alerts", value: "9", trend: "+2", tone: "danger" },
  { label: "Current Risk Score", value: "27/100", trend: "Normal", tone: "safe" },
  { label: "Scams Detected", value: "7", trend: "+100%", tone: "ai" },
];

function getKpiIcon(label: string) {
  const l = label.toLowerCase();
  if (l.includes("scam")) return MessageSquareWarning;
  if (l.includes("alert")) return ShieldAlert;
  if (l.includes("score") || l.includes("risk")) return IndianRupee;
  if (l.includes("suspicious")) return AlertTriangle;
  if (l.includes("safe")) return CheckCircle2;
  return CreditCard;
}

export function KpiGrid({ items }: { items?: KpiItem[] | undefined }) {
  const displayItems = items && items.length > 0 ? items : defaultKpis;

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {displayItems.map((item, i) => {
        const Icon = getKpiIcon(item.label);
        const tone = item.tone;

        return (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card className="p-5">
              <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-3">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-muted-foreground">{item.label}</p>
                  <p className="mt-2 font-mono text-2xl font-bold">{item.value}</p>
                  <p
                    className={`mt-2 flex items-center gap-1 text-xs font-semibold ${
                      tone === "danger"
                        ? "text-danger"
                        : tone === "warning"
                        ? "text-warning"
                        : tone === "ai"
                        ? "text-ai"
                        : "text-safe"
                    }`}
                  >
                    {item.trend.startsWith("+") ? (
                      <ArrowUpRight size={14} />
                    ) : item.trend.startsWith("-") ? (
                      <ArrowDownRight size={14} />
                    ) : null}{" "}
                    {item.trend}
                  </p>
                </div>
                <span className={`icon-box tone-${tone}`}>
                  <Icon size={22} />
                </span>
              </div>
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
}

export function ActivityChart({ data = activityData }: { data?: ActivityPoint[] | undefined }) {
  return (
    <Card className="p-5">
      <div className="mb-5">
        <h2 className="font-display text-lg font-bold">Transaction Activity</h2>
        <p className="text-sm text-muted-foreground">Amounts and risk events today</p>
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="normal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--info)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--info)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border)" vertical={false} />
            <XAxis
              dataKey="time"
              tickLine={false}
              axisLine={false}
              tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
              tickFormatter={(v) => `₹${v / 1000}k`}
            />
            <Tooltip
              contentStyle={{
                background: "var(--card)",
                border: "1px solid var(--border)",
                borderRadius: 8,
              }}
            />
            <Area
              type="monotone"
              dataKey="normal"
              stroke="var(--info)"
              fill="url(#normal)"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="suspicious"
              stroke="var(--warning)"
              fill="transparent"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="high"
              stroke="var(--danger)"
              fill="transparent"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export function AlertsList({
  alertsList = alerts,
  onView,
}: {
  alertsList?: Alert[] | undefined;
  onView?: ((id: number) => void) | undefined;
}) {
  if (alertsList.length === 0) {
    return (
      <Card className="col-span-full p-8 text-center">
        <p className="font-semibold text-safe">All clear</p>
        <p className="mt-1 text-sm text-muted-foreground">No active alerts requiring review.</p>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {alertsList.map((a) => (
        <Card key={a.id} className="p-4">
          <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-3">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <RiskBadge level={a.level} />
                <span className="font-mono text-lg font-bold">
                  ₹{a.amount.toLocaleString("en-IN")}
                </span>
              </div>
              <h3 className="mt-3 font-semibold">{a.title}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{a.detail}</p>
              <p className="mt-2 text-xs text-muted-foreground">{a.time}</p>
            </div>
            <div className="text-right">
              <p className="font-mono text-xl font-bold text-danger">{a.risk}</p>
              <p className="text-xs text-muted-foreground">Risk</p>
            </div>
          </div>
          {onView && (
            <Button
              variant="secondary"
              className="mt-4 w-full"
              onClick={() => onView(a.id)}
            >
              <Eye size={17} />
              View Details
            </Button>
          )}
        </Card>
      ))}
    </div>
  );
}
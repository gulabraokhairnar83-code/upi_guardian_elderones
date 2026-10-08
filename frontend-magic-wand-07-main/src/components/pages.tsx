import { useEffect, useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Brain,
  Check,
  CheckCircle2,
  Clock,
  Download,
  FileText,
  IndianRupee,
  Lock,
  MessageSquare,
  Phone,
  Plus,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  Smartphone,
  Sparkles,
  Users,
  Bell,
  Volume2,
  Trash2,
  Edit3,
  HeartHandshake,
  CheckCheck,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AppShell } from "./app-shell";
import { ActivityChart, AlertsList, KpiGrid, RiskGauge } from "./dashboard-parts";
import { Button, Card, Modal, RiskBadge, Toggle } from "./ui";
import { reportData, riskFactors, type Transaction } from "@/data/mock/transactions";
import { incidentTimeline } from "@/data/mock/incident-timeline";
import { useApp } from "@/lib/app-context";
import {
  useDashboard,
  useTransactions,
  useAlerts,
  useResolveAlert,
  useAnalyzeMessage,
  useFamily,
  useResolveFamilyAlert,
  useSettings,
  useUpdateSettings,
  useRiskAnalysis,
  useRiskEvents,
  useCaregivers,
  useCreateCaregiver,
  useUpdateCaregiver,
  useDeleteCaregiver,
  useVerifyCaregiver,
  useNotifications,
  useAcknowledgeNotification,
} from "@/hooks";
import type { MessageAnalysisResult } from "@/data/mock/sample-messages";
import type { Alert } from "@/data/mock/alerts";
import type { RiskFusionAnalysis } from "@/services/risk-service";
import type { Caregiver } from "@/services/caregiver-service";
import type { NotificationRecord } from "@/services/notification-service";

// ==========================================
// 1. DASHBOARD PAGE
// ==========================================
export function DashboardPage() {
  const [range, setRange] = useState("Today");
  const [alert, setAlert] = useState<number | null>(null);
  const { senior } = useApp();
  const { data: dashboard, isLoading, isError, refetch } = useDashboard();

  return (
    <AppShell title="Dashboard" subtitle="Your financial safety is being monitored.">
      <section className="protection-banner">
        <div className="flex items-center gap-4">
          <span className="grid h-14 w-14 shrink-0 place-items-center rounded-xl bg-safe text-safe-foreground">
            <ShieldCheck size={30} />
          </span>
          <div>
            <p className="text-sm font-semibold text-safe-strong">ALL SYSTEMS OPERATIONAL</p>
            <h2 className="font-display text-2xl font-bold">Your Account is Protected</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              UPI Guardian is watching transactions and communications for warning signs.
            </p>
          </div>
        </div>
        <div className="hidden items-center gap-2 rounded-lg bg-card/70 px-4 py-3 md:flex">
          <span className="h-2.5 w-2.5 rounded-full bg-safe" />
          <span className="text-sm font-semibold">Live monitoring</span>
        </div>
      </section>

      {isError && (
        <Card className="my-4 flex items-center justify-between border-danger/40 bg-danger-soft p-4">
          <div className="flex items-center gap-3 text-danger">
            <AlertCircle size={20} />
            <span className="text-sm font-medium">Failed to fetch latest dashboard telemetry.</span>
          </div>
          <Button variant="secondary" onClick={() => refetch()} className="h-9 px-3 text-xs">
            <RefreshCw size={14} /> Retry
          </Button>
        </Card>
      )}

      <KpiGrid items={dashboard?.kpis} />

      <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(18rem,.8fr)]">
        <div>
          <div className="mb-3 flex justify-end gap-1">
            {["Today", "7 Days", "30 Days", "6 Months"].map((x) => (
              <button
                key={x}
                className={`filter-chip ${range === x ? "filter-chip-active" : ""}`}
                onClick={() => setRange(x)}
              >
                {x}
              </button>
            ))}
          </div>
          <ActivityChart data={dashboard?.activity} />
        </div>

        <Card className="flex flex-col items-center justify-center p-5">
          <h2 className="font-display text-lg font-bold">Current Risk</h2>
          <RiskGauge score={Math.round(dashboard?.overall_risk_score ?? dashboard?.currentRiskScore ?? 27)} />
          <RiskBadge level={dashboard?.overall_risk_level ?? dashboard?.riskLevel ?? "safe"} />
          <p className="mt-3 text-center text-sm text-muted-foreground">
            {dashboard?.riskSummary ?? "Low risk. No immediate action needed."}
          </p>
        </Card>
      </div>

      {!senior && (
        <section className="mt-8">
          <div className="section-heading">
            <div>
              <h2>Recent Alerts</h2>
              <p>Activity that may need your attention</p>
            </div>
            <Link to="/alerts" className="text-sm font-semibold text-primary">
              View all alerts →
            </Link>
          </div>
          <div className="grid gap-4 xl:grid-cols-3">
            <AlertsList
              alertsList={dashboard?.recentAlerts}
              onView={(id: number) => setAlert(id)}
            />
          </div>
        </section>
      )}

      <Modal open={alert !== null} onClose={() => setAlert(null)} title="Fraud alert review">
        <AlertDetail alert={dashboard?.recentAlerts?.find((a) => a.id === alert)} />
        <Button className="mt-5 w-full" onClick={() => setAlert(null)}>
          I understand
        </Button>
      </Modal>
    </AppShell>
  );
}

function AlertDetail({ alert }: { alert?: Alert | null | undefined }) {
  const isHigh = (alert?.risk ?? 92) > 60;
  return (
    <div>
      <div
        className={`flex items-center gap-3 rounded-lg p-4 ${
          isHigh ? "bg-danger-soft text-danger" : "bg-warning-soft text-warning"
        }`}
      >
        <ShieldAlert size={28} />
        <div>
          <p className="font-semibold">{alert?.title || "Possible scam detected"}</p>
          <p className="text-sm font-mono font-bold">Risk score {alert?.risk ?? 92}/100</p>
        </div>
      </div>
      <div className="mt-4 space-y-2 text-sm leading-6">
        <p className="text-muted-foreground">{alert?.detail || "Unusual transaction activity detected."}</p>
        {alert?.amount ? (
          <p className="text-xs text-muted-foreground">
            Amount: <span className="font-mono font-bold text-foreground">₹{alert.amount.toLocaleString("en-IN")}</span> ({alert.time || "Recent"})
          </p>
        ) : null}
      </div>
    </div>
  );
}

// ==========================================
// 2. TRANSACTIONS PAGE
// ==========================================
export function TransactionsPage() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<Transaction | null>(null);

  const { data: transactionsData = [], isLoading, isError, refetch } = useTransactions({
    status: filter,
    query,
  });

  return (
    <AppShell
      title="Transaction Monitoring"
      subtitle="Review synthetic UPI activity and understand why payments are flagged."
    >
      <div className="toolbar">
        <label className="relative min-w-0 flex-1">
          <Search className="absolute left-3 top-3 text-muted-foreground" size={19} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="field pl-10"
            placeholder="Search transaction, payee or ID..."
          />
        </label>
        <select
          className="field w-full sm:w-48"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All statuses</option>
          <option value="safe">Safe</option>
          <option value="review">Please Review</option>
          <option value="high">High Risk</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="grid min-h-60 place-items-center p-8 text-center text-muted-foreground">
            <div className="flex items-center gap-2">
              <RefreshCw className="animate-spin" size={20} />
              <span>Loading transaction records...</span>
            </div>
          </div>
        ) : isError ? (
          <div className="p-8 text-center">
            <AlertTriangle className="mx-auto text-danger" size={32} />
            <h3 className="mt-3 font-display text-lg font-bold">Failed to load transactions</h3>
            <p className="mt-1 text-sm text-muted-foreground">Network connection could not be established.</p>
            <Button variant="secondary" className="mt-4" onClick={() => refetch()}>
              Try Again
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date & time</th>
                  <th>Payee</th>
                  <th>Amount</th>
                  <th>New payee</th>
                  <th>Location</th>
                  <th>Risk</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {transactionsData.map((t) => (
                  <tr key={t.id}>
                    <td>
                      <span>{t.date}</span>
                      <small>{t.time}</small>
                    </td>
                    <td>
                      <b>{t.payee}</b>
                      <small>{t.upiId}</small>
                    </td>
                    <td className="font-mono font-bold">₹{t.amount.toLocaleString("en-IN")}</td>
                    <td>{t.newPayee ? "Yes" : "No"}</td>
                    <td>{t.location}</td>
                    <td className="font-mono font-bold">{t.risk}/100</td>
                    <td>
                      <RiskBadge level={t.status} />
                    </td>
                    <td>
                      <Button variant="ghost" onClick={() => setSelected(t)}>
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!isLoading && !isError && transactionsData.length === 0 && (
          <div className="empty-state">
            <CheckCircle2 />
            <h3>No suspicious transactions found</h3>
            <p>Your account looks safe.</p>
          </div>
        )}
      </Card>

      <TransactionModal transaction={selected} onClose={() => setSelected(null)} />
    </AppShell>
  );
}

function TransactionModal({
  transaction,
  onClose,
}: {
  transaction: Transaction | null;
  onClose: () => void;
}) {
  const [confirm, setConfirm] = useState("");
  if (!transaction) return null;

  return (
    <Modal open onClose={onClose} title="Transaction details">
      <div className="grid gap-3 sm:grid-cols-2">
        {[
          ["Transaction ID", transaction.id],
          ["Date & time", `${transaction.date}, ${transaction.time}`],
          ["Amount", `₹${transaction.amount.toLocaleString("en-IN")}`],
          ["Payee", transaction.payee],
          ["UPI ID", transaction.upiId],
          ["Location", transaction.location],
          ["Device", transaction.device],
          ["New payee", transaction.newPayee ? "Yes" : "No"],
        ].map(([a, b]) => (
          <div className="detail-cell" key={a}>
            <span>{a}</span>
            <strong>{b}</strong>
          </div>
        ))}
      </div>

      <h3 className="mt-6 font-display text-lg font-bold">Why was this flagged?</h3>
      <div className="mt-3 space-y-3">
        {riskFactors.slice(1).map(([name, value]) => (
          <RiskFactor key={name} name={name} value={value} />
        ))}
      </div>

      <div className="mt-5 rounded-lg bg-danger-soft p-4">
        <p className="font-semibold text-danger">
          Combined Risk Score <span className="font-mono">{transaction.risk}/100</span>
        </p>
        <p className="mt-2 text-sm leading-6">
          This payment differs from normal behavior. It involves a new payee, an unusual time, and
          communication warning signs.
        </p>
      </div>

      <div className="mt-5 grid gap-2 sm:grid-cols-2">
        <Button variant="secondary" onClick={() => setConfirm("Mark this transaction as safe?")}>
          Mark as Safe
        </Button>
        <Button variant="danger" onClick={() => setConfirm("Report this transaction as possible fraud?")}>
          Report Fraud
        </Button>
        <Button variant="secondary" onClick={() => setConfirm("Contact Sunita’s family now?")}>
          Contact Family
        </Button>
        <Button variant="secondary" onClick={() => setConfirm("Block this demo payee?")}>
          Block Payee
        </Button>
      </div>

      <Modal open={!!confirm} onClose={() => setConfirm("")} title="Please confirm">
        <p>{confirm}</p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirm("")}>
            Cancel
          </Button>
          <Button
            onClick={() => {
              setConfirm("");
              onClose();
            }}
          >
            Confirm action
          </Button>
        </div>
      </Modal>
    </Modal>
  );
}

// ==========================================
// 3. ALERTS PAGE
// ==========================================
export function AlertsPage() {
  const [activeTab, setActiveTab] = useState<"risk_alerts" | "caregiver_dispatches">("risk_alerts");
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<number | null>(null);
  const { data: alertsData = [], isLoading, isError, refetch } = useAlerts(filter);
  const resolveMutation = useResolveAlert();

  const { data: notificationsData = [], isLoading: isNotifLoading } = useNotifications(50);
  const ackMutation = useAcknowledgeNotification();

  const handleResolve = (id: number) => {
    resolveMutation.mutate(id, {
      onSuccess: () => setSelected(null),
    });
  };

  const selectedAlert = alertsData.find((a) => a.id === selected) || null;

  return (
    <AppShell title="Fraud Alerts & Escalations" subtitle="Prioritized warnings and caregiver emergency dispatch logs.">
      {/* Tab Switcher */}
      <div className="mb-6 flex items-center gap-3 border-b border-border pb-3">
        <button
          onClick={() => setActiveTab("risk_alerts")}
          className={`flex items-center gap-2 pb-2 text-sm font-semibold transition border-b-2 -mb-3.5 ${
            activeTab === "risk_alerts"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <ShieldAlert size={17} />
          <span>Active Risk Alerts ({alertsData.length})</span>
        </button>
        <button
          onClick={() => setActiveTab("caregiver_dispatches")}
          className={`flex items-center gap-2 pb-2 text-sm font-semibold transition border-b-2 -mb-3.5 ${
            activeTab === "caregiver_dispatches"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Bell size={17} />
          <span>Caregiver Dispatches ({notificationsData.length})</span>
        </button>
      </div>

      {activeTab === "risk_alerts" ? (
        <>
          <div className="mb-5 flex flex-wrap gap-2">
            {["all", "critical", "high", "review"].map((x) => (
              <button
                className={`filter-chip capitalize ${filter === x ? "filter-chip-active" : ""}`}
                key={x}
                onClick={() => setFilter(x)}
              >
                {x}
              </button>
            ))}
          </div>

          {isLoading ? (
            <Card className="grid min-h-48 place-items-center p-8 text-muted-foreground">
              <div className="flex items-center gap-2">
                <RefreshCw className="animate-spin" size={18} />
                <span>Loading safety alerts...</span>
              </div>
            </Card>
          ) : isError ? (
            <Card className="p-8 text-center">
              <AlertTriangle className="mx-auto text-danger" size={28} />
              <p className="mt-2 text-sm text-muted-foreground">Failed to load fraud alerts.</p>
              <Button variant="secondary" className="mt-3" onClick={() => refetch()}>
                Retry
              </Button>
            </Card>
          ) : alertsData.length === 0 ? (
            <Card className="p-8 text-center">
              <CheckCircle2 className="mx-auto text-safe-strong" size={32} />
              <h3 className="mt-3 font-display text-lg font-bold">No active alerts</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                No fraud warnings detected for the selected filter.
              </p>
            </Card>
          ) : (
            <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
              <AlertsList alertsList={alertsData} onView={setSelected} />
            </div>
          )}

          <Modal open={selected !== null} onClose={() => setSelected(null)} title="Alert details">
            <AlertDetail alert={selectedAlert} />
            <div className="mt-5 grid gap-2 sm:grid-cols-2">
              <Button onClick={() => setSelected(null)}>Review transaction</Button>
              <Button
                variant="secondary"
                disabled={resolveMutation.isPending}
                onClick={() => {
                  if (selected !== null) handleResolve(selected);
                }}
              >
                {resolveMutation.isPending ? "Resolving..." : "Mark resolved"}
              </Button>
            </div>
          </Modal>
        </>
      ) : (
        /* Caregiver Telemetry & Escalations Tab */
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">
              Audit log of automated Twilio SMS & Voice alerts triggered by High/Critical risk events.
            </p>
            <span className="text-xs font-semibold text-safe-strong flex items-center gap-1">
              <CheckCheck size={14} />
              Idempotency & Deduplication Active
            </span>
          </div>

          {isNotifLoading ? (
            <Card className="p-8 text-center text-xs text-muted-foreground">
              <RefreshCw className="animate-spin mx-auto mb-2" size={18} />
              Loading caregiver telemetry...
            </Card>
          ) : notificationsData.length === 0 ? (
            <Card className="p-8 text-center">
              <CheckCircle2 className="mx-auto text-safe-strong" size={32} />
              <h3 className="mt-3 font-display text-lg font-bold">No Caregiver Dispatches Yet</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Automated alerts will appear here when high or critical transactions occur.
              </p>
            </Card>
          ) : (
            <div className="grid gap-4">
              {notificationsData.map((notif) => (
                <Card key={notif.notification_id} className="p-5 space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-3">
                    <div className="flex items-center gap-2">
                      <span
                        className={`grid h-8 w-8 place-items-center rounded-lg ${
                          notif.channel === "VOICE"
                            ? "bg-danger/10 text-danger"
                            : "bg-primary/10 text-primary"
                        }`}
                      >
                        {notif.channel === "VOICE" ? <Volume2 size={16} /> : <MessageSquare size={16} />}
                      </span>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-semibold text-sm">
                            {notif.channel === "VOICE" ? "Twilio Voice Call" : "Twilio SMS Notification"}
                          </p>
                          <RiskBadge level={notif.risk_level.toLowerCase() as "high" | "critical"} />
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {notif.provider_message_id
                            ? `SID: ${notif.provider_message_id}`
                            : "Provider Message Dispatched"}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-semibold uppercase ${
                          notif.status === "SENT" || notif.status === "DELIVERED"
                            ? "bg-safe/10 text-safe-strong"
                            : notif.status === "FAILED"
                            ? "bg-danger/10 text-danger"
                            : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {notif.status}
                      </span>

                      {notif.is_acknowledged ? (
                        <span className="flex items-center gap-1 rounded bg-safe/20 px-2.5 py-1 text-xs font-semibold text-safe-strong">
                          <CheckCheck size={14} />
                          Acknowledged
                        </span>
                      ) : (
                        <Button
                          variant="secondary"
                          className="h-8 px-3 text-xs text-primary"
                          disabled={ackMutation.isPending}
                          onClick={() => ackMutation.mutate(notif.notification_id)}
                        >
                          Acknowledge
                        </Button>
                      )}
                    </div>
                  </div>

                  <div className="bg-muted/30 rounded-lg p-3 text-xs space-y-1">
                    <p className="font-medium text-foreground">Message Preview:</p>
                    <p className="text-muted-foreground font-mono text-[11px] leading-relaxed">
                      {notif.message_preview || "Automated advisory warning dispatched to verified caregiver."}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center justify-between text-[11px] text-muted-foreground pt-1">
                    <span>Event Ref: {notif.risk_event_id || notif.notification_id}</span>
                    <span>
                      Dispatched:{" "}
                      {notif.sent_at
                        ? new Date(notif.sent_at).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : "Just now"}
                    </span>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </AppShell>
  );
}

// ==========================================
// 4. ANALYZER PAGES (CALL & SMS)
// ==========================================
function AnalyzerPage({ type }: { type: "call" | "sms" }) {
  const isSms = type === "sms";
  const defaultSample = isSms
    ? "URGENT: Your account will be suspended. Share OTP and verify now at secure-upi-check.example"
    : "Your bank account will be blocked today. Please share your OTP to verify your account immediately.";

  const [text, setText] = useState("");
  const [result, setResult] = useState<MessageAnalysisResult | null>(null);

  const analyzeMutation = useAnalyzeMessage();

  const handleAnalyze = () => {
    if (!text.trim()) return;
    analyzeMutation.mutate(
      { text, type },
      {
        onSuccess: (res) => setResult(res),
      }
    );
  };

  return (
    <AppShell
      title={isSms ? "SMS Scam Detector" : "Scam Call Analyzer"}
      subtitle={
        isSms
          ? "Check a suspicious message before responding."
          : "Analyze suspicious conversations and identify common scam patterns."
      }
    >
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(20rem,.8fr)]">
        <Card className="p-6">
          <label className="font-semibold" htmlFor="analyzer">
            {isSms ? "Paste suspicious SMS" : "Paste call transcript"}
          </label>
          <textarea
            id="analyzer"
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="field mt-3 min-h-56 resize-y"
            placeholder={defaultSample}
          />
          <div className="mt-4 flex flex-wrap gap-3">
            <Button onClick={handleAnalyze} disabled={analyzeMutation.isPending}>
              {analyzeMutation.isPending ? (
                <RefreshCw className="animate-spin" size={18} />
              ) : isSms ? (
                <MessageSquare size={18} />
              ) : (
                <Phone size={18} />
              )}
              {analyzeMutation.isPending
                ? "Analyzing..."
                : `Analyze ${isSms ? "SMS" : "Conversation"}`}
            </Button>
            <Button variant="secondary" onClick={() => setText(defaultSample)}>
              Use sample
            </Button>
          </div>
          {analyzeMutation.isError && (
            <div className="mt-4 flex items-center gap-2 rounded-lg border border-danger/30 bg-danger-soft p-4 text-sm text-danger">
              <AlertTriangle className="shrink-0" size={18} />
              <span>
                {analyzeMutation.error instanceof Error
                  ? analyzeMutation.error.message
                  : "Risk analysis could not be completed. Please try again."}
              </span>
            </div>
          )}
          <p className="mt-4 flex items-start gap-2 text-xs text-muted-foreground">
            <Sparkles className="shrink-0" size={15} />
            AI-assisted analysis prototype. Results are simulated patterns and not guaranteed fraud determination.
          </p>
        </Card>

        {result ? (
          <AnalysisResult result={result} sms={isSms} />
        ) : (
          <Card className="grid min-h-80 place-items-center p-8 text-center">
            <div>
              <span className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-info-soft text-info">
                <Brain size={30} />
              </span>
              <h2 className="mt-4 font-display text-xl font-bold">Ready to analyze</h2>
              <p className="mt-2 max-w-xs text-sm text-muted-foreground">
                Paste the message or transcript. Never include a real OTP or bank account number.
              </p>
            </div>
          </Card>
        )}
      </div>
    </AppShell>
  );
}

export function CallAnalyzerPage() {
  return <AnalyzerPage type="call" />;
}

export function SmsAnalyzerPage() {
  return <AnalyzerPage type="sms" />;
}

function AnalysisResult({
  result,
  sms,
}: {
  result: MessageAnalysisResult;
  sms: boolean;
}) {
  const isDangerous = result.level === "critical" || result.level === "high";
  const isReview = result.level === "review";

  return (
    <Card className="overflow-hidden">
      <div className={isDangerous ? "bg-danger-soft p-6" : isReview ? "bg-warning-soft p-6" : "bg-safe-soft p-6"}>
        <div className={`flex items-center gap-3 ${isDangerous ? "text-danger" : isReview ? "text-warning" : "text-safe-strong"}`}>
          <ShieldAlert size={28} />
          <div>
            <p className="text-sm font-bold">{result.title}</p>
            <p className="font-mono text-3xl font-bold">{result.riskScore}/100</p>
          </div>
        </div>
        <div className="mt-3 flex items-center gap-2">
          <RiskBadge level={result.level} />
          {result.isDemo ? (
            <span className="rounded bg-muted px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
              Demo Pattern Analysis
            </span>
          ) : (
            <span className="rounded bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary">
              Live Phase-5 NLP
            </span>
          )}
        </div>
      </div>
      <div className="p-6">
        <h3 className="font-display font-bold">Detected scam categories</h3>
        <ul className="mt-3 space-y-2">
          {result.detectedPatterns.map((x) => (
            <li key={x} className="flex gap-2 text-sm">
              <Check className={isDangerous ? "text-danger" : "text-warning"} size={18} />
              {x}
            </li>
          ))}
        </ul>

        {result.suspiciousPhrases && result.suspiciousPhrases.length > 0 && (
          <div className="mt-4">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Suspicious Phrases Identified
            </h4>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {result.suspiciousPhrases.map((phrase, idx) => (
                <span
                  key={idx}
                  className="rounded bg-danger/10 px-2.5 py-1 text-xs font-medium text-danger"
                >
                  "{phrase}"
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mt-5 rounded-lg bg-ai-soft p-4">
          <p className="font-semibold text-ai">Explanation</p>
          <p className="mt-2 text-sm leading-6">{result.explanation}</p>
        </div>

        {result.recommendations && result.recommendations.length > 0 && (
          <div className="mt-4 rounded-lg border border-border p-4">
            <p className="text-sm font-semibold text-foreground">Recommended Action</p>
            <p className="mt-1 text-sm text-muted-foreground">{result.recommendations[0]}</p>
          </div>
        )}
      </div>
    </Card>
  );
}

// ==========================================
// 5. RISK ANALYSIS PAGE
// ==========================================
export function RiskAnalysisPage() {
  const { senior } = useApp();
  const riskMutation = useRiskAnalysis();
  const { data: riskEvents = [], isLoading: eventsLoading } = useRiskEvents();
  const [activeAnalysis, setActiveAnalysis] = useState<RiskFusionAnalysis | null>(null);

  const runPreset = (scenario: "scam" | "routine" | "velocity") => {
    let payload = {
      user_id: "usr_sunita_68",
      transaction_id: `TXN-UG-${928400 + Math.floor(Math.random() * 900)}`,
      payee: "Rahul Sharma",
      amount: 35000,
      upiId: "rahul.sharma@okhdfcbank",
      is_new_payee: true,
      velocity: 3,
    };

    if (scenario === "routine") {
      payload = {
        user_id: "usr_sunita_68",
        transaction_id: `TXN-UG-${928400 + Math.floor(Math.random() * 900)}`,
        payee: "City Pharmacy",
        amount: 640,
        upiId: "citypharmacy@okaxis",
        is_new_payee: false,
        velocity: 1,
      };
    } else if (scenario === "velocity") {
      payload = {
        user_id: "usr_sunita_68",
        transaction_id: `TXN-UG-${928400 + Math.floor(Math.random() * 900)}`,
        payee: "Quick Payment Transfer",
        amount: 18500,
        upiId: "quickpay@okaxis",
        is_new_payee: true,
        velocity: 5,
      };
    }

    riskMutation.mutate(payload, {
      onSuccess: (data) => setActiveAnalysis(data),
    });
  };

  const analysis: RiskFusionAnalysis = activeAnalysis ?? {
    transaction_id: "TXN-UG-928405",
    user_id: "usr_sunita_68",
    transaction_anomaly_score: 84.5,
    communication_risk_score: 95.0,
    behavioral_deviation_score: 78.0,
    new_payee_score: 100.0,
    velocity_score: 70.0,
    temporal_correlation_score: 85.0,
    correlation_boost: 10.0,
    final_risk_score: 92.4,
    risk_level: "CRITICAL",
    top_contributing_factors: [
      "New or unfamiliar payee",
      "Suspicious communication detected",
      "Transaction occurred shortly after suspicious communication",
      "Unusual transaction amount",
    ],
    explanation:
      "High-risk activity detected because an unusual transaction occurred shortly after a suspicious communication. The transaction involves significant deviations from your normal pattern.",
    recommended_action:
      "Do not proceed. Contact a trusted caregiver or official bank/UPI support using a verified contact method.",
    communication_id: "msg_scam_01",
    alert_created: true,
  };

  const normalizedLevel = (analysis.risk_level || "CRITICAL").toLowerCase() as
    | "safe"
    | "review"
    | "high"
    | "critical";

  return (
    <AppShell
      title="Explainable Risk Analysis"
      subtitle="See how different warning signs combine into one understandable risk score."
    >
      {/* Preset simulation buttons */}
      <div className="mb-5 flex flex-wrap items-center gap-3">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Phase-6 Live Presets:
        </span>
        <Button
          variant="secondary"
          className="h-8 text-xs"
          disabled={riskMutation.isPending}
          onClick={() => runPreset("scam")}
        >
          {riskMutation.isPending ? <RefreshCw className="animate-spin" size={14} /> : null}
          Scam Call + Transfer (Critical)
        </Button>
        <Button
          variant="secondary"
          className="h-8 text-xs"
          disabled={riskMutation.isPending}
          onClick={() => runPreset("velocity")}
        >
          Rapid Burst Transfer (High)
        </Button>
        <Button
          variant="secondary"
          className="h-8 text-xs"
          disabled={riskMutation.isPending}
          onClick={() => runPreset("routine")}
        >
          Routine Pharmacy Payment (Safe)
        </Button>
      </div>

      {riskMutation.isError && (
        <div className="mb-5 flex items-center gap-2 rounded-lg border border-danger/30 bg-danger-soft p-4 text-sm text-danger">
          <AlertTriangle className="shrink-0" size={18} />
          <span>
            {riskMutation.error instanceof Error
              ? riskMutation.error.message
              : "Risk analysis could not be completed. Please try again."}
          </span>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[.75fr_1.25fr]">
        <Card className="flex flex-col items-center p-6 text-center">
          <h2 className="font-display text-xl font-bold">Combined Risk Score</h2>
          <RiskGauge score={Math.round(analysis.final_risk_score)} />
          <RiskBadge level={normalizedLevel} />
          <p className="mt-4 text-sm text-muted-foreground">
            Risk is evaluated using multiple signals instead of a single threshold.
          </p>
          {senior ? (
            <div className="mt-4 rounded-lg bg-warning-soft p-3 text-left text-sm text-warning font-medium">
              ⚠️ {analysis.recommended_action}
            </div>
          ) : null}
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-xl font-bold">Signal Breakdown</h2>
            {analysis.correlation_boost > 0 && (
              <span className="rounded bg-danger/10 px-2.5 py-1 text-xs font-bold text-danger">
                +{analysis.correlation_boost.toFixed(1)} Correlation Boost
              </span>
            )}
          </div>

          <div className="mt-5 space-y-4">
            <RiskFactor
              name="Transaction Anomaly"
              value={Math.round(analysis.transaction_anomaly_score)}
            />
            <RiskFactor
              name="Communication Risk"
              value={Math.round(analysis.communication_risk_score)}
            />
            <RiskFactor
              name="Behavioral Deviation"
              value={Math.round(analysis.behavioral_deviation_score)}
            />
            <RiskFactor name="New Payee" value={Math.round(analysis.new_payee_score)} />
            <RiskFactor name="Velocity" value={Math.round(analysis.velocity_score)} />
            <RiskFactor
              name="Temporal Correlation"
              value={Math.round(analysis.temporal_correlation_score)}
            />
          </div>
        </Card>
      </div>

      <Card className="mt-6 p-6">
        <h2 className="font-display text-xl font-bold">Risk Fusion Pipeline</h2>
        <div className="mt-5 grid items-center gap-3 md:grid-cols-[1fr_auto_1fr_auto_1fr_auto_1fr]">
          {[
            `Tx Anomaly: ${analysis.transaction_anomaly_score.toFixed(0)}`,
            "+",
            `Comm Risk: ${analysis.communication_risk_score.toFixed(0)}`,
            "+",
            `Behavior: ${analysis.behavioral_deviation_score.toFixed(0)}`,
            "=",
            `Final: ${analysis.final_risk_score.toFixed(0)} (${analysis.risk_level})`,
          ].map((x, i) => (
            <div
              key={`${x}${i}`}
              className={i % 2 ? "text-center text-2xl font-bold text-muted-foreground" : "fusion-node"}
            >
              {x}
            </div>
          ))}
        </div>

        <div className="mt-6 rounded-lg bg-ai-soft p-4">
          <p className="font-semibold text-ai">Explanation</p>
          <p className="mt-2 text-sm leading-6">{analysis.explanation}</p>
          <div className="mt-3 border-t border-ai/20 pt-3">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Recommended Action
            </p>
            <p className="mt-1 text-sm font-medium text-foreground">
              {analysis.recommended_action}
            </p>
          </div>
        </div>
      </Card>

      <Card className="mt-6 p-6">
        <h2 className="font-display text-xl font-bold">Recent Risk Events</h2>
        {eventsLoading ? (
          <div className="grid min-h-32 place-items-center text-muted-foreground">
            <RefreshCw className="animate-spin" size={20} />
          </div>
        ) : riskEvents.length > 0 ? (
          <div className="timeline mt-6">
            {riskEvents.map((evt) => (
              <div className="timeline-row" key={evt.id || evt.event_id}>
                <span className="timeline-icon">
                  <ShieldAlert size={18} />
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-mono text-xs font-bold text-primary">
                      {evt.created_at ? new Date(evt.created_at).toLocaleTimeString() : "Recent"}
                    </p>
                    <span className="font-mono text-xs text-muted-foreground">
                      {evt.transaction_id}
                    </span>
                    <span className="text-xs font-bold uppercase text-danger">
                      Score: {Math.round(evt.final_risk_score)}
                    </span>
                  </div>
                  <p className="mt-1 font-semibold text-sm">
                    {evt.explanation || "Risk event recorded by fusion engine."}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="timeline mt-6">
            {incidentTimeline.map((item) => {
              const Icon = item.icon;
              return (
                <div className="timeline-row" key={item.time}>
                  <span className="timeline-icon">
                    <Icon size={18} />
                  </span>
                  <div>
                    <p className="font-mono text-xs font-bold text-primary">{item.time}</p>
                    <p className="mt-1 font-semibold">{item.text}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </AppShell>
  );
}

function RiskFactor({ name, value }: { name: string; value: number }) {
  return (
    <div>
      <div className="mb-1.5 flex justify-between text-sm">
        <span className="font-medium">{name}</span>
        <span className="font-mono font-bold">{value}%</span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-muted">
        <div
          className={`h-full rounded-full ${
            value > 80 ? "bg-danger" : value > 60 ? "bg-warning" : "bg-info"
          }`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

// ==========================================
// 6. FAMILY & CAREGIVER PAGE
// ==========================================
export function FamilyPage() {
  const [resolved, setResolved] = useState(false);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [newCgName, setNewCgName] = useState("");
  const [newCgPhone, setNewCgPhone] = useState("");
  const [newCgEmail, setNewCgEmail] = useState("");
  const [newCgRel, setNewCgRel] = useState("SON");
  const [newCgSms, setNewCgSms] = useState(true);
  const [newCgVoice, setNewCgVoice] = useState(false);

  const { profile, isLoading: isFamilyLoading, isError, refetch } = useFamily();
  const resolveMutation = useResolveFamilyAlert();

  const { data: caregivers = [], isLoading: isCgLoading } = useCaregivers();
  const createCgMutation = useCreateCaregiver();
  const updateCgMutation = useUpdateCaregiver();
  const verifyCgMutation = useVerifyCaregiver();
  const deleteCgMutation = useDeleteCaregiver();

  const handleResolve = () => {
    resolveMutation.mutate(undefined, {
      onSuccess: () => setResolved(true),
    });
  };

  const handleCreateCaregiver = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCgName.trim()) return;

    createCgMutation.mutate(
      {
        name: newCgName.trim(),
        phone: newCgPhone.trim(),
        email: newCgEmail.trim(),
        relationship: newCgRel,
        notification_preferences: {
          sms_enabled: newCgSms,
          voice_enabled: newCgVoice,
          high_risk_enabled: true,
          critical_risk_enabled: true,
        },
      },
      {
        onSuccess: () => {
          setAddModalOpen(false);
          setNewCgName("");
          setNewCgPhone("");
          setNewCgEmail("");
          setNewCgVoice(false);
        },
      }
    );
  };

  const elder = profile ?? {
    name: "Sunita Devi",
    age: 68,
    location: "Pune",
    accountSafetyStatus: "Protected" as const,
    metrics: {
      currentRiskScore: 27,
      todayTransactionsCount: 8,
      activeAlertsCount: 2,
      scamCommunicationsCount: 3,
    },
  };

  return (
    <AppShell
      title="Family & Caregiver Safety"
      subtitle="Manage trusted family caregivers and configure automated Twilio risk escalation."
    >
      <section className="profile-banner">
        <span className="grid h-16 w-16 place-items-center rounded-full bg-primary text-xl font-bold text-primary-foreground shadow">
          SD
        </span>
        <div>
          <h2 className="font-display text-2xl font-bold">{elder.name}</h2>
          <p className="text-muted-foreground">Age {elder.age} · {elder.location}</p>
          <p className="mt-1 flex items-center gap-2 font-semibold text-safe-strong">
            <ShieldCheck size={18} />
            Account Safety: {elder.accountSafetyStatus}
          </p>
        </div>
      </section>

      {/* Phase 8 Active Status Banner */}
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-xs">
        <div className="flex items-center gap-2 text-foreground font-medium">
          <ShieldCheck className="text-primary" size={17} />
          <span>
            <strong>Active Phase 8:</strong> Caregiver Safety Network & Automated Twilio Escalation operational.
          </span>
        </div>
        <span className="rounded bg-safe/20 px-2 py-0.5 text-safe-strong font-semibold flex items-center gap-1">
          <CheckCheck size={13} />
          Twilio SMS & Voice Active
        </span>
      </div>

      {isError && (
        <Card className="mt-4 flex items-center justify-between border-danger/40 bg-danger-soft p-4">
          <span className="text-sm text-danger">Failed to sync family telemetry data.</span>
          <Button variant="secondary" onClick={() => refetch()} className="h-8 px-3 text-xs">
            Retry
          </Button>
        </Card>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          ["Current Risk", `${elder.metrics.currentRiskScore} / 100`],
          ["Today's Transactions", `${elder.metrics.todayTransactionsCount}`],
          ["Active Alerts", resolved ? "0" : `${elder.metrics.activeAlertsCount}`],
          ["Verified Caregivers", `${caregivers.filter((c) => c.is_verified).length}`],
        ].map(([a, b]) => (
          <Card className="p-5" key={a}>
            <p className="text-sm text-muted-foreground">{a}</p>
            <p className="mt-2 font-mono text-2xl font-bold">{b}</p>
          </Card>
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_.9fr]">
        {/* Urgent Family Alerts */}
        <Card className="p-6">
          <h2 className="font-display text-xl font-bold">Family Alerts</h2>
          {resolved ? (
            <div className="empty-state py-8 text-center">
              <CheckCircle2 className="mx-auto text-safe-strong" size={36} />
              <h3 className="mt-3 font-display font-bold text-lg">All alerts resolved</h3>
              <p className="text-sm text-muted-foreground">Sunita’s account is safe and protected.</p>
            </div>
          ) : (
            <div className="mt-5 rounded-lg border border-danger/30 bg-danger-soft p-5">
              <RiskBadge level="critical" />
              <h3 className="mt-4 text-lg font-bold">High-risk transaction detected</h3>
              <p className="mt-1 text-muted-foreground">₹35,000 sent to a new payee at 11:42 PM.</p>
              <p className="mt-3 font-mono font-bold text-danger">Risk Score: 92/100</p>
              <div className="mt-5 flex flex-wrap gap-2">
                <Button>
                  <Phone size={17} />
                  Call Sunita
                </Button>
                <Button variant="secondary">Review Transaction</Button>
                <Button
                  variant="secondary"
                  onClick={handleResolve}
                  disabled={resolveMutation.isPending}
                >
                  {resolveMutation.isPending ? "Resolving..." : "Mark Resolved"}
                </Button>
              </div>
            </div>
          )}
        </Card>

        {/* Caregiver Network Management */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-display text-xl font-bold">Caregiver Network</h2>
              <p className="text-xs text-muted-foreground">Authorized contacts for safety escalation</p>
            </div>
            <Button onClick={() => setAddModalOpen(true)} className="gap-1.5 text-xs h-9">
              <Plus size={15} />
              <span>Add Caregiver</span>
            </Button>
          </div>

          <div className="mt-5 divide-y divide-border">
            {isCgLoading ? (
              <div className="py-8 text-center text-xs text-muted-foreground">
                <RefreshCw className="animate-spin mx-auto mb-2" size={18} />
                Loading caregivers...
              </div>
            ) : caregivers.length === 0 ? (
              <div className="py-8 text-center text-xs text-muted-foreground">
                No caregivers added yet. Add a trusted family member to receive alerts.
              </div>
            ) : (
              caregivers.map((cg) => {
                const isVerified = cg.is_verified || cg.status === "VERIFIED";
                return (
                  <div key={cg.caregiver_id} className="py-4 space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-semibold">{cg.name}</p>
                          <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-bold text-muted-foreground uppercase">
                            {cg.relationship}
                          </span>
                          {isVerified ? (
                            <span className="flex items-center gap-1 text-[11px] font-semibold text-safe-strong">
                              <CheckCircle2 size={13} />
                              Verified
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-[11px] font-semibold text-warning">
                              <Clock size={13} />
                              Pending
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {cg.phone ? `${cg.phone.slice(0, 5)}•••••` : "No phone"} · {cg.email}
                        </p>
                      </div>

                      <div className="flex items-center gap-1">
                        {!isVerified && (
                          <Button
                            variant="secondary"
                            className="h-8 px-2.5 text-xs text-primary"
                            disabled={verifyCgMutation.isPending}
                            onClick={() => verifyCgMutation.mutate({ id: cg.caregiver_id })}
                          >
                            Verify
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          className="h-8 w-8 p-0 text-muted-foreground hover:text-danger"
                          onClick={() => deleteCgMutation.mutate(cg.caregiver_id)}
                          aria-label={`Remove ${cg.name}`}
                        >
                          <Trash2 size={15} />
                        </Button>
                      </div>
                    </div>

                    {/* Notification Preferences Badges & Quick Toggles */}
                    <div className="flex flex-wrap items-center gap-2 text-xs">
                      <span
                        className={`rounded px-2 py-0.5 font-medium flex items-center gap-1 text-[11px] ${
                          cg.notification_preferences?.sms_enabled
                            ? "bg-primary/10 text-primary border border-primary/20"
                            : "bg-muted text-muted-foreground"
                        }`}
                      >
                        <MessageSquare size={12} />
                        SMS Alert: {cg.notification_preferences?.sms_enabled ? "ON" : "OFF"}
                      </span>

                      <button
                        type="button"
                        onClick={() =>
                          updateCgMutation.mutate({
                            id: cg.caregiver_id,
                            updates: {
                              notification_preferences: {
                                voice_enabled: !cg.notification_preferences?.voice_enabled,
                              },
                            },
                          })
                        }
                        className={`rounded px-2 py-0.5 font-medium flex items-center gap-1 text-[11px] cursor-pointer transition ${
                          cg.notification_preferences?.voice_enabled
                            ? "bg-danger/10 text-danger border border-danger/20 font-bold"
                            : "bg-muted text-muted-foreground hover:bg-accent"
                        }`}
                      >
                        <Volume2 size={12} />
                        Voice Call: {cg.notification_preferences?.voice_enabled ? "ON" : "OFF"}
                      </button>

                      {cg.notification_preferences?.quiet_hours_enabled && (
                        <span className="rounded bg-muted px-2 py-0.5 text-[11px] text-muted-foreground flex items-center gap-1">
                          <Clock size={11} />
                          Quiet Hours: {cg.notification_preferences.quiet_hours_start}-
                          {cg.notification_preferences.quiet_hours_end}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>
      </div>

      {/* Add Caregiver Modal */}
      <Modal open={addModalOpen} onClose={() => setAddModalOpen(false)} title="Add Trusted Caregiver">
        <form onSubmit={handleCreateCaregiver} className="space-y-4 pt-2">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
              Caregiver Full Name
            </label>
            <input
              type="text"
              required
              className="field w-full"
              placeholder="e.g. Rohit Sharma"
              value={newCgName}
              onChange={(e) => setNewCgName(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                Relationship
              </label>
              <select
                className="field w-full bg-card"
                value={newCgRel}
                onChange={(e) => setNewCgRel(e.target.value)}
              >
                <option value="SON">Son</option>
                <option value="DAUGHTER">Daughter</option>
                <option value="SPOUSE">Spouse</option>
                <option value="RELATIVE">Relative</option>
                <option value="FRIEND">Friend</option>
                <option value="OTHER">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
                Phone (for SMS & Voice)
              </label>
              <input
                type="tel"
                required
                className="field w-full"
                placeholder="+91 98765 43210"
                value={newCgPhone}
                onChange={(e) => setNewCgPhone(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
              Email Address
            </label>
            <input
              type="email"
              className="field w-full"
              placeholder="rohit@example.com"
              value={newCgEmail}
              onChange={(e) => setNewCgEmail(e.target.value)}
            />
          </div>

          <div className="rounded-lg border border-border p-3 space-y-2 bg-muted/40">
            <p className="text-xs font-semibold">Notification Channels</p>
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={newCgSms}
                onChange={(e) => setNewCgSms(e.target.checked)}
                className="rounded"
              />
              <span>Send SMS on High & Critical risks</span>
            </label>
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={newCgVoice}
                onChange={(e) => setNewCgVoice(e.target.checked)}
                className="rounded"
              />
              <span>Initiate automated voice call on Critical risks</span>
            </label>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setAddModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createCgMutation.isPending}>
              {createCgMutation.isPending ? "Adding..." : "Add Caregiver"}
            </Button>
          </div>
        </form>
      </Modal>
    </AppShell>
  );
}

// ==========================================
// 7. REPORTS PAGE
// ==========================================
export function ReportsPage() {
  const { data: transactions = [] } = useTransactions();
  const { data: alerts = [] } = useAlerts();
  const { data: dashboard } = useDashboard();

  const safeCount = useMemo(
    () => transactions.filter((t) => t.status === "safe").length || (transactions.length ? 0 : 221),
    [transactions]
  );
  const reviewCount = useMemo(
    () => transactions.filter((t) => t.status === "review").length || (transactions.length ? 0 : 18),
    [transactions]
  );
  const highRiskCount = useMemo(
    () =>
      transactions.filter((t) => t.status === "high" || t.status === "critical").length ||
      (transactions.length ? 0 : 9),
    [transactions]
  );
  const activeAlertCount = useMemo(
    () => alerts.filter((a) => a.status === "pending").length || alerts.length,
    [alerts]
  );

  function download(type: string) {
    const content = `UPI Guardian Analytics & Safety Report
Generated: ${new Date().toISOString()}
User: Sunita Devi (usr_sunita_68)
Total Transactions Recorded: ${transactions.length || 24}
Safe Transactions: ${safeCount}
Transactions Requiring Review: ${reviewCount}
High-Risk Transactions: ${highRiskCount}
Active Fraud Alerts: ${activeAlertCount}
System Protection Status: ${dashboard?.accountStatus ?? "Protected"}`;

    const blob = new Blob([content], { type: type === "csv" ? "text/csv" : "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `upi-guardian-report.${type}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const pieData = [
    { name: "Safe", value: safeCount },
    { name: "Review", value: reviewCount },
    { name: "High risk", value: highRiskCount },
  ];

  return (
    <AppShell
      title="Reports & Analytics"
      subtitle="Patterns from real backend transactions and communication telemetry."
    >
      <div className="toolbar">
        <select className="field w-full sm:w-52">
          <option>Last 7 days</option>
          <option>Last 30 days</option>
          <option>Last 6 months</option>
        </select>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => download("csv")}>
            <Download size={17} />
            CSV
          </Button>
          <Button onClick={() => download("pdf")}>
            <FileText size={17} />
            PDF Report
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Chart title="Daily transaction volume">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={reportData}>
              <CartesianGrid stroke="var(--border)" vertical={false} />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="volume" fill="var(--info)" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Chart>

        <Chart title="Fraud risk trend">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={reportData}>
              <CartesianGrid stroke="var(--border)" vertical={false} />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Line dataKey="risk" stroke="var(--danger)" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </Chart>

        <Chart title="Safe vs suspicious">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                innerRadius={58}
                outerRadius={90}
              >
                {["var(--safe)", "var(--warning)", "var(--danger)"].map((c) => (
                  <Cell key={c} fill={c} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Chart>

        <Chart title="Scam communications detected">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={reportData}>
              <CartesianGrid stroke="var(--border)" vertical={false} />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="calls" fill="var(--ai)" />
              <Bar dataKey="sms" fill="var(--warning)" />
            </BarChart>
          </ResponsiveContainer>
        </Chart>
      </div>
    </AppShell>
  );
}

function Chart({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card className="p-5">
      <h2 className="font-display text-lg font-bold">{title}</h2>
      <div className="mt-4 h-72">{children}</div>
    </Card>
  );
}

// ==========================================
// 8. SETTINGS PAGE
// ==========================================
export function SettingsPage() {
  const { senior, toggleSenior, reducedMotion, setReducedMotion } = useApp();
  const [saved, setSaved] = useState(false);

  const { data: settings } = useSettings();
  const updateSettingsMutation = useUpdateSettings();

  const [profileName, setProfileName] = useState("");
  const [profileAge, setProfileAge] = useState("68");
  const [profilePhone, setProfilePhone] = useState("");
  const [profileEmail, setProfileEmail] = useState("");
  const [twoFactor, setTwoFactor] = useState(true);
  const [loginAlerts, setLoginAlerts] = useState(true);
  const [txAlerts, setTxAlerts] = useState(true);
  const [callAlerts, setCallAlerts] = useState(true);
  const [smsAlerts, setSmsAlerts] = useState(true);
  const [familyAlerts, setFamilyAlerts] = useState(true);
  const [highRiskSms, setHighRiskSms] = useState(true);
  const [criticalVoice, setCriticalVoice] = useState(true);
  const [quietHours, setQuietHours] = useState(false);

  useEffect(() => {
    if (settings) {
      if (settings.profile?.name) setProfileName(settings.profile.name);
      if (settings.profile?.age !== undefined) setProfileAge(String(settings.profile.age));
      if (settings.profile?.phone) setProfilePhone(settings.profile.phone);
      if (settings.profile?.email) setProfileEmail(settings.profile.email);
      if (settings.security?.twoFactor !== undefined) setTwoFactor(settings.security.twoFactor);
      if (settings.security?.loginActivityAlerts !== undefined)
        setLoginAlerts(settings.security.loginActivityAlerts);
      if (settings.alertPreferences?.highRiskTransactions !== undefined)
        setTxAlerts(settings.alertPreferences.highRiskTransactions);
      if (settings.alertPreferences?.scamCalls !== undefined)
        setCallAlerts(settings.alertPreferences.scamCalls);
      if (settings.alertPreferences?.scamSms !== undefined)
        setSmsAlerts(settings.alertPreferences.scamSms);
      if (settings.alertPreferences?.familyNotifications !== undefined)
        setFamilyAlerts(settings.alertPreferences.familyNotifications);
    }
  }, [settings]);

  const handleSave = () => {
    updateSettingsMutation.mutate(
      {
        profile: {
          name: profileName || settings?.profile?.name || "Sunita Devi",
          age: parseInt(profileAge, 10) || settings?.profile?.age || 68,
          phone: profilePhone || settings?.profile?.phone || "+91 ••••• ••410",
          email: profileEmail || settings?.profile?.email || "sunita.demo@example.com",
        },
        security: {
          twoFactor,
          loginActivityAlerts: loginAlerts,
        },
        alertPreferences: {
          highRiskTransactions: txAlerts,
          scamCalls: callAlerts,
          scamSms: smsAlerts,
          familyNotifications: familyAlerts,
        },
        accessibility: {
          seniorMode: senior,
          reducedMotion,
          highContrast: false,
          voiceAssistance: false,
        },
      },
      {
        onSuccess: () => {
          setSaved(true);
          setTimeout(() => setSaved(false), 2000);
        },
      }
    );
  };

  return (
    <AppShell title="Settings" subtitle="Personalize protection, alerts, and accessibility.">
      {updateSettingsMutation.isError && (
        <div className="mb-5 flex items-center gap-2 rounded-lg border border-danger/30 bg-danger-soft p-4 text-sm text-danger">
          <AlertTriangle className="shrink-0" size={18} />
          <span>
            {updateSettingsMutation.error instanceof Error
              ? updateSettingsMutation.error.message
              : "Failed to update settings. Please try again."}
          </span>
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-2">
        <SettingsCard title="Profile">
          <label className="block">
            <span className="field-label">Name</span>
            <input
              className="field"
              value={profileName}
              onChange={(e) => setProfileName(e.target.value)}
              placeholder="Sunita Devi"
            />
          </label>
          <label className="block">
            <span className="field-label">Age</span>
            <input
              className="field"
              value={profileAge}
              onChange={(e) => setProfileAge(e.target.value)}
              placeholder="68"
            />
          </label>
          <label className="block">
            <span className="field-label">Phone</span>
            <input
              className="field"
              value={profilePhone}
              onChange={(e) => setProfilePhone(e.target.value)}
              placeholder="+91 ••••• ••410"
            />
          </label>
          <label className="block">
            <span className="field-label">Email</span>
            <input
              className="field"
              value={profileEmail}
              onChange={(e) => setProfileEmail(e.target.value)}
              placeholder="sunita.demo@example.com"
            />
          </label>
        </SettingsCard>

        <SettingsCard title="Security">
          <SettingRow
            label="Two-factor authentication"
            sub="Extra protection when signing in"
            value={twoFactor}
            onChange={() => setTwoFactor(!twoFactor)}
          />
          <SettingRow
            label="Login activity"
            sub="Notify family about a new device"
            value={loginAlerts}
            onChange={() => setLoginAlerts(!loginAlerts)}
          />
          <Button variant="secondary">
            <Lock size={17} />
            Change password
          </Button>
        </SettingsCard>

        <SettingsCard title="Alert Preferences">
          <SettingRow
            label="High-risk transaction alerts"
            value={txAlerts}
            onChange={() => setTxAlerts(!txAlerts)}
          />
          <SettingRow
            label="Scam call alerts"
            value={callAlerts}
            onChange={() => setCallAlerts(!callAlerts)}
          />
          <SettingRow
            label="Scam SMS alerts"
            value={smsAlerts}
            onChange={() => setSmsAlerts(!smsAlerts)}
          />
          <SettingRow
            label="Family notifications"
            value={familyAlerts}
            onChange={() => setFamilyAlerts(!familyAlerts)}
          />
        </SettingsCard>

        <SettingsCard title="Caregiver & Escalation Preferences">
          <SettingRow
            label="High-risk SMS alerts"
            sub="Dispatch immediate SMS alert to verified caregivers"
            value={highRiskSms}
            onChange={() => setHighRiskSms(!highRiskSms)}
          />
          <SettingRow
            label="Critical-risk automated voice call"
            sub="Escalate critical alerts with automated phone calls"
            value={criticalVoice}
            onChange={() => setCriticalVoice(!criticalVoice)}
          />
          <SettingRow
            label="Quiet hours protection"
            sub="Suppress non-critical alerts between 10:00 PM and 7:00 AM"
            value={quietHours}
            onChange={() => setQuietHours(!quietHours)}
          />
          <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4 border-b border-border py-3">
            <div>
              <p className="font-medium">Hourly rate limit</p>
              <p className="mt-1 text-sm text-muted-foreground">Maximum alerts per caregiver per hour</p>
            </div>
            <span className="font-mono font-bold text-sm bg-muted px-2.5 py-1 rounded">5 alerts/hr</span>
          </div>
        </SettingsCard>

        <SettingsCard title="Accessibility">
          <SettingRow
            label="Senior Mode"
            sub="Larger text, buttons, and simpler dashboard"
            value={senior}
            onChange={toggleSenior}
          />
          <SettingRow label="High contrast mode" />
          <SettingRow
            label="Reduce animations"
            value={reducedMotion}
            onChange={() => setReducedMotion(!reducedMotion)}
          />
          <SettingRow label="Voice assistance" />
        </SettingsCard>
      </div>

      <Button
        className="mt-6"
        onClick={handleSave}
        disabled={updateSettingsMutation.isPending}
      >
        {updateSettingsMutation.isPending ? (
          <>
            <RefreshCw className="animate-spin" size={16} />
            Saving...
          </>
        ) : saved ? (
          <>
            <Check />
            Saved
          </>
        ) : (
          "Save preferences"
        )}
      </Button>
    </AppShell>
  );
}

function SettingsCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card className="space-y-4 p-6">
      <h2 className="font-display text-xl font-bold">{title}</h2>
      {children}
    </Card>
  );
}

function SettingRow({
  label,
  sub,
  value = true,
  onChange,
}: {
  label: string;
  sub?: string;
  value?: boolean;
  onChange?: () => void;
}) {
  const [local, setLocal] = useState(value);
  const checked = onChange ? value : local;
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4 border-b border-border py-3">
      <div>
        <p className="font-medium">{label}</p>
        {sub && <p className="mt-1 text-sm text-muted-foreground">{sub}</p>}
      </div>
      <Toggle
        label={label}
        checked={checked}
        onChange={() => (onChange ? onChange() : setLocal(!local))}
      />
    </div>
  );
}

// ==========================================
// 9. ABOUT PAGE
// ==========================================
export function AboutPage() {
  return (
    <AppShell
      title="About UPI Guardian"
      subtitle="A student-built financial safety system with a serious real-world purpose."
    >
      <Card className="p-6 sm:p-8">
        <span className="icon-box tone-info">
          <ShieldCheck size={28} />
        </span>
        <h2 className="mt-5 font-display text-3xl font-bold">
          Protection through understandable signals
        </h2>
        <p className="mt-4 max-w-3xl text-lg leading-8 text-muted-foreground">
          UPI Guardian is a student-built UPI fraud and scam communication detection system designed
          to help protect elderly users.
        </p>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {[
            { title: "Transaction Anomaly Engine", icon: Activity },
            { title: "Scam Call & SMS Analyzer", icon: Smartphone },
            { title: "Family Alert Dashboard", icon: Users },
          ].map(({ title, icon: Icon }) => (
            <div className="feature-block" key={title}>
              <Icon />
              <h3>{title}</h3>
            </div>
          ))}
        </div>
      </Card>
      <DemoNotice />
    </AppShell>
  );
}

// ==========================================
// 10. TECHNOLOGY PAGE
// ==========================================
export function TechnologyPage() {
  const tech = [
    "React.js",
    "Python",
    "Flask",
    "scikit-learn",
    "Isolation Forest",
    "TF-IDF",
    "Logistic Regression",
    "MongoDB / SQLite",
    "Twilio",
  ];

  return (
    <AppShell
      title="Technology"
      subtitle="The planned engineering stack behind the academic prototype."
    >
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {tech.map((x, i) => (
          <Card className="p-5" key={x}>
            <span
              className={`icon-box ${
                i % 3 === 0 ? "tone-info" : i % 3 === 1 ? "tone-ai" : "tone-safe"
              }`}
            >
              <Brain size={20} />
            </span>
            <h2 className="mt-4 font-display text-lg font-bold">{x}</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Part of the proposed analysis and demonstration workflow.
            </p>
          </Card>
        ))}
      </div>
      <DemoNotice />
    </AppShell>
  );
}

function DemoNotice() {
  return (
    <div className="mt-6 flex items-start gap-3 rounded-xl border border-warning/40 bg-warning-soft p-5">
      <AlertTriangle className="shrink-0 text-warning-strong" />
      <div>
        <h3 className="font-bold">Demo Mode — Synthetic Transaction Data</h3>
        <p className="mt-1 text-sm leading-6 text-muted-foreground">
          This academic prototype does not connect to bank systems and cannot guarantee fraud
          detection. All names and transactions are fictional.
        </p>
      </div>
    </div>
  );
}
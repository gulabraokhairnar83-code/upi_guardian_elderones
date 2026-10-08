import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { ShieldCheck, LogIn, AlertCircle, ArrowRight, UserCheck, HeartHandshake } from "lucide-react";
import { motion } from "motion/react";
import { useAuth } from "@/hooks/use-auth";
import { useApp } from "@/lib/app-context";
import { Button, Card } from "@/components/ui";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign In — UPI Guardian" },
      { name: "description", content: "Sign in to UPI Guardian to monitor and protect financial safety." },
      { property: "og:title", content: "Sign In — UPI Guardian" },
    ],
  }),
  component: LoginPage,
});

export function LoginPage() {
  const navigate = useNavigate();
  const { login, error, clearError } = useAuth();
  const { senior } = useApp();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const fillQuickDemo = (role: "elder" | "caregiver") => {
    clearError();
    setLocalError(null);
    if (role === "elder") {
      setEmail("sunita.devi@example.com");
      setPassword("GuardianPass123!");
    } else {
      setEmail("rohit.caregiver@example.com");
      setPassword("GuardianPass123!");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    clearError();

    if (!email.trim() || !password.trim()) {
      setLocalError("Please enter both email and password.");
      return;
    }

    setSubmitting(true);
    try {
      await login({ email: email.trim(), password });
      navigate({ to: "/dashboard" });
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : "Failed to sign in.");
    } finally {
      setSubmitting(false);
    }
  };

  const displayError = localError || error;

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-primary text-primary-foreground shadow-lg">
              <ShieldCheck size={24} />
            </span>
            <span className="font-display text-2xl font-bold tracking-tight">UPI Guardian</span>
          </Link>
          <h1 className="font-display text-2xl font-bold tracking-tight sm:text-3xl">
            Welcome back
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Sign in to access protected financial safety telemetry
          </p>
        </div>

        {/* Quick Demo Selector */}
        <div className="mb-6 rounded-xl border border-primary/20 bg-primary/5 p-3.5">
          <p className="text-xs font-semibold text-primary uppercase tracking-wider mb-2">
            One-Click Demo Accounts
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => fillQuickDemo("elder")}
              className="flex items-center justify-center gap-1.5 rounded-lg border border-border bg-card px-3 py-2 text-xs font-semibold hover:bg-accent transition"
            >
              <UserCheck size={14} className="text-primary" />
              Elder Account
            </button>
            <button
              type="button"
              onClick={() => fillQuickDemo("caregiver")}
              className="flex items-center justify-center gap-1.5 rounded-lg border border-border bg-card px-3 py-2 text-xs font-semibold hover:bg-accent transition"
            >
              <HeartHandshake size={14} className="text-accent" />
              Caregiver Account
            </button>
          </div>
        </div>

        <Card className="p-6 sm:p-8 shadow-xl border-border/80">
          {displayError && (
            <div className="mb-5 flex items-center gap-2 rounded-lg border border-danger/30 bg-danger-soft p-3 text-sm text-danger">
              <AlertCircle size={18} className="shrink-0" />
              <span>{displayError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                required
                className={`field w-full ${senior ? "text-lg py-3" : ""}`}
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Password
                </label>
              </div>
              <input
                type="password"
                required
                className={`field w-full ${senior ? "text-lg py-3" : ""}`}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <Button
              type="submit"
              disabled={submitting}
              className={`w-full mt-2 justify-center ${senior ? "h-14 text-lg" : "h-11"}`}
            >
              {submitting ? (
                "Signing In..."
              ) : (
                <>
                  <LogIn size={18} />
                  <span>Sign In</span>
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 border-t border-border pt-4 text-center text-sm text-muted-foreground">
            Don't have an account yet?{" "}
            <Link to="/register" className="font-semibold text-primary hover:underline">
              Register now
            </Link>
          </div>
        </Card>

        <div className="mt-6 text-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition"
          >
            <span>Continue as Guest Demo</span>
            <ArrowRight size={13} />
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

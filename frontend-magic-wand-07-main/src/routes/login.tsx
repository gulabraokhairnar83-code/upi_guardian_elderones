import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import {
  ShieldCheck,
  LogIn,
  AlertCircle,
  Eye,
  EyeOff,
  UserCheck,
  HeartHandshake,
  Mail,
  Lock,
} from "lucide-react";
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
  const { login, error, clearError, isAuthenticated, loading } = useAuth();
  const { senior } = useApp();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // If already authenticated, redirect straight to dashboard
  useEffect(() => {
    if (!loading && isAuthenticated) {
      navigate({ to: "/dashboard" });
    }
  }, [loading, isAuthenticated, navigate]);

  const fillQuickDemo = (role: "elder" | "caregiver") => {
    clearError();
    setLocalError(null);
    if (role === "elder") {
      setEmail("sunita.demo@example.com");
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

    const cleanEmail = email.trim();
    if (!cleanEmail || !password) {
      setLocalError("Please enter both email and password.");
      return;
    }

    setSubmitting(true);
    try {
      await login({ email: cleanEmail, password });
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
          <h1 className="font-display text-2xl font-bold tracking-tight sm:text-3xl text-foreground">
            Sign In to UPI Guardian
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Secure protection monitoring for elderly users & families
          </p>
        </div>

        {/* Quick Demo Accounts */}
        <div className="mb-6 rounded-xl border border-primary/20 bg-primary/5 p-4 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-bold text-primary uppercase tracking-wider">
              One-Click Demo Credentials
            </p>
            <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded-full font-semibold">
              Live Mock DB
            </span>
          </div>
          <p className="text-xs text-muted-foreground mb-3">
            Click an account below to populate verified credentials:
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => fillQuickDemo("elder")}
              className="flex items-center justify-center gap-1.5 rounded-lg border border-border bg-card px-3 py-2 text-xs font-semibold hover:border-primary hover:bg-accent transition"
            >
              <UserCheck size={14} className="text-primary" />
              Elder Account
            </button>
            <button
              type="button"
              onClick={() => fillQuickDemo("caregiver")}
              className="flex items-center justify-center gap-1.5 rounded-lg border border-border bg-card px-3 py-2 text-xs font-semibold hover:border-info hover:bg-accent transition"
            >
              <HeartHandshake size={14} className="text-info" />
              Caregiver Account
            </button>
          </div>
        </div>

        <Card className="p-6 sm:p-8 shadow-xl border-border/80">
          {displayError && (
            <div className="mb-5 flex items-center gap-2 rounded-lg border border-danger/30 bg-danger-soft p-3 text-sm text-danger animate-in fade-in">
              <AlertCircle size={18} className="shrink-0" />
              <span>{displayError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <input
                  type="email"
                  required
                  autoComplete="email"
                  className={`field w-full pl-10 ${senior ? "text-lg py-3" : ""}`}
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <Mail
                  size={18}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Password
                </label>
                <Link
                  to="/forgot-password"
                  className="text-xs font-semibold text-primary hover:underline"
                >
                  Forgot Password?
                </Link>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  autoComplete="current-password"
                  className={`field w-full pl-10 pr-10 ${senior ? "text-lg py-3" : ""}`}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <Lock
                  size={18}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1 transition focus:outline-none"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
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
              Create Account
            </Link>
          </div>
        </Card>

        <div className="mt-6 text-center">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition"
          >
            <span>Back to Home</span>
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

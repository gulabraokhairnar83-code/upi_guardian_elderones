import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ShieldCheck, Mail, ArrowLeft, CheckCircle2, AlertCircle, KeyRound } from "lucide-react";
import { motion } from "motion/react";
import { useAuth } from "@/hooks/use-auth";
import { useApp } from "@/lib/app-context";
import { Button, Card } from "@/components/ui";

export const Route = createFileRoute("/forgot-password")({
  head: () => ({
    meta: [
      { title: "Forgot Password — UPI Guardian" },
      { name: "description", content: "Reset your UPI Guardian account password securely." },
      { property: "og:title", content: "Forgot Password — UPI Guardian" },
    ],
  }),
  component: ForgotPasswordPage,
});

export function ForgotPasswordPage() {
  const { forgotPassword, error, clearError } = useAuth();
  const { senior } = useApp();

  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    clearError();

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      setLocalError("Please enter your registered email address.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(cleanEmail)) {
      setLocalError("Please enter a valid email address.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await forgotPassword(cleanEmail);
      setSuccessMessage(
        res.message ||
          "Password reset instructions and emergency verification have been dispatched to your registered contact."
      );
      setSubmitted(true);
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : "Failed to process reset request.");
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
            Reset Password
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Secure recovery for elderly users and trusted caregivers
          </p>
        </div>

        <Card className="p-6 sm:p-8 shadow-xl border-border/80">
          {submitted ? (
            <div className="text-center py-4">
              <div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-safe-soft text-safe-strong">
                <CheckCircle2 size={32} />
              </div>
              <h2 className="font-display text-lg font-bold text-foreground">
                Instructions Dispatched
              </h2>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                {successMessage}
              </p>
              <div className="mt-4 rounded-lg bg-info-soft/60 p-3 text-xs text-info-foreground border border-info/20 text-left">
                <p className="font-semibold text-info mb-1 flex items-center gap-1.5">
                  <ShieldCheck size={14} /> Caregiver Safety Safeguard
                </p>
                <p className="text-muted-foreground">
                  To prevent unauthorized account takeovers of elderly relatives, reset notifications
                  are also verified through registered caregiver contacts.
                </p>
              </div>
              <div className="mt-6 flex flex-col gap-2">
                <Link
                  to="/login"
                  className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition"
                >
                  <ArrowLeft size={16} />
                  Return to Sign In
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    setSubmitted(false);
                    setEmail("");
                  }}
                  className="text-xs text-muted-foreground hover:text-foreground mt-2"
                >
                  Try another email address
                </button>
              </div>
            </div>
          ) : (
            <>
              {displayError && (
                <div className="mb-5 flex items-center gap-2 rounded-lg border border-danger/30 bg-danger-soft p-3 text-sm text-danger">
                  <AlertCircle size={18} className="shrink-0" />
                  <span>{displayError}</span>
                </div>
              )}

              <p className="mb-5 text-sm text-muted-foreground leading-relaxed">
                Enter your registered email address. We will verify your account and initiate safety
                recovery protocols.
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                    Registered Email Address
                  </label>
                  <div className="relative">
                    <input
                      type="email"
                      required
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

                <Button
                  type="submit"
                  disabled={submitting}
                  className={`w-full mt-2 justify-center ${senior ? "h-14 text-lg" : "h-11"}`}
                >
                  {submitting ? (
                    "Sending Instructions..."
                  ) : (
                    <>
                      <KeyRound size={18} />
                      <span>Send Reset Instructions</span>
                    </>
                  )}
                </Button>
              </form>

              <div className="mt-6 border-t border-border pt-4 text-center text-sm text-muted-foreground">
                Remembered your password?{" "}
                <Link to="/login" className="font-semibold text-primary hover:underline">
                  Sign in
                </Link>
              </div>
            </>
          )}
        </Card>

        <div className="mt-6 text-center">
          <Link
            to="/login"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition"
          >
            <ArrowLeft size={13} />
            <span>Back to Login</span>
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

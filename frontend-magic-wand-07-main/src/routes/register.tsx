import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { ShieldCheck, UserPlus, AlertCircle, ArrowRight, UserCheck, HeartHandshake } from "lucide-react";
import { motion } from "motion/react";
import { useAuth } from "@/hooks/use-auth";
import { useApp } from "@/lib/app-context";
import { Button, Card } from "@/components/ui";

export const Route = createFileRoute("/register")({
  head: () => ({
    meta: [
      { title: "Create Account — UPI Guardian" },
      { name: "description", content: "Register an Elder or Caregiver account on UPI Guardian." },
      { property: "og:title", content: "Create Account — UPI Guardian" },
    ],
  }),
  component: RegisterPage,
});

export function RegisterPage() {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuth();
  const { senior } = useApp();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"ELDER" | "CAREGIVER">("ELDER");
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    clearError();

    if (!name.trim() || !email.trim() || !password.trim()) {
      setLocalError("Please fill in all required fields.");
      return;
    }

    if (password.length < 8) {
      setLocalError("Password must be at least 8 characters.");
      return;
    }

    setSubmitting(true);
    try {
      await register({
        name: name.trim(),
        email: email.trim(),
        phone: phone.trim(),
        password,
        role,
      });
      navigate({ to: "/dashboard" });
    } catch (err: unknown) {
      setLocalError(err instanceof Error ? err.message : "Registration failed.");
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
            Create an Account
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Join the safety network protecting elderly family members
          </p>
        </div>

        <Card className="p-6 sm:p-8 shadow-xl border-border/80">
          {displayError && (
            <div className="mb-5 flex items-center gap-2 rounded-lg border border-danger/30 bg-danger-soft p-3 text-sm text-danger">
              <AlertCircle size={18} className="shrink-0" />
              <span>{displayError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Role Selection */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Account Role
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setRole("ELDER")}
                  className={`flex items-center justify-center gap-2 rounded-lg border p-2.5 text-xs font-semibold transition ${
                    role === "ELDER"
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border bg-card text-muted-foreground hover:bg-accent"
                  }`}
                >
                  <UserCheck size={16} />
                  <span>Protected Elder</span>
                </button>
                <button
                  type="button"
                  onClick={() => setRole("CAREGIVER")}
                  className={`flex items-center justify-center gap-2 rounded-lg border p-2.5 text-xs font-semibold transition ${
                    role === "CAREGIVER"
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border bg-card text-muted-foreground hover:bg-accent"
                  }`}
                >
                  <HeartHandshake size={16} />
                  <span>Trusted Caregiver</span>
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                required
                className={`field w-full ${senior ? "text-lg py-3" : ""}`}
                placeholder="Ramesh Sharma"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                required
                className={`field w-full ${senior ? "text-lg py-3" : ""}`}
                placeholder="ramesh@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Phone Number (for SMS & Voice Alerts)
              </label>
              <input
                type="tel"
                className={`field w-full ${senior ? "text-lg py-3" : ""}`}
                placeholder="+91 98765 43210"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Password (min. 8 characters)
              </label>
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
                "Creating Account..."
              ) : (
                <>
                  <UserPlus size={18} />
                  <span>Create Account</span>
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 border-t border-border pt-4 text-center text-sm text-muted-foreground">
            Already registered?{" "}
            <Link to="/login" className="font-semibold text-primary hover:underline">
              Sign in
            </Link>
          </div>
        </Card>

        <div className="mt-6 text-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition"
          >
            <span>Skip to Dashboard</span>
            <ArrowRight size={13} />
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

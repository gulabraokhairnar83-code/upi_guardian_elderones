import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import {
  ShieldCheck,
  UserPlus,
  AlertCircle,
  Eye,
  EyeOff,
  UserCheck,
  HeartHandshake,
  Mail,
  Lock,
  User,
  Phone,
} from "lucide-react";
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
  const { register, error, clearError, isAuthenticated, loading } = useAuth();
  const { senior } = useApp();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [role, setRole] = useState<"ELDER" | "CAREGIVER">("ELDER");
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (!loading && isAuthenticated) {
      navigate({ to: "/dashboard" });
    }
  }, [loading, isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    clearError();

    const cleanName = name.trim();
    const cleanEmail = email.trim();
    const cleanPhone = phone.trim();

    if (!cleanName || !cleanEmail || !password || !confirmPassword) {
      setLocalError("Please fill in all required fields.");
      return;
    }

    if (cleanName.length < 2) {
      setLocalError("Full name must be at least 2 characters.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(cleanEmail)) {
      setLocalError("Please enter a valid email address.");
      return;
    }

    if (password.length < 8) {
      setLocalError("Password must be at least 8 characters long.");
      return;
    }

    if (!/[A-Za-z]/.test(password) || !/\d/.test(password)) {
      setLocalError("Password must contain at least one letter and one number.");
      return;
    }

    if (password !== confirmPassword) {
      setLocalError("Passwords do not match. Please re-enter.");
      return;
    }

    setSubmitting(true);
    try {
      await register({
        name: cleanName,
        email: cleanEmail,
        phone: cleanPhone,
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
        className="w-full max-w-lg"
      >
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-primary text-primary-foreground shadow-lg">
              <ShieldCheck size={24} />
            </span>
            <span className="font-display text-2xl font-bold tracking-tight">UPI Guardian</span>
          </Link>
          <h1 className="font-display text-2xl font-bold tracking-tight sm:text-3xl text-foreground">
            Create Your Account
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Join the safety network protecting elderly users from financial fraud
          </p>
        </div>

        <Card className="p-6 sm:p-8 shadow-xl border-border/80">
          {displayError && (
            <div className="mb-5 flex items-center gap-2 rounded-lg border border-danger/30 bg-danger-soft p-3 text-sm text-danger animate-in fade-in">
              <AlertCircle size={18} className="shrink-0" />
              <span>{displayError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* User Role Selection */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
                Select Your Role
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setRole("ELDER")}
                  className={`flex flex-col items-center justify-center rounded-xl border p-3.5 text-center transition ${
                    role === "ELDER"
                      ? "border-primary bg-primary/10 text-primary ring-2 ring-primary/20"
                      : "border-border bg-card text-muted-foreground hover:bg-accent"
                  }`}
                >
                  <UserCheck size={22} className="mb-1 text-primary" />
                  <span className="text-xs font-bold text-foreground">Elderly User</span>
                  <span className="text-[11px] text-muted-foreground mt-0.5">
                    Protected Individual
                  </span>
                </button>
                <button
                  type="button"
                  onClick={() => setRole("CAREGIVER")}
                  className={`flex flex-col items-center justify-center rounded-xl border p-3.5 text-center transition ${
                    role === "CAREGIVER"
                      ? "border-primary bg-primary/10 text-primary ring-2 ring-primary/20"
                      : "border-border bg-card text-muted-foreground hover:bg-accent"
                  }`}
                >
                  <HeartHandshake size={22} className="mb-1 text-info" />
                  <span className="text-xs font-bold text-foreground">Caregiver</span>
                  <span className="text-[11px] text-muted-foreground mt-0.5">
                    Family Guardian
                  </span>
                </button>
              </div>
            </div>

            {/* Full Name */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  autoComplete="name"
                  className={`field w-full pl-10 ${senior ? "text-lg py-3" : ""}`}
                  placeholder="e.g. Ramesh Sharma"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
                <User
                  size={18}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
                />
              </div>
            </div>

            {/* Email Address */}
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

            {/* Phone Number */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Phone Number (optional, for SMS & emergency alerts)
              </label>
              <div className="relative">
                <input
                  type="tel"
                  autoComplete="tel"
                  className={`field w-full pl-10 ${senior ? "text-lg py-3" : ""}`}
                  placeholder="+91 98765 43210"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
                <Phone
                  size={18}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Password (min. 8 characters with letter & number)
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  autoComplete="new-password"
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

            {/* Confirm Password */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Confirm Password
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  required
                  autoComplete="new-password"
                  className={`field w-full pl-10 pr-10 ${senior ? "text-lg py-3" : ""}`}
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
                <Lock
                  size={18}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1 transition focus:outline-none"
                  aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                >
                  {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              disabled={submitting}
              className={`w-full mt-3 justify-center ${senior ? "h-14 text-lg" : "h-11"}`}
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
            Already have an account?{" "}
            <Link to="/login" className="font-semibold text-primary hover:underline">
              Sign in
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

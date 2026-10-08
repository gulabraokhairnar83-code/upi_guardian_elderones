import { X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, type ButtonHTMLAttributes, type ReactNode } from "react";

export function Button({ className = "", variant = "primary", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "danger" | "ghost" }) {
  const styles = { primary: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm", secondary: "border border-border bg-card text-foreground hover:bg-muted", danger: "bg-danger text-danger-foreground hover:bg-danger/90", ghost: "text-muted-foreground hover:bg-muted hover:text-foreground" };
  return <button className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50 ${styles[variant]} ${className}`} {...props} />;
}

export function Modal({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: ReactNode }) {
  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  return <AnimatePresence>{open && <motion.div className="fixed inset-0 z-50 grid place-items-center bg-overlay p-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={onClose}><motion.div role="dialog" aria-modal="true" aria-label={title} className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border border-border bg-card shadow-2xl" initial={{ opacity: 0, y: 18, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 12 }} onMouseDown={(e) => e.stopPropagation()}><div className="sticky top-0 z-10 grid grid-cols-[minmax(0,1fr)_auto] items-center border-b border-border bg-card px-5 py-4"><h2 className="truncate font-display text-xl font-bold">{title}</h2><Button variant="ghost" className="h-10 w-10 p-0" onClick={onClose} aria-label="Close dialog"><X size={20}/></Button></div><div className="p-5">{children}</div></motion.div></motion.div>}</AnimatePresence>;
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-xl border border-border bg-card shadow-card ${className}`}>{children}</div>;
}

export function RiskBadge({ level }: { level: "safe" | "review" | "high" | "critical" }) {
  const copy = { safe: "✓ Safe", review: "⚠ Please Review", high: "! High Risk", critical: "✕ Possible Scam" };
  return <span className={`risk-badge risk-${level}`}>{copy[level]}</span>;
}

export function Toggle({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) {
  return <button role="switch" aria-checked={checked} aria-label={label} onClick={() => onChange(!checked)} className={`relative h-7 w-12 shrink-0 rounded-full border transition ${checked ? "border-primary bg-primary" : "border-border bg-muted"}`}><span className={`absolute top-1 h-5 w-5 rounded-full bg-primary-foreground shadow transition ${checked ? "left-6" : "left-1"}`}/></button>;
}
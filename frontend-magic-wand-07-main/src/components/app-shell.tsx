import { Link, useRouterState } from "@tanstack/react-router";
import { Activity, Bell, Brain, ChartNoAxesCombined, ChevronDown, CreditCard, FileText, Menu, MessageSquare, Moon, Phone, Settings, ShieldAlert, ShieldCheck, Sun, UserRound, Users, X } from "lucide-react";
import { useState, useEffect, type ReactNode } from "react";
import { useApp } from "@/lib/app-context";
import { useHealthCheck, useAuth, useNotifications } from "@/hooks";
import { Button } from "./ui";

const nav = [
  ["/dashboard", "Dashboard", Activity], ["/transactions", "Transactions", CreditCard], ["/alerts", "Fraud Alerts", ShieldAlert],
  ["/call-analyzer", "Call Analyzer", Phone], ["/sms-analyzer", "SMS Analyzer", MessageSquare], ["/risk-analysis", "Risk Analysis", Brain],
  ["/family", "Family / Caregiver", Users], ["/reports", "Reports", ChartNoAxesCombined], ["/settings", "Settings", Settings],
] as const;

export function AppShell({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  const [menu, setMenu] = useState(false);
  const [notifications, setNotifications] = useState(false);
  const [profile, setProfile] = useState(false);
  const { dark, senior, toggleDark, toggleSenior } = useApp();
  const path = useRouterState({ select: (s) => s.location.pathname });
  const { data: health } = useHealthCheck();
  const { user, logout, isAuthenticated } = useAuth();
  const { data: notifData = [] } = useNotifications(10);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMenu(false);
        setNotifications(false);
        setProfile(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const isHealthy = health?.status === "healthy";
  const isOffline = health?.status === "offline";
  const statusLabel = isOffline ? "API Offline" : "AI Engine Online";
  const statusSub = health?.isMock
    ? "Demo mock mode"
    : isHealthy
    ? `Flask API v${health?.version || "1.0.0"}`
    : isOffline
    ? "Check Flask server"
    : "Connecting...";

  const userName = user?.name || "Sunita Devi";
  const userRole = user?.role || "ELDER";
  const userAvatar = user?.avatar || userName.slice(0, 2).toUpperCase();
  const unreadAlerts = notifData.filter((n) => !n.is_acknowledged);

  const sidebar = (
    <>
      <div className="flex h-20 items-center gap-3 px-5">
        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-primary text-primary-foreground shadow">
          <ShieldCheck size={23} />
        </span>
        <div className="min-w-0">
          <p className="font-display text-lg font-bold text-sidebar-foreground">UPI Guardian</p>
          <p className="truncate text-xs text-sidebar-muted">UPI Safety System</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {nav.map(([to, label, Icon]) => (
          <Link
            key={to}
            to={to}
            onClick={() => setMenu(false)}
            activeProps={{ className: "nav-link-active" }}
            inactiveProps={{ className: "nav-link" }}
          >
            <Icon size={19} />
            <span>{label}</span>
          </Link>
        ))}
      </nav>
      <div className="m-3 space-y-3 border-t border-sidebar-border pt-4">
        <div className="rounded-lg bg-sidebar-accent p-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-sidebar-foreground">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                isOffline ? "bg-danger" : isHealthy ? "bg-safe animate-pulse" : "bg-warning"
              }`}
            />
            {statusLabel}
          </div>
          <p className="mt-1 text-xs text-sidebar-muted">{statusSub}</p>
        </div>
        <div className="flex items-center justify-between px-2 py-1">
          <Link
            to="/settings"
            className="flex items-center gap-2.5 text-sm text-sidebar-muted hover:text-sidebar-foreground"
          >
            <UserRound size={17} />
            <span className="truncate max-w-[120px]">{userName}</span>
          </Link>
          <span className="rounded bg-primary/20 px-1.5 py-0.5 text-[10px] font-bold uppercase text-primary">
            {userRole}
          </span>
        </div>
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-background text-foreground">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col bg-sidebar lg:flex">
        {sidebar}
      </aside>

      {menu && (
        <div
          className="fixed inset-0 z-50 bg-overlay lg:hidden"
          onClick={() => setMenu(false)}
        >
          <aside
            className="flex h-full w-[min(20rem,88vw)] flex-col bg-sidebar"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="absolute right-3 top-3">
              <Button
                variant="ghost"
                className="text-sidebar-foreground"
                onClick={() => setMenu(false)}
                aria-label="Close menu"
              >
                <X />
              </Button>
            </div>
            {sidebar}
          </aside>
        </div>
      )}

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 grid h-18 grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 border-b border-border bg-background/95 px-4 backdrop-blur sm:px-6">
          <Button
            variant="ghost"
            className="h-11 w-11 p-0 lg:hidden"
            onClick={() => setMenu(true)}
            aria-label="Open navigation"
          >
            <Menu />
          </Button>

          <div className="min-w-0">
            <p className="truncate text-xs font-semibold uppercase text-muted-foreground">
              UPI Guardian / {title}
            </p>
            <h1 className="truncate font-display text-xl font-bold sm:text-2xl">{title}</h1>
          </div>

          <div className="flex shrink-0 items-center gap-1 sm:gap-2">
            <button
              className={`senior-pill ${senior ? "senior-pill-active" : ""}`}
              onClick={toggleSenior}
              aria-pressed={senior}
              aria-label="Toggle Senior Mode interface"
            >
              Senior <span className="hidden sm:inline">Mode</span>
            </button>
            <Button
              variant="ghost"
              className="h-11 w-11 p-0"
              onClick={toggleDark}
              aria-label="Toggle theme"
            >
              {dark ? <Sun /> : <Moon />}
            </Button>

            {/* Notifications Telemetry Center */}
            <div className="relative">
              <Button
                variant="ghost"
                className="relative h-11 w-11 p-0"
                onClick={() => setNotifications(!notifications)}
                aria-label="Notifications"
                aria-expanded={notifications}
                aria-haspopup="true"
              >
                <Bell />
                {unreadAlerts.length > 0 && (
                  <span className="absolute right-2 top-2 h-2.5 w-2.5 rounded-full bg-danger animate-pulse" />
                )}
              </Button>

              {notifications && (
                <div className="absolute right-0 top-12 w-[min(24rem,88vw)] rounded-xl border border-border bg-card p-3 shadow-2xl z-50">
                  <div className="flex items-center justify-between px-2 pb-2 border-b border-border">
                    <p className="font-display font-bold">Emergency & Caregiver Alerts</p>
                    <Link to="/alerts" className="text-xs text-primary font-semibold hover:underline">
                      View all
                    </Link>
                  </div>
                  <div className="max-h-72 overflow-y-auto divide-y divide-border">
                    {notifData.length === 0 ? (
                      <p className="py-4 text-center text-xs text-muted-foreground">
                        No recent emergency dispatches.
                      </p>
                    ) : (
                      notifData.slice(0, 5).map((n) => (
                        <div key={n.notification_id} className="px-2 py-3 text-sm">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-danger">
                              {n.channel} Alert · {n.risk_level}
                            </span>
                            <span className="text-[10px] text-muted-foreground">
                              {n.status}
                            </span>
                          </div>
                          <p className="mt-1 font-medium text-xs line-clamp-2">
                            {n.message_preview || "Emergency caregiver risk notification dispatched."}
                          </p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Profile Dropdown */}
            <div className="relative hidden sm:block">
              <Button
                variant="secondary"
                onClick={() => setProfile(!profile)}
                aria-label="User account and settings menu"
                aria-expanded={profile}
                aria-haspopup="true"
              >
                <span className="grid h-7 w-7 place-items-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                  {userAvatar}
                </span>
                <ChevronDown size={15} />
              </Button>

              {profile && (
                <div className="absolute right-0 top-12 w-52 rounded-xl border border-border bg-card p-2 shadow-xl z-50">
                  <div className="px-3 py-2 border-b border-border mb-1">
                    <p className="font-semibold text-sm truncate">{userName}</p>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider">{userRole}</p>
                  </div>
                  <Link
                    to="/settings"
                    onClick={() => setProfile(false)}
                    className="block rounded-md px-3 py-2 text-sm hover:bg-muted"
                  >
                    Profile & settings
                  </Link>
                  <Link
                    to="/family"
                    onClick={() => setProfile(false)}
                    className="block rounded-md px-3 py-2 text-sm hover:bg-muted"
                  >
                    Caregivers & Family
                  </Link>
                  {isAuthenticated ? (
                    <button
                      onClick={() => {
                        logout();
                        setProfile(false);
                      }}
                      className="w-full text-left rounded-md px-3 py-2 text-sm text-danger hover:bg-muted"
                    >
                      Sign Out
                    </button>
                  ) : (
                    <Link
                      to="/login"
                      onClick={() => setProfile(false)}
                      className="block rounded-md px-3 py-2 text-sm text-primary font-semibold hover:bg-muted"
                    >
                      Sign In
                    </Link>
                  )}
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[1500px] p-4 pb-24 sm:p-6 lg:p-8">
          {subtitle && <p className="mb-6 -mt-4 text-muted-foreground">{subtitle}</p>}
          {children}
        </main>
      </div>

      <nav className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-5 border-t border-border bg-card px-1 py-1.5 lg:hidden">
        {nav.slice(0, 5).map(([to, label, Icon]) => (
          <Link
            key={to}
            to={to}
            className={`flex min-w-0 flex-col items-center gap-1 rounded-md py-2 text-[10px] ${
              path === to ? "text-primary" : "text-muted-foreground"
            }`}
          >
            <Icon size={20} />
            <span className="truncate">{label.replace("Fraud ", "")}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
}
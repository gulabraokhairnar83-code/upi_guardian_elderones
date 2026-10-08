# Frontend Architecture & Status Audit: UPI Guardian

> **Project Name:** UPI Guardian (previously labeled as "FraudShield" in templates)  
> **Repository Folder:** `frontend-magic-wand-07-main`  
> **Audit Date:** October 8, 2026  
> **Scope:** Complete frontend inspection, static analysis, type checking, build validation, SSR testing, and backend-integration readiness review.

---

## 1. Executive Summary

The **UPI Guardian** frontend is a modern, high-fidelity single-page application built with **React 19**, **TanStack Start / TanStack Router**, and **Tailwind CSS v4**. It features an extensive design system, dark mode, senior accessibility mode, comprehensive dashboards, interactive scam analyzers, family/caregiver portals, and synthetic transaction monitors.

**Key Findings:**
1. **Build Status:** Production bundler (`vite build`) successfully generates client and SSR bundles with zero bundle compilation failures.
2. **Runtime Health:** 11 out of 12 routes render and hydrate without issue. However, `/about` triggers an uncaught `ReferenceError: Activity is not defined` during SSR and client evaluation due to an unimported Lucide icon.
3. **Type Safety:** `tsc --noEmit` flags 8 TypeScript errors primarily caused by strict tsconfig settings (`noUncheckedIndexedAccess`, `noPropertyAccessFromIndexSignature`), loose array tuples in the timeline, and the missing `Activity` import.
4. **Code Quality:** ESLint reports 7 non-critical React Refresh warnings (exporting non-components from UI primitive files), and Prettier reports formatting issues due to minified JSX layouts in `pages.tsx`.
5. **Backend Readiness:** There is currently no active HTTP integration or API state layer. Mock data is partially centralized in `src/lib/fraud-data.ts` and partially hardcoded within UI components. A clean abstraction layer is needed before introducing the Python/Flask ML services.

---

## 2. Current Technology Stack

| Layer | Technology | Version | Purpose & Notes |
| :--- | :--- | :--- | :--- |
| **Framework / SSR** | TanStack Start (`@tanstack/react-start`) | `1.168.32` | Full-stack React SSR framework powered by Nitro (`3.0.260603-beta`) |
| **Runtime & UI** | React / React DOM | `^19.2.0` | React 19 core library |
| **Language** | TypeScript | `^5.8.3` | Strict TypeScript configuration enabled in `tsconfig.json` |
| **Routing** | TanStack Router (`@tanstack/react-router`) | `1.170.18` | Type-safe, file-based routing (`src/routes/*`) with auto-generated tree (`routeTree.gen.ts`) |
| **Bundler & Tooling** | Vite | `8.1.5` | Configured via `@lovable.dev/vite-tanstack-config` (`^2.24.0`) |
| **Styling** | Tailwind CSS v4 (`@tailwindcss/vite`) | `^4.2.1` | Modern `@theme` and `@utility` rules in `src/styles.css`, OKLCH color palettes |
| **Animation** | Motion (`motion`) | `^13.4.4` | Framer Motion modern package (`motion/react`) for smooth transitions and gauge animations |
| **Data Visualization** | Recharts | `^2.15.4` | Used for Activity Area charts, volume Bar charts, risk Line charts, and Donut charts |
| **Icons** | Lucide React (`lucide-react`) | `^0.575.0` | Iconography across navigation, status badges, timelines, and action buttons |
| **Server State / Cache** | TanStack Query (`@tanstack/react-query`) | `^5.101.1` | Configured in root router context; currently idle (no queries/mutations implemented) |
| **UI Primitives** | Radix UI Primitives | Various | 46 pre-installed shadcn/Radix component wrappers in `src/components/ui/*` |
| **Forms & Validation** | React Hook Form & Zod | `^7.71.2` / `^3.25.76` | Installed in `package.json`; forms currently use lightweight React state |
| **Notifications** | Sonner (`sonner`) | `^2.0.7` | Installed; custom notification popover also implemented in `app-shell.tsx` |

---

## 3. Current Folder Structure

```text
UPI Guardian/
├── docs/
│   └── CURRENT_FRONTEND_AUDIT.md             <-- This audit document
└── frontend-magic-wand-07-main/
    ├── .gitignore
    ├── .lovable/
    ├── .prettierignore / .prettierrc
    ├── AGENTS.md                              <-- Architecture and editing guidelines
    ├── README.md
    ├── bun.lock / bunfig.toml                 <-- Generator artifacts (system uses npm & node v26)
    ├── components.json                        <-- shadcn UI configuration file
    ├── eslint.config.js                       <-- ESLint 9 configuration with Prettier
    ├── package.json                           <-- Dependencies and npm scripts
    ├── tsconfig.json                          <-- Strict TypeScript configuration
    ├── vite.config.ts                         <-- Lovable Vite TanStack configuration
    ├── public/
    │   └── favicon.ico
    └── src/
        ├── components/
        │   ├── app-shell.tsx                  <-- Responsive layout, sidebar, header, theme & senior toggles
        │   ├── dashboard-parts.tsx            <-- RiskGauge, KpiGrid, ActivityChart, AlertsList
        │   ├── pages.tsx                      <-- Monolithic view implementations for all application routes
        │   ├── ui.tsx                         <-- Lightweight UI primitives (Button, Modal, Card, RiskBadge, Toggle)
        │   └── ui/                            <-- 46 Radix UI wrappers (accordion, dialog, table, sidebar, etc.)
        ├── hooks/
        │   └── use-mobile.tsx                 <-- Viewport media query hook for mobile screen detection
        ├── lib/
        │   ├── app-context.tsx                <-- AppProvider for dark mode, senior mode, and reduced motion
        │   ├── error-capture.ts               <-- Error tracking & formatting pipeline
        │   ├── error-page.ts                  <-- Static fallback HTML error template
        │   ├── fraud-data.ts                  <-- Synthetic dataset (transactions, charts, alerts, API map)
        │   ├── lovable-error-reporting.ts     <-- Client error boundary reporting bridge
        │   └── utils.ts                       <-- Utility function `cn()` (clsx + tailwind-merge)
        ├── routes/
        │   ├── __root.tsx                     <-- Root HTML shell, metadata, query provider, error boundaries
        │   ├── index.tsx                      <-- Route: / (Landing Page)
        │   ├── dashboard.tsx                  <-- Route: /dashboard
        │   ├── transactions.tsx               <-- Route: /transactions
        │   ├── alerts.tsx                     <-- Route: /alerts
        │   ├── call-analyzer.tsx              <-- Route: /call-analyzer
        │   ├── sms-analyzer.tsx               <-- Route: /sms-analyzer
        │   ├── risk-analysis.tsx              <-- Route: /risk-analysis
        │   ├── family.tsx                     <-- Route: /family
        │   ├── reports.tsx                    <-- Route: /reports
        │   ├── settings.tsx                   <-- Route: /settings
        │   ├── about.tsx                      <-- Route: /about
        │   ├── technology.tsx                 <-- Route: /technology
        │   └── README.md                      <-- TanStack Router conventions guide
        ├── routeTree.gen.ts                   <-- Auto-generated TanStack Router route tree
        ├── router.tsx                         <-- TanStack Router initialization and context binding
        ├── server.ts                          <-- Nitro/SSR server entry point and error normalizer
        ├── start.ts                           <-- TanStack Start CSRF & server middleware configuration
        └── styles.css                         <-- Tailwind v4 stylesheet, CSS variables, utility classes
```

---

## 4. Existing Pages and Routes

| Route | File Path | Component | Status | Visual & Functional Summary |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `src/routes/index.tsx` | `Index` | **Working** | Public landing page. Features hero header, animated interactive shield graphic with signal callouts, 5-stage fraud lifecycle process, multi-layered defense breakdown, and footer. (Currently branded as *FraudShield*). |
| `/dashboard` | `src/routes/dashboard.tsx` | `DashboardPage` | **Working** | Main financial guardian dashboard. Features system operational banner, 6 KPI cards, interactive 4-range filter chips, 24-hour activity area chart, SVG circular risk gauge (Score 27/100), and recent alert cards. |
| `/transactions` | `src/routes/transactions.tsx` | `TransactionsPage` | **Working** | Comprehensive transaction table showing 24 synthetic records. Live text search by payee/ID, status filter dropdown, risk badges, and click-to-view modal with detailed factor analysis and simulated action dialogs. |
| `/alerts` | `src/routes/alerts.tsx` | `AlertsPage` | **Working** | Prioritized alert center. Filter chips by severity (`all`, `critical`, `high`, `review`), alert card grid showing risk ratings and transaction values, with detail modal for reviewing or resolving alerts. |
| `/call-analyzer` | `src/routes/call-analyzer.tsx` | `CallAnalyzerPage` | **Working** | Speech/transcript scanner. Includes transcript input textarea, "Use sample" pre-fill button, and instantaneous AI threat breakdown displaying scam risk score (94/100), detected fraud flags, and senior-focused guidance. |
| `/sms-analyzer` | `src/routes/sms-analyzer.tsx` | `SmsAnalyzerPage` | **Working** | SMS text scanner. Includes text message input textarea, "Use sample" pre-fill button, and risk assessment card displaying SMS danger score (88/100), detected urgency/OTP patterns, and explanation. |
| `/risk-analysis` | `src/routes/risk-analysis.tsx` | `RiskAnalysisPage` | **Working** | Explainable AI risk fusion page. Features circular risk gauge (92/100 Critical), 6 contributing factor percentage bars, visual mathematical fusion block, and chronological event sequence timeline from initial SMS to family alert. |
| `/family` | `src/routes/family.tsx` | `FamilyPage` | **Working** | Caregiver dashboard for elderly user "Sunita Devi" (Age 68). 4 caregiver metric cards, urgent family alert alert banner with "Call Sunita", "Review Transaction", and "Mark Resolved" buttons, and an emergency contacts roster. |
| `/reports` | `src/routes/reports.tsx` | `ReportsPage` | **Working** | Analytics page featuring timeframe selector, client-side CSV and PDF download actions, and 4 Recharts data visualizations (daily volume, fraud trend, safe vs. suspicious pie chart, scam channel bar chart). |
| `/settings` | `src/routes/settings.tsx` | `SettingsPage` | **Working** | User preferences with 4 cards: Personal Profile, Security settings, Alert Channels, and Accessibility (Senior Mode, High Contrast, Reduced Motion, Voice Assistance). Working "Save preferences" action with visual confirmation. |
| `/about` | `src/routes/about.tsx` | `AboutPage` | **BROKEN** | Academic project background page. **Runtime Bug:** Fails with `ReferenceError: Activity is not defined` because `Activity` icon is referenced on line 37 of `pages.tsx` without being imported from `lucide-react`. |
| `/technology` | `src/routes/technology.tsx` | `TechnologyPage` | **Working** | Technology showcase featuring 9 architectural cards (React, Python, Flask, scikit-learn, Isolation Forest, TF-IDF, Logistic Regression, MongoDB, Twilio) and synthetic prototype disclaimer. |

---

## 5. Existing Components

### 5.1 Application Shell (`src/components/app-shell.tsx`)
- **Desktop Sidebar:** Persistent sidebar on `lg:` viewports featuring application branding, navigation links with active state styling, AI engine online pulsing status indicator, and user profile anchor.
- **Top Navigation Bar:** Sticky top header with mobile hamburger trigger, breadcrumb path indicator, Senior Mode toggle button, Dark/Light mode theme switch, notifications bell with unread indicator badge and drop-down list of recent alerts, and user avatar dropdown menu.
- **Mobile Navigation Bar:** Fixed bottom bar on `< lg:` viewports showing 5 primary navigation tabs with iconography and labels.
- **Mobile Drawer:** Overlay modal drawer for navigation on smaller screens.

### 5.2 Dashboard Widgets (`src/components/dashboard-parts.tsx`)
- **`RiskGauge`:** SVG circular gauge utilizing SVG dash arrays and animated via `motion.circle`. Supports `small` and `large` variants.
- **`KpiGrid`:** 6 animated KPI cards displaying metric values, percentage trends, and color-coded tone icons (Transactions, Safe, Suspicious, High Risk Alerts, Current Risk Score, Scams Detected).
- **`ActivityChart`:** Area chart powered by Recharts with custom SVG linear gradients showing transaction distribution over time.
- **`AlertsList`:** Reusable list component rendering alert cards with severity badges, amounts, details, and action triggers.

### 5.3 Core UI Primitives (`src/components/ui.tsx`)
- **`Button`:** Styled button with variants: `primary`, `secondary`, `danger`, and `ghost`.
- **`Modal`:** Accessible modal dialog with backdrop overlay, smooth Framer Motion entry/exit animations, and focus/escape management.
- **`Card`:** Styled border, rounded corners, and shadow token based container.
- **`RiskBadge`:** Semantic badge for risk levels (`safe`, `review`, `high`, `critical`).
- **`Toggle`:** Accessible animated toggle switch widget for preferences.

### 5.4 Radix UI Library (`src/components/ui/*`)
46 fully implemented components adhering to modern shadcn/Radix conventions (e.g. `accordion`, `alert-dialog`, `avatar`, `badge`, `button`, `calendar`, `card`, `dialog`, `dropdown-menu`, `form`, `input`, `select`, `sidebar`, `table`, `tabs`, `sonner`, etc.). Note: Most application views currently use the lightweight primitives in `ui.tsx` rather than these wrappers.

---

## 6. Existing Services & Architecture Layer

- **Current State:** There is **NO live HTTP service layer** currently communicating with a backend server.
- **API Definition (`src/lib/fraud-data.ts`):**  
  An `api` object exists declaring the planned endpoints:
  ```ts
  export const api = {
    baseUrl: import.meta.env['VITE_API_BASE_URL'] ?? "/api",
    endpoints: {
      transactions: "/transactions",
      alerts: "/alerts",
      analyzeTransaction: "/analyze-transaction",
      analyzeSms: "/analyze-sms",
      analyzeCall: "/analyze-call",
      riskScore: "/risk-score",
      family: "/family",
      reports: "/reports",
    },
  };
  ```
- **TanStack React Query:** Configured at root in `src/routes/__root.tsx` via `QueryClientProvider`, but not yet leveraged by components to fetch or mutate data.
- **Telemetry & Error Services:**
  - `src/lib/error-capture.ts`: Out-of-band exception capture pipeline for SSR.
  - `src/lib/error-page.ts`: HTML template rendered upon fatal unhandled exceptions.
  - `src/lib/lovable-error-reporting.ts`: Error boundary reporting bridge.

---

## 7. Existing Mock Data

| Data Structure | Location | Schema / Content | Centralized? |
| :--- | :--- | :--- | :--- |
| `transactions` | `src/lib/fraud-data.ts` | Array of 24 `Transaction` objects (ID, date, time, payee, amount, location, risk, status, newPayee, upiId, device) | **Yes** (in `fraud-data.ts`) |
| `activityData` | `src/lib/fraud-data.ts` | 8 hourly points (time, normal, suspicious, high) | **Yes** (in `fraud-data.ts`) |
| `reportData` | `src/lib/fraud-data.ts` | 7 daily points (day, volume, risk, calls, sms) | **Yes** (in `fraud-data.ts`) |
| `riskFactors` | `src/lib/fraud-data.ts` | 6 factor tuples: Behavioral Drift, Velocity, Amount, New Payee, Time, Communication | **Yes** (in `fraud-data.ts`) |
| `alerts` | `src/lib/fraud-data.ts` | 3 alert objects (id, level, amount, title, detail, time, risk) | **Yes** (in `fraud-data.ts`) |
| **KPIs** | `src/components/dashboard-parts.tsx` | Array of 6 KPI items with static values and trends | **No** (hardcoded in component) |
| **Elder Profile** | `src/components/pages.tsx` | "Sunita Devi", Age 68, Pune | **No** (hardcoded in component) |
| **Emergency Contacts** | `src/components/pages.tsx` | Rajesh Devi (Son), Kavita Rao (Daughter), Dr. Mehta | **No** (hardcoded in component) |
| **Sample Scam Texts** | `src/components/pages.tsx` | Pre-filled sample text for SMS and phone calls | **No** (hardcoded in component) |
| **Risk Timeline** | `src/components/pages.tsx` | 5 timestamped events between 11:15 PM and 11:44 PM | **No** (hardcoded in component) |
| **Notifications** | `src/components/app-shell.tsx` | 3 sample notifications in header bell | **No** (hardcoded in component) |

---

## 8. Existing Charts

All charts are implemented using **Recharts** and SVG vector graphics:
1. **Circular Risk Score Gauge** (`src/components/dashboard-parts.tsx`):
   - SVG-based circular progress gauge using OKLCH safe/danger colors with animated entry via `motion.circle`.
2. **Transaction Activity Area Chart** (`src/components/dashboard-parts.tsx`):
   - `ResponsiveContainer` wrapping `AreaChart` with gradient fill (`#normal`), Cartesian grid lines, and formatted rupee currency Y-axis (`₹{v/1000}k`).
3. **Daily Transaction Volume Bar Chart** (`src/components/pages.tsx` - `/reports`):
   - `BarChart` plotting synthetic daily volume by day of week.
4. **Fraud Risk Trend Line Chart** (`src/components/pages.tsx` - `/reports`):
   - `LineChart` plotting risk scores with danger stroke color.
5. **Safe vs. Suspicious Donut/Pie Chart** (`src/components/pages.tsx` - `/reports`):
   - `PieChart` with `innerRadius={58}` and `outerRadius={90}`, with color-coded slices for Safe, Review, and High Risk.
6. **Scam Communications Bar Chart** (`src/components/pages.tsx` - `/reports`):
   - Grouped `BarChart` displaying calls vs. SMS volumes over 7 days.

---

## 9. Existing Forms & User Input

1. **Transaction Search & Filter** (`/transactions`):
   - Uncontrolled text input for payee / transaction ID search.
   - `<select>` dropdown for status filtering (`all`, `safe`, `review`, `high`, `critical`).
2. **Analyzer Input Area** (`/call-analyzer` and `/sms-analyzer`):
   - `<textarea>` accepting raw text or conversation transcripts.
   - "Use sample" pre-fill button.
   - "Analyze" submission trigger.
3. **Settings Preferences** (`/settings`):
   - Text input fields for Name, Age, Phone, and Email.
   - 8 toggle switches managing 2FA, login alerts, transaction alerts, scam calls, scam SMS, family notices, Senior Mode, high contrast, reduced motion, and voice assistance.
   - "Save preferences" action button with temporary 2-second success animation.

*Note:* React Hook Form and Zod are installed as project dependencies, but existing forms currently operate using standard React state hooks (`useState`).

---

## 10. Existing Authentication UI

- **Status:** **Missing / Simulated Only**.
- No login (`/login`), registration (`/register`), or authentication gate routes exist.
- In `src/components/app-shell.tsx`, the top-right header features an elder avatar circle ("SD") which toggles a small menu containing "Profile & settings" (`/settings`) and a simulated "Log out demo" link leading back to `/`.
- There is no session token storage, auth context, or protected route wrapper.

---

## 11. Existing Transaction Analyzer UI

- **Status:** **Working (Synthetic UI)**.
- **Route:** `/transactions`.
- **Features:**
  - Filtering by status and real-time substring search.
  - Interactive table displaying 24 transactions with currency formatting, new payee indicator, location, risk score, and status badges.
  - Modal drilldown (`TransactionModal`):
    - Shows 8 transaction metadata fields.
    - Factor breakdown with visual percentage progress bars (Behavioral Drift, Transaction Velocity, Amount Anomaly, New Payee, Unusual Time, Communication Risk).
    - Combined Risk Score badge with plain-language explanation.
    - 4 operational buttons: "Mark as Safe", "Report Fraud", "Contact Family", "Block Payee".
    - Confirmation dialog modal for each action.

---

## 12. Existing Scam-Call / SMS Analyzer UI

- **Status:** **Working (Simulated AI)**.
- **Routes:** `/call-analyzer` and `/sms-analyzer`.
- **Features:**
  - Textarea supporting raw copy-paste with sample prompt insertion.
  - Analyze action triggering the `AnalysisResult` card.
  - Realistic risk metrics:
    - Call Analyzer: Scam Risk 94/100 (Critical).
    - SMS Analyzer: Suspicious Message Detected 88/100 (Critical).
  - Detected pattern checklist (OTP request, Urgency or threat, Account blocking claim, Confidential info request, Impersonation).
  - Clear AI explanation tailored for elderly users and caregivers.
  - Academic disclaimer regarding AI assistance limitations.

---

## 13. Existing Alerts UI

- **Status:** **Working**.
- **Routes:** `/alerts` and `/dashboard`.
- **Features:**
  - Category filter tabs: `all`, `critical`, `high`, `review`.
  - Alert card layout with risk badges, amounts in ₹, title descriptions, relative timestamps, and risk score indicator.
  - "View Details" modal showing alert context, risk breakdown, and "Review transaction" / "Mark resolved" action buttons.
  - Header bell icon with badge and popover listing the 3 most recent warnings.

---

## 14. Existing Caregiver / Family UI

- **Status:** **Working**.
- **Route:** `/family`.
- **Features:**
  - Profile header for elder "Sunita Devi" (Age 68, Pune, Protected Status).
  - 4 Caregiver KPI indicators (Current Risk, Today's Transactions, Active Alerts, Scam Communications).
  - Urgent Family Alert banner displaying suspicious ₹35,000 late-night payment with direct caregiver actions:
    - "Call Sunita"
    - "Review Transaction"
    - "Mark Resolved" (interactively clears active alerts into a confirmed safe empty state).
  - Emergency Contacts list (Rajesh Devi - Son, Kavita Rao - Daughter, Dr. Mehta - Doctor) with direct call trigger icons and "Add contact" action.

---

## 15. Existing Settings UI

- **Status:** **Working**.
- **Route:** `/settings`.
- **Features:**
  - **Profile Information:** Editable fields for Name, Age, Phone, and Email.
  - **Security Settings:** 2FA toggle, login activity alert toggle, change password action.
  - **Alert Preferences:** Granular switches for High-risk transaction alerts, Scam call alerts, Scam SMS alerts, and Family notifications.
  - **Accessibility Settings:**
    - **Senior Mode:** Directly modifies `AppContext`, toggling the `.senior` CSS class on `document.documentElement` to increase font sizing to 112% and enforce 48px minimum touch target heights.
    - **Reduced Motion:** Toggles `.reduce-motion` CSS class to suppress animations.
    - High contrast and Voice assistance switches.
  - Working "Save preferences" action button with confirmation state.

---

## 16. Current Build & Error Audit

### 16.1 Production Build (`npm run build` / `vite build`)
- **Status:** **PASSED (Exit Code: 0)**.
- Bundler completes client environment build, SSR server build, and Nitro output generation (`.output/public` and `.output/server`) without build-breaking syntax errors.

### 16.2 Static Type Checking (`npx tsc --noEmit`)
- **Status:** **FAILED (Exit Code: 1, 8 Errors)**.
- **Specific Errors:**
  1. `src/components/pages.tsx:37`: `Cannot find name 'Activity'`.
     - *Cause:* Icon used in `AboutPage` feature blocks is missing from `lucide-react` imports.
  2. `src/components/pages.tsx:25`: `error TS2604 / TS2786 / TS2322`:
     - *Cause:* Timeline icon tuple in `RiskAnalysisPage` is inferred loosely without `as const`, causing JSX element signature mismatch.
  3. `src/lib/fraud-data.ts:21 & 33`: `error TS2322 & TS18048`:
     - *Cause:* Array indexing under strict `noUncheckedIndexedAccess: true` infers `string | undefined` and `number | undefined`.
  4. `src/lib/fraud-data.ts:73`: `error TS4111`:
     - *Cause:* `import.meta.env.VITE_API_BASE_URL` violated `noPropertyAccessFromIndexSignature: true`. Must be accessed as `import.meta.env['VITE_API_BASE_URL']`.

### 16.3 Runtime & SSR Execution
- **Status:** **11 Routes Passed / 1 Route Failed**.
- **The Bug:** Visiting `/about` triggers `ReferenceError: Activity is not defined` inside `AboutPage`, causing SSR to fail and the server to fall back to client rendering error boundary.
- **All other 11 routes** (`/`, `/dashboard`, `/transactions`, `/alerts`, `/call-analyzer`, `/sms-analyzer`, `/risk-analysis`, `/family`, `/reports`, `/settings`, `/technology`) render HTTP 200 with complete SSR payloads.

### 16.4 Linter & Formatter (`npm run lint`)
- **Status:** 7 Fast Refresh warnings in UI wrappers, and 99 Prettier formatting errors due to generated one-line JSX blocks.

---

## 17. Missing Functionality (Gap Analysis)

1. **Brand Consistency:** The application is internally labeled "FraudShield" across metadata, landing page, sidebar, and headers, whereas the project name is **UPI Guardian**.
2. **Dedicated Service / API Layer:** No centralized `src/services/` directory exists. All components consume static arrays from `fraud-data.ts` or local state.
3. **TanStack Query Hooks:** React Query is mounted, but custom hooks (e.g. `useTransactions`, `useAnalyzeText`, `useAlerts`, `useRiskScore`) have not been written.
4. **Interactive Analyzer Backend:** The Call and SMS analyzers currently display fixed static scores (94 and 88) regardless of input text.
5. **Real Authentication & Protected Routes:** No user authentication flow (login, token management, caregiver login vs. senior login).
6. **Dynamic Timeline & Live Risk Fusion:** The timeline and fusion math on `/risk-analysis` are static constants.
7. **Form Validation Schemas:** Settings and input forms lack Zod schema validation.

---

## 18. Where the Future Flask REST API Should Connect

When the Python/Flask backend is introduced, the frontend architecture should connect seamlessly through a dedicated service layer without disturbing existing UI components:

```text
src/
├── services/                          <-- [NEW SERVICE LAYER]
│   ├── api-client.ts                  <-- Axios or fetch wrapper with baseURL, interceptors, auth headers
│   ├── transaction-service.ts         <-- GET /api/transactions, POST /api/transactions/analyze
│   ├── analyzer-service.ts            <-- POST /api/analyze-sms, POST /api/analyze-call (NLP / ML models)
│   ├── risk-service.ts                <-- GET /api/risk-score, GET /api/risk-timeline (Isolation Forest)
│   ├── alert-service.ts               <-- GET /api/alerts, PATCH /api/alerts/:id/resolve (Twilio notifications)
│   └── family-service.ts              <-- GET /api/family/profile, POST /api/family/contacts
└── hooks/                             <-- [QUERY HOOKS LAYER]
    ├── use-transactions.ts            <-- useQuery(['transactions']), useMutation(...)
    ├── use-analyzers.ts               <-- useMutation(['analyze-call']), useMutation(['analyze-sms'])
    └── use-alerts.ts                  <-- useQuery(['alerts']), useMutation(...)
```

The components in `src/components/pages.tsx` will simply swap their direct imports of static arrays (`transactions`, `alerts`) with these React Query hooks.

---

## 19. What Must Be Preserved (Do Not Touch)

1. **Design System & Styling (`src/styles.css`):**  
   The bespoke OKLCH color palette (safe, warning, danger, info, ai, sidebar tokens), custom utilities (`.protection-banner`, `.data-table`, `.fusion-node`, `.timeline`), and responsive grid structures.
2. **Accessibility Features:**  
   The `.senior` mode font-scaling and enlarged click targets, and `.reduce-motion` transitions managed via `AppContext`.
3. **Core Shell & Navigation (`src/components/app-shell.tsx`):**  
   The desktop sidebar, responsive top header, mobile drawer, and bottom navigation bar.
4. **All 12 Active Routes (`src/routes/*`):**  
   Preserve file routes and TanStack Router routing conventions.
5. **UI Widgets & Data Visualizations:**  
   `RiskGauge`, `ActivityChart`, `KpiGrid`, `AlertsList`, and Recharts graphs in `ReportsPage`.
6. **Data Models:**  
   The `Transaction` and `RiskLevel` TypeScript definitions in `src/lib/fraud-data.ts`.

---

## 20. Recommended Next Implementation Step

**Phase 1 — Frontend Consolidation & Bug Resolution (Immediate):**
1. Fix the runtime bug in `src/components/pages.tsx` by importing `Activity` from `lucide-react`.
2. Fix the 8 strict TypeScript errors in `src/components/pages.tsx` and `src/lib/fraud-data.ts` to ensure `tsc --noEmit` exits with code 0.
3. Update brand labels from "FraudShield" to "UPI Guardian" across page headers, metadata, landing page, and sidebar while maintaining all styling.
4. Separate `src/components/pages.tsx` into individual modular page files (e.g., `src/pages/DashboardPage.tsx`, `src/pages/TransactionsPage.tsx`, etc.) to improve maintainability before connecting API queries.
5. Introduce a clean mock-ready service layer (`src/services/`) that powers existing pages with TanStack React Query, ensuring 100% plug-and-play compatibility when the Flask backend arrives in Phase 2.

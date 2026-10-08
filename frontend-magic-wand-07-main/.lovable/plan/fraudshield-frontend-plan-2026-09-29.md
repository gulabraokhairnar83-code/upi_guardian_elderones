# FraudShield Frontend Plan

## Goal
Build a complete, polished cybersecurity and financial-safety product for elderly users and their caregivers. The app will use realistic synthetic data, clear risk explanations, accessible controls, and responsive layouts suitable for a college demonstration and portfolio.

## Product structure
- Public home page introducing FraudShield, its five-step workflow, three-layer protection model, demo disclaimer, and dashboard entry.
- Shared application shell with desktop sidebar, compact tablet navigation, mobile menu, top bar, breadcrumbs, notification panel, profile menu, Demo Mode label, and AI/backend status indicators.
- Separate working pages for Dashboard, Transactions, Fraud Alerts, Scam Call Analyzer, SMS Analyzer, Risk Analysis, Family Safety Center, Reports, Settings, About, and Technology.
- Purpose-built not-found, empty, loading, and error states.

## Core experiences
- Dashboard with protection status, six KPI summaries, time-range filters, Recharts transaction activity, animated risk gauge, and recent alert actions.
- Searchable/filterable transaction table with 20+ realistic records and a detailed transaction modal containing signals, explanation, and confirmation-protected actions.
- Fraud alert review with severity filters and reusable alert details.
- Call and SMS analyzers that accept pasted text, produce mock AI-assisted risk results, identify scam patterns, highlight suspicious phrases, and clearly state limitations.
- Explainable risk page with score visualization, contributing factors, risk-fusion model, and a communication-to-transaction event timeline.
- Caregiver dashboard with Sunita Devi’s status, family alerts, emergency contacts, and functional call/review/resolve actions.
- Reports with date filters, multiple Recharts visualizations, and functional CSV/PDF-style download controls.
- Settings with editable profile/security, alert, risk, accessibility, notification, and privacy controls.

## Design and accessibility
- Premium light-first navy security aesthetic with white surfaces, restrained blue, green, amber, red, and subtle AI purple accents.
- Inter body text, Poppins headings, and JetBrains Mono for scores and IDs, loaded through the document head.
- Large readable type, strong contrast, icon-plus-text statuses, generous touch targets, keyboard focus states, and confirmation dialogs for risky actions.
- Working light/dark theme and Senior Mode; Senior Mode enlarges controls and simplifies the dashboard while preserving essential safety information.
- Subtle transitions and chart/gauge motion, disabled when reduced-motion is selected or requested by the device.

## Technical implementation
- Preserve TanStack Start routing while implementing the requested React/Vite/Tailwind experience; each major page gets its own route and unique metadata.
- Add reusable UI and domain components, centralized mock data, shared application state, and an API service configured through `VITE_API_BASE_URL` for future Flask endpoints.
- Use Lucide icons and Recharts; keep all security colors, typography, elevations, and motion values in semantic design tokens.
- Keep all data synthetic and label the product as an academic prototype without bank integration or guaranteed fraud detection claims.

## Validation
- Verify navigation, filters, analyzers, dialogs, settings, theme, Senior Mode, and report downloads in the running preview.
- Check desktop and mobile layouts for clipping, readability, table usability, and interaction feedback.
- Confirm the latest preview build has no errors and every content route has complete metadata.

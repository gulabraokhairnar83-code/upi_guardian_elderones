# UPI Guardian — Evaluator Demo Checklist & Screenshot Guide

**Document Purpose**: Guided checklist for academic evaluators, viva presentations, and project video walkthroughs.  
**Demonstration Routes**: Covers all 14 primary screens and interactive flows.  

---

## Screen & Flow Capture Checklist

| # | Screen / Feature | Route / Action | Key Elements to Verify | Screenshot Target |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Landing / Intro** | `/` | System overview, multi-signal shield scene, feature highlights, and navigation links. | `01_landing_page.png` |
| **2** | **Sign In / Registration** | `/login` | Email/password fields, role selection (`Elder` / `Caregiver`), clean validation errors, password security. | `02_auth_login.png` |
| **3** | **Main Dashboard** | `/dashboard` | System status banner (AI Engine Online), active risk gauge, recent transaction timeline, KPI cards. | `03_dashboard_overview.png` |
| **4** | **Senior Mode View** | Any route + click `Senior Mode` pill | Enlarged typography ($112\%$), high-contrast text, minimum 48px touch targets, simplified advisory banners. | `04_senior_mode_dashboard.png` |
| **5** | **Transaction History** | `/transactions` | Payee details, amount formatted in INR (₹), risk status badges (`✓ Safe`, `⚠ Please Review`, `! High Risk`). | `05_transactions_table.png` |
| **6** | **SMS Scam Analyzer** | `/sms-analyzer` | Text input box, quick sample message injection (KYC Scam / Utility Bill), TF-IDF probability score, keyword badges. | `06_sms_analyzer_active.png` |
| **7** | **Call Transcript Analyzer**| `/call-analyzer` | Simulated voice transcript input, urgency indicators, social engineering detection keywords. | `07_call_analyzer_screen.png` |
| **8** | **Risk Fusion Studio** | `/risk-analysis` | Cross-signal correlation simulator, multi-signal radar/bar chart, temporal window toggle (+10 boost indicator). | `08_risk_fusion_engine.png` |
| **9** | **Critical Risk Alert Overlay** | Trigger Scenario 4 (`CRITICAL`) | High-visibility warning modal ("✕ Possible Scam"), explicit action recommendation ("STOP: Verify with Rohit"). | `09_critical_alert_modal.png` |
| **10** | **Caregiver Management** | `/family` | Nominated family caregivers, relationship tags (`Son`, `Daughter`), active channels, add caregiver dialog. | `10_caregiver_directory.png` |
| **11** | **Emergency Dispatch & Telemetry** | `/alerts` or Header Bell Drawer | Dispatched mock SMS and Voice call records, channel indicators, delivery status timestamps. | `11_notification_telemetry.png` |
| **12** | **Caregiver Acknowledgement** | Click `Acknowledge Alert` button | Status transitions to `ACKNOWLEDGED`, caregiver verification timestamp displayed, alert dismissed. | `12_alert_acknowledgement.png` |
| **13** | **Reports & Behavioral Analytics**| `/reports` | Weekly risk score trends, merchant distribution breakdown, category spending breakdown charts. | `13_analytics_reports.png` |
| **14** | **Settings & Preferences** | `/settings` | Profile preferences, notification quiet hours configuration (10 PM - 7 AM), accessibility contrast toggles. | `14_user_settings.png` |

---

## Demonstration Execution Best Practices

1. **Synthetic Data Only**: Always demonstrate using pre-seeded synthetic identities (`Sunita Devi` and `Rohit Sharma`).
2. **Never Display Backend Credentials**: Ensure server terminal outputs, browser developer consoles, and screen recordings do not display `.env` files or API connection strings.
3. **Showcase Senior Mode Early**: Emphasize how the interface adapts to senior citizen visual requirements with a single click on the header toggle.
4. **Demonstrate Cross-Signal Fusion**: Show how an SMS scam analysis immediately boosts the risk score of a subsequent high-value transaction from Medium to Critical.
5. **Demonstrate Idempotency**: Re-submit an identical critical transaction to prove that duplicate SMS/Voice alerts are automatically suppressed.

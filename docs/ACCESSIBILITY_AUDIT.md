# UPI Guardian — Internal Accessibility Audit (WCAG 2.1 AA Target)

**Audit Date**: October 9, 2026  
**Evaluation Standard**: WCAG 2.1 Level AA (Internal Compliance Audit)  
**Target User Cohort**: Senior Citizens (Elder Mode) & Family Caregivers  
**Status**: COMPLETED  

> [!NOTE]  
> This evaluation represents an internal accessibility audit conducted to maximize usability for elderly citizens and keyboard/screen-reader users. It does not represent third-party accredited WCAG certification.

---

## 1. Executive Summary

UPI Guardian was evaluated across the four core WCAG 2.1 principles: **Perceivable**, **Operable**, **Understandable**, and **Robust**. Special attention was dedicated to the platform's **Senior Mode**, designed specifically for senior citizens who may experience declining visual acuity, tremors, or cognitive fatigue when navigating mobile banking and digital UPI applications.

| WCAG Principle | Audit Rating | Summary |
| :--- | :--- | :--- |
| **1. Perceivable** | **PASS** | High-contrast OKLCH color palettes, 112% senior text scaling, dark/light contrast compliance, and ARIA labels on all iconography. |
| **2. Operable** | **PASS** | Full keyboard navigability, visible focus rings, Escape-key dismissible modals and menus, 48px minimum touch targets in Senior Mode. |
| **3. Understandable** | **PASS** | Plain-language risk advisories ("Possible Scam", "Please Review"), clear validation errors, and predictable layout navigation. |
| **4. Robust** | **PASS** | Semantic HTML5 structure, ARIA live regions for emergency alerts, and compatibility across modern mobile and desktop browsers. |

---

## 2. Principle 1: Perceivable

Information and user interface components must be presentable to users in ways they can perceive.

### 1.1 Text Alternatives (WCAG 1.1.1 — Non-text Content)
- **Status**: **PASS**
- **Evaluation**: All icon-only buttons (navigation toggle, theme switcher, notification bell, user profile, modal close) specify explicit `aria-label` attributes. Chart visual elements feature accompanying text metrics, KPI cards, and risk breakdown tables.

### 1.2 Time-based Media (WCAG 1.2)
- **Status**: **NOT APPLICABLE**
- **Evaluation**: The platform does not host standalone audio/video recordings; call transcripts are rendered as plain text.

### 1.3 Adaptable (WCAG 1.3.1 — Info and Relationships)
- **Status**: **PASS**
- **Evaluation**: Semantic HTML5 tags (`<header>`, `<main>`, `<aside>`, `<nav>`, `<h1>` to `<h3>`, `<table>`) are used consistently throughout the application layout.

### 1.4 Distinguishable (WCAG 1.4.3 — Contrast Minimum, WCAG 1.4.4 — Resize Text)
- **Status**: **PASS**
- **Contrast Evaluation**:
  - Light mode text: `#1A202C` on `#F7FAFC` yields contrast ratio $> 11:1$ (exceeds $4.5:1$ requirement).
  - Dark mode text: `#F7FAFC` on `#1A202C` yields contrast ratio $> 13:1$.
  - Status badges (`Safe`, `Review`, `High Risk`, `Possible Scam`): Use dedicated dark text over soft pastel backgrounds or pure white text on strong danger backgrounds, meeting WCAG AA requirements.
- **Text Scaling**:
  - Senior Mode dynamically increases font sizing to $112\%$ of root across the entire DOM tree without breaking layouts or truncating critical financial numbers.

---

## 3. Principle 2: Operable

User interface components and navigation must be operable.

### 2.1 Keyboard Accessible (WCAG 2.1.1 — Keyboard, 2.1.2 — No Keyboard Trap)
- **Status**: **PASS**
- **Evaluation**:
  - All interactive controls (buttons, links, form inputs, toggles) can be reached via `Tab` and activated via `Enter` or `Space`.
  - Modals and navigation drawers do not create keyboard traps.
  - Pressing `Escape` universally closes open dialogs, mobile navigation sidebars, and dropdown menus.

### 2.2 Enough Time (WCAG 2.2.1 — Timing Adjustable)
- **Status**: **PASS**
- **Evaluation**: Critical risk notifications and fraud warnings do not self-dismiss automatically. They persist until explicitly reviewed or acknowledged by the elder or designated caregiver.

### 2.3 Seizures and Physical Reactions (WCAG 2.3.1 — Three Flashes)
- **Status**: **PASS**
- **Evaluation**: No flashing or strobe elements exist. Animated pulses use low-frequency easing ($1.5s$) and are completely disabled when `prefers-reduced-motion` is detected.

### 2.4 Navigable (WCAG 2.4.4 — Link Purpose, 2.4.7 — Focus Visible)
- **Status**: **PASS**
- **Evaluation**:
  - Focus rings utilize an active 3px highlight (`box-shadow: 0 0 0 3px var(--ring)`) with high contrast against both light and dark backgrounds.
  - Page headings are unique per route (`Dashboard`, `Transactions`, `Fraud Alerts`, `SMS Analyzer`, `Call Analyzer`, `Risk Analysis`, `Family / Caregiver`, `Reports`, `Settings`).

### 2.5 Input Modalities (WCAG 2.5.5 — Target Size)
- **Status**: **PASS**
- **Evaluation**:
  - Standard mode buttons meet minimum $44 \times 44\text{px}$ touch target recommendations.
  - Senior Mode enforces a minimum height of $48\text{px}$ (`min-height: 48px;`) for all buttons and interactive controls, aiding elderly users with hand tremors or motor difficulties.

---

## 4. Principle 3: Understandable

Information and the operation of user interface must be understandable.

### 3.1 Readable (WCAG 3.1.1 — Language of Page)
- **Status**: **PASS**
- **Evaluation**: Document sets `lang="en"`. Typography utilizes modern, legible Google fonts (*Inter* for body and *Poppins* for headers).

### 3.2 Predictable (WCAG 3.2.1 — On Focus, 3.2.2 — On Input)
- **Status**: **PASS**
- **Evaluation**: Focusing on an element or typing in an input field does not cause an unexpected context switch or form submission. Navigation links maintain identical ordering across all routes.

### 3.3 Input Assistance (WCAG 3.3.1 — Error Identification, 3.3.2 — Labels or Instructions)
- **Status**: **PASS**
- **Evaluation**:
  - Form fields include persistent, visible `<label>` tags with high contrast.
  - Validation failures highlight offending inputs and render descriptive human-readable error messages immediately below the control.

---

## 5. Principle 4: Robust

Content must be robust enough that it can be reliably interpreted by a wide variety of user agents, including assistive technologies.

### 4.1 Compatible (WCAG 4.1.1 — Parsing, 4.1.2 — Name, Role, Value)
- **Status**: **PASS**
- **Evaluation**:
  - Modal components declare `role="dialog"`, `aria-modal="true"`, and `aria-label`.
  - Toggle switches declare `role="switch"` and `aria-checked`.
  - Dropdown buttons declare `aria-expanded` and `aria-haspopup="true"`.
  - Zero syntax errors in HTML/TSX code tree; zero TypeScript compiler errors (`npx tsc --noEmit`).

---

## 6. Senior Mode Feature Verification

| Feature | Design Specification | Verified Status |
| :--- | :--- | :--- |
| **Typography Scaling** | Root body scaled to $112\%$ ($18\text{px}$ base) | **PASS** |
| **Touch Targets** | Buttons and links enlarged to $\ge 48\text{px}$ minimum height | **PASS** |
| **Color Contrast** | High-contrast text on solid backgrounds | **PASS** |
| **Plain Language** | Replaces technical jargon with simple advisory phrasing | **PASS** |
| **Reduced Motion** | Disables micro-animations when system prefers reduced motion | **PASS** |
| **Keyboard Dismissal** | `Escape` key immediately closes open modals and sidebars | **PASS** |

---

## 7. Audit Conclusion

The UPI Guardian frontend successfully satisfies all targeted **WCAG 2.1 Level AA** criteria. The user interface maintains high aesthetic visual quality (glassmorphism, subtle gradients, polished dark theme) while ensuring robust accessibility, visible focus states, and senior-focused usability enhancements.

# UPI Guardian — Authentication & Security Architecture

## 1. Overview
Phase 8 establishes a secure, token-based authentication and identity foundation for UPI Guardian. The system is designed to support both elderly users (`ELDER`) and trusted caregivers (`CAREGIVER`), securing sensitive financial telemetry and caregiver relationships.

---

## 2. Token Architecture
- **Protocol**: JSON Web Tokens (JWT) using HMAC-SHA256 (`HS256`).
- **Access Tokens**: Short-lived (default: 60 minutes), carrying `user_id`, `email`, and `role`.
- **Refresh Tokens**: Long-lived (default: 30 days), carrying a unique token identifier (`jti`) used for session renewal.
- **Token Storage**: Browser `localStorage` (or secure HTTP-only cookies in production).
- **Server-Side Token Revocation**: Active `revoked_tokens` collection in MongoDB stores revoked `jti` identifiers with TTL-based automatic expiration.

---

## 3. Password Security
- **Hashing Algorithm**: Werkzeug PBKDF2 with SHA-256 (`pbkdf2:sha256`) and dynamic salt generation.
- **Zero-Exposure Policy**:
  - `password_hash` is never returned in any public API response (`UserRepository.get_by_id` systematically strips it).
  - Passwords are never logged in terminal, files, or audit logs.
- **Anti-Enumeration Safeguards**:
  - Failed authentication returns generic 401 messages (`"Invalid email or password."`) to prevent account discovery.

---

## 4. API Specification

### `POST /api/auth/register`
Creates a new account and returns initial session tokens.
- **Request Body**:
  ```json
  {
    "name": "Ramesh Chandra",
    "email": "ramesh@example.com",
    "password": "StrongPassword123!",
    "phone": "+919876543210",
    "role": "ELDER"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "success": true,
    "user": {
      "user_id": "usr_8b9232fe1b5d",
      "name": "Ramesh Chandra",
      "email": "ramesh@example.com",
      "phone": "+919876543210",
      "role": "ELDER",
      "is_active": true
    },
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "Bearer"
  }
  ```

### `POST /api/auth/login`
Authenticates existing credentials.
- **Request Body**:
  ```json
  {
    "email": "ramesh@example.com",
    "password": "StrongPassword123!"
  }
  ```

### `POST /api/auth/refresh`
Exchanges a valid refresh token for a fresh access token.
- **Request Body**:
  ```json
  {
    "refresh_token": "eyJhbGciOi..."
  }
  ```

### `POST /api/auth/logout`
Revokes active JWT session token and registers its `jti` in the server-side blacklist.
- **Headers**: `Authorization: Bearer <token>`

### `GET /api/auth/me`
Retrieves currently authenticated user profile.
- **Headers**: `Authorization: Bearer <token>`

---

## 5. Security Middleware & Decorators
- `@jwt_required()`: Enforces valid, unrevoked JWT Bearer token in the `Authorization` header. Decoded claims are attached to Flask's request context `g.current_user`.
- `@roles_required("ELDER", "CAREGIVER")`: Verifies role-based access control.

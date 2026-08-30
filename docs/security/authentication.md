# Authentication & Access Control Architecture

This document details the security standards, password handling policies, JWT token specifications, and Role-Based Access Control (RBAC) rules implemented in VertiCare AI.

---

## 1. Password Security Policies

- **Hashing Algorithm:** Salted `bcrypt` with work factor 12.
- **Length Constraint:** Minimum 8 characters; passwords are truncated to 72 bytes prior to hashing per bcrypt specifications to avoid library wrap issues.
- **Privacy Invariants:**
  - Plaintext passwords are never logged, stored in cache, or returned in API responses.
  - Password hashes are excluded from all serialized Pydantic responses (`UserResponse`).

---

## 2. JWT Access Token Flow

```
[ Client: /auth/login ] ──(Credentials)──> [ Server: Verify Hash ]
                                                   │
                                                   ▼
[ Client: Bearer Token in Header ] <──(JWT Token)── [ Server: Sign JWT with SECRET_KEY ]
              │
              ▼
[ Protected Endpoint Request ] ────> [ FastAPI Dependency: verify_token() ]
                                                   │
                                                   ▼
                                     [ Authenticated User + Role Check ]
```

### JWT Claims Specification
```json
{
  "sub": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "role": "PATIENT",
  "email": "user@verticare.org",
  "exp": 1756598400,
  "iat": 1756512000,
  "type": "access"
}
```
*Note: Tokens never carry passwords or sensitive medical records.*

---

## 3. Role-Based Access Control (RBAC)

Two distinct roles are enforced across backend dependencies and frontend route guards:

| Role | Permitted Actions | Restricted Actions |
| :--- | :--- | :--- |
| `PATIENT` | Authenticate, view `/patient/dashboard`, manage own profile | Access `/doctor/dashboard`, query clinical reviews |
| `DOCTOR` | Authenticate, view `/doctor/dashboard`, access assigned dossiers | Access patient-only logging forms where restricted |

---

## 4. Database Transaction Safety

Registration workflows are atomic:
1. Create `User` record with hashed password.
2. Create corresponding `PatientProfile` or `DoctorProfile`.
3. Flush and commit in a single database transaction.
4. If profile creation raises any error, the transaction rolls back completely to prevent orphaned user records.


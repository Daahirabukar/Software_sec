# STRIDE threat model

Assets: account hashes and local secrets; private notes; report input/output; service authorities; source/helper/dependencies; test and CI evidence.

| STRIDE | Threat and boundary | Implemented control | Verification |
|---|---|---|---|
| Spoofing | Fake user/session or forged service identity at TB1–TB3 | Argon2id login; random opaque sessions; per-service HMAC grants with audience, caller and expiry | Login/session and invalid/malformed/wrong-audience/expired-authority tests |
| Tampering | Change owner, note UUID, report selection or input at TB1–TB3 | Owner is derived from verified grant; exact note scope; report input digest; bounded Pydantic schemas; SQL parameters | Owner field ignored/not accepted; scope, digest, bounds tests |
| Repudiation | Deny action or leak secrets through logs | No credential, token or note-content logging is added; synthetic local data | Review emitted application output during process test |
| Information disclosure | Alice reads Bob's note or report across TB1–TB3 | Notes checks ID and owner on every read; API fetches each report note through Notes; no shared report cache | Bidirectional note tests and report workflow isolation |
| Denial of service | Oversized notes or repeated login consume resources | Note/title/report input bounds; synchronous local service calls with request timeout | Boundary tests; rate limiting remains a future limitation |
| Elevation of privilege | Ordinary user disables accounts; Admin accesses private content | API checks explicit role; Admin note/report routes denied; Notes still enforces owners | User/Admin authorization tests |

## Trust assumptions and limitations

API is authoritative for user identity and roles; Notes is authoritative for note ownership. Each internal HMAC key is configured only on API and its destination service. The current implementation is for synthetic local use: service sessions and accounts are simple, local HTTP is not encrypted, and no deployment isolation or rate limiting exists yet. Production use needs authenticated TLS, managed/rotated secrets, abuse controls, backups and operational monitoring.

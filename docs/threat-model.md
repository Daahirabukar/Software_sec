# STRIDE threat model

Assets: account credentials/hashes and signing keys; private notes; report input/output; service authorities; source/helper/dependencies; test and CI evidence.

| STRIDE | Threat and boundary | Planned control | Verification |
|---|---|---|---|
| Spoofing | Stolen/fake user token or forged service identity at TB1–TB4 | Argon2id login, signed short-lived tokens, separate service keys, audience/caller checks | Invalid, expired, wrong-key and wrong-audience tests |
| Tampering | User changes owner, ID, title/search input, or report selection at TB1/TB2 | Strict schemas, immutable owner, parameterized SQL, exact scopes | Owner-field, SQL-payload, and input-boundary tests |
| Repudiation | User denies an action or logs omit useful results | Minimal structured outcome logging; never log passwords, bearer tokens, or note content | Review logs and assert synthetic secrets are absent |
| Information disclosure | Alice reads Bob's note or receives his report through service composition at TB1–TB4 | Notes owner check on every read; report reads only forwarded scoped notes; no cross-user cache | Bidirectional IDOR and cache-composition probes |
| Denial of service | Oversized input or repeated login consumes resources | Bounded inputs, simple login throttling, small synchronous report cap and request limits | Boundary, throttling/recovery, and invalid-input tests |
| Elevation of privilege | Ordinary user invokes Admin operation; Admin uses role to read private content | Explicit role check; Admin disable permission is narrow and never bypasses note ownership | Alice/Bob denied; Admin can disable an ordinary account but cannot read notes or disable Admin |

## Trust assumptions

API is authoritative for user identity and roles; Notes is authoritative for note ownership. Service keys are secret and protected; local ports are restricted to the test host. The Report Service and helper receive only data covered by the specific request. Production deployment would additionally require TLS, secret/key rotation, hardened hosts, monitoring, backups, and operational review.

# Initial SSDLC plan

Initial plan committed before feature implementation (`0aa087c`). Updated as implementation proceeds. Required traceability: **Asset → threat → requirement/control → lifecycle activity → test/evidence → gate decision.**

## Lifecycle phases and gates

| Phase | Activities | Gate |
|---|---|---|
| Requirements | Confirm scope, functions, three process boundaries, assets, data flow, roles, STRIDE, access matrix, catalog selections | G1: planning committed before implementation; service grants bind subject, service, resource, action and expiry |
| Implementation and build | Three FastAPI processes, service-owned SQLite, installable helper, authentication, authorization, reproducible install | G2: clean install succeeds; no embedded credentials or cross-service database access |
| Testing | Run functional, authorization, real-process integration, and four isolated vulnerable/fixed experiments; retain sanitized evidence | G3: required tests pass; each planted weakness is reproducible before mitigation and denied after; scanners/gates pass |
| Release, deployment, operation | Review configuration, key handling, backups, logs, recovery, Jenkins, report and remaining production needs | G4: tested source and evidence match; no unresolved required security failure; limitations stated |

## Assets and traceability

| Asset → threat | Requirement/control | Lifecycle activity | Test/evidence | Gate decision |
|---|---|---|---|---|
| User accounts → spoofing/elevation | Argon2id passwords; opaque 15-minute session; explicit roles and active-status checks | API authentication and Admin operation | Login, expiry, disabled-account, and role tests passed | Block invalid authentication or ordinary-user Admin action |
| Private notes → disclosure/tampering | Notes owns data; server-side owner filter; parameterized queries | Notes routes and Pydantic input validation | Alice/Bob isolation and input-bound tests passed; SQL experiment pending | Block any cross-user access or mutation |
| Service authority → confused deputy | Bind subject, service, action, exact resource/input digest, audience and validity | HMAC grant verification at Notes and Report | Wrong-scope/audience/expiry tests and real-process flow pass; composition experiment pending | Block invalid or out-of-scope processing |
| Report output → disclosure | API fetches Notes-authorized selection; helper is separately installed | Report validates bound input before formatting | End-to-end report and identity/digest tests pass | Block cross-user or changed input |
| Build/dependencies → compromised code | Reproducible dependency list; static and dependency analysis | Jenkins build and scanning | Scanner outputs and dependency manifest | Block scanner failure, unapproved dependency, or defined advisory |
| Evidence → unverifiable claims | Preserve sanitized tests/scans/experiment results; no secrets in artifacts | Test/review/report | JUnit, scanner JSON, experiment diffs and outcome records | Block missing evidence or secret leakage |

## Initial security gates

Fail on build/install errors, unexpected dependencies, secret leakage, unresolved high/critical dependency findings, unreviewed static findings, test failures, cross-user access, invalid authority accepted, missing experiment evidence, or artifact/log exposure. Scanner unavailability blocks the gate. Confirmed unauthorized access and credential exposure are never waived.

Optional malicious-package/hash experiments are outside the mandatory baseline. Jenkins, four vulnerability experiments, scanner gates, and the academic report remain incomplete. The separate Overleaf report will include a truthful AI-use declaration.

# Initial SSDLC plan

Prepared before application features. Required traceability: **Asset → threat → requirement/control → lifecycle activity → test/evidence → gate decision.**

## Lifecycle phases and gates

| Phase | Activities | Gate |
|---|---|---|
| Requirements | Confirm scope, functions, three process boundaries, assets, data flow, roles, STRIDE, access matrix, catalog selections | G1: review planning documents and bind authority to subject, service, resource, action, and expiry before coding |
| Implementation and build | Implement the three independent FastAPI processes, separate SQLite ownership, helper package dependency, auth/authorization, and reproducible install | G2: clean install/build succeeds; no unlisted dependency, embedded secret, or direct cross-service database access |
| Testing | Run functional, authorization, process-integration, and four isolated vulnerable/fixed experiments; retain sanitized evidence | G3: required tests pass; each planted weakness is reproducible before mitigation and denied after; scanners/gates pass |
| Release, deployment, operation | Review release configuration, key handling/rotation, backups, logs, recovery, and rollback; document production needs | G4: report and artifacts match tested source; no unresolved required security failure; production-only gaps stated |

## Assets and traceability

| Asset → threat | Requirement/control | Lifecycle activity | Test/evidence | Gate decision |
|---|---|---|---|---|
| User accounts → spoofing/elevation | Argon2id passwords; signed expiry-bound user token; explicit roles | Implement login and Admin disable | Login, expiry, disabled-account, and role tests | Block invalid authentication or ordinary-user Admin action |
| Private notes → disclosure/tampering | Notes owns data; server-side owner filter; parameterized queries | Implement Notes routes and validate input | Alice/Bob read isolation, owner-field and SQL tests | Block any cross-user access or mutation |
| Service authority → confused deputy/replay | Bind subject, service, action, resource, audience, and validity; Report cannot widen Notes grants | Implement and review HTTP boundaries | Wrong-scope/audience/expiry tests and three-process workflow | Block authority expansion or out-of-scope processing |
| Report output → disclosure | Report uses only Notes-authorized selection; helper is an installed dependency | Build/report workflow | All-three-service test and report-content assertions | Block cross-user or unselected content |
| Build/dependencies → compromised code | Reproducible dependency list; static and dependency analysis | Jenkins build and scanning | Scanner outputs and dependency manifest | Block scanner failure, unapproved dependency, or defined advisory |
| Evidence → unverifiable claims | Preserve sanitized tests/scans/experiment results; no secrets in artifacts | Test/review/report | JUnit, scanner JSON, experiment diffs and outcome records | Block missing evidence or secret leakage |

## Initial security gates

Fail on build/install errors, unexpected dependencies, secret leakage, unresolved high/critical dependency findings, unreviewed static findings, test failures, cross-user access, invalid authority accepted, missing experiment evidence, or artifact/log exposure. Scanner unavailability blocks the gate. Confirmed unauthorized access and credential exposure are never waived.

Optional malicious-package/hash experiments are outside the mandatory baseline. The academic report is maintained separately in Overleaf and will include a truthful AI-use declaration.

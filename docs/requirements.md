# Requirements checklist

Source: local Software Security Assignment I (6 pages; SHA-256 efb4f3462df8cabae6a92057366f57b53e9ba2e8f52d08099fb967848696eb85). This file records mandatory requirements only; optional supply-chain experiments are excluded from the baseline.

## Functional scope

- [x] Login seeded users Alice and Bob; include privileged Admin. Implemented in `services/api/main.py`; passwords supplied through local environment and hashed with Argon2id. Tested in `tests/test_services.py`.
- [x] Alice and Bob can create and read their own notes; neither can access the other's notes. Owner enforcement is in `services/notes/main.py`; tests cover both directions.
- [x] Generate a simple report from only the requesting user's authorized notes. `services/api/main.py` fetches each note through Notes and sends a digest-bound selection to `services/reports/main.py`; the helper formats it.
- [x] Admin can disable an ordinary account; Admin cannot access private notes. Implemented and tested in `tests/test_services.py`.
- [x] At least three useful functions; report generation crosses all three application services. Real three-process HTTP workflow is tested in `tests/test_process_workflow.py`.

## Architecture and security

- [x] Exactly three independent application processes communicating through explicit HTTP interfaces: API, Notes, Report.
- [x] A separate installable helper package is declared and used by Report. Build/install is specified in `requirements.txt`; it is tested by `tests/test_helper.py`.
- [x] Authenticate users; enforce role and resource ownership at the service that owns notes.
- [x] Service requests bind user, caller/service, audience, action, resource/input digest, and short validity period in `services/common.py`.
- [x] Use synthetic data, protected configuration, and deny-by-default behavior. Secrets and seed passwords are environment-only; missing values fail closed.
- [x] Demonstrate least privilege, complete mediation, and fail-safe defaults with tests/evidence in `docs/security-principles.md`.

## SSDLC, CI, and evidence

- [x] Commit the initial four-phase SSDLC plan before application features. Verified as commit `0aa087c` before any feature files were created.
- [x] Include requirements/scope, architecture/data flow, asset register, trust boundaries, STRIDE, access-control matrix, tests, and gate decisions in the Phase 1 documents.
- [x] Plant and investigate three catalog vulnerabilities plus one distinct cross-component composition vulnerability; show vulnerable behavior, impact, mitigation, regression, and actual local evidence. See `experiments/` and `docs/vulnerability-plan.md`.
- [ ] Jenkins runs for pushes and pull requests; build/install, static scan, dependency scan, create a fresh test environment, run functional/authorization tests, archive evidence, and fail on blocking findings. Jenkinsfile and actual Jenkins execution are not implemented yet.
- [ ] Report production-release considerations and maintain an accurate AI-use declaration in the separate academic report.
- [x] README gives current exact install, seed, run, and test commands. Jenkins and experiment reproduction instructions remain to be added in later phases.
- [ ] Complete Jenkinsfile/security gates and Overleaf report before submission; the four experiment probes and evidence are complete.

## Out of scope

The brief does not require a GUI, registration, email, public hosting, real payment, high availability, or large-scale performance work. The optional malicious-package and approved-hash experiments are not mandatory.

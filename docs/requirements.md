# Requirements checklist

Source: local Software Security Assignment I (6 pages; SHA-256 efb4f3462df8cabae6a92057366f57b53e9ba2e8f52d08099fb967848696eb85). This file records mandatory requirements only; optional supply-chain experiments are excluded from the baseline.

## Functional scope

- [ ] Login seeded users Alice and Bob; include privileged Admin.
- [ ] Alice and Bob can create and read their own notes; neither can access the other's notes.
- [ ] Generate a simple report from only the requesting user's authorized notes.
- [ ] Admin can disable an ordinary account; Admin cannot access private notes.
- [ ] At least three useful functions; report generation crosses all three application services.

## Architecture and security

- [ ] Exactly three independent application processes communicating through explicit HTTP interfaces: API, Notes, Report.
- [ ] A separate installable helper package is declared and used by Report.
- [ ] Authenticate users; enforce role and resource ownership at the service that owns notes.
- [ ] Service requests identify the user, caller/service, audience, action, resource, and short validity period.
- [ ] Use synthetic data, protected configuration, and deny-by-default behavior.
- [ ] Demonstrate least privilege, complete mediation, and fail-safe defaults with tests/evidence.

## SSDLC, CI, and evidence

- [ ] Commit the initial four-phase SSDLC plan before application features.
- [ ] Include requirements/scope, architecture/data flow, asset register, trust boundaries, STRIDE, access-control matrix, tests, and gate decisions.
- [ ] Plant and investigate three catalog vulnerabilities plus one distinct cross-component composition vulnerability; show exploit, impact, mitigation, regression, and evidence.
- [ ] Jenkins runs for pushes and pull requests; build/install, static scan, dependency scan, create a fresh test environment, run functional/authorization tests, archive evidence, and fail on blocking findings.
- [ ] Report production-release considerations and maintain an accurate AI-use declaration.
- [ ] README gives exact install, seed, run, and test commands. Preserve Git history and include the helper, Jenkinsfile, docs, and non-sensitive evidence.

## Out of scope

The brief does not require a GUI, registration, email, public hosting, real payment, high availability, or large-scale performance work. The optional malicious-package and approved-hash experiments are not mandatory.

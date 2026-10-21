# Secure Notes Mini

A small, three-process university project for Software Security Assignment I. **Current state: Phase 1 planning only; application code has not started.**

The proposed application has an API Service for login and coordination, a Notes Service that owns and authorizes notes, and a Report Service that obtains narrowly authorized notes over HTTP and formats a report through the separately installable secure-notes-helper package. Alice and Bob are ordinary users. Admin can disable ordinary accounts, but cannot read their notes.

The initial security plans are in docs/. They were prepared before application implementation. Do not begin feature work until this planning state has been committed and reviewed.

## Planned local workflow

The eventual setup is intended to use a Python virtual environment, install the project and local helper, seed synthetic accounts, and start three independent FastAPI processes. Exact commands will be added with the implementation rather than presented as already working. Tests will use temporary SQLite databases and synthetic credentials.

## Planned checks

- Functional and role/ownership tests with pytest.
- Three-process HTTP report workflow.
- Isolated vulnerable/fixed experiments from the official catalog.
- Jenkins build, static/dependency scans, clean test environment, archived evidence, and blocking gates.

No services, tests, Jenkinsfile, helper package, or vulnerability mutations exist in this planning phase. The academic report will be maintained separately in Overleaf.

## Proposed minimal project structure

This is a proposal only; the directories below are not created in Phase 1.

    pyproject.toml
    Jenkinsfile
    services/api/       login, user store, orchestration, Admin route
    services/notes/     note API, owner checks, notes SQLite
    services/reports/   report HTTP endpoint and helper use
    packages/secure-notes-helper/
    tests/              functional, authorization, and process tests
    experiments/        isolated mutation runner and probes
    docs/               planning, evidence, final submission notes

Keep service code separate by process, helper code in its own installable package, and experiment mutations out of normal service startup.

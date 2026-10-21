# Access-control matrix

Default deny: a permission exists only where explicitly granted. User-facing operations require a valid, unexpired token and an active account.

## User permissions

| Operation | Alice | Bob | Admin |
|---|---|---|---|
| Login / read own identity | Allow | Allow | Allow |
| Create note | Own as Alice | Own as Bob | Deny |
| List/read notes | Alice-owned only | Bob-owned only | Deny |
| Generate report | Own notes only | Own notes only | Deny |
| Disable ordinary account | Deny | Deny | Allow; cannot disable Admin |

Identifiers supplied by a user do not establish ownership. Notes checks ownership on every resource read, including reads initiated by Report. Admin privilege is limited to disabling ordinary accounts; it does not grant access to notes or reports.

## Service permissions

| Caller → service | Allowed action | Scope and enforcement |
|---|---|---|
| API → Notes | Create/list/read (and search for the CWE-89 test surface) | Signed short-lived authority; subject and action checked; Notes checks owner |
| API → Report | Generate a text report | Signed authority, active subject, exact selected note IDs |
| Report → Notes | Read selected notes only | Forwarded API-signed note-specific authority; Report cannot mint grants |
| Other caller/action | Deny | Missing, invalid, wrong-audience, expired, wrong-action, or out-of-scope authority fails closed |

The Report Service has no direct database access. The helper package has no independent service authority.

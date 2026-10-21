# Access-control matrix

Default deny: an operation is allowed only where explicitly granted. User endpoints require a valid unexpired session and an active account.

## User permissions

| Operation | Alice | Bob | Admin |
|---|---|---|---|
| Login / read own identity | Allow | Allow | Allow |
| Create note | Own account | Own account | Deny |
| List/read notes | Alice-owned only | Bob-owned only | Deny |
| Generate report | Own authorized notes | Own authorized notes | Deny |
| Disable ordinary account | Deny | Deny | Allow; cannot disable Admin |

API obtains identity from the authenticated session, never an owner parameter. Notes enforces ownership for every read, including reads used for reports. Disabling an account prevents both new login and use of existing sessions.

## Service permissions

| Caller → service | Permitted operation | Authority scope and enforcement |
|---|---|---|
| API → Notes | Create | Subject-bound `note:create` on `new-note`; Notes obtains owner from verified authority |
| API → Notes | List | Subject-bound `note:list` on `collection`; Notes filters by that subject |
| API → Notes | Read | `note:read` for exact note UUID; Notes independently matches note owner |
| API → Report | Generate | `report:create` bound to subject, username and digest of exact authorized input records |
| Other caller/action | Deny | Missing, invalid, expired, wrong-audience, wrong-action, or wrong-resource authority rejected |

API and each service share a different HMAC key for that service boundary. Report receives note data only after API has fetched it through Notes; Report has neither a Notes key nor direct database access.

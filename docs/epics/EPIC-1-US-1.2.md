# EPIC-1 / US-1.2 - Implement authentication and role model

## Story

As an admin, I want role-based access for editors, publishers, and admins so that publishing is controlled.

## Implementation in this repository

- API app scaffold:
  - `app/main.py`
- Auth and RBAC module:
  - `app/auth.py`
  - Verifies Google OAuth ID tokens (`google.oauth2.id_token.verify_oauth2_token`)
  - Resolves roles from `CMS_ROLE_BINDINGS` environment configuration
  - Enforces endpoint access with role dependencies
- Automated tests:
  - `tests/test_auth.py`
  - Includes explicit 401 and 403 coverage

## Configuration

Set runtime auth configuration with environment variables:

```bash
export GOOGLE_OAUTH_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export CMS_ROLE_BINDINGS='{"editor@example.com":["editor"],"publisher@example.com":["publisher"],"admin@example.com":["admin","publisher","editor"]}'
```

## Acceptance criteria mapping

- [x] Google OAuth integrated for admin/API access.
- [x] Roles enforced on protected endpoints.
- [x] Unauthorized calls return expected 401/403 responses.

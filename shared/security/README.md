# Security Documentation & Testing

This folder contains security-related documentation, scripts, and audit results.

## Managed By

**Cybersecurity Lead:** Monira Lizu (moniralizu1@gmail.com)

## Files to Create Here

| File | Description | Sprint |
|------|-------------|--------|
| `SECURITY_CHECKLIST.md` | Pre-deployment security checklist | Sprint 1 |
| `penetration_test_results.md` | Pen test findings | Sprint 3 |
| `vulnerability_report.md` | Known vulnerabilities & fixes | Sprint 3 |
| `auth_audit.md` | Authentication flow audit | Sprint 1 |

## Security Concerns for This Project

### Authentication
- [ ] Passwords hashed with bcrypt (cost factor ≥ 10)
- [ ] JWT tokens have expiration
- [ ] Refresh token rotation implemented
- [ ] Rate limiting on auth endpoints

### API Security
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (use ORM)
- [ ] XSS prevention
- [ ] CORS properly configured
- [ ] HTTPS enforced in production

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] No secrets in code or logs
- [ ] Environment variables for credentials
- [ ] Database backups encrypted

### Monitoring
- [ ] Failed login attempts logged
- [ ] Sentry for error tracking
- [ ] Audit trail for sensitive actions

## Tools

- **OWASP ZAP** - Vulnerability scanning
- **Burp Suite** - API security testing
- **SQLMap** - SQL injection testing (if applicable)

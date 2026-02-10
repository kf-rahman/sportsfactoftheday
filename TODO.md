# Sports Facts MVP - Todo List

## High Priority

### 1. Fix Front End Design
- [ ] Review current UI/UX 
- [ ] Identify design issues or improvements needed
- [ ] Implement design fixes
- [ ] Test responsiveness on mobile/desktop

### 2. Database Hosting & Setup
- [ ] Choose database hosting option (Railway PostgreSQL recommended)
- [ ] Provision PostgreSQL database on Railway
- [ ] Verify DATABASE_URL environment variable is set
- [ ] Test database connection on production
- [ ] Migrate existing data if needed
- [ ] Document database backup strategy

### 3. Robust Testing & Understanding
- [ ] Test all API endpoints
  - [ ] GET /api/generate (MLB, NBA, Random)
  - [ ] POST /api/subscribe
  - [ ] GET /api/sports
  - [ ] GET /api/email/status
  - [ ] POST /api/email/send-test
- [ ] Verify data sources (NBA.com API, MLB Stats API)
- [ ] Test LLM integration with different models
- [ ] Document how each component works
- [ ] Check error handling

### 4. Testing Email Sign Up
- [ ] Test email subscription form submission
- [ ] Verify email validation works
- [ ] Test database persistence (subscribers saved to PostgreSQL)
- [ ] Test sport preferences (NBA, MLB, both)
- [ ] Test duplicate email handling
- [ ] Verify unsubscribe functionality
- [ ] Test Resend email delivery
- [ ] Test data persists after server restart

## Medium Priority

### 5. Overall Clean Up
- [ ] Remove any unused code
- [ ] Clean up imports
- [ ] Add comments where needed
- [ ] Update documentation
- [ ] Check for any TODOs in code
- [ ] Verify .env.example is up to date
- [ ] Review requirements.txt

## Status Legend
- [ ] Not started
- [~] In progress  
- [x] Complete

Last updated: 2026-02-10

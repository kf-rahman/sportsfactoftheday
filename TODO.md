# Sports Facts MVP - Todo List

## High Priority

### 1. Fix Front End Design
- [x] Review current UI/UX
- [x] Implement glassmorphism design (glass notebook aesthetic)
- [x] Lighten background to cool cream, golf-ball-white cards
- [ ] Test responsiveness on mobile/desktop

### 2. Database Hosting & Setup
- [ ] Choose database hosting option (Railway PostgreSQL recommended)
- [ ] Provision PostgreSQL database on Railway
- [ ] Verify DATABASE_URL environment variable is set
- [ ] Test database connection on production
- [ ] Migrate existing data if needed
- [ ] Document database backup strategy

### 3. OpenRouter / LLM Investigation
- [ ] Confirm OPENROUTER_API_KEY is set in Railway env vars
- [ ] Confirm OPENROUTER_MODEL is set correctly
- [ ] Test /api/generate?debug=1 in production to see LLM vs fallback
- [ ] Check Railway logs for OpenRouter error messages
- [ ] Verify fallback blurb renders correctly if LLM fails

### 4. Robust Testing & Understanding
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

### 5. Testing Email Sign Up
- [ ] Test email subscription form submission
- [ ] Verify email validation works
- [x] Add welcome/confirmation email on new signup
- [ ] Test database persistence (subscribers saved to PostgreSQL)
- [ ] Test sport preferences (NBA, MLB, both)
- [ ] Test duplicate email handling (upserts preferences, no duplicate welcome)
- [ ] Verify unsubscribe functionality
- [ ] Test Resend email delivery (welcome email + daily email)
- [ ] Test data persists after server restart

## Medium Priority

### 6. Overall Clean Up
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

Last updated: 2026-02-18

# Sports Facts MVP - Todo List

## High Priority

### 1. Fix Front End Design
- [ ] Review current UI/UX 
- [ ] Identify design issues or improvements needed
- [ ] Implement design fixes
- [ ] Test responsiveness on mobile/desktop

### 2. Robust Testing & Understanding
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

### 3. Testing Email Sign Up
- [ ] Test email subscription form submission
- [ ] Verify email validation works
- [ ] Check subscriber saved to database
- [ ] Test sport preferences (NBA, MLB, both)
- [ ] Test duplicate email handling
- [ ] Verify unsubscribe functionality
- [ ] Test Resend email delivery

## Medium Priority

### 4. Overall Clean Up
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

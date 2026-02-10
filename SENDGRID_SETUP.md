# SendGrid Setup Guide

## Quick Start (MVP)

### Step 1: Create SendGrid Account
1. Go to [sendgrid.com](https://sendgrid.com)
2. Sign up for free account (100 emails/day)
3. Verify your account via email

### Step 2: Verify Single Sender (Fastest for MVP)

**Option A: Use Your Personal Email**
1. In SendGrid Dashboard → Settings → Sender Authentication
2. Click "Verify a Single Sender"
3. Fill in:
   - From Name: Sports Facts
   - From Email: your-email@gmail.com
   - Reply To: your-email@gmail.com
   - Company Address: Your address (required by law)
4. Click "Create"
5. Check your email and click verification link

**Option B: Use Custom Domain (Better long-term)**
1. Buy domain (Namecheap ~$10/year)
2. In SendGrid → Settings → Domain Authentication
3. Click "Authenticate Your Domain"
4. Select your DNS provider
5. Add the DNS records shown to your domain provider
6. Wait 5-10 minutes, then click "Verify"

### Step 3: Get API Key
1. SendGrid Dashboard → Settings → API Keys
2. Click "Create API Key"
3. Name: "Sports Facts Production"
4. Permissions: "Full Access" (or restrict to Mail Send only)
5. Copy the API key (starts with `SG.`)

### Step 4: Add to Railway
In Railway Dashboard → Your Project → Variables:
```
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=your-verified-email@gmail.com
FROM_NAME=Sports Facts
```

### Step 5: Test Email
```bash
curl -X POST "https://your-app.up.railway.app/api/email/send-test?email=youremail@gmail.com"
```

---

## Important Notes

### Free Tier Limits
- 100 emails/day
- Perfect for MVP testing
- Upgrade to paid ($19.95/month) for more

### Email Deliverability Tips
1. **Use custom domain** - Better than Gmail for production
2. **Warm up slowly** - Start with <50 emails/day
3. **Include unsubscribe link** - Already in your template ✓
4. **Don't use spam words** - Your facts are safe!

### Common Issues

**Issue: Emails go to spam**
- Solution: Use custom domain, not Gmail
- Add SPF/DKIM records (SendGrid provides these)

**Issue: "Sender address not verified"**
- Solution: Complete Step 2 above - verify your sender

**Issue: Rate limit exceeded**
- Solution: You're on free tier (100/day). Upgrade or wait.

---

## Production Checklist

Before sending to many users:
- [ ] Domain authenticated (not just single sender)
- [ ] SPF record added
- [ ] DKIM record added
- [ ] DMARC record added (optional but recommended)
- [ ] Unsubscribe link works
- [ ] "From" name is recognizable

---

## Domain DNS Records Example

If using custom domain `sportsfacts.app`, add these DNS records:

**CNAME Records:**
```
s1._domainkey.sportsfacts.app → s1.domainkey.u123456.wl123.sendgrid.net
s2._domainkey.sportsfacts.app → s2.domainkey.u123456.wl123.sendgrid.net
em1234.sportsfacts.app → u123456.wl123.sendgrid.net
```

SendGrid will give you exact records during setup.

---

## Next Steps

1. ✅ Set up SendGrid account
2. ✅ Verify sender (single or domain)
3. ✅ Add API key to Railway
4. ✅ Test email sending
5. ✅ Set up daily cron job
6. 🎉 Start collecting subscribers!

**Questions?** Check [SendGrid Docs](https://docs.sendgrid.com)

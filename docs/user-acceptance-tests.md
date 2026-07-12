## UAT-001: Subscribe to a free team
**Linked to:** User Story US-01
**Type:** old (mvp v1)
**Status:** Active

**User goal:** 
As a user, I want to use one of my three free team subscriptions, so that I can get notifications about matches with my favourite team without payment.

**Preconditions:**
- User is logged in in website
- User is on his profile page
- The team user wants to subscribe is in KHL
- User has fewer than three active free team subscriptions

**Step-by-step instructions:**
1. User push the button "Manage subscriptions"
2. After pushing he is on the "Managing subscriptions" page
3. User see the list of all KHL teams and right to each team button "Subscribe" or "Unsubscribe" (if user already subscribed team)
4. User push button "Subscribe"

**Expected outcome:**
After all steps:
- On step 3: user see all teams and if he is already subscribed to some team, the button "Unsubscribe" is next to this team 
- On step 4: no payment is requested and the button changes to "Unsubscribe"
- On profile page: user see updated list of teams he subscribed.

**Result:** Pass
**Executed by:** Daniil
**Date:** 3.07.2026
**Notes:** Change button "Back" to button "Save changes"

## UAT-002: Unsubscribe team
**Linked to:** User Story US-01
**Type:** old (mvp v1)
**Status:** Active

**User goal:** 
As a user, I want to unsubscribe specific hockey team, so that I will not get notifications about this team from this time.

**Preconditions:**
- User is logged in in website
- User is on his profile page
- The team user wants to unsubscribe is in KHL

**Step-by-step instructions:**
1. User push the button "Manage subscriptions"
2. After pushing he is on the "Managing subscriptions" page
3. User see the list of all KHL teams and right to each team button "Subscribe" or "Unsubscribe" (if user already subscribed team)
4. User push button "Unsubscribe"

**Expected outcome:**
After all steps:
- On step 4: the bitton changes to "Subscribe"
- On profile page: user see updated list of teams he subscribed without the team he unsubscribed.

**Result:** Pass
**Executed by:** Daniil
**Date:** 3.07.2026
**Notes:** Change button "Back" to button "Save changes"

## UAT-003: Password Recovery
**Linked to:** User Story US-10
**Type:** old (mvp v1)
**Status:** Active

**User goal:** 
As a user, I want to have an opportunity to recover the password, so that I do not worry if I forget it.

**Preconditions:**
- User is logged in in website
- User is on Log in page
- User wants to recover the password

**Step-by-step instructions:**
1. User push the button "Forget password?"
2. After pushing he is on the "Password recovery" page
3. User input the email with which he has account.
4. User push button "Send code"
5. After pushing he is on the "New password" page
6. User input email, code, new password and repeat password
7. User push button "Change password"

**Expected outcome:**
After all steps:
- On step 4: email notification with code send to user
- On step 7: password changes in database
- User can Log in with new password

**Result:** Pass
**Executed by:** Daniil
**Date:** 3.07.2026
**Notes:** All good, no need changes

## UAT-004: Managing parsing time
**Linked to:** [PBI] Admin Panel
**Type:** new (mvp v2)
**Status:** Active

**User goal:** 
As an admin, I want to manage the parsing time, so that I make parsing time faster on playoff and make it slower in other time.

**Preconditions:**
- Admin is in admin website
- Admin logged in and pass the verification
- Admin wants to change parsing time

**Step-by-step instructions:**
1. Admin push the button "Settings"
2. After pushing he see the input box "Parsing time"
3. Admin input the parsing time
4. Admin push button "Save"

**Expected outcome:**
After all steps:
- On step 4: the parsing time is changed

**Result:** Pass
**Executed by:** Daniil
**Date:** 3.07.2026
**Notes:** Add validation to parsing time (1-999)

## UAT-005: Add proxy
**Linked to:** [PBI] Admin Panel
**Type:** new (mvp v2)
**Status:** Active

**User goal:** 
As an admin, I want to add proxy, so that I can by pass CAPTCHA to parse information from KHL teams websites.

**Preconditions:**
- Admin is in admin website
- Admin logged in and pass the verification
- Admin wants to add proxy

**Step-by-step instructions:**
1. Admin push the button "Proxy"
2. After pushing he see the input box "Add proxy"
3. Admin input the proxy
4. Admin push button "Save"

**Expected outcome:**
After all steps:
- On step 4: new proxy added

**Result:** Pass
**Executed by:** Daniil
**Date:** 3.07.2026
**Notes:** All good, no changes

## UAT-006: Upload avatar
**Linked to:** [PBI] Implement a backend for uploading avatars, [PBI] Avatar adding Frontend
**Type:** new (mvp v2)
**Status:** Active

**User goal:** 
As an user, I want to upload avatar, so that I can have my photo on my profile page.

**Preconditions:**
- User logged in
- User in his profile page
- User wants to upload photo as avatar

**Step-by-step instructions:**
1. User push button "Upload photo"
2. User chooses the part of photo which will be visible on it profile page
3. User push button "Save"

**Expected outcome:**
After all steps:
- User's photo in database
- User can view the photo he uploaded on his profile page

**Result:** Pass
**Executed by:** Daniil
**Date:** 3.07.2026
**Notes:** All good, no chages

## UAT-007: Purchase and manage a monthly team subscription
**Linked to:** User Story US-06, Monetisation Backend, Monetisation Frontend
**Type:** new (mvp v3)
**Status:** Active

**User goal:**
As a user who already uses all three free team subscriptions, I want to purchase a 30-day subscription for a specific additional team and manage its auto-renewal.

**Preconditions:**
- User is logged in on the website
- User already has three active free team subscriptions
- User is not subscribed to the additional team
- For a production test, YooKassa is configured and available
- For a local UI test, the application is running with `BILLING_DEMO_MODE=true`

**Step-by-step instructions:**
1. User opens the team subscription management page
2. User pushes "Subscribe" for a fourth team
3. The website opens the payment page for that specific team
4. User sees the price of 39 RUB and a subscription period of 30 days
5. On the first paid purchase, user accepts saving the payment method in YooKassa; enabling auto-renewal is optional
6. User pushes "Pay 39 RUB" and completes the payment
7. User opens the "My paid teams" page
8. User switches auto-renewal for this team on or off
9. User unsubscribes from notifications for the paid team and then subscribes to the same team again before the paid period expires

**Expected outcome:**
- The fourth team is not added before a successful payment is confirmed
- The payment applies only to the team selected by the user
- After successful payment, the team is active for 30 days and appears in the user's subscriptions
- The paid team appears on the "My paid teams" page with its expiry date, price, and auto-renewal setting
- Auto-renewal can be enabled or disabled separately for each paid team
- The payment method saved during the first paid purchase can be reused for later team purchases and auto-renewals without entering the card again
- Unsubscribing stops notifications but does not delete the active paid period
- Resubscribing to the same paid team before its expiry does not require another payment
- A paid team does not consume one of the user's three free team slots

**Result:** Not executed
**Executed by:** Not assigned
**Date:** Not executed
**Notes:** Production payment acceptance must be tested with YooKassa test credentials. Local demo mode verifies only the HockeyScrapper interface and application logic; it does not verify the real YooKassa integration.

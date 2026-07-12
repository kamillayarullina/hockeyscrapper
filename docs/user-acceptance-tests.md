## UAT-001: Subscribe to a team
**Linked to:** User Story US-01
**Type:** old (mvp v1)
**Status:** Active

**User goal:** 
As a user, I want to subscribe to a specific hockey team, so that I can get notifications about mathches with my favourite team.

**Preconditions:**
- User is logged in in website
- User is on his profile page
- The team user wants to subscribe is in KHL

**Step-by-step instructions:**
1. User push the button "Manage subscriptions"
2. After pushing he is on the "Managing subscriptions" page
3. User see the list of all KHL teams and right to each team button "Subscribe" or "Unsubscribe" (if user already subscribed team)
4. User push button "Subscribe"

**Expected outcome:**
After all steps:
- On step 3: user see all teams and if he is already subscribed to some team, the button "Unsubscribe" is next to this team 
- On step 4: the bitton changes to "Unsubscribe"
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

## UAT-007: Purchase premium subscription
**Linked to:** US-06 Monetization
**Type:** new (mvp v3)
**Status:** Active

**User goal:**
As a user, I want to purchase a premium subscription, so that I can unlock subscriptions more then 3 teams.

**Preconditions:**
- User is logged in
- User is on the pricing page
- User has a valid payment method (card)

**Step-by-step instructions:**
1. User navigates to the "Pricing" page
2. User sees two plans: "Free" and "Premium"
3. User pushes button "Buy Premium"
4. System redirects user to YooKassa payment page
5. User enters card details and confirms payment
6. System redirects user back to the application
7. User sees confirmation message "Premium subscription activated"

**Expected outcome:**
After all steps:
- On step 2: user sees the free plan limits and premium plan benefits
- On step 5: payment is processed successfully via YooKassa
- On step 7: user's profile shows "Premium" status
- On step 7: user can now subscribe to unlimited teams

**Result:**
**Executed by:**
**Date:**
**Notes:**

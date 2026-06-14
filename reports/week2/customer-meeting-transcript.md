# Interview Transcript

**Team:** Hello.

**Client:** Hello.

**Team:** So, let's start with some questions we need to ask. Do you mind if the repository is public on GitHub and everything is done under an open-source license?

**Client:** I read that question, but I don't actually know the answer yet. I probably need to check with the course instructor about how this should be set up properly.

**Team:** No, the question is exactly about that — that it should be like that. So we need to ask, and if you don't mind, it would be great if you could also confirm it in writing in the chat. And we'll need to include that in the assignment and confirm that you agree.

**Client:** Okay.

**Team:** Yes, thank you. And the second question is: may we record our conversation?

**Client:** Yes, yes, yes.

**Team:** Great, perfect. So, today we would like to first show a demo version — we already have one — and confirm the user stories. Now I'll do the demonstration, and then the user stories. They have priorities: Must, Should, Could, Won't. So the first one is — well, you can subscribe to a hockey team and receive notifications. I think there's no question that this is a must.

**Client:** That's the essence. Yes.

**Team:** The second story: match date and time — we also decided that should be included.

**Client:** Yes, exactly.

**Team:** Next: ticket price. We decided to give it a slightly lower priority — it should be there, but for now it's lower.

**Client:** Agreed.

**Team:** And the list of KHL teams is also high priority, so it's clear what to subscribe to.

**Client:** Yes, definitely somewhere during registration or right after, the user should choose which teams to subscribe to.

**Team:** Then notifications via Telegram and email. At this stage, notifications only go through Telegram. Email is not ready yet, but I think it's needed. Monetization also — I understand it's a lower priority, but it's not ready yet. In the future, I assume.

**Client:** Okay.

**Team:** Oh, and seeing your subscriptions — that should be there, I think. And the ability to unsubscribe as well. Then stadium subscriptions — that's quite a low priority for implementation, but for now it works. Actually, it was for testing, because there is no regular season right now. When you subscribe to a team, you also automatically subscribe to that team's stadium. For now, this cannot be configured. Is it necessary to configure it, or leave it as is?

**Client:** Well, it's basically the same thing. Every team has its own stadium.

**Team:** Yes, we subscribe to the team, but we did this now for testing. Because right now there's the All-Star Game, so there are no real teams. We just subscribed to a stadium to test it.

**Client:** Alright, let it be that way.

**Team:** And the number of people subscribed to specific teams — I marked that as low priority. I don't think users really need that.

**Client:** Okay.

**Team:** Oh, and setting a password on the site — that's a must. And the last thing: allowing the user to adjust the parsing time themselves, but again, that won't be implemented.

**Client:** Okay.

**Team:** So, that's it. So you agree with all the items and priorities, right?

**Client:** Yes.

**Team:** Then I'll start the demo and show what we have ready. Here, first the website, how it looks in terms of design.

**Client:** That's great.

**Team:** You need to register, obviously. Registration works. You can manage subscriptions and link Telegram. Let's subscribe to someone, like Lokomotiv or Dynamo, and link Telegram. Telegram seems to have crashed. Let me restart it. It was working just now. Interesting. Anyway, the site looks like this for now. I'll figure out Telegram.

**Client:** Did you make any design prototype for the site, or did you start coding right away?

**Team:** Hmm, we did design prototype, we used Figma. Yes. Actually, it should have automatically linked Telegram. For some reason it decided not to.

**Client:** Is Telegram's VPN not working?

**Team:** No, messages are coming through and everything works, but here it's a problem. Maybe because I started Telegram with a VPN, that's why it's not working. I'll try a different way. Do you have any questions?

**Client:** Well, a couple of comments about the site: I'd like to add more nice visual touches, for example, logos for each team.

**Team:** Okay.

**Client:** And use up‑to‑date ones. I think at the registration stage some logos were huge. Looks a bit strange.

**Team:** Okay, we'll work on that. Now let me try to run the bot separately to show you. For some reason, running it separately doesn't work either. So, the bot greets us. We can also subscribe — enter a team name and see the list of all teams, and my subscriptions. Right now... In general, it should link to the site, but for some reason it's not working.

**Client:** I understand that your first iteration was to implement the subscription functionality — choosing a team, the full list — and then you'll parse the sites either via an API or something else?

**Team:** Yes. We already have a parser ready, it parses something — again, it's in demo mode because it's hard to test properly. Plus we have an admin panel, only in the bot for now, which allows managing parser intervals, adding proxies to avoid problems. Right now it parses directly because we don't have proxies yet, but the ability to add them is there.

**Client:** What are proxies for? Please explain.

**Team:** Proxies are to avoid issues like being asked to solve a CAPTCHA. The parser would fail because of too many requests from our IP. So we have the option to add proxies.

**Client:** You got started quickly.

**Team:** Well, it's fast for now. This is what we have. We still need to debug some things and implement a few features, like monetization, email notifications, password recovery — that's not ready yet. Basically everything related to email is still in development.

**Client:** I see. Well done.

**Team:** Any other questions?

**Client:** No, all good.

**Team:** So, about design — add pictures, team blogs, etc.

**Client:** Yes. Can I take a look at your Figma?

**Team:** Sure. We'll send it to you in the Telegram chat. The Figma for the site? Or the Figma for the bot? Or both?

**Client:** Both, let me see everything.

**Team:** We don't have a Figma for the bot, sorry. Only for the site.

**Client:** How did you divide roles within the team?

**Team:** One person does the bot and parser completely. Then frontend for the site, backend for the site, the database, and another person works with email.

**Client:** Great.

**Team:** I'll send you the link now.

**Client:** I'll take a look later.

**Team:** Okay.

**Client:** Well, if there are no more questions…

**Team:** Let me try one more time to show how it should work. Maybe it will work now. If not, well, something must have broken. We have no more questions either. Thank you for the meeting.

**Client:** Thank you very much as well.

**Team:** Goodbye.

**Client:** Have a nice day.

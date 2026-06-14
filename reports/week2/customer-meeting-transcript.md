## Interview Transcript
\begin{description}[leftmargin=*, labelsep=1em, itemsep=0.7em]
    \item[Team:] Hello. 
    \item[Client:] Hello. 
    \item[Team:]  So, let's start with some questions we need to ask. Do you mind if the repository is public on GitHub and everything is done under an open-source license?
    \item[Client:] I read that question, but I don't actually know the answer yet. I probably need to check with the course instructor about how this should be set up properly.
    \item[Team:] No, the question is exactly about that — that it should be like that. So we need to ask, and if you don't mind, it would be great if you could also confirm it in writing in the chat. And we'll need to include that in the assignment and confirm that you agree.
    \item[Client:] Okay.
    \item[Team:] Yes, thank you. And the second question is: may we record our conversation?
    \item[Client:] Yes, yes, yes.
    \item[Team:] Great, perfect. So, today we would like to first show a demo version — we already have one — and confirm the user stories. Now I'll do the demonstration, and then the user stories. They have priorities: Must, Should, Could, Won't. So the first one is — well, you can subscribe to a hockey team and receive notifications. I think there's no question that this is a must.
    \item[Client:] That's the essence. Yes.
    \item[Team:] The second story: match date and time — we also decided that should be included.
    \item[Client:] Yes, exactly.
    \item[Team:] Next: ticket price. We decided to give it a slightly lower priority — it should be there, but for now it's lower.
    \item[Client:] Agreed.
    \item[Team:] And the list of KHL teams is also high priority, so it's clear what to subscribe to.
    \item[Client:] Yes, definitely somewhere during registration or right after, the user should choose which teams to subscribe to.
    \item[Team:] Then notifications via Telegram and email. At this stage, notifications only go through Telegram. Email is not ready yet, but I think it's needed. Monetization also — I understand it's a lower priority, but it's not ready yet. In the future, I assume.
    \item[Client:] Okay.
    \item[Team:] Oh, and seeing your subscriptions — that should be there, I think. And the ability to unsubscribe as well. Then stadium subscriptions — that's quite a low priority for implementation, but for now it works. Actually, it was for testing, because there is no regular season right now. When you subscribe to a team, you also automatically subscribe to that team's stadium. For now, this cannot be configured. Is it necessary to configure it, or leave it as is?
    \item[Client:] Well, it's basically the same thing. Every team has its own stadium.
    \item[Team:] Yes, we subscribe to the team, but we did this now for testing. Because right now there's the All-Star Game, so there are no real teams. We just subscribed to a stadium to test it.
    \item[Client:] Alright, let it be that way.
    \item[Team:] And the number of people subscribed to specific teams — I marked that as low priority. I don't think users really need that.
    \item[Client:] Okay.
    \item[Team:] Oh, and setting a password on the site — that's a must. And the last thing: allowing the user to adjust the parsing time themselves, but again, that won't be implemented.
    \item[Client:] Okay.
    \item[Team:] So, that's it. So you agree with all the items and priorities, right?
    \item[Client:] Yes.
    \item[Team:] Then I'll start the demo and show what we have ready. Here, first the website, how it looks in terms of design.
    \item[Client:] That's great.
    \item[Team:] You need to register, obviously. Registration works. You can manage subscriptions and link Telegram. Let's subscribe to someone, like Lokomotiv or Dynamo, and link Telegram. Telegram seems to have crashed. Let me restart it. It was working just now. Interesting. Anyway, the site looks like this for now. I'll figure out Telegram.
    \item[Client:] Did you make any design prototype for the site, or did you start coding right away?
    \item[Team:] Hmm, we did design prototype, we used Figma. Yes. Actually, it should have automatically linked Telegram. For some reason it decided not to.
    \item[Client:] Is Telegram's VPN not working?
    \item[Team:] No, messages are coming through and everything works, but here it's a problem. Maybe because I started Telegram with a VPN, that's why it's not working. I'll try a different way. Do you have any questions?
    \item[Client:] Well, a couple of comments about the site: I'd like to add more nice visual touches, for example, logos for each team.
    \item[Team:] Okay.
    \item[Client:] And use up‑to‑date ones. I think at the registration stage some logos were huge. Looks a bit stange.
    \item[Team:] Okay, we'll work on that. Now let me try to run the bot separately to show you. For some reason, running it separately doesn't work either. So, the bot greets us. We can also subscribe — enter a team name and see the list of all teams, and my subscriptions. Right now... In general, it should link to the site, but for some reason it's not working.
    \item[Client:] I understand that your first iteration was to implement the subscription functionality — choosing a team, the full list — and then you'll parse the sites either via an API or something else?
    \item[Team:] Yes. We already have a parser ready, it parses something — again, it's in demo mode because it's hard to test properly. Plus we have an admin panel, only in the bot for now, which allows managing parser intervals, adding proxies to avoid problems. Right now it parses directly because we don't have proxies yet, but the ability to add them is there.
    \item[Client:] What are proxies for? Please explain.
    \item[Team:] Proxies are to avoid issues like being asked to solve a CAPTCHA. The parser would fail because of too many requests from our IP. So we have the option to add proxies.
    \item[Client:] You got started quickly.
    \item[Team:] Well, it's fast for now. This is what we have. We still need to debug some things and implement a few features, like monetization, email notifications, password recovery — that's not ready yet. Basically everything related to email is still in development.
    \item[Client:] I see. Well done.
    \item[Team:] Any other questions?
    \item[Client:] No, all good.
    \item[Team:] So, about design — add pictures, team blogs, etc.
    \item[Client:] Yes. Can I take a look at your Figma?
    \item[Team:] Sure. We'll send it to you in the Telegram chat. The Figma for the site? Or the Figma for the bot? Or both?
    \item[Client:] Both, let me see everything.
    \item[Team:] We don't have a Figma for the bot, sorry. Only for the site.
    \item[Client:] How did you divide roles within the team?
    \item[Team:] One person does the bot and parser completely. Then frontend for the site, backend for the site, the database, and another person works with email.
    \item[Client:] Great.
    \item[Team:] I'll send you the link now.
    \item[Client:] I'll take a look later.
    \item[Team:] Okay.
    \item[Client:] Well, if there are no more questions…
    \item[Team:] Let me try one more time to show how it should work. Maybe it will work now. If not, well, something must have broken. We have no more questions either. Thank you for the meeting.
    \item[Client:] Thank you very much as well.
    \item[Team:] Goodbye.
    \item[Client:] Have a nice day.
\end{description}

**Team:**

00:00
Can we record the meeting so that the TA has access to it and the transcript is available in the repository?

**Customer:**

Okay, sure.

**Team:**

Thank you. Then we will start with the fact that Bulat is also with us today, he will show you how the parser works.

**Team:**

I will turn on the demonstration now. In general, as it turned out, the parser had a problem not with how it works, but with the protections that were in place on Yandex and on the KHL website. So we had to change the idea a bit. That is, now it simulates a real user so that there are no problems. Now I will launch the project, and we will see that notifications will arrive. Open your screen then. While we wait for the parser to work. And thanks to this, it was possible to fix it. And right now, matches have appeared on the KHL website, and on other sites as well. To be specific, on Ticket.KHL and on KHL itself. So, we see that the parsing went through, a match was found. There is even a link where you can buy tickets. This is from Ticket.Hockey. So, now we can say that KHL and Ticket.Hockey definitely work. It’s hard to say about Yandex and specifically club websites yet, because the match hasn’t appeared there yet. The only thing is that it immediately writes that there are no tickets, and as soon as they appear, it will send a new notification that tickets have become available.

**Customer:**

Do I understand correctly that this user is subscribed to the CSKA team?

**Team:**

Yes, yes, that is, he is subscribed only to CSKA, and accordingly, he receives only CSKA matches.

**Customer:**

And how many minutes are currently set for the search, well, for the parser's search work?

**Team:**

When launched, it simply searches, and then every 6 minutes. That is, I just launched the project, it was running before this. So, for each parser, TicketHockey, KHL, Yandex, and further specifically club websites. It is set like this. 30 minutes for the main websites where everything appears immediately, well, universal ones, because all teams are there, and club websites less frequently.

**Customer:**

Cool.

**Team:**

It immediately displays how many matches are currently found, how far it has progressed, and you can view the list of matches in the Telegram bot.

**Customer:**

Cool.

**Team:**

Do you have any questions regarding the parser?

**Customer:**

Well, some kind of negative case. I want to check if it works or not. If we subscribe to a team where we know for sure that there are no tickets on sale yet. Oh, tickets for sale specifically.

**Team:**

That is, a team that currently has no matches?

**Customer:**

Well, tickets for sale specifically not yet.

**Team:**

Ah, exactly. Well, here, for example, CSKA vs Torpedo, there are no tickets yet, just on the KHL website, well, now let’s go over, the match page has appeared, but tickets haven’t appeared yet. It just sends a link to the match for now, and as soon as a ticket appears, it will also see it and send a notification that a ticket has appeared.

**Customer:**

Understood, was the status written there as "no", right?

**Team:**

Yes, no tickets, and accordingly... only the information that is available is displayed.

**Customer:**

Okay, super.

**Team:**

So, that is, KHL and ticket.hockey definitely work. So, while we wait for appearances on club websites and on Yandex, because there seem to be no tickets there at all. Ah, and among the downsides, the parser is quite resource-intensive, because it directly emulates a user, and in terms of performance, it certainly requires a lot.

**Customer:**

And how exactly does it work?

**Team:**

Well, previously it used just Playwright, and the problem was that an error would just pop up, and it wouldn't find anything, because there was some protection there, and we had to use an additional library that specifically emulates mouse movements so that everything works, and therefore this is very resource-intensive. On Yandex too there was a problem that Yandex divides everything heavily by cities, and when the Yandex parser launches, it launches separately for each city, and therefore this all turned out to be very costly, and for now, if we optimize it somehow, think about it somehow, but for now it works like this.

**Customer:**

Well, super. I have no questions. I assume this is our final meeting with you, you already have a presentation scheduled?

**Team:**

Yes, this is the final meeting.

**Team:**

Can we ask you, before that, what you asked us to show what we did last week, you asked to change the monetization system.

**Customer:**

I also saw in Git that you implemented logout.

**Team:**

That is, we have, well, small features, when you enter a password, proper error messages are displayed, such small features, you can log out of your account, and respectively, how it works, that is, when a person wants to subscribe to any team, he subscribes, well, I have CSKA purchased, so nothing happened now, for Ak Bars, for example, subscribe, it redirects him immediately to the purchase page, supposedly purchasing a subscription, but here there is a warning, that is, a spoiler that we don't have anything, that this is all in test mode. And respectively, you can choose for a year, or you can choose for a month and enable auto-renewal. After that, one more spoiler, and that's it. And then you can go to separate pages where you can control which teams you are subscribed to, until what date they are valid, enable and disable auto-renewal.

**Customer:**

Super. Everything is great, as agreed last time.

**Team:**

(07:53) Yes, super. Then we can ask you to try using this product, because we need this. That is, register there, or log in and try to subscribe to a team.

**Customer:**

Yes, please duplicate the link. Do you need me to show my screen or how?

**Team:**

Well, if possible, of course, it would be good, but if there is no possibility, no problem. Are you on a laptop or phone?

**Customer:**

From the laptop, I'll show now. Strange button text. To my paid teams. To my paid subscriptions.

**Team:**

Yes, just because subscriptions there translate specifically as receiving notifications. Paid teams. If you unsubscribe, the purchase remains. And to receive notifications again, you will need to select this team again. But repeated purchase will not occur. Only if the limit hasn't been exceeded. Less than 30 days have passed.

**Customer:**

Well, just if I unsubscribe, then probably Auto-renewal should turn off. Well yes, if I unsubscribe. Ah, although no, okay. Subscription means receiving notifications. Remind me how to access the admin panel, please. Just write admin here.

**Team:**

It won't work, because an admin account is needed. I can send you the credentials.

**Customer:**

Let's do that. If you have 10-20 minutes extra. You can add protection against logging out of the account.

**Team:**

Okay.

**Customer:**

Just a confirmation. Are you sure you want to log out? An additional button. You showed it was 40. What changed?

**Customer:**

The parsers were working, and apparently some parser still found something somewhere. Try adding a subscription, the interface has changed now.

**Customer:**

Selection now. Tell me about the ID, please. Why are some like this, others like that?

**Team:**

The long ones are those who linked Telegram, and this is their Telegram ID. And the negative ones are those who only registered on the website.

**Customer:**

And so first the ID is one, then it changes to such if I link Telegram?

**Team:**

Yes.

**Customer:**

Does this not break subscriptions in any way? If I first create an account, subscribe somewhere, and then link Telegram and my ID is applied?

**Team:**

I checked this, it's definitely not a problem.

**Customer:**

Good. What changes in the user interface if he is blocked?

**Team:**

In the interface specifically for the user, nothing changes, but he does not receive notifications.

**Customer:**

Okay. What is this? What kind of button is this? Test email.

**Team:**

To check if email sending works, but now it won't work, because not all data for email is entered in ENV, so it won't be able to send now.

**Customer:**

Can we somehow make it so that I receive notifications now?

**Team:**

Yes, I can. You can go to settings, clear matches, and I will restart the project now, and you will receive notifications. Then I am restarting the project now. Now we wait for the parser to find and send on the internet.

**Customer:**

Yes, it's coming. Mayor of Moscow Cup. And do you show the price in the bot notification? Is this the minimum?

**Team:**

Yes, yes. Well, if there is some range there.

**Customer:**

Cool. And how does the parser understand, if it found a match, how does it understand if tickets are available or not?

**Team:**

The website also indicates ticket availability. If it didn't find anything at all about tickets, then there are no tickets. If it found that there are none, then there are no tickets. And if suddenly it has some problems, that is, something unclear, conditionally, there are tickets, but something unclear with availability, it writes "clarifying".

**Customer:**

Yes super, understood. And I even found such a notification. Cool, I have no more questions.

**Team:**

(20:30) Good, excellent. Then you can tell us how you evaluate, that is, if anything is clear or unclear. Does this need to be redone, maybe?

**Customer:**

Well, for me, perhaps the only part of the project that I don’t understand is about proxies. What it does, how to configure it. Everything else is very, very clear. Nothing needs to be redone. Well, this improvement with logging out of the account, I would say, if it's not difficult to add, not necessary.

**Team:**

Okay.

**Customer:**

Well yes. Well okay, one more. The indentation here. Just make it bigger. Too close to the text. But it is optional.

**Team:**

Okay.

**Customer:**

You did everything very cool.

**Team:**

Excellent. Now we need to show the handover document. Right now. One second.

**Customer:**

I read it today actually.

**Team:**

Do you agree with it? Are there any questions about it?

**Customer:**

Well, of course, I haven't tried installing all this on my computer yet, but in general everything is described in great detail, and I think there will be no problems.

**Team:**

Yes, that is, here are the environment variables. Described. No objections? Good. We just need to ask this explicitly. Then one more question. How will the product transfer be carried out? That is, all environment variables are there. How to configure them? That is also in the document. And it turns out we need to transfer the repository to you, or how do you want to do this?

**Customer:**

Well, the repository... We seemed to agree at the very beginning that it would be open. If, of course, there is a possibility for me to somehow take ownership of it, then let's do it. Well, and here is the only bot, the bot is currently on your team account, as you write.

**Team:**

Yes, that is, we transfer both the bot and the repository to you. All good. And now another thing, we need to clarify with you, is the product fully ready for transfer?

**Customer:**

Yes, that's right. You guys are great, you handled everything.

**Team:**

Alright then, excellent, that is, the product is fully ready for transfer and we just need to transfer it to you. That's all then. Thank you.

**Customer:**

Good luck with the presentation on Tuesday. Thank you very much.

**Team:**

It was very pleasant to work with you. Thank you. Goodbye.

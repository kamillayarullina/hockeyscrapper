**Team:**
(00:00)
Can we record the meeting so that the TA has access to it and the transcript is available in the repository?

**Customer:**

Okay, sure.

**Team:**
(00:03)
Thank you. Then we will start with the fact that Bulat is also with us today, he will show you how the parser works.

**Team:**
(00:13)
I will turn on the demonstration now. In general, as it turned out, the parser had a problem not with how it works, but with the protections that were in place on Yandex and on the KHL website. So we had to change the idea a bit. That is, now it simulates a real user so that there are no problems. Now I will launch the project, and we will see that notifications will arrive. Open your screen then. While we wait for the parser to work. And thanks to this, it was possible to fix it. And right now, matches have appeared on the KHL website, and on other sites as well. To be specific, on Ticket.KHL and on KHL itself. So, we see that the parsing went through, a match was found. There is even a link where you can buy tickets. This is from Ticket.Hockey. So, now we can say that KHL and Ticket.Hockey definitely work. It’s hard to say about Yandex and specifically club websites yet, because the match hasn’t appeared there yet. The only thing is that it immediately writes that there are no tickets, and as soon as they appear, it will send a new notification that tickets have become available.

**Customer:**
(01:39)
Do I understand correctly that this user is subscribed to the CSKA team?

**Team:**
(01:46)
Yes, yes, that is, he is subscribed only to CSKA, and accordingly, he receives only CSKA matches.

**Customer:**
(01:55)
And how many minutes are currently set for the search, well, for the parser's search work?

**Team:**
(02:07)
When launched, it simply searches, and then every 6 minutes. That is, I just launched the project, it was running before this. So, for each parser, TicketHockey, KHL, Yandex, and further specifically club websites. It is set like this. 30 minutes for the main websites where everything appears immediately, well, universal ones, because all teams are there, and club websites less frequently.

**Customer:**

Cool.

**Team:**
(02:42)
It immediately displays how many matches are currently found, how far it has progressed, and you can view the list of matches in the Telegram bot.

**Customer:**

Cool.

**Team:**
(2:57)
Do you have any questions regarding the parser?

**Customer:**
(03:00)
Well, some kind of negative case. I want to check if it works or not. If we subscribe to a team where we know for sure that there are no tickets on sale yet. Oh, tickets for sale specifically.

**Team:**
(03:17)
That is, a team that currently has no matches?

**Customer:**
(03:22)
Well, tickets for sale specifically not yet.

**Team:**
(03:27)
Ah, exactly. Well, here, for example, CSKA vs Torpedo, there are no tickets yet, just on the KHL website, well, now let’s go over, the match page has appeared, but tickets haven’t appeared yet. It just sends a link to the match for now, and as soon as a ticket appears, it will also see it and send a notification that a ticket has appeared.

**Customer:**
(03:47)
Understood, was the status written there as "no", right?

**Team:**
(03:51)
Yes, no tickets, and accordingly... only the information that is available is displayed.

**Customer:**
(4:00)
Okay, super.

**Team:**
(04:03)
So, that is, KHL and ticket.hockey definitely work. So, while we wait for appearances on club websites and on Yandex, because there seem to be no tickets there at all. Ah, and among the downsides, the parser is quite resource-intensive, because it directly emulates a user, and in terms of performance, it certainly requires a lot.

**Customer:**
(04:26)
And how exactly does it work?

**Team:**
(04:29)
Well, previously it used just Playwright, and the problem was that an error would just pop up, and it wouldn't find anything, because there was some protection there, and we had to use an additional library that specifically emulates mouse movements so that everything works, and therefore this is very resource-intensive. On Yandex too there was a problem that Yandex divides everything heavily by cities, and when the Yandex parser launches, it launches separately for each city, and therefore this all turned out to be very costly, and for now, if we optimize it somehow, think about it somehow, but for now it works like this.

**Customer:**
(05:25)
Well, super. I have no questions. I assume this is our final meeting with you, you already have a presentation scheduled?

**Team:**
(05:40)
Yes, this is the final meeting.

**Team:**
(06:00)
Can we ask you, before that, what you asked us to show what we did last week, you asked to change the monetization system.

**Customer:**
(06:19)
I also saw in Git that you implemented logout.

**Team:**
(06:30)
That is, we have, well, small features, when you enter a password, proper error messages are displayed, such small features, you can log out of your account, and respectively, how it works, that is, when a person wants to subscribe to any team, he subscribes, well, I have CSKA purchased, so nothing happened now, for Ak Bars, for example, subscribe, it redirects him immediately to the purchase page, supposedly purchasing a subscription, but here there is a warning, that is, a spoiler that we don't have anything, that this is all in test mode. And respectively, you can choose for a year, or you can choose for a month and enable auto-renewal. After that, one more spoiler, and that's it. And then you can go to separate pages where you can control which teams you are subscribed to, until what date they are valid, enable and disable auto-renewal.

**Customer:**
(07:42)
Super. Everything is great, as agreed last time.

**Team:**
(07:53)
Yes, super. Then we can ask you to try using this product, because we need this. That is, register there, or log in and try to subscribe to a team.

**Customer:**
(08:13)
Yes, please duplicate the link. Do you need me to show my screen or how?

**Team:**
(08:47)
Well, if possible, of course, it would be good, but if there is no possibility, no problem. Are you on a laptop or phone?

**Customer:**
(08:57)
From the laptop, I'll show now. Strange button text. To my paid teams. To my paid subscriptions.

**Team:**
(11:20)
Yes, just because subscriptions there translate specifically as receiving notifications. Paid teams. If you unsubscribe, the purchase remains. And to receive notifications again, you will need to select this team again. But repeated purchase will not occur. Only if the limit hasn't been exceeded. Less than 30 days have passed.

**Customer:**
(12:10)
Well, just if I unsubscribe, then probably Auto-renewal should turn off. Well yes, if I unsubscribe. Ah, although no, okay. Subscription means receiving notifications. Remind me how to access the admin panel, please. Just write admin here.

**Team:**
(13:20)
It won't work, because an admin account is needed. I can send you the credentials.

**Customer:**
(13:27)
Let's do that. If you have 10-20 minutes extra. You can add protection against logging out of the account. Just a confirmation. Are you sure you want to log out? An additional button. You showed it was 40. What changed?

**Team:**
(13:51)
Okay.

**Team:**
(14:21)
The parsers were working, and apparently some parser still found something somewhere. Try adding a subscription, the interface has changed now.

**Customer:**
(15:12)
Tell me about the ID, please. Why are some like this, others like that?

**Team:**
(15:21)
The long ones are those who linked Telegram, and this is their Telegram ID. And the negative ones are those who only registered on the website.

**Customer:**
(15:35)
And so first the ID is one, then it changes to such if I link Telegram?

**Team:**
(15:40)
Yes.

**Customer:**
(15:43)
Does this not break subscriptions in any way? If I first create an account, subscribe somewhere, and then link Telegram and my ID is applied?

**Team:**
(15:55)
I checked this, it's definitely not a problem.

**Customer:**
(16:00)
Good. What changes in the user interface if he is blocked?

**Team:**
(16:14)
In the interface specifically for the user, nothing changes, but he does not receive notifications.

**Customer:**
(16:40)
What is this? What kind of button is this? Test email.

**Team:**
(16:44)
To check if email sending works, but now it won't work, because not all data for email is entered in ENV, so it won't be able to send now.

**Customer:**
(17:19)
Can we somehow make it so that I receive notifications now?

**Team:**
(17:24)
Yes, I can. You can go to settings, clear matches, and I will restart the project now, and you will receive notifications. Then I am restarting the project now. Now we wait for the parser to find and send on the internet.

**Customer:**
(18:17)
Yes, it's coming. Mayor of Moscow Cup.

**Customer:**
(18:46)
And do you show the price in the bot notification? Is this the minimum?

**Team:**
(18:54)
Well, if there is some range there.

**Customer:**
(19:30)
And how does the parser understand, if it found a match, how does it understand if tickets are available or not?

**Team:**
(19:37)
The website also indicates ticket availability. If it didn't find anything at all about tickets, then there are no tickets. If it found that there are none, then there are no tickets. And if suddenly it has some problems, that is, something unclear, conditionally, there are tickets, but something unclear with availability, it writes "clarifying".

**Customer:**
(20:10)
Yes super, understood. And I even found such a notification. Cool, I have no more questions.

**Team:**
(20:30)
Good, excellent. Then you can tell us how you evaluate, that is, if anything is clear or unclear. Does this need to be redone, maybe?

**Customer:**
(20:40)
Well, for me, perhaps the only part of the project that I don’t understand is about proxies. What it does, how to configure it. Everything else is very, very clear. Nothing needs to be redone. Well, this improvement with logging out of the account, I would say, if it's not difficult to add, not necessary.

**Team:**
(21:16)
Okay.

**Customer:**
(20:20)
Well yes. Well okay, one more. The indentation here. Just make it bigger. Too close to the text. But it is optional.

**Team:**
(21:32)
Okay.

**Customer:**
(22:01)
You did everything very cool.

**Team:**
(22:05)
Excellent. Now we need to show the handover document. Right now. One second.

**Customer:**
(22:32)
I read it today actually.

**Team:**
(22:39)
Do you agree with it? Are there any questions about it?

**Customer:**
(22:47)
Well, of course, I haven't tried installing all this on my computer yet, but in general everything is described in great detail, and I think there will be no problems.

**Team:**
(22:59)
Yes, that is, here are the environment variables. Described. No objections? Good. We just need to ask this explicitly. Then one more question. How will the product transfer be carried out? That is, all environment variables are there. How to configure them? That is also in the document. And it turns out we need to transfer the repository to you, or how do you want to do this?

**Customer:**
(23:36)
Well, the repository... We seemed to agree at the very beginning that it would be open. If, of course, there is a possibility for me to somehow take ownership of it, then let's do it. Well, and here is the only bot, the bot is currently on your team account, as you write.

**Team:**
(23:55)
Yes, that is, we transfer both the bot and the repository to you. All good. And now another thing, we need to clarify with you, is the product fully ready for transfer?

**Customer:**
(24:25)
Yes, that's right. You guys are great, you handled everything.

**Team:**
(24:34)
Alright then, excellent, that is, the product is fully ready for transfer and we just need to transfer it to you. That's all then. Thank you.

**Customer:**
(24:46)
Good luck with the presentation on Tuesday. Thank you very much.

**Team:**

It was very pleasant to work with you. Thank you. Goodbye.

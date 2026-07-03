# Sprint Review Transcript

**Team**  
(00:05)  
Can we record the meeting so that the instructor has access to it and the transcript is in the repository?

**Customer**  
Yes, okay.

---

**Team**  
(10:46)  
Yes, good. So in this sprint we made the admin panel, and regarding how we slightly changed the design, we fixed it, made some things bigger, like with the teams - is everything okay with you now? And the admin panel - should we remove something, add something?

**Customer**  
(11:07)  
I'm looking now.

**Customer**  
(11:20)  
Have you already connected to the hockey ticket sales websites?

**Team**  
(11:25)  
Yes, so the parsers that are there now, they parse them, but there's nothing to parse yet. For now. But on test... There are three parsers. One is relatively universal - you can just add KHL club websites there. So specifically a specific club's website. That's the universal parser, that's one. And the other two are for separate sites - for Yandex Tickets and for KHL-Ticket. Two separate parsers for that. To make sure we don't miss anything anywhere. So for now the idea is that we collect from three different sources, so if something appears somewhere earlier, we get it earlier. But the only thing is that now we'll need to add all club websites under the parser.

**Customer**  
(12:44)  
And what logs will there be? What logs will be here?

**Customer**  
(12:53)  
Am I not showing? I just have a profile.

**Team**  
In the admin panel? All logs that go to the terminal are displayed here. So absolutely everything that... There's no specific filtering, absolutely everything.

**Customer**  
(13:29)  
This functionality confused me a bit. I just added this subscription 1, 2, 3. What is this addition for?

**Team**  
(13:40)  
Well, conditionally, when monetization appears. If there's some bug, conditionally, a person bought a subscription and suddenly it didn't appear, so that, well, support could, conditionally, do it manually.

**Customer**  
(14:03)  
Well, okay.

**Customer**  
(14:04)  
You just need to make sure that if I write nonsense, how it should react. If I write the team name in lowercase, uppercase, there will probably be different behavior.

**Team**  
(14:17)  
Yes, we'll work on that some more.

**Customer**  
(14:27)  
Now it will probably create two LADA subscriptions. Or does it give an error?

**Team**  
(14:33)  
Generally, well, there were some basic checks, but very basic.

**Customer**  
(14:38)  
Subscription already exists. Yes, but not here.

**Team**  
(14:45)  
Well, we'll deal with that. Then I'll pass the word to my colleague, he'll tell you about some other points.

---

**Team**  
(15:00)  
Hello, I'll show you the diagrams we made: static view, dynamic view, deployment view. This is what the static diagram looks like, there are parsers, websites we interact with, web user, Telegram. Can you see the demonstration?

**Customer**  
I can see it.

**Team**  
Is everything okay for you? Maybe you have some questions?

**Customer**  
(16:45)  
Can you just tell me about these different entities.

**Customer**  
(16:57)  
And I see different club parser, khl parser, yandex parser. Can you tell me more about them? So these are different websites that you scrape?

**Team**  
(17:24)  
Yes, that's exactly what I was talking about. That we have three different parsers for different purposes. Something for KHL ticket, something for Yandex, something just universal, for clubs.

**Customer**  
(17:45)  
Can you also tell me about the proxy rotator? What is it for and why can we change it through the admin panel?

**Team**  
(17:57)  
Well, it's needed to bypass captchas. If suddenly we get a captcha on one proxy, how does it work? It goes through all proxies and finds the one where it works. If it doesn't pass, it goes through absolutely all of them. And then it tries direct connection if nothing works. And that's exactly why we need it to find a working one. And if suddenly there are problems with specific ones, we can add a new one just in case.

**Customer**  
(18:28)  
And how is your scraping actually set up? Do you call the sites' APIs or, I don't know, use Selenium to click buttons and see if there's any info?

**Team**  
(18:40)  
We just read the JavaScript of the sites and look.

**Customer**  
(18:47)  
But to get to the page where they post these matches, tickets, you probably need to do some actions. Log into an account, for example.

**Team**  
(19:00)  
Regarding the account, I understand, there was no need to log into an account anywhere. It's clear that there are no tickets on the main page, but it goes through the nearest pages. There are some buttons. First, the link immediately leads not to the main site, but to the tickets section. And there it goes through the nearest pages. And looks at what's there.

**Customer**  
(19:33)  
And is this some universal method for all sites or is it customized because of, for example, URL problems? Somewhere you need to write "tickets" in the link, somewhere "ticket", somewhere add something else?

**Team**  
(19:53)  
No, well there specifically, for example, in Yandex there's a specific link to tickets.

**Customer**  
(20:00)  
Well yes, with Yandex and KHL I understand, but if you take, for example, there's the CSKA website, there's the SKA website.

**Team**  
(20:09)  
No, the club parser doesn't look, well specifically this parser that exists, it doesn't work by looking at all sites. You can add a site to it in the admin panel, well any, for example, CSKA. Give it a link, and it looks. It's relatively universal. Yes, specifically the club parser, I think we'll look at clubs. It's clear that the sites are different, well. Now it's relatively universal and works worst of all parsers, because it's hard to make something universal, for everything. So we'll either implement, well somehow, possibly divide clubs into groups where something is similar, something somehow, or already optimize for each separately and do it for each club separately.

**Customer**  
(21:05)  
Understood, I have no questions about the diagram.

---

**Team**  
Now I'll turn on another diagram, the parser cycle itself. Can you see the diagram?

**Customer**  
(21:40)  
I can see it.

**Team**  
Is everything okay for you?

**Customer**  
(22:08)  
Guys, you probably spent hours making this diagram and want me to come up with some question in 30 seconds. I can't do that quickly. Either you tell me the details, tell me about the processes, or give me a day to study it myself.

**Team**  
(22:48)  
The person who made this diagram couldn't attend the meeting now, so it's difficult for us to tell you something because we didn't work on it specifically. So let's do this. We'll send it to you separately and ask the person who worked on it to describe everything in a voice message.

**Customer**  
(23:21)  
Everything is good, everything is beautiful.

---

**Team**  
(23:29)  
Thank you. Well, the last point is about next week, the next sprint. We planned to start, at least try to make monetization and adapt the site for mobile devices. And, accordingly, fix bugs from your comments about the admin panel, of course.

**Customer**  
(23:53)  
I think you're wrong to leave the parser for last. This, I think, is actually the most difficult task of all the volumes.

**Team**  
(24:03)  
Well, there are just tasks that, well, conditionally, need to be delivered specifically this week. There are tasks that you can just do, conditionally, and just do them in the background. So if there are tasks that we definitely need to close in a week. Some such difficulties arise. It's clear that this is also being done. The parser is also touched sometimes, but it's clear that it's difficult to do in a week. So, possibly, something from this is not needed, or something, well, as you said, has higher priority, well, besides the parser.

**Customer**  
(24:47)  
No, parser is number one priority. Monetization is the last priority.

**Team**  
(24:58)  
We also have tests, CI tests, possibly some tests for some specific user actions, some specific tests needed, in general, to make.

**Customer**  
(25:23)  
I didn't understand the question.

**Team**  
(25:25)  
Well, we have a version of tests. Do we need to make some specific features specifically, are you interested in any specific ones? Under some specific scenarios.

**Customer**  
(25:40)  
Well, the key scenario, I think, should be covered by tests. Registration, subscription, subscription checkout, the scraping itself.

**Team**  
(25:48)  
Yes, well, there are already tests for all this. So, nothing else is needed?

**Customer**  
(25:58)  
And at what level - API and UI tests? Both, or units?

**Team**  
(26:05)  
Unit tests, CI tests we have. Do you have any questions, maybe?

**Customer**  
(26:19)  
No.

**Team**  
Well, then, that's all for today. Thank you for the meeting. Goodbye.

**Customer**  
Thank you. Yes, good. Goodbye.

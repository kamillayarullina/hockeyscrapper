
**Team**  
00:00
Can we record the meeting so that the TA has access to it and the transcript is available in the repository?

**Customer**
Okay, sure.

**Team**  
00:05 
Unfortunately, it turned out that... our canvas ended up on the Bulat branch. And on the main branch, something went wrong with the version. I don’t know why this happened; it occurred right after we pushed the changes.
00:24 
It just happened that way, so I’ll show you some parts of the feature locally and others on the main host, okay?

**Customer**
00:37 
- Yes, yes, of course.

**Team**  
00:40 
So, the first thing we did was instead of having an error window pop up for password issues, the message now appears directly on the website. Suppose I try to register here. I enter the password "one, two, three, a”
01:07 
Wait, no. That’s a bug on the live host. Let me go here "one, two, three, a” And there you go, instead of an ugly popup box, a message appears directly on the site saying: "Please use the required format," along with a description of what the password should look like.
01:38 
Then, if the format is correct—for example, "one, two, three, four, five, six, seven"—and a different password here.

**Team**  
01:50 
Here, the passwords don’t match. We’ll combine everything and make it work properly. It just broke at the last moment, so some things work and others don’t. This part is running locally.
02:17 
Now, the most important part is the monetization system. Let me show you.
02:35 
We’ve implemented subscription management. Regarding the monetization model: as we discussed, we decided that users get three free subscriptions. A person can freely subscribe to and unsubscribe from three teams without charge. However, when attempting to subscribe to a fourth team, a notification appears stating that the first three teams are free, but subscribing to the next team requires a payment of 39 RUB.
03:04 
We’ll discuss this further with you now, but I wanted to demonstrate. Since this is running locally, the payment will go through in this demo, but in reality... The payment process works, and it costs 39 RUB per month. If you try to pay again, a message will appear saying you are already subscribed. Let’s switch to Russian.
03:29 
From a separate window, you can manage and view which teams you are subscribed to and enable or disable auto-renewal. How does the system work? Instead of processing a one-time payment every time someone subscribes to a new team, all payments are handled through YooMoney via YooKassa. Rather than making individual one-time payments, upon the first purchase, the user’s account on the site is linked to their YooMoney account. Consequently, the user doesn’t need to re-enter card details. If they wish to enable or disable auto-renewal, they can do so easily.
04:22 
There is also a confirmation step to prevent accidental enabling of auto-renewal. Currently, this is how it works, but we still need API keys from YooKassa. To set up YooKassa, you need either an Individual Entrepreneur (IP) status or a legal entity. We don’t have that, so we wanted to ask if you could provide those credentials or if we should handle it ourselves somehow.

**Customer**
04:51 
Yes, let’s keep this part mocked for now. We won’t connect any real payment processing. You’ve built the functionality, I see it works great. The only thing is, I don’t recall specifying the requirement that the first three teams are free and the fourth is paid, but that’s okay.

**Team**  
05:09 
May I ask? How would you prefer it to be?

**Customer**
05:11 
Just make the very first subscription paid.

**Team**  
05:14 
So, the first one is already paid, right? Okay, got it.

**Customer**
05:18 
By the way, how are things going with the website scraping functionality?

**Team**  
05:26 
Well, we made changes. Previously, the interval could be set from 1 minute to 1440, but now we’ve changed it to range from 1 minute to 1999 minutes.

**Customer**
05:36 
No, I mean, for example, if I subscribe to a team, let’s say Ak Bars, what happens next? Will I receive a notification when tickets go on sale? Or have you not implemented that yet?

**Team**  
05:53 
Let me pass the word to my colleague now. Mute your microphone.

**Team**  
06:03 
Ah, yes.

**Team**  
06:08 
So, overall, we haven’t done anything with the Parser this week. That was scheduled for next week, so we’ll move that task to next week.

**Customer**
06:23 
Okay, okay, understood.

**Team**  
06:29 
So, how do you evaluate the monetization system? Do you like how it works?

**Customer**
06:42 
Yes, I saw the monetization part, it’s cool, guys. I really hope you manage to figure out the parsing by the end of next week.

**Team**  
06:54 
Yes, yes, of course, we will. Also, could you clarify again how the payment process should work? Should there be no actual payment processing at all? We could make it look realistic, so that when a person clicks the "Pay" button, instead of actually redirecting them to YooMoney, a message appears stating that no real monetary transactions are being conducted, everything is for educational purposes, and the payment is simulated.

**Customer**
07:37 
Yes, yes, let’s do it that way. Include a button like "Pay," and after clicking it, the subscription is created for the user.
07:51 
Exactly. So, no real money involved, no integration with YooKassa or YooMoney for now. Just display a text message explaining this.

**Team**  
08:03 
Ah, okay, great. We also need to ask you—is the product ready for handover in general? Well, not really ready yet. Okay.

**Customer**
08:20 
As I already mentioned, the most critical functionality I’m waiting for is the website parsing and receiving information about ticket availability. Once you implement that, then of course, it will be ready.

**Team**  
08:37 
Apart from that, do you have any other requests?

**Customer**
08:42 
Hmm, no, not for now. I don’t have access to my computer at the moment. If you’ve updated the host environment that you shared earlier, I’ll check it out tonight. If you haven’t updated it yet, please let me know when you do.

**Team**  
08:57 
Yes, let’s fix it and inform you when we upload the proper version. Also, we wanted to know if you used the system between our meetings?

**Customer**
09:12 
- I checked it out a bit after the meeting last week, but haven’t logged in since.

**Team**  
09:21 
Got it.

**Customer**
09:31 
- Well, you guys figured out the monetization really quickly, indeed. You made significant progress in just one week.

**Team**  
09:38 
Thank you. Yes, yes. Actually, the entire monetization system is ready. I even wanted to complete the full integration, but I couldn’t register with YooKassa. It turns out you need either a legal entity or an Individual Entrepreneur status, so it didn’t work out. Now, let me show you the documentation, and you can take a look, okay?

**Team**  
10:22 
So, currently... By documentation, we mean the README in the repository.
10:56 
This section describes how to launch the product on the server.

**Team**  
11:10 
This is also documentation. All tests, how everything works, how to test it, and the development history. Here is the diagram showing how it works; you’ve already seen it last week. And this is a description of the technologies used in the product.

**Team**  
12:03 
We can send you the link, and you can review the repository, documentation, and the custom handover plan, how the transfer will be carried out. Overall, that’s all for the documentation.

**Customer**
12:40 
Super. Alright then, guys, thank you very much for showing and explaining everything.

**Team**  
12:47 
Thank you very much for your time. One last clarification I wanted to ask: there is another option for monetization, such as a premium subscription. Instead of subscribing to each team individually, users could purchase a single subscription that grants access to any team. What do you think about that? Should we keep the current system or switch to this?

**Customer**
13:15 
Let’s keep the current system. Also, let’s slightly adjust the terms. For example, users could choose a monthly or yearly subscription, with the yearly price being ten times higher.

**Team**  
13:28 
Okay. Thank you very much. Goodbye.

Customer:
13:41 
- Bye everyone.


# Review transcript

00:01:26  
**Team:** Hello.

00:01:30

**Customer:** Hello.

00:01:32  
**Team:** So, today we want to show the deployed product and get some feedback. Before we start, can we record our conversation?

**Customer:** Yes.

**Team:** This product is already deployed on the Render website, so you can go to it.

00:02:07  
**Team:** So, we've implemented the main functionality: parser, registration, subscriptions.

00:02:32  
**Team:** Password recovery is still left. Email sending is not yet implemented. But we've started working on password recovery. I think password recovery is more important than email sending at the moment.

00:03:12  
**Team:** So, you can subscribe through the site. And also, if we connect Telegram now, all subscriptions will be both there and here. You can subscribe via Telegram as well as from here.

00:03:39  
**Customer:** And can I already go to this site myself?

00:03:42  
**Team:** For now it's on a rather weak server, it works very slowly, lags a lot.

00:04:09  
**Team:** Well, that is, here you can also subscribe to all teams. There is also an admin panel, so far only implemented in Telegram, you can change the parsing time, you can add or remove proxies. The only thing that needs improvement in the admin panel is that we can't manage the database at all.

00:04:40  
**Team:** We can't remove users, add them, change their passwords, while this is missing. We would like to ask how to implement this specifically for the admin panel, that is, to make a separate site, a separate bot, or leave it as is in this bot for now?

00:05:05  
**Customer:** Well, if you have time, you can make a separate admin panel website.

00:05:12  
**Team:** Okay.

00:05:17  
**Customer:** Well, in terms of functionality there I need to think.

00:05:26  
**Team:** Based on what you've seen, is there anything that might need to be changed or added?

00:05:41  
**Customer:** Well, I mentioned those icons last time.

00:05:44  
**Team:** We are actually doing that right now. We've been busy fixing bugs. During registration, if you specify Telegram without the @ symbol, it won't work. In general, we want to make it so that it doesn't matter how you specify it.

00:06:13  
**Customer:** But in the future. Also, I saw when you entered the password, I think during registration, it was three characters. Let's add some validation so that there are more characters.

00:06:24  
**Team:** By standard, at least eight characters and any letter of the English alphabet. That's fine. We will add icons to the site. As for the Telegram bot, icons there too.

**Customer:** No need.

00:06:57  
**Customer:** And in terms of parsing, have you tried interacting with any ticket sales website?

00:07:06  
**Team:** So far I've only tested on the All-Star match site. Now I want to try the same with the FIFA World Cup, test it on that.

00:07:36  
**Team:** Actually, on Yandex.Afisha there are tickets for the World Cup, and to check if there are any captcha issues when parsing every 30 minutes, for example. And we discussed that while the playoffs haven't started, once every 3 hours; if there are no problems every half hour, then every 3 hours will be even better.

00:08:01  
**Team:** The only thing we haven't tested yet is proxies. And in the near future we plan to deploy not through some external site but specifically on our own server.

00:08:33  
**Customer:** Okay. Can you send the link already?

00:08:36  
**Team:** Maybe we'll deploy to the server first, and then we'll send you a link for a smoother experience.

00:09:19  
**Team:** So, right now, after we finish the functionality, we'll start debugging some minor issues, that is, we need to test everything.

00:09:46  
**Team:** Regarding this 'Avatar' icon. We're thinking whether to remove it or add the ability to upload an avatar?

00:10:14  
**Customer:** Well, let it have avatars. With the ability to upload a picture.

00:10:17  
**Team:** Alright, good. Do you have any other questions?

00:10:25  
**Customer:** I think when I try out the site you'll send me, I'll have questions.

00:10:30  
**Team:** Okay, all right. Specifically about the functionality, what would you possibly like to see in a future version?

00:10:45  
**Customer:** I'll think about the admin panel, I'll write to you.

00:10:49  
**Team:** Okay. Then we have no questions for you. Thank you for the meeting.

00:10:58  
**Customer:** Yes, thank you too.


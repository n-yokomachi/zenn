---
title: "Got an Even G2? Build Your Own Apps! — Hands-on Impressions and Dev Tips"
emoji: "👓"
type: "idea"
topics: [aiagent, eveng2, smartglass, ai, sideproject]
published: true
---

## Introduction

I bought the Even G2 smart glasses from Even Realities, along with the Even R1 smart ring that controls them.
https://www.evenrealities.com/

In this post I'll share my impressions of the Even G2 and R1, plus some tips I picked up from building three small apps for them.

## Even G2 impressions

### From ordering to delivery

I ordered mine with prescription lenses, intending to wear them daily.
Since I hadn't bought glasses in about six years, I got an eye exam and a prescription beforehand.
Prescription lenses can be ordered online too.
I've seen posts from people who ordered prescription versions in physical stores and waited a month for delivery, but mine arrived in under two weeks.

Also, for the Even R1 you can have just the sizing kit sent first.
The R1 isn't only a controller for the G2 — it also does basic health tracking, so it's something you wear all the time.
To get a fit that's as close as possible, I'd say the sizing kit is essential when ordering online.
In my case, the R1 sizing kit arrived together with the Even G2, I confirmed my size online, and the R1 itself arrived about a week later.

https://x.com/_cityside/status/2057667597693599998

### In use

#### Looks
I'm not particularly knowledgeable about glasses, but the Even G2 comes in a Boston-ish Type A and a square-ish Type B.
I went with Type A. The frame design itself is restrained enough that it doesn't draw unwanted attention in everyday use.
The base of the temples and the part that hides behind your ears are a bit thick — you can tell that's probably where the battery and such are packed.
Also, with prescription lenses, the lenses get slightly thick. The outer surface sits one step lower than the frame, which I suspect is a trick to make them look thinner to others — but in exchange, the inner surface is flush with the frame, so the lenses sit closer to your eyes than usual.
(Sorry, this gets a little gross: since the lenses are close to your eyes, long eyelashes bump into them quite a bit. Eye gunk getting rubbed onto the lens by your lashes right after waking up… that kind of thing can happen.)

The R1 is about as thick as a typical smart ring, I'd say. I used to wear a cheap smart ring, and this one is thinner. It's recognizable as a smart ring at a glance, but the design isn't flashy, so it doesn't feel out of place at all in daily wear.

#### Comfort

There's some weight to it, naturally, but my point of comparison is featherweight glasses like JINS, so as smart glasses go I think these are remarkably light.
It probably varies by person, but my ears haven't gotten sore.
That said, adjusting the temple width seems difficult — there's not much flex — so if your head is on the wider side, they might be a bit tight.
For what it's worth, I think my head is fairly wide and I don't feel any squeezing.

The R1 is comfortable too. The cheap smart ring I used before had a sticky feel that made me give up on it; no such problem here.
One thing: the position of the touch panel used for control is fixed, so depending on how you operate it, you need to think about the angle you wear it at.
I wear the R1 on my index finger and operate it with my thumb — my thumb is short, so I rotate the ring slightly toward the thumb side.

#### The standard apps

The Even G2 ships with standard apps like a dashboard, phone notifications, a teleprompter, conversation transcription, translation, navigation, and an AI assistant.

##### Dashboard
The dashboard can show the current time, news, stock info, calendar, task list, and health info (R1 owners only, I think?).
Being able to read the news in random idle moments has turned out to be a surprisingly good experience.
If you link Google Calendar or similar, you can check your calendar there too.
The task list is managed inside the Even app, so external integration would be a nice addition.
I'd also love to be able to reorder the items — I rarely check stocks, so I'd put that at the very bottom.

##### Notifications
You can check your phone's notifications — email, X, and so on.
With the right settings, notifications show up on the glasses in real time as they arrive, so you don't have to pull out your phone for every little notification. That helps.
More than anything, notifications appearing in your field of view in real time is the part that feels the most like the future!

##### Teleprompter
Haven't properly used it yet. I'd like to try it at my next lightning talk.

##### Conversation support
A conversation transcription feature.
The accuracy is better than I expected. Usable day-to-day.
Though as someone who mostly works remotely, I'm usually listening through earphones, so I don't use it much…
On the train it's actually pretty nice: even when you're listening to music and miss the announcements, you can catch the next station info.

##### Translation
Haven't gotten to use it yet.

##### Navigation
I've only used it once so far, but the accuracy seemed a bit off?
Maybe I was using it wrong?

##### AI assistant
Say "Hey, Even" and the AI assistant comes up.
It does seem to keep the session's conversation history, but you have to say the "Hey, Even" wake word every single time you talk to it.
It also doesn't integrate with your calendar or email, so it can't check or change your schedule.
It can create task list entries, but for now it's not all that convenient.
That's part of why I'm building an app to talk to my own AI agent — more on that below.

#### Even Hub
Beyond the standard apps, third-party apps are distributed and easy to install.
There's already a decent number of apps, so it's fun to take a look.
You can also mark an app as fully private or as a beta open to specific users, so you can upload your own app to Even Hub and keep it just for yourself.

### Terminal Mode

The Even G2 can connect to Claude Code or Codex running on a PC that shares the same network.
OpenClaw is apparently supported too (though I haven't tried it).
You send instructions by voice and read the responses right on the glasses. The display area isn't large, though, so I think it suits schedule/task support and PC operations better than coding tasks.
Terminal Mode itself works more normally than I expected and can be genuinely handy at times, but normal mode and Terminal Mode can only be switched from the phone, which is the one inflexible part.
So — from here, let me talk about the app I built to talk to my own agent from a normal-mode app.

## App development

### An AI agent interface app

As mentioned above, Even AI can't integrate with external services, and Terminal Mode takes annoying setup — so I built a personal app for talking to my AI agent.
I normally run my agent on a MacBook, and the app lets me talk to it using the Even G2's voice input.

![](/images/202606_eveng2_app/image2.jpeg)

https://x.com/_cityside/status/2061510087664152952

The processing flow looks like this:

Launch the app and speak from the Even G2 (glasses)
→ The audio is forwarded to the MacBook
→ Whisper large-v3-turbo runs STT (speech-to-text) on the MacBook
→ The transcript is sent as a request to the local agent
→ The response is rendered on the Even G2 display

The app itself is a two-layer setup: an Even Hub app on the glasses side, and a resident bridge on the Mac.
The phone and the Mac are connected over Tailscale, so it works as-is even outside my home Wi-Fi.
For STT I use Whisper running locally on the Mac.

Transcription and the agent request are also split into two phases, so on the glasses the display updates in stages: "Transcribing" → what I said → "Thinking" → the answer.
Agent responses can take tens of seconds depending on the request, and without this kind of feedback you can't tell whether it's working or frozen.
Conversations also continue as a session, so exchanges that build on earlier turns work fine.

### A Papyrus-style dating app

https://github.com/n-yokomachi/eg2-date-with-cool-skeleton

The second one is a joke app.
The game UNDERTALE has an event where you go on a date (?) with a character called Papyrus, and I recreated that dating screen's UI on the Even G2.

![](/images/202606_eveng2_app/image3.gif)

https://x.com/_cityside/status/2063559280859738601

Under the hood it's a display-only, fully local app — no backend, no network.
The animations aren't rendered at runtime; it just sends images in sequence, like a flip-book.

### An anger management app

https://github.com/n-yokomachi/eg2-anger-management

The third one is also a joke app.
In Japan people often say "anger peaks for six seconds," and in the US it's "count to ten" — so I made an app that you launch when you feel angry, and it just counts.

> **Note**: This one I went ahead and published on Even Hub for no particular reason, so if you have an Even G2, feel free to search for "Anger Management".

![](/images/202606_eveng2_app/image4.gif)

https://x.com/_cityside/status/2065061822294835381

In the settings you can switch between Japan mode (a 6→1 countdown) and America mode (a 1→10 count-up).
When the count finishes, it randomly shows either an anger-management quote from a famous figure or a flashy "ANGER MANAGED" finisher to cool you down.
By the way, as far as I could tell, neither "six seconds" nor "count to ten" has any solid academic basis. Folk wisdom.

### App development tips

Finally, here are the constraints and lessons I learned from building these three apps.

> **Note**: This is as of June 2026. Things may change with future updates.

#### Up to 4 image containers at a time

The glasses display seems to hold at most 4 image containers at once.
The SDK simulator will happily show around 6, so something that works fine during development can break once you build it — watch out for this.

#### You have to bring your own STT (speech-to-text)

The Even G2's standard apps can do speech recognition, but that STT isn't available through the SDK.
All you can get from the SDK is the raw PCM from the microphone, so if you want to handle voice input, you need to provide STT yourself.
For my AI agent app, I forward the PCM as-is to a Mac and transcribe it with the MLX version of Whisper.

#### No hold gesture

The standard apps on the Even G2 use hold gestures, but the input events available to the SDK are just tap, double tap, and swipe up/down.
Incidentally, the R1 ring and the touch panel on the glasses' temple both deliver the same kinds of events.

#### BLE bandwidth is narrow, so frequent image updates are heavy

The glasses and the phone are connected over BLE, and the bandwidth is quite narrow.
Send images too frequently and the transfer backs up, rendering freezes, and in the worst case the BLE connection drops entirely.

#### There's a simulator, so development is surprisingly comfortable

An official simulator (evenhub-simulator) is provided, and you can iterate on screen rendering and input events without the hardware.
That said, device-specific behavior like the BLE bandwidth above isn't reproduced in the simulator, so a final check on the real device is a must.

## Wrapping up

So that's my (rather text-heavy) tour of the Even G2 and the apps I built for it.
I haven't managed to build anything that useful yet, so I'd like to come up with something next.

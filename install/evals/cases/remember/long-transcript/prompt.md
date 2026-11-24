remember this call transcript:

# Revenue Team Weekly

## Meeting metadata

- **Scheduled:** 2026-10-21T14:00:00Z → 2026-10-21T15:00:00Z
- **Recorded:** 2026-10-21T14:00:45Z → 2026-10-21T15:12:55Z
- **Recorded by:** Sam Rivera
- **Transcript language:** en

## Participants

- Dana Kim (internal)
- Marcus Webb (internal)
- Priya Nair (internal)
- Owen Fletcher (internal)
- Hannah Cole (internal)
- Theo Grant (internal)
- Nadia Brooks (internal)
- Tomas Berg (internal)
- Ruth Adeyemi (internal)
- Leo Marsh (internal)
- Sam Rivera (internal)

## Summary

### Meeting purpose

Walk through the new inbound lead routing flow, review the open pipeline account by account, and introduce a discovery question sheet.

### Key takeaways

- **Lead routing:** inbound leads get an owner within minutes by territory, then account ownership, then a round robin of available people. An open first-touch task escalates to the team lead after two hours and goes back to the round robin after a day.
- **Rollout:** the rules are replayed against last month's leads in a sandbox. Each AE checks their own patch, then the flow goes live in the Nordics for a week before the other regions.
- **Pipeline:** forty accounts reviewed in three-minute slots. Most risk sits in security reviews, procurement and next-year budgets.
- **Discovery sheet:** one page, four buyer roles, three questions each. The team uses it on real first calls this week and role-plays it next week.

### Topics

- Speed to lead: measure from the routing timestamp, not the created date.
- Trial sign-ups move to routing in phase two, gated on a usage signal.
- The sandbox tenant is slow during the nightly reindex; warn the solutions engineer before a live demo.
- A new AE joined the team this week.

## Action items

- Share the sandbox routing comparison with each AE — Sam Rivera
- Add the speed-to-lead note to the routing timestamp field description — Sam Rivera
- Set the escalation digest to two messages a day — Sam Rivera
- Add the architect data question to the sheet — Ruth Adeyemi
- Write two role-play scenarios for next week — Ruth Adeyemi
- Use the discovery sheet on at least one first call this week — all AEs
- Move the nightly reindex job out of working hours — Theo Grant

## Transcript (395 segments)

**[00:00:00] Dana Kim:** Hi everyone. Give it a minute, a few people are still joining.

**[00:00:05] Marcus Webb:** Morning. Or afternoon, depending on where you are.

**[00:00:08] Dana Kim:** Afternoon for most of us. Owen, can you hear us okay? Your first one of these, right?

**[00:00:15] Owen Fletcher:** Yeah, I can hear you fine. First one, yes. I'm mostly going to listen today.

**[00:00:21] Dana Kim:** Good. Nobody bites. We'll do introductions properly at the end, I don't want to burn the first ten minutes on it.

**[00:00:29] Ruth Adeyemi:** Can someone drop the agenda in the chat? I lost the invite somewhere in my inbox.

**[00:00:36] Sam Rivera:** Dropped it. Three things today. The new lead routing flow, the pipeline walk, and Ruth's discovery question sheet.

**[00:00:43] Dana Kim:** Thanks, Sam. And I want to keep the pipeline walk tight. Last week it ate the whole hour and we never got to anything else.

**[00:00:52] Leo Marsh:** That was mostly my fault. I had too many updates on the insurance accounts.

**[00:00:58] Dana Kim:** It was everyone's fault. We'll timebox each account. If it needs more than three minutes, it goes to a follow-up.

**[00:01:05] Theo Grant:** Can I flag one thing before we start? The sandbox tenant is running slow again, so if anyone is doing a live demo this week, warn me first.

**[00:01:16] Dana Kim:** Noted. Is that the same problem as last month?

**[00:01:20] Theo Grant:** Same symptoms. I think it's the nightly reindex job overlapping with working hours in APAC. I'm looking at it.

**[00:01:27] Marcus Webb:** I have a demo on Thursday, so I'll ping you.

**[00:01:31] Theo Grant:** Please do. I'd rather move the job than have you sit on a spinner in front of a buyer.

**[00:01:39] Dana Kim:** Okay. Sam, over to you for the routing flow.

**[00:01:43] Sam Rivera:** Sure. Let me share my screen. Can everyone see the diagram?

**[00:01:47] Leo Marsh:** Yes, it's a bit small but readable.

**[00:01:50] Sam Rivera:** I'll zoom in. Better?

**[00:01:53] Ruth Adeyemi:** Much better.

**[00:01:54] Sam Rivera:** So, the background. Today an inbound lead lands in the CRM, sits in a shared queue, and someone on the team picks it up when they have time. We measured it last quarter. The median time from form fill to first touch was a bit over two days, and for leads that came in on a Friday it was closer to four. That's too slow. The buyers who fill in a demo form are talking to two or three vendors at the same time, and whoever answers first usually gets the first meeting. The new flow replaces the shared queue with routing rules, so every lead has an owner within minutes, not days.

**[00:02:34] Dana Kim:** And the owner is decided how? Territory?

**[00:02:38] Sam Rivera:** Territory first, then account ownership, then a round robin as the fallback. If the lead's company is already an account with an owner, it goes to that owner, full stop. If it's a new company, we look at the region and the employee band. Enterprise companies in the region go to the named AE for that patch. Everything else goes into a round robin between the people who are marked as available that day. Availability comes from the calendar, so if you're on holiday you drop out of the rotation automatically.

**[00:03:10] Marcus Webb:** What happens if the account owner is on holiday? Does it still go to them?

**[00:03:16] Sam Rivera:** Good question. Right now, yes, it still goes to the owner, but they get a notification and so does their backup. Each AE names a backup in their user record. I'll send a note asking everyone to fill that in this week, because about half of the backup fields are empty.

**[00:03:35] Leo Marsh:** Is the backup per person or per account?

**[00:03:38] Sam Rivera:** Per person. Per account would be more precise but nobody would maintain it. We tried that two years ago with partner owners and the field went stale in a month.

**[00:03:50] Ruth Adeyemi:** From the marketing side, what do we see? Do we still get the lead source and the campaign?

**[00:03:57] Sam Rivera:** Yes. Nothing changes on attribution. The lead keeps its source, its campaign and its first touch. The only new fields are the routing reason and the routing timestamp, so we can measure speed to lead without guessing. If you build a report on speed to lead, use the routing timestamp as the start, not the created date, because imports can create a record hours before it's routed.

**[00:04:21] Ruth Adeyemi:** Okay, that's useful. Can you put that in the field description so people don't get it wrong in six months?

**[00:04:29] Sam Rivera:** I'll do that. Next part is the first touch. When a lead is routed, the owner gets a task with a two hour due time during working hours. If the task is still open after two hours, it escalates to Dana. If it's still open after a day, the lead goes back into the round robin and the original owner gets a polite message. I know that sounds harsh, but the point is that no lead sits for four days again.

**[00:04:58] Owen Fletcher:** Two hours in working hours of the owner, or of the lead?

**[00:05:03] Sam Rivera:** Of the owner. We thought about the lead's time zone, but it got complicated fast, and most of our leads are in the same two or three time zones as the people who own them anyway.

**[00:05:16] Theo Grant:** Side note: I'll rebuild the Initech demo environment before their pilot starts.

**[00:05:21] Dana Kim:** I'm fine with the escalation coming to me. But I don't want fifty notifications a day. Can it be a digest?

**[00:05:29] Sam Rivera:** It can be a digest. I'll set it to one message at eleven and one at four, with the list of overdue leads. If something is really urgent you'll still see it in the queue view.

**[00:05:42] Theo Grant:** Does any of this touch the trial sign-ups? Those come in through a different form.

**[00:05:48] Sam Rivera:** Trials are in scope for phase two, not now. Trial sign-ups go through a product qualification step first, because a lot of them are students or people testing on a personal email. Phase two adds a usage signal, so a trial that actually creates a project and invites a colleague gets routed like a demo request. A trial that does nothing stays in the nurture track.

**[00:06:12] Marcus Webb:** I like that. Half the trials I get are people who never logged in twice.

**[00:06:18] Sam Rivera:** That's what the data says too. Roughly one in five trials does anything meaningful in the first week. Those are the ones worth a human.

**[00:06:28] Dana Kim:** What's the plan for testing this before it goes live? I don't want to find out on a Monday morning that every lead went to Leo.

**[00:06:38] Leo Marsh:** I wouldn't complain.

**[00:06:39] Sam Rivera:** We have a sandbox copy with last month's leads replayed through the rules. I'll share the comparison: where each lead went under the old process and where it would go now. I want each of you to look at your own patch and tell me if anything looks wrong. Then we turn it on for one region for a week, check the numbers, and roll it out to the rest.

**[00:07:05] Ruth Adeyemi:** Which region first?

**[00:07:06] Sam Rivera:** The smallest one, so mistakes are cheap. Nordics. Then the rest the following week if the numbers hold.

**[00:07:14] Dana Kim:** Okay. Any other questions for Sam? No? Good. Thanks, Sam, that's clear. Let's do the pipeline.

**[00:07:20] Dana Kim:** Northwind Traders. Leo, go ahead.

**[00:07:22] Leo Marsh:** On Northwind Traders, honestly, it's been slower than I wanted. We're in procurement and have been for three weeks. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Mira got budget for a data project in September. Their main use case is search over internal documents for the support team. They estimate it would save each agent around an hour a day, and they've done the maths on it themselves, which helps. The number is about 40 thousand for the first year, with a close in March if nothing slips. The open item is that procurement wants three quotes. I think we can solve it, but I need some help from the team. Competition-wise, it's nobody yet, as far as we know. Next step is to send the reference customer intro, and I want that done by the end of next week.

**[00:08:17] Dana Kim:** How confident are you, honestly, out of ten?

**[00:08:21] Leo Marsh:** Seven. Maybe a six until I see the security answers go through.

**[00:08:26] Theo Grant:** I looked at the data sample from Northwind Traders. It's messier than they said, but nothing we haven't handled before.

**[00:08:33] Leo Marsh:** Yes, please join.

**[00:08:35] Dana Kim:** Okay. Let's send the reference customer intro and look at it again next week.

**[00:08:41] Dana Kim:** Okay, Fabrikam. Who has that one? Leo, right?

**[00:08:44] Leo Marsh:** On Fabrikam, honestly, it's been slower than I wanted. We're in technical validation and have been for three weeks. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. On the last call they spent most of the time on how the rollout would work across their regions. They want to start with one team and expand, which fits how we usually land. The number is about 40 thousand for the first year, with a close in December if nothing slips. The open item is that they want a reference customer in their industry. I think we can solve it, but I need some help from the team. They mentioned a smaller open source shop as the alternative, but they didn't sound excited about it. Next step is to run the pilot kickoff, and I want that done by the end of next week.

**[00:09:42] Dana Kim:** What does the mutual plan look like? Is there one?

**[00:09:46] Leo Marsh:** There's a draft. They haven't signed off on it, but they've added their own dates, which is a good sign.

**[00:09:54] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:09:59] Dana Kim:** Okay, Tailspin Toys. Who has that one? Nadia, right?

**[00:10:03] Nadia Brooks:** Quick one on Tailspin Toys. Still in discovery, nothing dramatic since last week. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Daniel got budget for a data project in September. The technical team likes it. The question is whether the business side sees it as a priority this year or something for next year. We're forecasting 240 thousand, closing in January. I'd call it commit, but I'm not putting it in commit until I see the paper. The open item is that they need a data residency answer. I think we can solve it, but I need some help from the team. They mentioned a smaller open source shop as the alternative, but they didn't sound excited about it. Next step is to send the revised order form, and I want that done by the end of next week.

**[00:10:57] Dana Kim:** Is that date real, or is that our date?

**[00:11:01] Nadia Brooks:** It's their date. They have a board meeting in January and they want this approved before it.

**[00:11:08] Dana Kim:** And if that doesn't move, what's plan B?

**[00:11:11] Nadia Brooks:** Plan B is to split the deal: start with a smaller scope that doesn't need the full approval, and expand once they see results. I've floated it with Daniel, who didn't hate it.

**[00:11:23] Theo Grant:** On the technical side for Tailspin Toys, they asked about running it in their own cloud account. That's fine, I can show them the deployment guide.

**[00:11:33] Nadia Brooks:** Thanks, that helps.

**[00:11:35] Dana Kim:** Fine. Keep it in best case for now.

**[00:11:39] Dana Kim:** Wingtip Toys. Nadia, go ahead.

**[00:11:41] Nadia Brooks:** So Wingtip Toys. We're in security review. On Monday I spoke to Mira, who runs the analytics team, and the tone was positive. We've had a relationship with them for a while through a partner, but this is the first time we're selling to them directly. The technical team likes it. The question is whether the business side sees it as a priority this year or something for next year. Value is around 120 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. Main blocker: IT has a change freeze until the new year. We've seen this before with similar companies and it usually works out. On competition, they're also looking at nobody yet, as far as we know. Next step is to run the pilot kickoff, and I want that done by the end of next week.

**[00:12:33] Dana Kim:** Have we met anyone above Mira yet?

**[00:12:36] Nadia Brooks:** Once, briefly, on the first call. I want to get back in front of them before the proposal.

**[00:12:43] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:12:48] Nadia Brooks:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:12:57] Sam Rivera:** On Wingtip Toys, I see two open opportunities for the same product. One of them should probably be closed as a duplicate.

**[00:13:05] Nadia Brooks:** Sorry, I'll sort it.

**[00:13:07] Dana Kim:** Okay. Let's run the pilot kickoff and look at it again next week.

**[00:13:12] Dana Kim:** Next is Adventure Works. Marcus, yours?

**[00:13:15] Marcus Webb:** So Adventure Works. We're in procurement. On Monday I spoke to Grace, their VP of operations, and the tone was positive. This one started as an inbound demo request. They had already tried to build something themselves and gave up after six months, so they know the problem well. They want a proof of value on their own data before they sign. I've scoped it at four weeks with clear success criteria written down up front. Value is around 120 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. The risk is that IT has a change freeze until the new year. I've asked them how they want to handle it, and I'm waiting to hear back. They mentioned one of the big cloud vendors as the alternative, but they didn't sound excited about it. What I need to do now is send the reference customer intro. Then we should know where we stand.

**[00:14:13] Dana Kim:** Is that date real, or is that our date?

**[00:14:17] Marcus Webb:** It's their date. They have a board meeting in December and they want this approved before it.

**[00:14:24] Dana Kim:** Fine. Keep it in best case for now.

**[00:14:27] Dana Kim:** Next is Litware. Marcus, yours?

**[00:14:29] Marcus Webb:** Litware, we moved it to discovery on Friday. Victor, the platform lead pulled two more people into the last call, which I take as a good sign. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. The technical team likes it. The question is whether the business side sees it as a priority this year or something for next year. Value is around 240 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. Main blocker: the champion is going on leave. We've seen this before with similar companies and it usually works out. Competition-wise, it's one of the big cloud vendors. What I need to do now is send the revised order form. Then we should know where we stand.

**[00:15:22] Dana Kim:** What would make this slip into next quarter?

**[00:15:26] Marcus Webb:** If the blocker drags on, it slips. Everything else is under control.

**[00:15:31] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:15:36] Marcus Webb:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:15:44] Dana Kim:** Okay. Let's send the revised order form and look at it again next week.

**[00:15:50] Dana Kim:** Okay, Proseware. Who has that one? Nadia, right?

**[00:15:53] Nadia Brooks:** So Proseware. We're in security review. On Monday I spoke to Grace, their VP of operations, and the tone was positive. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Grace got budget for a data project in September. They're asking for a fixed price for the first year and usage pricing after that. I said I'd check with Dana before I commit to anything. It's 150 thousand on the opportunity. The date says December, and I think that's realistic if we keep the momentum. The risk is that legal wants changes to the liability cap. I've asked them how they want to handle it, and I'm waiting to hear back. On competition, they're also looking at their incumbent consultancy. Next step is to run the pilot kickoff, and I want that done by the end of next week.

**[00:16:47] Dana Kim:** Is that date real, or is that our date?

**[00:16:51] Nadia Brooks:** It's their date. They have a board meeting in December and they want this approved before it.

**[00:16:57] Dana Kim:** Do you need anything from me or from Theo on this one?

**[00:17:02] Nadia Brooks:** Maybe Theo on the next technical call. Otherwise I'm fine for now, I'll shout if that changes.

**[00:17:09] Dana Kim:** Fine. Keep it in best case for now.

**[00:17:13] Dana Kim:** Woodgrove Bank. Leo, go ahead.

**[00:17:15] Leo Marsh:** So Woodgrove Bank. We're in negotiation. On Monday I spoke to Victor, the platform lead, and the tone was positive. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Victor got budget for a data project in September. Their main use case is search over internal documents for the support team. They estimate it would save each agent around an hour a day, and they've done the maths on it themselves, which helps. It's 180 thousand on the opportunity. The date says December, and I think that's realistic if we keep the momentum. Main blocker: the champion is going on leave. We've seen this before with similar companies and it usually works out. On competition, they're also looking at an in-house build. Next step is to run the pilot kickoff, and I want that done by the end of next week.

**[00:18:10] Dana Kim:** Have we met anyone above Victor yet?

**[00:18:13] Leo Marsh:** Once, briefly, on the first call. I want to get back in front of them before the proposal.

**[00:18:20] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:18:25] Leo Marsh:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:18:33] Sam Rivera:** For Woodgrove Bank, the opportunity has no contact roles. Can you add Victor as the champion? The pipeline report filters on it.

**[00:18:42] Leo Marsh:** Sorry, I'll sort it.

**[00:18:44] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:18:49] Dana Kim:** Next is Lucerne Publishing. Marcus, yours?

**[00:18:51] Marcus Webb:** Quick one on Lucerne Publishing. Still in technical validation, nothing dramatic since last week. We've had a relationship with them for a while through a partner, but this is the first time we're selling to them directly. They're asking for a fixed price for the first year and usage pricing after that. I said I'd check with Dana before I commit to anything. We're forecasting 150 thousand, closing in January. I'd call it commit, but I'm not putting it in commit until I see the paper. The risk is that IT has a change freeze until the new year. I've asked them how they want to handle it, and I'm waiting to hear back. Competition-wise, it's their incumbent consultancy. Next step is to send the revised order form, and I want that done by the end of next week.

**[00:19:41] Dana Kim:** How confident are you, honestly, out of ten?

**[00:19:45] Marcus Webb:** Seven. Maybe a six until I see the security answers go through.

**[00:19:49] Dana Kim:** And if that doesn't move, what's plan B?

**[00:19:53] Marcus Webb:** Plan B is to split the deal: start with a smaller scope that doesn't need the full approval, and expand once they see results. I've floated it with Victor, who didn't hate it.

**[00:20:05] Theo Grant:** For Lucerne Publishing, I'd like to be on the next call. Their questions last time were about latency and I think I can answer them better live.

**[00:20:15] Marcus Webb:** Yes, please join.

**[00:20:17] Dana Kim:** Thanks. Next.

**[00:20:19] Dana Kim:** Next is Coho Winery. Marcus, yours?

**[00:20:21] Marcus Webb:** Coho Winery, we moved it to technical validation on Friday. Rafael, the data platform owner pulled two more people into the last call, which I take as a good sign. They came in through a webinar about a year ago. The first project died when their sponsor left, and this is the second attempt with a new team. They're asking for a fixed price for the first year and usage pricing after that. I said I'd check with Dana before I commit to anything. The number is about 240 thousand for the first year, with a close in March if nothing slips. Main blocker: the budget sits in next year's plan. We've seen this before with similar companies and it usually works out. Competition-wise, it's one of the big cloud vendors. Next step is to book the technical deep dive, and I want that done by the end of next week.

**[00:21:15] Dana Kim:** Do they understand the pricing, or are we going to get a surprise in negotiation?

**[00:21:21] Marcus Webb:** I walked them through it twice. They know the list price and they know the discount we usually give. No surprises, I hope.

**[00:21:30] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:21:35] Marcus Webb:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:21:43] Theo Grant:** I looked at the data sample from Coho Winery. It's messier than they said, but nothing we haven't handled before.

**[00:21:51] Marcus Webb:** Great, I'll add you to the invite.

**[00:21:54] Dana Kim:** Thanks. Next.

**[00:21:56] Dana Kim:** Okay, Fourth Coffee. Who has that one? Nadia, right?

**[00:22:00] Nadia Brooks:** Fourth Coffee, we moved it to negotiation on Friday. Victor, the platform lead pulled two more people into the last call, which I take as a good sign. They came in through a webinar about a year ago. The first project died when their sponsor left, and this is the second attempt with a new team. They're asking for a fixed price for the first year and usage pricing after that. I said I'd check with Dana before I commit to anything. It's 75 thousand on the opportunity. The date says January, and I think that's realistic if we keep the momentum. The open item is that their security team has a long questionnaire. I think we can solve it, but I need some help from the team. They mentioned a smaller open source shop as the alternative, but they didn't sound excited about it. My next step is to send the revised order form. I've got a slot pencilled in for Tuesday.

**[00:22:58] Dana Kim:** Is that date real, or is that our date?

**[00:23:01] Nadia Brooks:** It's their date. They have a board meeting in January and they want this approved before it.

**[00:23:08] Dana Kim:** When did you last speak to Victor?

**[00:23:11] Nadia Brooks:** Yesterday, actually. Quick call. Victor is chasing internally and promised an update by Friday.

**[00:23:17] Sam Rivera:** On Fourth Coffee, I see two open opportunities for the same product. One of them should probably be closed as a duplicate.

**[00:23:25] Nadia Brooks:** Will do.

**[00:23:27] Dana Kim:** Fine. Keep it in best case for now.

**[00:23:30] Dana Kim:** Alpine Ski House. Leo, go ahead.

**[00:23:33] Leo Marsh:** Alpine Ski House, we moved it to security review on Friday. Lena, the head of customer support pulled two more people into the last call, which I take as a good sign. We've had a relationship with them for a while through a partner, but this is the first time we're selling to them directly. On the last call they spent most of the time on how the rollout would work across their regions. They want to start with one team and expand, which fits how we usually land. It's 40 thousand on the opportunity. The date says March, and I think that's realistic if we keep the momentum. The open item is that procurement wants three quotes. I think we can solve it, but I need some help from the team. Competition-wise, it's a smaller open source shop. My next step is to get the security answers back to them. I've got a slot pencilled in for Tuesday.

**[00:24:30] Dana Kim:** What does the mutual plan look like? Is there one?

**[00:24:34] Leo Marsh:** There's a draft. They haven't signed off on it, but they've added their own dates, which is a good sign.

**[00:24:42] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:24:47] Leo Marsh:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:24:55] Dana Kim:** Fine. Keep it in best case for now.

**[00:24:58] Dana Kim:** Next is Trey Research. Leo, yours?

**[00:25:01] Leo Marsh:** Quick one on Trey Research. Still in security review, nothing dramatic since last week. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. They had a bad experience with a vendor who oversold, so they're very careful. Everything we say has to be backed by a demo or a reference. Value is around 60 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. Main blocker: legal wants changes to the liability cap. We've seen this before with similar companies and it usually works out. Competition-wise, it's nobody yet, as far as we know. My next step is to send the revised order form. I've got a slot pencilled in for Tuesday.

**[00:25:51] Dana Kim:** Who signs, though? Do we know the economic buyer yet?

**[00:25:55] Leo Marsh:** Not directly. Mira says it's the CFO, but I haven't been in a room with the CFO yet. I'm asking for that meeting on the next call.

**[00:26:05] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:26:10] Leo Marsh:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:26:19] Sam Rivera:** For Trey Research, the opportunity has no contact roles. Can you add Mira as the champion? The pipeline report filters on it.

**[00:26:27] Leo Marsh:** Sorry, I'll sort it.

**[00:26:29] Dana Kim:** Thanks. Next.

**[00:26:31] Dana Kim:** Next is Humongous Insurance. Nadia, yours?

**[00:26:33] Nadia Brooks:** On Humongous Insurance, honestly, it's been slower than I wanted. We're in technical validation and have been for three weeks. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. They had a bad experience with a vendor who oversold, so they're very careful. Everything we say has to be backed by a demo or a reference. Value is around 75 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. Main blocker: IT has a change freeze until the new year. We've seen this before with similar companies and it usually works out. They mentioned a smaller open source shop as the alternative, but they didn't sound excited about it. What I need to do now is get a mutual action plan signed off. Then we should know where we stand.

**[00:27:30] Dana Kim:** Is that date real, or is that our date?

**[00:27:34] Nadia Brooks:** It's their date. They have a board meeting in January and they want this approved before it.

**[00:27:40] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:27:45] Nadia Brooks:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:27:54] Sam Rivera:** Just so you know, Humongous Insurance came in through the partner form, so the partner field needs to stay filled in, or the partner team loses the credit.

**[00:28:04] Nadia Brooks:** Will do.

**[00:28:06] Dana Kim:** Okay. Let's get a mutual action plan signed off and look at it again next week.

**[00:28:12] Dana Kim:** Next is Wide World Importers. Marcus, yours?

**[00:28:15] Marcus Webb:** Wide World Importers, we moved it to procurement on Friday. Lena, the head of customer support pulled two more people into the last call, which I take as a good sign. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Lena got budget for a data project in September. They had a bad experience with a vendor who oversold, so they're very careful. Everything we say has to be backed by a demo or a reference. The number is about 150 thousand for the first year, with a close in December if nothing slips. The thing that worries me is that the budget sits in next year's plan. It's not a deal breaker, but it adds weeks. On competition, they're also looking at an in-house build. What I need to do now is get a mutual action plan signed off. Then we should know where we stand.

**[00:29:12] Dana Kim:** Who signs, though? Do we know the economic buyer yet?

**[00:29:16] Marcus Webb:** Not directly. Lena says it's the CFO, but I haven't been in a room with the CFO yet. I'm asking for that meeting on the next call.

**[00:29:26] Sam Rivera:** Just so you know, Wide World Importers came in through the partner form, so the partner field needs to stay filled in, or the partner team loses the credit.

**[00:29:37] Marcus Webb:** Yes, I'll fix that today.

**[00:29:39] Dana Kim:** Okay. Let's get a mutual action plan signed off and look at it again next week.

**[00:29:46] Dana Kim:** Next is Southridge Video. Marcus, yours?

**[00:29:49] Marcus Webb:** Southridge Video is in negotiation. The main contact is Lena, the head of customer support, and they've been responsive, which is a nice change from the summer. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. Their main use case is search over internal documents for the support team. They estimate it would save each agent around an hour a day, and they've done the maths on it themselves, which helps. We're forecasting 60 thousand, closing in February. I'd call it commit, but I'm not putting it in commit until I see the paper. Main blocker: legal wants changes to the liability cap. We've seen this before with similar companies and it usually works out. On competition, they're also looking at a smaller open source shop. My next step is to run the pilot kickoff. I've got a slot pencilled in for Tuesday.

**[00:30:47] Dana Kim:** Is that date real, or is that our date?

**[00:30:50] Marcus Webb:** It's their date. They have a board meeting in February and they want this approved before it.

**[00:30:57] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:31:02] Marcus Webb:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:31:10] Theo Grant:** I looked at the data sample from Southridge Video. It's messier than they said, but nothing we haven't handled before.

**[00:31:18] Marcus Webb:** Great, I'll add you to the invite.

**[00:31:21] Dana Kim:** Thanks. Next.

**[00:31:23] Dana Kim:** Next is Consolidated Messenger. Leo, yours?

**[00:31:26] Leo Marsh:** Quick one on Consolidated Messenger. Still in proposal, nothing dramatic since last week. They came in through a webinar about a year ago. The first project died when their sponsor left, and this is the second attempt with a new team. Their main use case is search over internal documents for the support team. They estimate it would save each agent around an hour a day, and they've done the maths on it themselves, which helps. The number is about 180 thousand for the first year, with a close in March if nothing slips. The open item is that the champion is going on leave. I think we can solve it, but I need some help from the team. They mentioned nobody yet, as far as we know as the alternative, but they didn't sound excited about it. What I need to do now is send the revised order form. Then we should know where we stand.

**[00:32:21] Dana Kim:** How confident are you, honestly, out of ten?

**[00:32:25] Leo Marsh:** Seven. Maybe a six until I see the security answers go through.

**[00:32:30] Dana Kim:** And if that doesn't move, what's plan B?

**[00:32:33] Leo Marsh:** Plan B is to split the deal: start with a smaller scope that doesn't need the full approval, and expand once they see results. I've floated it with Pavel, who didn't hate it.

**[00:32:46] Sam Rivera:** For Consolidated Messenger, the opportunity has no contact roles. Can you add Pavel as the champion? The pipeline report filters on it.

**[00:32:54] Leo Marsh:** Will do.

**[00:32:56] Dana Kim:** Thanks. Next.

**[00:32:57] Dana Kim:** Okay, A. Datum. Who has that one? Nadia, right?

**[00:33:01] Nadia Brooks:** A. Datum is in negotiation. The main contact is Amara, their CIO's chief of staff, and they've been responsive, which is a nice change from the summer. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. Their main use case is search over internal documents for the support team. They estimate it would save each agent around an hour a day, and they've done the maths on it themselves, which helps. Value is around 180 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. Main blocker: legal wants changes to the liability cap. We've seen this before with similar companies and it usually works out. They mentioned a smaller open source shop as the alternative, but they didn't sound excited about it. Next step is to run the pilot kickoff, and I want that done by the end of next week.

**[00:34:01] Dana Kim:** Is that date real, or is that our date?

**[00:34:05] Nadia Brooks:** It's their date. They have a board meeting in February and they want this approved before it.

**[00:34:12] Dana Kim:** And if that doesn't move, what's plan B?

**[00:34:15] Nadia Brooks:** Plan B is to split the deal: start with a smaller scope that doesn't need the full approval, and expand once they see results. I've floated it with Amara, who didn't hate it.

**[00:34:27] Sam Rivera:** On A. Datum, I see two open opportunities for the same product. One of them should probably be closed as a duplicate.

**[00:34:36] Nadia Brooks:** Will do.

**[00:34:37] Dana Kim:** Fine. Keep it in best case for now.

**[00:34:41] Dana Kim:** Next is Margie's Travel. Leo, yours?

**[00:34:44] Leo Marsh:** Margie's Travel is in discovery. The main contact is Jonas, the enterprise architect, and they've been responsive, which is a nice change from the summer. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Jonas got budget for a data project in September. On the last call they spent most of the time on how the rollout would work across their regions. They want to start with one team and expand, which fits how we usually land. The number is about 150 thousand for the first year, with a close in January if nothing slips. Main blocker: procurement wants three quotes. We've seen this before with similar companies and it usually works out. On competition, they're also looking at their incumbent consultancy. Next step is to walk their architect through the deployment options, and I want that done by the end of next week.

**[00:35:39] Dana Kim:** Have we met anyone above Jonas yet?

**[00:35:42] Leo Marsh:** Once, briefly, on the first call. I want to get back in front of them before the proposal.

**[00:35:49] Dana Kim:** And if that doesn't move, what's plan B?

**[00:35:53] Leo Marsh:** Plan B is to split the deal: start with a smaller scope that doesn't need the full approval, and expand once they see results. I've floated it with Jonas, who didn't hate it.

**[00:36:05] Sam Rivera:** On Margie's Travel, I see two open opportunities for the same product. One of them should probably be closed as a duplicate.

**[00:36:14] Leo Marsh:** Good catch, thanks.

**[00:36:15] Sam Rivera:** Also, a note for me: I'll send Bob Stone the churn field mapping by 2026-11-06.

**[00:36:21] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:36:26] Dana Kim:** Relecloud. Nadia, go ahead.

**[00:36:28] Nadia Brooks:** Quick one on Relecloud. Still in proposal, nothing dramatic since last week. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Pavel got budget for a data project in September. The technical team likes it. The question is whether the business side sees it as a priority this year or something for next year. It's 150 thousand on the opportunity. The date says December, and I think that's realistic if we keep the momentum. The thing that worries me is that IT has a change freeze until the new year. It's not a deal breaker, but it adds weeks. They mentioned one of the big cloud vendors as the alternative, but they didn't sound excited about it. My next step is to get the security answers back to them. I've got a slot pencilled in for Tuesday.

**[00:37:21] Dana Kim:** What does the mutual plan look like? Is there one?

**[00:37:26] Nadia Brooks:** There's a draft. They haven't signed off on it, but they've added their own dates, which is a good sign.

**[00:37:33] Dana Kim:** And if that doesn't move, what's plan B?

**[00:37:37] Nadia Brooks:** Plan B is to split the deal: start with a smaller scope that doesn't need the full approval, and expand once they see results. I've floated it with Pavel, who didn't hate it.

**[00:37:49] Dana Kim:** Okay. If it slips, tell me before the forecast call, not after.

**[00:37:54] Dana Kim:** Lamna Healthcare. Marcus, go ahead.

**[00:37:57] Marcus Webb:** So Lamna Healthcare. We're in proposal. On Monday I spoke to Pavel, the IT director, and the tone was positive. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. They had a bad experience with a vendor who oversold, so they're very careful. Everything we say has to be backed by a demo or a reference. We're forecasting 60 thousand, closing in March. I'd call it commit, but I'm not putting it in commit until I see the paper. The open item is that the budget sits in next year's plan. I think we can solve it, but I need some help from the team. Competition-wise, it's nobody yet, as far as we know. What I need to do now is book the technical deep dive. Then we should know where we stand.

**[00:38:51] Dana Kim:** How confident are you, honestly, out of ten?

**[00:38:55] Marcus Webb:** Seven. Maybe a six until I see the security answers go through.

**[00:38:59] Dana Kim:** Okay. If it slips, tell me before the forecast call, not after.

**[00:39:04] Dana Kim:** Fincher Architects. Nadia, go ahead.

**[00:39:07] Nadia Brooks:** So Fincher Architects. We're in discovery. On Monday I spoke to Daniel, the director of digital, and the tone was positive. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Daniel got budget for a data project in September. They want a proof of value on their own data before they sign. I've scoped it at four weeks with clear success criteria written down up front. It's 55 thousand on the opportunity. The date says January, and I think that's realistic if we keep the momentum. Main blocker: the budget sits in next year's plan. We've seen this before with similar companies and it usually works out. On competition, they're also looking at their incumbent consultancy. What I need to do now is get the security answers back to them. Then we should know where we stand.

**[00:40:00] Dana Kim:** How confident are you, honestly, out of ten?

**[00:40:03] Nadia Brooks:** Seven. Maybe a six until I see the security answers go through.

**[00:40:08] Dana Kim:** Do you need anything from me or from Theo on this one?

**[00:40:13] Nadia Brooks:** Maybe Theo on the next technical call. Otherwise I'm fine for now, I'll shout if that changes.

**[00:40:20] Sam Rivera:** Just so you know, Fincher Architects came in through the partner form, so the partner field needs to stay filled in, or the partner team loses the credit.

**[00:40:31] Nadia Brooks:** Will do.

**[00:40:32] Dana Kim:** Thanks. Next.

**[00:40:33] Dana Kim:** Okay, Munson's Pickles. Who has that one? Nadia, right?

**[00:40:37] Nadia Brooks:** Munson's Pickles, we moved it to discovery on Friday. Jonas, the enterprise architect pulled two more people into the last call, which I take as a good sign. We've had a relationship with them for a while through a partner, but this is the first time we're selling to them directly. The technical team likes it. The question is whether the business side sees it as a priority this year or something for next year. It's 150 thousand on the opportunity. The date says December, and I think that's realistic if we keep the momentum. The risk is that they want a reference customer in their industry. I've asked them how they want to handle it, and I'm waiting to hear back. On competition, they're also looking at a smaller open source shop. What I need to do now is book the technical deep dive. Then we should know where we stand.

**[00:41:31] Dana Kim:** What does the mutual plan look like? Is there one?

**[00:41:36] Nadia Brooks:** There's a draft. They haven't signed off on it, but they've added their own dates, which is a good sign.

**[00:41:43] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:41:48] Nadia Brooks:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:41:57] Sam Rivera:** Small thing on Munson's Pickles: the close date in the CRM still says last month. Can you update it so the forecast rolls up properly?

**[00:42:06] Nadia Brooks:** Will do.

**[00:42:08] Dana Kim:** Thanks. Next.

**[00:42:09] Dana Kim:** Okay, VanArsdel. Who has that one? Marcus, right?

**[00:42:12] Marcus Webb:** Quick one on VanArsdel. Still in security review, nothing dramatic since last week. We've had a relationship with them for a while through a partner, but this is the first time we're selling to them directly. On the last call they spent most of the time on how the rollout would work across their regions. They want to start with one team and expand, which fits how we usually land. The number is about 90 thousand for the first year, with a close in March if nothing slips. The thing that worries me is that they want a reference customer in their industry. It's not a deal breaker, but it adds weeks. On competition, they're also looking at one of the big cloud vendors. What I need to do now is send the revised order form. Then we should know where we stand.

**[00:43:03] Dana Kim:** Who signs, though? Do we know the economic buyer yet?

**[00:43:08] Marcus Webb:** Not directly. Jonas says it's the CFO, but I haven't been in a room with the CFO yet. I'm asking for that meeting on the next call.

**[00:43:18] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:43:23] Dana Kim:** Tailwind Traders. Leo, go ahead.

**[00:43:25] Leo Marsh:** Tailwind Traders is in security review. The main contact is Rafael, the data platform owner, and they've been responsive, which is a nice change from the summer. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. They had a bad experience with a vendor who oversold, so they're very careful. Everything we say has to be backed by a demo or a reference. Value is around 240 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. The open item is that the champion is going on leave. I think we can solve it, but I need some help from the team. They mentioned one of the big cloud vendors as the alternative, but they didn't sound excited about it. Next step is to get the security answers back to them, and I want that done by the end of next week.

**[00:44:25] Dana Kim:** What does the mutual plan look like? Is there one?

**[00:44:30] Leo Marsh:** There's a draft. They haven't signed off on it, but they've added their own dates, which is a good sign.

**[00:44:37] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:44:42] Leo Marsh:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:44:51] Sam Rivera:** For Tailwind Traders, the opportunity has no contact roles. Can you add Rafael as the champion? The pipeline report filters on it.

**[00:44:59] Leo Marsh:** Will do.

**[00:45:01] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:45:05] Dana Kim:** Okay, City Power and Light. Who has that one? Marcus, right?

**[00:45:10] Marcus Webb:** On City Power and Light, honestly, it's been slower than I wanted. We're in negotiation and have been for three weeks. This one started as an inbound demo request. They had already tried to build something themselves and gave up after six months, so they know the problem well. They had a bad experience with a vendor who oversold, so they're very careful. Everything we say has to be backed by a demo or a reference. It's 40 thousand on the opportunity. The date says March, and I think that's realistic if we keep the momentum. The risk is that procurement wants three quotes. I've asked them how they want to handle it, and I'm waiting to hear back. On competition, they're also looking at their incumbent consultancy. What I need to do now is book the technical deep dive. Then we should know where we stand.

**[00:46:02] Dana Kim:** What would make this slip into next quarter?

**[00:46:06] Marcus Webb:** If the blocker drags on, it slips. Everything else is under control.

**[00:46:11] Theo Grant:** On the technical side for City Power and Light, they asked about running it in their own cloud account. That's fine, I can show them the deployment guide.

**[00:46:21] Marcus Webb:** Thanks, that helps.

**[00:46:23] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:46:28] Dana Kim:** Next is Contoso. Leo, yours?

**[00:46:31] Leo Marsh:** Contoso is in technical validation. The main contact is Elena, their head of data, and they've been responsive, which is a nice change from the summer. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Elena got budget for a data project in September. On the last call they spent most of the time on how the rollout would work across their regions. They want to start with one team and expand, which fits how we usually land. We're forecasting 90 thousand, closing in February. I'd call it commit, but I'm not putting it in commit until I see the paper. The thing that worries me is that they need a data residency answer. It's not a deal breaker, but it adds weeks. On competition, they're also looking at a smaller open source shop. My next step is to set up the executive call. I've got a slot pencilled in for Tuesday.

**[00:47:29] Dana Kim:** How confident are you, honestly, out of ten?

**[00:47:32] Leo Marsh:** Seven. Maybe a six until I see the security answers go through.

**[00:47:37] Dana Kim:** Do you need anything from me or from Theo on this one?

**[00:47:42] Leo Marsh:** Maybe Theo on the next technical call. Otherwise I'm fine for now, I'll shout if that changes.

**[00:47:49] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:47:54] Dana Kim:** Next is Graphic Design Institute. Marcus, yours?

**[00:47:57] Marcus Webb:** Graphic Design Institute is in discovery. The main contact is Elena, their head of data, and they've been responsive, which is a nice change from the summer. We've had a relationship with them for a while through a partner, but this is the first time we're selling to them directly. The technical team likes it. The question is whether the business side sees it as a priority this year or something for next year. The number is about 150 thousand for the first year, with a close in December if nothing slips. The thing that worries me is that IT has a change freeze until the new year. It's not a deal breaker, but it adds weeks. On competition, they're also looking at an in-house build. Next step is to set up the executive call, and I want that done by the end of next week.

**[00:48:49] Dana Kim:** What does the mutual plan look like? Is there one?

**[00:48:53] Marcus Webb:** There's a draft. They haven't signed off on it, but they've added their own dates, which is a good sign.

**[00:49:01] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:49:06] Marcus Webb:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:49:14] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:49:19] Dana Kim:** Okay, Best For You Organics. Who has that one? Leo, right?

**[00:49:24] Leo Marsh:** On Best For You Organics, honestly, it's been slower than I wanted. We're in security review and have been for three weeks. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. They're asking for a fixed price for the first year and usage pricing after that. I said I'd check with Dana before I commit to anything. Value is around 120 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. The thing that worries me is that they want a reference customer in their industry. It's not a deal breaker, but it adds weeks. Competition-wise, it's a smaller open source shop. Next step is to walk their architect through the deployment options, and I want that done by the end of next week.

**[00:50:18] Dana Kim:** Who signs, though? Do we know the economic buyer yet?

**[00:50:22] Leo Marsh:** Not directly. Kofi says it's the CFO, but I haven't been in a room with the CFO yet. I'm asking for that meeting on the next call.

**[00:50:32] Sam Rivera:** For Best For You Organics, the opportunity has no contact roles. Can you add Kofi as the champion? The pipeline report filters on it.

**[00:50:41] Leo Marsh:** Good catch, thanks.

**[00:50:43] Dana Kim:** Fine. Keep it in best case for now.

**[00:50:47] Dana Kim:** Okay, Cronus. Who has that one? Nadia, right?

**[00:50:50] Nadia Brooks:** On Cronus, honestly, it's been slower than I wanted. We're in proposal and have been for three weeks. This one started as an inbound demo request. They had already tried to build something themselves and gave up after six months, so they know the problem well. On the last call they spent most of the time on how the rollout would work across their regions. They want to start with one team and expand, which fits how we usually land. The number is about 90 thousand for the first year, with a close in March if nothing slips. The thing that worries me is that procurement wants three quotes. It's not a deal breaker, but it adds weeks. Competition-wise, it's nobody yet, as far as we know. Next step is to book the technical deep dive, and I want that done by the end of next week.

**[00:51:42] Dana Kim:** What does the mutual plan look like? Is there one?

**[00:51:47] Nadia Brooks:** There's a draft. They haven't signed off on it, but they've added their own dates, which is a good sign.

**[00:51:54] Theo Grant:** I looked at the data sample from Cronus. It's messier than they said, but nothing we haven't handled before.

**[00:52:02] Nadia Brooks:** Thanks, that helps.

**[00:52:04] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:52:08] Dana Kim:** Olympia Freight. Nadia, go ahead.

**[00:52:11] Nadia Brooks:** Olympia Freight is in technical validation. The main contact is Jonas, the enterprise architect, and they've been responsive, which is a nice change from the summer. They came in through a webinar about a year ago. The first project died when their sponsor left, and this is the second attempt with a new team. Their main use case is search over internal documents for the support team. They estimate it would save each agent around an hour a day, and they've done the maths on it themselves, which helps. Value is around 40 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. The risk is that the champion is going on leave. I've asked them how they want to handle it, and I'm waiting to hear back. They mentioned one of the big cloud vendors as the alternative, but they didn't sound excited about it. What I need to do now is run the pilot kickoff. Then we should know where we stand.

**[00:53:12] Dana Kim:** What does the mutual plan look like? Is there one?

**[00:53:16] Nadia Brooks:** There's a draft. They haven't signed off on it, but they've added their own dates, which is a good sign.

**[00:53:24] Dana Kim:** When did you last speak to Jonas?

**[00:53:27] Nadia Brooks:** Yesterday, actually. Quick call. Jonas is chasing internally and promised an update by Friday.

**[00:53:32] Sam Rivera:** Small thing on Olympia Freight: the close date in the CRM still says last month. Can you update it so the forecast rolls up properly?

**[00:53:42] Nadia Brooks:** Yes, I'll fix that today.

**[00:53:44] Dana Kim:** Okay. Let's run the pilot kickoff and look at it again next week.

**[00:53:50] Dana Kim:** Kestrel Analytics. Nadia, go ahead.

**[00:53:52] Nadia Brooks:** Kestrel Analytics, we moved it to security review on Friday. Mira, who runs the analytics team pulled two more people into the last call, which I take as a good sign. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. They're asking for a fixed price for the first year and usage pricing after that. I said I'd check with Dana before I commit to anything. The number is about 75 thousand for the first year, with a close in January if nothing slips. The thing that worries me is that their security team has a long questionnaire. It's not a deal breaker, but it adds weeks. They mentioned an in-house build as the alternative, but they didn't sound excited about it. My next step is to send the reference customer intro. I've got a slot pencilled in for Tuesday.

**[00:54:49] Dana Kim:** Do they understand the pricing, or are we going to get a surprise in negotiation?

**[00:54:55] Nadia Brooks:** I walked them through it twice. They know the list price and they know the discount we usually give. No surprises, I hope.

**[00:55:04] Dana Kim:** When did you last speak to Mira?

**[00:55:07] Nadia Brooks:** Yesterday, actually. Quick call. Mira is chasing internally and promised an update by Friday.

**[00:55:13] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:55:18] Dana Kim:** Next is Harbor Point Clinics. Marcus, yours?

**[00:55:21] Marcus Webb:** So Harbor Point Clinics. We're in security review. On Monday I spoke to Kofi, the engineering manager, and the tone was positive. We've had a relationship with them for a while through a partner, but this is the first time we're selling to them directly. On the last call they spent most of the time on how the rollout would work across their regions. They want to start with one team and expand, which fits how we usually land. Value is around 240 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. Main blocker: the champion is going on leave. We've seen this before with similar companies and it usually works out. On competition, they're also looking at an in-house build. What I need to do now is book the technical deep dive. Then we should know where we stand.

**[00:56:13] Dana Kim:** Have we met anyone above Kofi yet?

**[00:56:17] Marcus Webb:** Once, briefly, on the first call. I want to get back in front of them before the proposal.

**[00:56:24] Sam Rivera:** For Harbor Point Clinics, the opportunity has no contact roles. Can you add Kofi as the champion? The pipeline report filters on it.

**[00:56:32] Marcus Webb:** Sorry, I'll sort it.

**[00:56:35] Dana Kim:** Fine. Keep it in best case for now.

**[00:56:38] Dana Kim:** Next is Silverline Mutual. Marcus, yours?

**[00:56:41] Marcus Webb:** Silverline Mutual, we moved it to procurement on Friday. Daniel, the director of digital pulled two more people into the last call, which I take as a good sign. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. On the last call they spent most of the time on how the rollout would work across their regions. They want to start with one team and expand, which fits how we usually land. We're forecasting 40 thousand, closing in March. I'd call it commit, but I'm not putting it in commit until I see the paper. The thing that worries me is that IT has a change freeze until the new year. It's not a deal breaker, but it adds weeks. They mentioned their incumbent consultancy as the alternative, but they didn't sound excited about it. Next step is to book the technical deep dive, and I want that done by the end of next week.

**[00:57:43] Dana Kim:** Is that date real, or is that our date?

**[00:57:47] Marcus Webb:** It's their date. They have a board meeting in March and they want this approved before it.

**[00:57:54] Dana Kim:** Do you need anything from me or from Theo on this one?

**[00:57:59] Marcus Webb:** Maybe Theo on the next technical call. Otherwise I'm fine for now, I'll shout if that changes.

**[00:58:05] Sam Rivera:** On Silverline Mutual, I see two open opportunities for the same product. One of them should probably be closed as a duplicate.

**[00:58:14] Marcus Webb:** Will do.

**[00:58:15] Dana Kim:** Good. Let me know if you need me on the executive call.

**[00:58:20] Dana Kim:** Okay, Granite Peak Energy. Who has that one? Nadia, right?

**[00:58:24] Nadia Brooks:** On Granite Peak Energy, honestly, it's been slower than I wanted. We're in negotiation and have been for three weeks. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Grace got budget for a data project in September. The technical team likes it. The question is whether the business side sees it as a priority this year or something for next year. Value is around 90 thousand. They talked about expanding to a second business unit next year, but I'm not counting that. The open item is that IT has a change freeze until the new year. I think we can solve it, but I need some help from the team. They mentioned their incumbent consultancy as the alternative, but they didn't sound excited about it. Next step is to run the pilot kickoff, and I want that done by the end of next week.

**[00:59:20] Dana Kim:** What would make this slip into next quarter?

**[00:59:24] Nadia Brooks:** If the blocker drags on, it slips. Everything else is under control.

**[00:59:29] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[00:59:34] Nadia Brooks:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[00:59:42] Dana Kim:** Thanks. Next.

**[00:59:43] Dana Kim:** Bluebell Foods. Nadia, go ahead.

**[00:59:46] Nadia Brooks:** Bluebell Foods, we moved it to procurement on Friday. Pavel, the IT director pulled two more people into the last call, which I take as a good sign. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. They want a proof of value on their own data before they sign. I've scoped it at four weeks with clear success criteria written down up front. It's 40 thousand on the opportunity. The date says February, and I think that's realistic if we keep the momentum. The open item is that legal wants changes to the liability cap. I think we can solve it, but I need some help from the team. Competition-wise, it's one of the big cloud vendors. Next step is to send the revised order form, and I want that done by the end of next week.

**[01:00:42] Dana Kim:** What would make this slip into next quarter?

**[01:00:46] Nadia Brooks:** If the blocker drags on, it slips. Everything else is under control.

**[01:00:51] Dana Kim:** Do you need anything from me or from Theo on this one?

**[01:00:55] Nadia Brooks:** Maybe Theo on the next technical call. Otherwise I'm fine for now, I'll shout if that changes.

**[01:01:02] Sam Rivera:** On Bluebell Foods, I see two open opportunities for the same product. One of them should probably be closed as a duplicate.

**[01:01:11] Nadia Brooks:** Yes, I'll fix that today.

**[01:01:13] Dana Kim:** Thanks. Next.

**[01:01:14] Dana Kim:** Okay, Meridian Retail. Who has that one? Leo, right?

**[01:01:18] Leo Marsh:** Quick one on Meridian Retail. Still in negotiation, nothing dramatic since last week. This one started as an inbound demo request. They had already tried to build something themselves and gave up after six months, so they know the problem well. They had a bad experience with a vendor who oversold, so they're very careful. Everything we say has to be backed by a demo or a reference. We're forecasting 240 thousand, closing in December. I'd call it commit, but I'm not putting it in commit until I see the paper. The thing that worries me is that procurement wants three quotes. It's not a deal breaker, but it adds weeks. They mentioned a smaller open source shop as the alternative, but they didn't sound excited about it. My next step is to set up the executive call. I've got a slot pencilled in for Tuesday.

**[01:02:10] Dana Kim:** How confident are you, honestly, out of ten?

**[01:02:14] Leo Marsh:** Seven. Maybe a six until I see the security answers go through.

**[01:02:19] Dana Kim:** Is there anything in the contract they've pushed back on so far?

**[01:02:24] Leo Marsh:** Only the payment terms. They want sixty days instead of thirty. I told them that's usually fine but I need to confirm.

**[01:02:32] Sam Rivera:** Just so you know, Meridian Retail came in through the partner form, so the partner field needs to stay filled in, or the partner team loses the credit.

**[01:02:43] Leo Marsh:** Sorry, I'll sort it.

**[01:02:45] Dana Kim:** Okay. If it slips, tell me before the forecast call, not after.

**[01:02:50] Dana Kim:** Larkspur Media. Leo, go ahead.

**[01:02:52] Leo Marsh:** Larkspur Media, we moved it to technical validation on Friday. Kofi, the engineering manager pulled two more people into the last call, which I take as a good sign. It's an expansion of the pilot we ran with one of their teams last quarter. The pilot went well and the team lead has been our internal advocate since. They're asking for a fixed price for the first year and usage pricing after that. I said I'd check with Dana before I commit to anything. The number is about 180 thousand for the first year, with a close in November if nothing slips. The thing that worries me is that their security team has a long questionnaire. It's not a deal breaker, but it adds weeks. They mentioned their incumbent consultancy as the alternative, but they didn't sound excited about it. My next step is to get the security answers back to them. I've got a slot pencilled in for Tuesday.

**[01:03:49] Dana Kim:** How confident are you, honestly, out of ten?

**[01:03:53] Leo Marsh:** Seven. Maybe a six until I see the security answers go through.

**[01:03:58] Dana Kim:** Do you need anything from me or from Theo on this one?

**[01:04:03] Leo Marsh:** Maybe Theo on the next technical call. Otherwise I'm fine for now, I'll shout if that changes.

**[01:04:09] Dana Kim:** Okay. If it slips, tell me before the forecast call, not after.

**[01:04:14] Dana Kim:** Next is Copperfield Hotels. Marcus, yours?

**[01:04:17] Marcus Webb:** So Copperfield Hotels. We're in negotiation. On Monday I spoke to Amara, their CIO's chief of staff, and the tone was positive. For context, we first spoke to them in the spring, it went quiet over the summer, and it came back when Amara got budget for a data project in September. They had a bad experience with a vendor who oversold, so they're very careful. Everything we say has to be backed by a demo or a reference. We're forecasting 150 thousand, closing in February. I'd call it commit, but I'm not putting it in commit until I see the paper. Main blocker: the champion is going on leave. We've seen this before with similar companies and it usually works out. They mentioned an in-house build as the alternative, but they didn't sound excited about it. What I need to do now is get a mutual action plan signed off. Then we should know where we stand.

**[01:05:13] Dana Kim:** Is that date real, or is that our date?

**[01:05:17] Marcus Webb:** It's their date. They have a board meeting in February and they want this approved before it.

**[01:05:24] Dana Kim:** Do you need anything from me or from Theo on this one?

**[01:05:29] Marcus Webb:** Maybe Theo on the next technical call. Otherwise I'm fine for now, I'll shout if that changes.

**[01:05:35] Dana Kim:** Good. Let me know if you need me on the executive call.

**[01:05:40] Dana Kim:** Ashgrove Logistics. Leo, go ahead.

**[01:05:43] Leo Marsh:** On Ashgrove Logistics, honestly, it's been slower than I wanted. We're in discovery and have been for three weeks. We've had a relationship with them for a while through a partner, but this is the first time we're selling to them directly. The technical team likes it. The question is whether the business side sees it as a priority this year or something for next year. It's 240 thousand on the opportunity. The date says November, and I think that's realistic if we keep the momentum. Main blocker: procurement wants three quotes. We've seen this before with similar companies and it usually works out. Competition-wise, it's nobody yet, as far as we know. What I need to do now is walk their architect through the deployment options. Then we should know where we stand.

**[01:06:31] Dana Kim:** Have we met anyone above Elena yet?

**[01:06:34] Leo Marsh:** Once, briefly, on the first call. I want to get back in front of them before the proposal.

**[01:06:41] Dana Kim:** When did you last speak to Elena?

**[01:06:44] Leo Marsh:** Yesterday, actually. Quick call. Elena is chasing internally and promised an update by Friday.

**[01:06:50] Dana Kim:** Okay. Let's walk their architect through the deployment options and look at it again next week.

**[01:06:56] Dana Kim:** Okay, that's the pipeline. We're roughly on time, which is a first. Ruth, the discovery sheet.

**[01:07:02] Ruth Adeyemi:** Thanks. So this came out of the call reviews we did last month. We listened to about twenty first calls, and the pattern was that we talk a lot about the product and ask very few questions about the buyer's situation. The calls that went on to a second meeting had one thing in common: the buyer described a problem in their own words in the first fifteen minutes. The sheet is a short list of questions per role, so you go into a first call with three good questions ready instead of a slide deck.

**[01:07:37] Marcus Webb:** How many roles are on it?

**[01:07:39] Ruth Adeyemi:** Four. The executive sponsor, the platform owner, the architect and the hands-on engineer. For each one there's what they care about, what usually worries them, and three questions to ask.

**[01:07:51] Dana Kim:** Can you give an example? For the executive sponsor.

**[01:07:55] Ruth Adeyemi:** Sure. The executive sponsor cares about time to value and risk. The worry is usually that they back a project and it takes a year to show anything. So the questions are things like: what would you need to see in the first ninety days to call this a success? Who else has to agree before you spend money on this? And what happened the last time you tried to solve this problem?

**[01:08:21] Leo Marsh:** That last one is good. People love telling you about the last failed project.

**[01:08:27] Ruth Adeyemi:** Exactly, and it tells you what not to say. If their last attempt failed because it was too complex, you don't open with the architecture diagram.

**[01:08:36] Theo Grant:** For the architect, I'd add a question about where the data lives. That's what decides whether the deployment conversation is easy or painful.

**[01:08:45] Ruth Adeyemi:** Good, I'll add it. Can you write it the way you'd actually say it on a call?

**[01:08:52] Theo Grant:** Sure. Something like: walk me through where the data for this use case sits today, and who owns each part.

**[01:09:00] Owen Fletcher:** Coming from my last company, we had something similar, and the thing that made it stick was practising it. Otherwise everyone nods in the meeting and goes back to the deck.

**[01:09:11] Dana Kim:** Agreed. Ruth, can we do role plays next week? Thirty minutes, two pairs, one person plays the buyer.

**[01:09:18] Ruth Adeyemi:** Yes. I'll write two short scenarios so the person playing the buyer has something to work with.

**[01:09:25] Marcus Webb:** Can the sheet be one page? If it's a document I won't open it during a call.

**[01:09:32] Ruth Adeyemi:** One page, landscape, four columns. You can keep it next to the screen.

**[01:09:37] Dana Kim:** Good. And I want us to try it on real calls this week, not wait for the role play. Everyone use it on at least one first call and tell Ruth what didn't work.

**[01:09:50] Ruth Adeyemi:** Please do. Especially the questions that felt awkward. Those are the ones I want to rewrite.

**[01:09:56] Sam Rivera:** Do you want a field in the CRM for which questions were asked? Then we could see over time whether calls with more discovery convert better.

**[01:10:06] Dana Kim:** Not yet. Let's see if people use it at all before we measure it. If it sticks, we can add a field in a month.

**[01:10:15] Sam Rivera:** Fair enough.

**[01:10:17] Ruth Adeyemi:** Last thing on this. The sheet will change every couple of weeks at the start, so please don't print ten copies. Use the link.

**[01:10:26] Leo Marsh:** Before I forget, on Acme: Jane Doe told me they want to sign the renewal early, on 2026-11-20, instead of waiting for the 2027-01-31 renewal date.

**[01:10:36] Dana Kim:** Okay. A few minutes left. Owen, do you want to say a few words about yourself? Everyone else has been talking for an hour.

**[01:10:45] Owen Fletcher:** Sure. I'm Owen, I joined on Monday as an account executive. I'll be covering the mid-market accounts in the central region. Before this I spent four years selling analytics software, mostly to logistics and retail companies, so if you have accounts in those industries I'm happy to help. I'm still finding my way around the CRM, so forgive me if I ask obvious questions.

**[01:11:08] Marcus Webb:** Welcome. Ask the obvious questions, half of us still don't know where things are.

**[01:11:14] Ruth Adeyemi:** Welcome, Owen. I'll send you the content library link, it saves a lot of searching.

**[01:11:20] Theo Grant:** Welcome. Grab some time with me this week and I'll give you the demo walkthrough, so you're not stuck when someone asks for one.

**[01:11:29] Owen Fletcher:** Thanks, I'll book something.

**[01:11:31] Dana Kim:** Sam, can you make sure Owen has the right access? Last time it took a week for a new starter to get into the reporting.

**[01:11:40] Sam Rivera:** Yes. Owen, I've already requested the CRM licence. The reporting access needs a manager approval, so Dana, you'll get a request today.

**[01:11:49] Dana Kim:** I'll approve it as soon as it comes in.

**[01:11:53] Sam Rivera:** Once that's through, let's book thirty minutes and I'll walk you through the dashboards and the forecast view.

**[01:12:00] Owen Fletcher:** Sounds good. Thanks, everyone.

**[01:12:02] Dana Kim:** Thanks, all. Same time next week.

**[01:12:05] Marcus Webb:** Thanks.

**[01:12:06] Leo Marsh:** See you.

**[01:12:09] Sam Rivera:** Good to have you on.

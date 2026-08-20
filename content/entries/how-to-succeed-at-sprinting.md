Title: How to Succeed at Sprinting
Date: 2026-06-23 10:00:00
Summary: Over the last 12 years, BeeWare has earned a reputation as being a model project for running sprints. I’ve been running (or helping to run) Django sprints for 7 years before that. This is a playbook of what I’ve learned over the years about running a successful sprint.

Over the last 12 years, [BeeWare](https://beeware.org/) has earned a reputation as being a model project for running sprints. I’ve been running (or helping to run) Django sprints for 7 years before that. This is a playbook of what I’ve learned over the years about running a successful sprint.

Firstly - a caveat: the sprints that BeeWare (and to a lesser extent, [Django](https://djangoproject.com)) have run have been very focused on attracting first-time Open Source contributors and building buzz about the project. That’s not the only way to run a sprint, and it’s not the only audience to attract. If your goals are different, you might not gain as much from this guide.

However, my experience has been that for projects that are targeting "entry level" programmers, the process of engaging beginners can serve as a great way to build positive energy around your project. I attribute a lot of the success of BeeWare in the broader Python community to the explicit outreach we’ve done in making first-time contributors feel welcome. The sprinting process is as much advertising/marketing for BeeWare as a great community to be part of, as it is the classical understanding of "improving the project".

## Before the sprint

### Work out what you want to accomplish

Go to the sprint with a clear vision of what you want to achieve from the sprint. Are you looking to gain new contributors? Do you want to make as many people as possible feel good about the project? Are you looking for a multi-day opportunity to deep dive into a topic with experts? Do you have an area of focus where warm bodies can help? Know what you want to achieve, and clearly communicate that in your community ahead of time.
This is an area where long term momentum helps - BeeWare is, by now, a known quantity at PyCon US sprints. Long term PyCon attendees with no attribution to BeeWare will point confused first-timers (or first-timers who have been disillusioned with sprinting on other projects) at BeeWare, based purely on our historical reputation. That reputation takes time to build, but every long journey starts with a single step.

Most of the rest of this guide assumes that your goal in the sprints will be to attract new people to contribute to your project.

### Polish your contribution guide

You need a contribution guide, and it needs to be bulletproof. [BeeWare's contribution guide](https://beeware.org/contributing/guide/) has developed over many years. It needs to describe everything that is needed to set up a development environment, run tests, and anything that needs to be done to pass CI (e.g. running pre-commit checks). The instructions need to work on Windows, macOS and as many Linux distros as you can manage (or, it needs to be clear ahead of time where they won't work). Any friction in getting a working development environment will be an impediment to the sprinter sticking around.

### Curate your first "good first issue" list

Make sure you have an easy to find subset of issues that are clearly understood, are easily reproducible, are well described, and have a reasonably clear path to a fix. The more introductory your audience, the more explicit these instructions need to be. BeeWare is an unusual project in that it is an umbrella project of many smaller projects, so we use a [GitHub project board](https://github.com/orgs/beeware/projects/1) with a specific view for [issues ready to be completed](https://beeware.org/bee/ready). That list can be filtered by priority, complexity, experience level, and anything other detail that might be useful.

It’s also important that the good-first-issue list is clear about the skillset that is required. If you need to know non-Python languages to fix an issue, then that needs to be clear. The vast majority of sprint attendees will only know Python - so that also needs to be factored in.

This can be an opportunity to teach people new skills, though. For example, attendees might not know C, but if you can present an issue that only requires a small amount of C, in a way that utilizes transferable knowledge from Python, you might be able to get someone contributing in this way. BeeWare gets this with Toga contribution - contributing to the macOS/Cocoa backend strictly requires knowing Objective C… but for simple issues, you really only need to be able to read some Objective C docs and see that a `doFooBar()` method exists, so it’s approachable for Python-only developers.

### If you can: have a "big picture" project

One of the reasons BeeWare got good at sprints is that, in the early days, we had a complete test suite, but a lot of the tests were marked as skips because of a missing implementation. We could point someone at the list of tests that were marked as skipped, and say "make one of them pass".

This sort of specific situation is obviously difficult to reproduce, but if you can, it’s magic. Large scale housekeeping projects are a good candidate here - something like "we’re updating all of our documentation from ReStructuredText to Markdown" is something where individual files can be tackled independently. There’s a long TODO list which are all similar and can be described in abstract terms, but require individual independent contributions.

It doesn’t have to mean writing code, either. It could mean working through a ticket backlog - if you’ve got 1000 open issues, that’s the sort of thing where having a group of individuals to try and reproduce each problem and confirm if they are still problems. If you can clearly articulate your triage process, a sprint is a great opportunity to throw bodies at a backlog.

## During the sprint

### Get there early on the first day

The early bird gets the worm - in so many ways. You get to claim the best sprinting spots; and you get to claim the enthusiastic people who show up early on the first day. If you roll in at 11AM, you’ve missed 3 hours of contributors who wanted to contribute, but had no point of contact.

### Make it easy to be found

If you’re going to the trouble to tell people you’re sprinting, make sure they can find you. It’s worth having some signs to draw attention to which table/room you are in, on top of anything the conference provides. I travel to PyCon US with pop-up banners - they’re great to stand in front of the room to draw attention - but tape or Blu-tack and an A4 printed page, or a plastic sign holder in the middle of your table can be just as effective.

### Welcome everyone to the room

Don't assume you can just put up a sign and people will "find their own way". If you see someone enter the room, go out of your way to say hello, introduce yourself, and see if you can get them hooked. It helps to have a short canned speech describing the first steps for contributing - for many, "do the tutorial" is a good first step. BeeWare has honed this down to a specific [Sprint Guide](https://beeware.org/contributing/sprint-guide/) to help us shape that initial conversation, and give a clear TODO list for people when they arrive.

It also helps if that speech is focused on *them* rather than you and your project. If you can make your project feel like a place that needs *them* specifically, or is well suited to *their* specific skills, or aligned with *their* or needs, then all the better. This could be as simple as asking "What brings you to our sprint?", or asking where they work and what they use Python for. In addition to making a personal connection, it gives you an opportunity to tailor your "pitch" to their interests, and a way to narrow any suggestions for sprint projects that are more likely to be "on topic" for them.

### Help every attendee find their first issue

If someone turns up and flails for an hour, they're going to go away disappointed - and probably won't tell you when they leave. You need to help them get initial traction. This is where the contribution guide, curated first-issue list and welcome script all come together.

Make sure that you have a process to make sure that two people don't pick the same issue. This doesn't have to be high tech - it can be as simple as posting a comment on the issue they've picked saying they're working on it.

### Set them up for success

When you help someone pick a first issue, don't throw them a nasty crunchy bug that is hard to reproduce. Get them to fix a typo, or add an error message for a bug that can be easily reproduced. The first issue is where they will be learning about your project's contribution process. Make it easy for them to get the first win; their *second* issue can be something more complicated.

### Circulate around the room

Don’t plant yourself in the corner and assume people will find you when they need help - circulate around the room and ask how people are doing. If nothing else, this is a chance to make a personal connection with the audience; but it is also surprisingly effective at getting someone who is beating their head against a simple problem to admit they’re having a simple problem, and get them unstuck.

### Be wary of assumed knowledge

You might think that everyone at PyCon knows how to use Github. You would be wrong. I've had to walk sprint attendees through very entry level Github tasks. It is inevitable that someone will submit a pull request from the main branch of a fork, and you'll then have to walk them through cleaning up the mess they've made. The same goes with assumptions about Python environments, environment variables - things that you'd think would be assumed knowledge for someone attending a Python conference. Often part of the challenge of helping sprinters is working out what it is they don't know - because often they don't even know enough to know they don't know something.

### Make yourself available

If you're committing to running a sprint, you won't get anything of your *own* work done. For the first half day, you'll be introducing and onboarding contributors; for the rest of the time, you'll be reviewing PRs. You can't just put on headphones and focus - you need to be there for the community that has joined you. If you’re sprinting well, you will get nothing done on your own TODO list.

### Celebrate every win

When you merge someone's PR, make a big deal about it. Django sprints have historically had a gong (or other obnoxious musical instrument, like an air horn or bike bell) that you get to bang when your PR is merged. It doesn't have to involve equipment, though - I usually try to start a round of applause in the room - pretty soon, everyone knows if you hear applause, someone just got their wings.

If you have the budget, having a small token of appreciation for that first win can also be a useful incentive. BeeWare has [challenge coins](https://beeware.org/contributing/challenge-coins/) that are given to everyone on their first commit; but it doesn't need to be an expensive thing - even a "sprint exclusive sticker" could work.

### Be relentlessly positive

People attending sprints often have a lot of imposter syndrome. After all - they're attending a conference, and they've just seen all these super-rock-star-ninjas speak about their projects... how could they possibly contribute? A big part of running a successful sprint is to dispel that mental model, and get them over the mental hurdle of contributing at all. Reinforcing the "yes, you can contribute" message at every opportunity is important to ensuring nobody bounces off because of imposter syndrome.

This is one of the reasons that Challenge Coins work - it provides a very small, but tangible reason why it's worth working through the imposter syndrome. You’d be shocked how much people will struggle through to get $1.50 worth of enamel and steel.

### Be aware of CI limits

BeeWare has literally broken CI systems during sprints through the load that has been generated. At the very least, expect a CI backlog. If you're giving out tokens for completion like challenge coins, you might need to use "review approval" rather than "merge" as the success criterion. If you have any way to optimize your CI processes, that’s also worth doing ahead of time.

### Set boundaries for yourself

Sprinting for 3-4 days, being "on" and positive for the whole time, is exhausting. Make sure you take time for yourself - step away for coffee and for meals, and don’t be afraid to step away at 5PM.

## After the sprint

### Have realistic expectations

I go into every sprint hoping that we’ll uncover the Next Great Contributor. Realistically - this never happens. Sprinting isn’t magic. In my experience, it’s more about exposure and marketing - a way to make a community feel good about your project. Over time, those good vibes accumulate.

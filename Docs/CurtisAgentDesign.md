Most people think a subagent is “just a prompt” or let the client generate it automagically.



It’s not how I see it…



After building dozens of subagents for Claude Code 

@AnthropicAI

&nbsp;and now 

@FactoryAI

&nbsp;here’s the actual process I use to build subagents that work… it’s probably not what you think.



The purpose of a subagent isn’t to be another generic coding assistant. It’s to be a trust-delegated expert that’s the BEST fit for a specific task… with expertise that goes beyond all your other agents. 🧵

Show more replies

John Curtis

@Social\_Quotient

·

7h

After making agents and tech scope, I ask the main agent to work with ALL subagents to get feedback on our scope. Each writes concerns to `/ai-artifacts/research/agent-concerns` in its own file. (This way it runs in parallel.) Then the main agent tells me so I can read.



I take agent criticism at this step very seriously. The outcomes are:



1\. I got it wrong and they are right



2\. They don’t know and are wrong, so I need to edit context, break the feature down differently, or be ready to code this part myself

3\. They stepped out of their expertise and don’t know what the other agent knows via my agent definition training

John Curtis

@Social\_Quotient

·

7h

Building subagents isn’t about writing better prompts.



It’s about teaching them context they couldn’t have known. It’s about curating their knowledge sources, giving them location awareness, making them team-aware, and letting them critique your architecture.



Context > prompts, every time.



Hope this was enjoyable and a good glimpse in to my thinking and flow! Remember it’s (n) of 1 and I made all this in a vacuum for just myself, not as a best practice for you!



Thanks again to 

@RayFernando1337

&nbsp;For the into to factory and droids. Thanks to the others that have taught me a ton about how to conceptualize llms 

@AmandaAskell

&nbsp;

@DaveShapi

&nbsp;

@natebjones

John Curtis

@Social\_Quotient

·

Oct 9

I had a productive and fascinating session coding with 

@FactoryAI

&nbsp;today. I worked on scoping, researching, and detailing the project for about two hours before handing it off to the subagent droid experts, who spent roughly 1.5 hours coding the solution. (Maybe just over 4-4.5mm tokens. At one point, I stepped in to remind it to prompt me for the necessary 

@CloudflareDev

&nbsp;and 

@OpenAI

&nbsp;API keys. By the time it wrapped up, all tests had passed, and the solution was declared “production-ready”… hmmm



Skeptical but curious, I immediately checked cloudflare just to see if it had actually deployed by itself - wrangler not gh cheating! …. Not only did it, but the tests and the payload in the file system were real. I then spent an additional 30 minutes asking the main droid to evaluate areas where the sub droids could improve. From there, I reviewed and approved about 80% of the updates to the droid definitions. It was a great exercise in refining and optimizing the process. (Btw I would encourage everyone to do this even if you don’t accept the changes after each agent dev session. Write the notes to obsidian and maybe weekly go through it and then make changes)



The droids below are hyper specific (and artfully named) … I asked main droid what would be helpful to have based on my scope doc and it proposed these. I had it write a 3 sentence summary of the skills for each role. Tbh… I have a ton of claude code utils so I had CC build the droids.. I have hook utils and context7 researcher all ironed out that I haven’t ported over yet. 



But this was a flawless. Coding session.


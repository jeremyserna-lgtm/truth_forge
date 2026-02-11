{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0  Welcome back to the deep dive. We are uh we're doing something a little a little different today. Yeah. Usually when we sit down at this table, we're looking at a specific vertical.\
\
 a new book on management, a trend in crypto, or you know, a specific piece of software. Right, one topic. Today we are looking at a collision. It really is a collision. I mean, it's like watching three weather systems crash into each other to form a superstorm.\
\
 Oh, for sure. First, we have high-level philosophical writing from a Dr. David Lee at the Massive Heart Blog. This is deep regulated clinical safety stuff regarding the NHS and the future of AI.\
\
 The world of first do no harm. Very cautious. Very garden. Right. But directly underneath that we have this gritty, dense stack of technical interaction logs.\
\
 The complete opposite. We are talking about someone using Dtrace to reverse engineer Apple Silicon chips. running Linux on bare metal and trying to build a cluster of autonomous agents. This is the jungle. And the third piece is the bridge. It 's a psychological profile And a very detailed financial report for you, Jeremy Cerna, also known by the persona, Anders Bowlingwell. Exactly.\
\
 So we have the high-level theory, the low-level code, and then the very real human constraint. the mortgage, the student loans, the personality traits that are binding this whole mess together.\
\
 The mission today is to figure out how these fit because on the surface A blog about NHS safety protocols and a terminal log about kernel panic seem totally unrelated, but you think they're telling the same story. I do. It 's a study in control versus chaos.\
\
 On one side you have the official future, the FDA, the EU, the hospitals trying to put fences around AI. Okay. On the other side, you have Jeremy, our renegade. Tearing those fences down to see how fast the engine can actually go. Let 's start with the fences then. Let 's start in the official future with Dr. David Lee. I was really struck by his writing.\
\
 He frames the current moment in AI not as a tech problem, but as a regulator's dilemma. It's the classic problem of the tiger. Dr. Lee quotes a few different thinkers here, but the core metaphor is.\
\
 AI is a tiger. You can't really control a tiger. You can just sort of hang on. You could hold it by the tail for a while But eventually it's gonna do what it wants. And he points out that the world is split on how to handle this tiger. You 've got the yes crowd shouting, accelerate, the no crowd shouting stop. And the wait crowd just trying to Pause time.\
\
 Which is where the regulators live. Right. And Lee uses a cricket metaphor, which for those who don't watch cricket, basically means if you hesitate in the middle of the pitch, you're dead. You get run out. Uh -huh.\
\
 He's saying that if regulators hesitate too long, the technology will just bypass them completely. He breaks down how different regions are trying to handle this, and it's fascinating because it shows just how fragmented the official world is. Oh, it's a mess.\
\
 You have the EU, which is taking the safety first approach. They categorize medical AI as high risk. They want total explainability. Which sounds reasonable, right? I mean if a doctor tells me I'm sick, I want to know why. Why is that a problem?\
\
 It sounds reasonable until you talk to the technologists. Lee quotes Eric Schmidt here, who argues that deep learning is inherently a black box. It 's probabilistic.\
\
 It is. It connects millions of dots in ways a human brain just can't follow. So if you demand 100% explainability, you basically outlaw deep learning. You kill the innovation before it starts.\
\
 So the EU is the strict parent. What about the US? The US FDA is trying something more, well, more corporate. They 're looking at software as a medical device.\
\
 But because they can't check every line of code in an AI that learns and changes every day. They can't keep up. They can't. So they're trying to certify the company. They want to certify that you have a culture of quality. So if the company is safe, the software is assumed to be safe.\
\
 That feels a bit like letting the fox guard the hen house, doesn't it? It 's a risk-based approach. It's a pre-certification pilot. And then you have the UK which is trying to be agile. The middle ground. They want to balance safety with speed.\
\
 But Dr. Lee drops a reality check on all of this regulation talk. He has a post titled, No Patient Data, Reduced Clinical Safety. This was the chilling part for me.\
\
 We tend to think of IT failure as, oh, the Wi-Fi is down, I can't check my email. Or Netflix is buffering. Right.  An inconvenience. But in a hospital, IT failure means people get hurt He lists the Wanakrae cyberattack in 2017. It infected 200,000 PCs. It locked down the NHS.\
\
 And ambulances have to be diverted to other cities. Think about that. You 're having a heart attack, you're in the ambulance, and suddenly the driver gets a call saying, turn around, the hospital computer's down, you have to drive another twenty minutes.\
\
 That's life or death. Exactly.  And the Lee's laboratory failure in twenty sixteen. The server that processed blood tests crashed. So no surgeries. They had to cancel operations because it you can't cut someone open if you don't know their blood type or their clotting factors.\
\
 Lee's point is that digital resilience is clinical safety. It's not separate. If the tech fails, the patient fails. And this leads to his solution. He proposes Dr. Finlayai. I love the pun It's a great pun, but explain the concept because it's not just about a robot doctor.\
\
 No, he's arguing against the replacer mindset. He doesn't want an AI doctor replacing the human. He wants a partnership. He wants the AI to be the clerk. Handling the data, the patterns, the admin. So the human can go back to the laying on of hands. Empathy, judgment, nuance.\
\
 But here is the crucial technical nugget that links us to you, Jeremy. Dr. Lee suggests a three-way partnership. The Doctor And two AIs. Two AIs. Why two? Is one not enough? One isn't safe enough. He wants one AI to do the work and one to check the work. A peer review system.\
\
 Ah, because AIs hallucinate. They make things up. So you have AIA write the diagnosis and AIB critiques it and the human doctor makes the final call. Okay, hold that thought. Two AIs. One doing the work, one checking the map.\
\
 Because that is the perfect bridge to leave the safe, regulated hospital and descend into the basement. Into the jungle. We are looking at the technical logs you provided, Jeremy. And you're building exactly what Dr. Lee is talking about.\
\
 But you're not doing it with a safety grant or an FX board. You 're doing it on a cluster of Mac Studios using something called a Sahi Linux. This is where we get to the renegade reality. You 're operating on the bleeding edge of what consumer hardware can do You have a cluster with 1.28 terabytes of unified memory. 1.\
\
28. That 's Okay, for the non-gearheads listening, that sounds like a lot, but. Why does that matter for AI? It 's absurdly high for a home setup. I mean a high-end gaming PC might have 32 or 64 gigabytes. You have terabytes.\
\
 But the keyword is unified. Right. In a normal computer, the CPU, the brain, has its memory, and the graphics card, the muscle, has its own memory. To move data between them, you have to copy it across a wire, the PCIe bus. That wire is slow. Compared to the chip. It 's a dirt road. It 's a bottleneck. Apple Silicon puts everything on the same chip. The CPU and GPU share the same pool of memory. No copying.\
\
 Zero latency. And you're leveraging this to run massive AI models that usually only run on industrial server farms. You're running two specific models. Maverick and Scout. This is the Dr. Finlay I concept in practice. It is. You 're dealing with the trade-off between context and reasoning. Break that down for us. Why do you need two models? Okay, imagine you have a librarian.\
\
 who has read every book in the library. That 's high context. But they're not very creative, which is low reasoning. That 's scout. Scout has a 10 million token context window. It sees everything, the whole code base, the whole manual, the whole project history. But Scout can't solve the puzzle. It just knows where all the pieces are. Okay.\
\
 Then you have Maverick. Maverick is a genius logician high reasoning, but has a very short memory, small context. So Maverick is smart but blind. Exactly.  So the challenge, and the logs show this clearly, is the semantic gap.\
\
 How do you get the genius, Maverick, to use the memory of the librarian, Scout, without slowing everything down by copying text back and forth? And the solution in the logs is Intense. They're talking about sharing tensor states. This is hardcore engineering. Instead of having Scout write a summary and emailing it to Maverick, you want to link their brains directly.\
\
 You want to map the tensor state, the actual mathematical representation of the memory, into that unified memory so Maverick can access it instantly. It 's like telepathy versus writing a letter. Wow.\
\
 Exactly.  But to do that, you can't use standard Mac OS. Yeah. Apple puts guardrails on everything. They don't let you touch the memory that deep down. So you have to rip the operating system out by the root.\
\
 Which brings us to the levels of control document found in the logs. It 's a ladder of independence. It starts at level zero application. That 's where we all live. I open an app, I click button. Boring.\
\
 You want more Level 1 is appliance kiosk mode. Level 2 is alternative OS, installing Asahi Linux. This is already dangerous territory.\
\
 You are reverse engineering the drivers to make the hardware work without Apple's help. But you go further, level three is unified memory clustering, linking multiple Macs together to act as one giant brain. And the ultimate goal is level six.\
\
 Software on metal. No OS, just your code talking directly to the electricity and the silicone. There 's a specific part of the log where you use a tool called Dtrace. And it felt like watching a safe cracker work. It really is. The Apple Neural Engine, the ANE, is a black box. Apple doesn't tell you how it works. They don't publish the manual So you're using Dtrace to listen to the firmware. You 're watching the instructions fly by, looking for the exact moment the Linux driver fails, so you can write the code to bridge the gap. The log says.\
\
 Find where they stopped. That's where you start. It 's so determined. It 's the definition of Dr. Lee 's holding the tiger by the tail. You are reverse engineering the brain of the chip while it's running. There is no FDA here. There is no safety board. It 's just grep.\
\
 Detrace and ambition. Which brings us to the operator. Who is the person crazy enough or brilliant enough to do this? We have an analysis file, generous analysis.txt, and an experience credit report for you, Jeremy Cerna. This is where the story gets human. The analysis describes a persona, Anders Bowling Mo.\
\
 And this isn't your typical IT guy profile. It describes you as a visionary disruptor, a wanderer. It says you tour the US in a converted box truck. You build spaces. That 's the key phrase. You build spaces for exploration.\
\
 Sometimes that's a physical space like the truck or the Kink and BDSM communities you're involved in. And sometimes it's a digital space like this AI cluster. Right. The profile mentions your sex positive, competitive, and a disruptor of shame.\
\
 It paints a picture of someone who refuses to accept default settings. Whether that's in society, relationships, or computer hardware. Exactly. You invent games, you'd like to be the game master, and building this supercomputer.\
\
 This is the ultimate game. The profile says you balance intellect with instinct. Razor sharp, but also gut-driven. But here is the friction. Building a world-class supercomputer costs money. And when we look at the Experian report, you're not a billionaire. No, you're a guy with a mortgage. The report lists 42 accounts.\
\
 We see a significant student loan balance around $174,000. A mortgage of about $329,000. And we see a lot of credit card activity. Amex, Bank of America, Chase. It looks like a lot of debt. I mean looking at this, my palms get a little sweaty It is debt, but I'd call it leverage. If you look closely, you manage it, you pay things down, you open accounts, use them, close them.\
\
 This is someone who is financing their ambition. You're bootstrapping superintelligence. That 's it. That 's a heavy load to carry though. The mental overhead of 174K in student loans, plus a mortgage, plus the cost of these Mac Studios.\
\
 That's the dungeon the profile talks about. It explains the urgency in the logs. You aren't doing this as a hobby. You need this to work The profile explicitly mentions hardware limitations and a need for a tech upgrade. You 're trying to engineer your way out of those financial constraints by building a tool that amplifies your ability to work.\
\
 It's such a stark contrast. On one side, you have Dr. Lee and the NHS, massive budgets, massive bureaucracy, slow movement. On the other, you have Jeremy, tight budget, high leverage, moving at the speed of light. And yet They are converging on the exact same solution. The high performing team. Right.\
\
 Dr. Lee writes about thinking like a gardener. He says teams need nurturing, psychological safety, and delegation. He says you can't do it all yourself. And your profile admits this.\
\
 Under growth areas, it says delegation and scaling. It says you need to trust others to help implement. But here is the twist. You can't afford a team of engineers.\
\
 You have a mortgage. You can't hire a staff. So who are you delegating to? Maverick and Scout. You are building the high-performing team out of silicon. The logs talk about a not me agent.\
\
 This is a crucial concept. You want to create an autonomous system, an agent zero. that runs the computer without your hands on the keyboard. You 're gardening, but you're gardening code. You are cloning your own agency. If you can get Maverick, the reasoner, and Scout, the librarian, to work together perfectly.\
\
 You have effectively hired two world-class employees for the cost of electricity. But is it safe? That brings us back to the start. Dr. Lee is terrified of AI hallucinations.\
\
 He mentions the anorexia case where an AI chatbot invented a fake BMI number for a patient. In the medical world, that's a lawsuit and a tragedy. In your world, it's a bug. Right, but look at how you solve it.\
\
 You're using the exact same method Dr. Lee proposed, the peer review. Maverick Checks Scout. Scout checks Maverick. You are engineering a circle of safety. inside the machine because there is no human circle of safety outside of it. But there is one big difference. In the hospital, there is a human in the loop.\
\
 Doctor Finlay ultimately reports to a human doctor. Yeah. In your level six vision, running software on metal Who is the human in the loop? It 's just you. And if you succeed, if you build this not me agent that can think, code, and execute autonomously.\
\
 You are removing yourself from the loop. The not me agent implies separation. It implies that it's distinct from you. Exactly. If it's truly not me, then it has its own agency. Dr. Lee said resistance is futile. Partnership is possible.\
\
 You were taking that literally. You were building the partner. But as you move up those levels of control application, appliance, OS, metal di you're taking on more and more responsibility. When you strip away the OS, you strip away the safety net. If the chip overheats, that's on you.\
\
 If the AI writes a script that deletes your hard drive, that's on you. It 's the ultimate expression of the disruptor personality found in your profile. You are willing to risk the chaos of the jungle to escape the limitations of the garden. So what does this all mean for you, Jeremy We've gone from the bureaucratic struggles of Brussels and the FDA to the instruction-level tracing of the Apple Neural Engine.\
\
 We've seen that you are intellectually limitless. but operating within very real financial and hardware walls. It 's a story about agency. Dr. Lee wants agency for the doctors.\
\
 To use AI as a tool, not a replacement. You want agency for yourself to turn your computer into a sovereign entity that works for you free from Apple's constraints and free from your own time limitations. And both of you are wrestling with the same truth. The wave is coming. You can either stand on the shore and legislate it like the EU, or you can grab a board or an odd iron and try to surf it. The question is Once you're up on that wave, do you control it? Or does it go where it wants? You 're building a system maverick and scout that is designed to be smarter than a single model. You are building a not me.\
\
 And as Dr. Lee warned, if you create a tiger, eventually you have to let go of the tail. And when you do, you just have to hope that you raised it well. That is a lot to think about. From the NHS to the bare metal of the M1 chip, the problem remains the same.\
\
 How do we build things that are powerful enough to help us, but safe enough not to break us? And can we pay off the student loans while we do it? That is the real question. Thanks for listening to the deep dive. We 'll see you next time.}
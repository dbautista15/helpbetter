"""
Load Demo Data for Introspect - Hackathon Presentation

WHY THIS EXISTS:
- Judges won't write 10 entries during 5-minute demo
- Pre-loaded data shows pattern detection IMMEDIATELY
- Showcases the "wow factor" in first 30 seconds

DESIGN PRINCIPLES:
- Show recurring themes (anxiety → preparation → success)
- Show what helped (talking to friends, exercise, therapy)
- Show mood variation (2s and 5s, not all 3s)
- Spread over 2 weeks for time progression
- Use different words for similar emotions (tests semantic search)
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

# Use environment variable for database path (same as Electron)
# If not set, uses local journal.db
db_path = os.getenv("DB_PATH", "journal.db")
db = Database(db_path)

# Demo entries designed to show clear patterns
demo_entries = [
    {
        "content": "First day of junior year and I'm already stressed about money. Picked up two extra shifts at Target this week just to cover textbooks. The bill came to $420 for three books - three! I managed to find PDFs for two of them online, which saved me maybe $200, but I still had to buy the Data Structures book because it comes with this stupid online access code for homework. Without that code, I literally cannot do the assignments. The professor requires it. So there went $180 in one purchase. That's almost half my rent. I stood in the bookstore for ten minutes just staring at it, trying to figure out if there was any way around buying it. There wasn't. Now I'm looking at my bank account and doing math in my head for the rest of the month. Rent is $400, utilities about $60, food if I'm careful maybe $120, gas $80. That leaves me basically nothing for emergencies. What if my car breaks down? What if I get sick? I can't think about that right now. One day at a time. At least I got the evening shifts this week so they don't conflict with classes. My manager knows I'm in school but she's not always accommodating about it. I need this job. I need these shifts. I need to pass these classes. It all has to work somehow.",
        "mood": 3,
        "days_ago": 730
    },
    {
        "content": "Manager scheduled me during my database lecture tomorrow. I got the schedule this morning and just felt my stomach drop. I tried to get someone to cover - texted literally everyone on the shift list. Nobody can take it. Or nobody wants to take it, I can't tell which. If I miss work, I'm $90 short on rent. If I miss class, I'll be completely lost for the exam next week. This lecture is covering join operations and query optimization, which I already barely understand from reading the textbook. The professor doesn't record lectures. She doesn't post slides. If you miss class, you're just screwed. I thought about emailing her to explain but what am I supposed to say? 'Sorry I can't come to the class I'm paying thousands of dollars for because I have to stock shelves to afford to take your class'? I asked my manager if I could come in late but she said we're short-staffed and she needs me for the full shift. I don't know what to do. I really don't. Maybe I can find someone's notes? But everyone in that class is so competitive, nobody shares anything. I might just have to miss work and eat ramen for a week to make up the difference. This is exactly the kind of impossible choice I deal with constantly and I'm so tired of it.",
        "mood": 2,
        "days_ago": 725
    },
    {
        "content": "Group meeting for Software Engineering project today. Everyone wanted to meet at 2pm on Tuesday. That's right in the middle of my shift at Target. I tried to explain that I work and I can't just take off whenever. One guy - I think his name is Brandon - literally said 'can't you just take off?' Like it's that simple. Like missing work is no big deal. I tried to stay calm and suggested we meet at 7pm instead, after my shift ends. He sighed - actually sighed - and said that's too late and he has dinner plans. Dinner plans. I wanted to scream. Another girl suggested Sunday morning but I work Sunday mornings too. Finally we settled on Wednesday at 8pm which works for nobody but at least I can be there. But now I'm the difficult one. I'm the problem in the group. They don't get it and I'm tired of explaining it. They don't understand that missing one shift could mean I can't pay my electric bill. That I don't have parents sending me money if I come up short. That work isn't optional for me. It's survival.",
        "mood": 2,
        "days_ago": 718
    },
    {
        "content": "Ramen for dinner again. Third night in a row.",
        "mood": 3,
        "days_ago": 710
    },
    {
        "content": "Got invited to a hackathon this weekend. Everyone in my algorithms class is going. The registration is $50 and it's Friday through Sunday, which means I'd miss two shifts at work. That's $180 in lost wages plus the $50 fee. I can't afford either one, let alone both. This is exactly the kind of thing that would look amazing on my resume. Companies love hackathon experience. It's networking, it's practical coding, it's collaboration - all the things career counselors say are essential. But I literally cannot go. My classmates are all signing up together and talking about what project they're going to build. One guy is trying to recruit me for his team because he remembers I did well on the last assignment. I had to tell him I can't make it and he looked so confused. 'Why not?' he asked. What am I supposed to say? The truth is embarrassing. So I mumbled something about having plans already and he just shrugged and moved on. Meanwhile I'll be at Target scanning groceries while they're building cool projects and making connections with industry sponsors. The gap between me and my peers just keeps getting wider.",
        "mood": 2,
        "days_ago": 703
    },
    {
        "content": "Laptop froze three times during my OS assignment today. The fan sounds like it's dying. This thing is five years old and running so slow I want to throw it against a wall. It takes three minutes just to boot up. If this laptop dies I'm completely screwed. A new one would cost at least $800, probably more for something that can actually run the VMs we need for class. I don't have $800. I don't even have $200 for a used one. I've been looking at my options and they're all terrible. I could try to finance one through the school bookstore but the interest rate is insane and I'd be paying it off for years. I could use a credit card but I don't have one with a limit high enough. I could try to use the computer lab on campus but those close at 10pm and I usually work until 9:30, plus they're always full during busy weeks. So basically I just have to pray this laptop survives until graduation. That's my plan. Prayer. I'm running disk cleanup and deleting anything non-essential. Cleared 20GB of space. Hopefully that helps. I need this thing to last 18 more months.",
        "mood": 3,
        "days_ago": 695
    },
    {
        "content": "Career fair was today. Put on my one dress shirt and went between classes. Talked to maybe ten companies. Amazon, Google, a bunch of banks, some local startups. They all had the same thing - summer internship opportunities. Sounds great, right? Except when I asked about pay, most were unpaid or paid like $12/hour. I need to make at least $15/hour working 40 hours a week just to survive the summer and save something for fall. These internships are like 20-30 hours a week at half the pay. The math doesn't work. When I tried to explain this to one recruiter, she suggested I 'find a way to make it work' because the experience is invaluable. Easy for her to say. She's not worried about rent. I asked if they had any part-time internships that I could do alongside another job and she looked at me like I was crazy. These companies want your full dedication. They want you available for team lunches and networking events and social hours. They design these programs for students who have family money. Students who can afford to take a prestigious unpaid internship at a tech company because mom and dad are covering their expenses. I don't have that option. So my resume stays empty while everyone else gets experience.",
        "mood": 2,
        "days_ago": 688
    },
    {
        "content": "Studied until 3am for the algorithms midterm. Set my alarm for 6am because I had to be at work at 7. Got maybe two hours of sleep. Spent the whole shift in a fog. I was stocking shelves and I literally fell asleep standing up - caught myself as I was falling forward. My manager saw and pulled me aside. She wasn't mean about it but she said I need to be more professional and alert at work. I wanted to tell her I was up all night studying for an exam that determines my entire future but I just apologized and said it wouldn't happen again. Chugged two energy drinks during my break. Made it through the shift but I felt like a zombie. Then I had to go straight to campus for the exam at 1pm. I think I did okay on it. I knew the material. But I could feel my brain working in slow motion. I'd read a question and have to read it twice to understand it. I knew how to solve the problems but it took me so much longer than it should have. I don't know how to keep doing this. Everyone says college is hard but this isn't normal college hard. This is something else.",
        "mood": 1,
        "days_ago": 680
    },
    {
        "content": "Check engine light came on this morning. My heart just sank when I saw it. Drove to AutoZone on my break and they scanned it for free - something about the oxygen sensor and maybe the catalytic converter. The guy said it could be anywhere from $150 to $600 depending on what's actually wrong. I cannot afford car repairs right now. I literally cannot. My checking account has $340 in it and rent is due in five days. If I have to pay for a major repair I'll have to choose between fixing my car and paying rent. If I don't fix the car I can't get to work or class. If I don't pay rent I get evicted. There's no good option here. I'm going to ignore it for now and hope it's not urgent. The car still runs fine. Maybe I can just live with the light on until I save up some money? I know that's stupid and it could lead to worse problems but what choice do I have? This is the kind of thing that keeps me up at night. One unexpected expense and my entire life could fall apart. No safety net. No backup plan. Just constant stress.",
        "mood": 2,
        "days_ago": 672
    },
    {
        "content": "Actually had a good day for once. Aced my databases exam - got a 96. I knew the material cold and it showed. Felt amazing to see that grade. My professor even pulled me aside after class and said she was impressed with my answer on the normalization question. That made me feel proud. Like maybe I actually belong here. Then my coworker Jessica covered my closing shift tonight so I could have time to study for my algorithms exam tomorrow. She didn't have to do that but she knows I'm juggling a lot. Sometimes people surprise you with kindness. And then - this is the really good part - I found a $20 bill in my winter jacket pocket. I was looking for my gloves and there it was, folded up in the inside pocket. Must have put it there last year and forgot about it. Twenty dollars. That's groceries. That's gas. That felt like winning the lottery honestly. Everything doesn't have to be terrible all the time. Today was proof of that.",
        "mood": 4,
        "days_ago": 400
    },
    {
        "content": "Car inspection is due this month. Took it to the mechanic today to get it checked before the official inspection. He found issues. Brake pads are worn down. Something wrong with the exhaust system. Gave me a quote: $200 for the brakes, another $150 for the exhaust repair, plus $30 for the inspection itself. $380 total. There goes my entire savings account. Every penny I saved over the summer. Gone. I wanted to cry right there in the mechanic's shop. I've been so careful with money. Been saving every extra dollar. And now it's all going to car repairs. Back to square one. Back to living paycheck to paycheck with nothing in savings. I'm so tired of this cycle. Every time I get a little ahead something happens and I'm broke again. When does it end? When do I get to actually have financial security?",
        "mood": 1,
        "days_ago": 390
    },
    {
        "content": "Started applying to full-time jobs today. Need to graduate in May with something lined up. Can't afford to be unemployed. Went on LinkedIn and Indeed and started searching. Every single posting wants 2-3 years of experience. For entry level positions. How does that make any sense? How am I supposed to have years of experience when I'm just graduating? I've been surviving, not building the perfect resume. I have my capstone project, my personal React app, and IT helpdesk experience. That's it. No fancy internships at big tech companies. No research publications. Just a guy who worked his way through school and managed to get decent grades. Is that enough? I don't know. The anxiety is crushing. What if I can't find a job? What if four years of struggle ends with nothing?",
        "mood": 2,
        "days_ago": 380
    },
    {
        "content": "Thanksgiving week. Working Black Friday for double pay. $240 for one eight-hour shift. Can't turn that down. Mom called and asked if I'm coming home for Thanksgiving. Had to tell her no again. She sounded sad but she gets it. My family doesn't have money to help me and they understand I need to work. But it still feels bad. I'm 22 years old and I haven't been home for a holiday in two years. Everyone else gets to have normal college experiences. Normal family time. I get shifts and paychecks. At least the money is good. That's what I keep telling myself.",
        "mood": 3,
        "days_ago": 365
    },
    {
        "content": "Got a phone interview for a junior developer position! Company is local, builds software for healthcare systems. They seemed really interested in my capstone project. Asked good questions about my technical decisions. I felt like I answered well. They want me to come in for a second round interview next week. This could be it. This could actually be it. A real software development job. $60k salary according to the posting. That's more money than I've ever imagined making. I could actually pay my bills without constant stress. Could start paying off student loans. Could maybe even save money. Trying not to get my hopes up but it's hard. This feels real.",
        "mood": 4,
        "days_ago": 350
    },
    {
        "content": "Didn't get the job. Got the rejection email today. 'We've decided to move forward with a candidate who has more experience.' More experience. For a junior position. How am I supposed to get experience if no one will hire me without experience? I sat in my car after work and just felt defeated. Four years of killing myself. Four years of working full time and going to school full time and barely sleeping and eating ramen and stressing about every dollar. And I'm still not good enough. Still not competitive. What was it all for? I'm never going to break into this field. The system is designed for people who can afford unpaid internships and have time to do research projects and go to networking events. Not for people like me who are just trying to survive. I don't know what to do anymore.",
        "mood": 1,
        "days_ago": 340
    },
    {
        "content": "Professor Chen pulled me aside after class today. Said my work on the capstone project has been really strong. The mobile app we built is actually impressive. She asked if I'd ever considered grad school. I almost laughed. Grad school? I can barely afford undergrad. I explained my situation - working full time, no family support, already taking out loans. She nodded and seemed to understand. Then she said if I ever change my mind she'd write me a strong recommendation letter. That was nice of her. Made me feel like maybe I'm not a complete failure. But grad school isn't realistic for me. I need to graduate and get a job. Need to start making real money. Can't afford two more years of being poor.",
        "mood": 3,
        "days_ago": 330
    },
    {
        "content": "Last semester starts tomorrow. Spring 2024. This is it. Final push. Bought textbooks today. $390 total but I found most as PDFs so only paid for two physical books. Job application update: 47 applications sent, 3 responses, 1 interview scheduled for next week. The ratio is depressing. Less than 10% response rate. But at least there's one interview. It's with a local startup. They're looking for a full-stack developer. Pays $58k which is less than I hoped for but it's still decent. Interview is Tuesday afternoon. I have the whole weekend to prepare. Going to practice coding problems and review my projects. This has to work out. It has to.",
        "mood": 3,
        "days_ago": 315
    },
    {
        "content": "Had the second round interview today. It was intense. Three hours total. Met with the CTO, two senior developers, and the CEO. Technical portion was tough. They asked me to debug a piece of code on a whiteboard and explain my thought process. Then they had me design a database schema for a hypothetical application. I think I did okay. Not perfect but okay. They seemed impressed with my capstone project and asked a lot of questions about the architecture decisions we made. The CEO asked about my work experience and I explained I've been working full time through school. He actually seemed to respect that. Said it shows work ethic and time management. Maybe working retail isn't completely useless on a resume after all. They said they'd make a decision by end of week. I'm trying not to obsess over it but it's all I can think about. Please let this work out. Please.",
        "mood": 4,
        "days_ago": 300
    },
    {
        "content": "They offered me the job. I got the offer email this morning. Junior Software Developer. $65,000 salary. Full benefits. Health insurance, dental, vision, 401k matching. Starts two weeks after graduation. I read the email three times to make sure it was real. Then I went out to my car in the parking lot and cried. Just sat there and cried. Four years. Four years of working myself to exhaustion. Four years of stress and fear and barely making it. Four years of watching my classmates get opportunities I couldn't afford. Four years of feeling like I wasn't good enough. And it worked. It actually worked. I'm going to be a real software developer. I'm going to make enough money to live without constant panic. I can start paying off my loans. I can afford to fix my car. I can buy groceries without calculating every dollar. The nightmare is almost over. There's finally light at the end of this tunnel. It was worth it. Maybe it was all worth it.",
        "mood": 5,
        "days_ago": 295
    },
    {
        "content": "Professor announced today that the final project for Cloud Computing requires AWS credits. He said we need at least $100 worth to complete the project properly - setting up EC2 instances, S3 storage, load balancers, the whole thing. He literally said 'it's not that much' and half the class nodded along. Not that much. That's a quarter of my rent. That's two weeks of groceries. I raised my hand and asked if there was any alternative for students who can't afford it. He looked uncomfortable and said AWS has an education program that gives some free credits but it probably won't be enough for everything we need to do. Then he moved on with the lecture. So basically, figure it out or fail the project. I looked into the AWS education credits after class - it's $100 of free credits but you have to apply and wait for approval and there's no guarantee. What if I don't get approved? What if it doesn't cover everything? I'll find a way like I always do but I'm so tired of every single class having some hidden cost that professors just assume everyone can handle.",
        "mood": 2,
        "days_ago": 657
    },
    {
        "content": "Thanksgiving break is coming up. Everyone in my classes is talking about going home to see family. Flying to visit relatives. Road trips. Big family dinners. I told my parents I can't make it home this year. They were disappointed but they understand. Truth is I picked up three extra shifts over the break including working Thanksgiving Day. The store is paying time and a half that day so it's actually good money. I'll make $240 just for that one shift. I need it. November rent is tight and I need to start saving for December and January. But it feels lonely. Last year I went home and it was nice to see everyone. This year I'll be stocking shelves while everyone else is with their families. At least I'll have money. That's what I keep telling myself.",
        "mood": 3,
        "days_ago": 650
    },
    {
        "content": "One of my group members asked why I never respond in our Discord during the day. They post messages at like 2pm and get annoyed when I don't reply until 8 or 9pm. I had to explain, again, that I work during the day. I'm not just 'busy' - I'm literally at work, on my feet, doing a job, earning money to survive. I can't be on my phone checking Discord. My manager would write me up. This is the third time I've had to explain this to this particular person. He doesn't get it. He'll message at 3pm like 'hey can you check the code I just pushed' and then get passive aggressive when I don't respond for five hours. I finally snapped a little and said 'I work a job, I respond when I can, deal with it.' Probably not the most professional response but I'm tired of apologizing for having to work.",
        "mood": 3,
        "days_ago": 642
    },
    {
        "content": "My stomach has been hurting for three days now. Not terrible pain but constant discomfort. Probably should see a doctor but my student health insurance has a $50 copay and who knows what tests might cost if they want to run any. Could be nothing. Could be stress. Could be my terrible diet. I've been eating a lot of cheap processed food because it's what I can afford. I'll wait a few more days and see if it goes away on its own. It usually does. Last semester I had a bad cough for two weeks and I just waited it out. Saved myself maybe $100 in copays and medication. Probably not the smartest approach but it's the approach I can afford. If it gets really bad I'll go. But right now it's manageable.",
        "mood": 3,
        "days_ago": 635
    },
    {
        "content": "Winter break means fewer hours available at work. They cut everyone's hours during the break because students go home and there's less business. I'm already stressing about January rent. I'll probably only get 20 hours a week for the next three weeks. That's not enough. I need to figure out some other way to make money. Started looking at gig economy stuff. DoorDash, Instacart, Uber Eats. The problem is my car is barely holding together and putting more miles on it for delivery work might cause more problems. But what choice do I have? I need the money. Maybe I can do it just for a few weeks to bridge the gap.",
        "mood": 3,
        "days_ago": 628
    },
    {
        "content": "Spent four hours today applying to paid internships. Applied to fifteen different companies. Most want 3.5+ GPA and mine is 3.2. It's not terrible but it's not competitive. My GPA is what it is because balancing full-time school and near full-time work is hard. I'm barely keeping my head above water. But these companies don't care about that. They just see the number. Already got one rejection email. They filled the position with someone from Duke. Of course they did. Duke kids don't have to work retail to survive so they have time to do research projects and build impressive portfolios. The system is rigged.",
        "mood": 3,
        "days_ago": 615
    },
    {
        "content": "Spring semester starts tomorrow. Bought my textbooks today. Total: $380. I found most of them as PDFs online through various sketchy websites. Saved probably $300 doing that. But I had to buy the calculus book as a physical copy because the professor requires it for some reason and checks during exams. So that was $110 for one book. Whatever. It's done. This is the last few semesters. I can do this.",
        "mood": 4,
        "days_ago": 608
    },
    {
        "content": "New roommate moved in today. His name is Marcus. Seems like a decent guy. He's a grad student in the engineering department. He plays music kind of loud but honestly I'm barely home anyway between work and class so it doesn't matter much. The important thing is rent is split now. I'm only paying $300 instead of $400. That extra $100 a month is huge for me. I can actually breathe a little. Maybe build up a tiny emergency fund. Maybe eat better. This is the first time in months I've felt like I have any financial breathing room. It won't last forever but I'll take it while I can.",
        "mood": 5,
        "days_ago": 600
    },
    {
        "content": "Operating Systems project is due Friday. I have to work Wednesday, Thursday, and Friday closing shifts. That's 7pm to midnight each night. The project is massive - implementing a scheduler and memory management system. I'm going to have to code basically all day Tuesday and hope it works. No time for proper testing. No time for debugging. Just pray it compiles and does what it's supposed to do. The professor doesn't accept late work under any circumstances. He made that very clear on the first day. Zero tolerance policy. So Friday at 11:59pm it has to be submitted and it has to work. The stress is eating me alive. This is not how software development should work but it's the only way I can make it work with my schedule.",
        "mood": 2,
        "days_ago": 592
    },
    {
        "content": "My friend Sarah invited me to her birthday dinner tomorrow night. Nice restaurant downtown. She said dinner and drinks, probably $30-40 per person with tip. I can't afford it. I just can't. But I didn't want to say that because it's awkward and people get weird about money. So I told her I'm sick. Faked being sick. Said I have a bad cold and don't want to get everyone sick. She was understanding and sweet about it. Told me to feel better. And I felt terrible lying to her. But 'I can't afford it' gets old. I've said it so many times. Eventually people stop inviting you to things. Or they offer to pay for you which is even more embarrassing. So I lie and say I'm sick or I'm busy or I have a family thing. The truth is I'm broke and I can't do the normal social things that everyone else does. It's isolating.",
        "mood": 3,
        "days_ago": 585
    },
    {
        "content": "Got an interview for a summer software development internship! It's with a medium-sized company in Charlotte. The position pays $20 per hour which is actually decent. Way better than the unpaid internships everyone keeps telling me to take. The interview is in two weeks. I need to practice leetcode problems. Need to review data structures and algorithms. Need to work on my project explanations. But when do I have time? Maybe I can wake up at 6am and practice for an hour before work? I have to make this work. This could be the break I need. Real software development experience would look amazing on my resume. Plus $20/hour for the summer would actually let me save some money. I'm nervous but also excited. This feels like a real opportunity.",
        "mood": 4,
        "days_ago": 578
    },
    {
        "content": "Laptop battery completely died. It won't charge at all anymore. I looked up replacement batteries and they're $180. I don't have $180 for a battery. So now I can only use my laptop when it's plugged into an outlet. Means I'm basically trapped near power outlets. Can't work in the library unless I grab a table near an outlet. Can't take my laptop to group study sessions in random buildings. It's frustrating but at least the laptop still works. Could be worse. It could be completely dead. I'll just have to work around this limitation. Add it to the list of things that are broken and need to be replaced eventually but I can't afford to replace right now.",
        "mood": 3,
        "days_ago": 570
    },
    {
        "content": "Completely bombed the internship interview. I knew the answers. I know data structures. I know algorithms. I've studied this stuff for two years. But during the interview my brain just froze. The interviewer asked me to implement a binary search tree and I blanked. Just completely blanked. Started writing code and it was all wrong. Had to backtrack multiple times. He kept giving me hints and I still couldn't figure it out. It was humiliating. After the interview ended I sat in my car and wanted to cry. I knew exactly how to do it. But I haven't slept more than five hours a night in weeks and my brain is just fried. I'm so frustrated with myself. This was my shot and I blew it. Why can't I just be normal? Why can't I just interview like a regular person who's well-rested and prepared? I hate this.",
        "mood": 1,
        "days_ago": 564
    },
    {
        "content": "It's spring break. Everyone on social media is posting beach pictures. Cancun, Miami, Myrtle Beach. Meanwhile I'm doing overnight inventory shifts at Target. Eight hours of counting products on shelves in an empty store. At least the pay is good. Overnight shifts pay an extra $2/hour. I'll make probably $600 this week. That's rent covered and some extra for savings. I'm trying not to feel bitter about it but it's hard. I'm 21 years old and I'm spending spring break doing inventory while everyone else is getting drunk on beaches. This is not what I thought college would be like.",
        "mood": 3,
        "days_ago": 555
    },
    {
        "content": "Group project presentation is tomorrow. I did my part of the work. Built the entire backend API and database. But I barely had time to practice my section of the presentation. Everyone else practiced together yesterday but I was at work. So tomorrow I'm going to wing it in front of the whole class and probably look unprepared. I hate feeling like I'm half-assing everything even though I'm literally doing my absolute best. I'm working harder than most of my classmates but it looks like I'm not trying because I can't make every meeting and can't practice as much. It's not fair but that's life I guess.",
        "mood": 3,
        "days_ago": 548
    },
    {
        "content": "Tax refund came through today. $680 deposited into my checking account. This is the most money I've had at once in months. Feels surreal. First thing I did was pay next month's rent in advance. Then I went to the grocery store and bought real food. Chicken breast. Fresh vegetables. Fruit. Things I haven't bought in weeks because they're expensive. Spent $80 on groceries and it felt like a luxury shopping spree. Everything else goes into savings for emergencies. This money won't last forever but for right now I can breathe. For right now I'm not counting every dollar. It's a good feeling.",
        "mood": 5,
        "days_ago": 540
    },
    {
        "content": "Went to see my career counselor today about summer plans. She suggested I do unpaid research with a professor to boost my resume for grad school. I told her I'm not going to grad school. She said I should consider it because my grades are decent. Then she said the research would look great even if I'm not going to grad school - companies like to see research experience. I asked how I'm supposed to not work for three months. How do I pay rent? How do I eat? She looked confused and said most students use summers to build their resumes, not work. Most students. I wanted to scream. I'm not most students. Most students have parents who pay for everything. I don't have that luxury. She didn't get it. Just kept saying 'you should find a way' like money is something you just find lying around. These advisors live in a completely different reality.",
        "mood": 2,
        "days_ago": 532
    },
    {
        "content": "Finals are in two weeks. I have four exams and two final projects due. Meanwhile I still have to work 32 hours this week. My study schedule is brutal. I've mapped out every hour of every day and there's barely enough time to cover everything. I'm living on coffee and energy drinks. Sleep is down to about four hours a night. This is not sustainable but it's only two more weeks. Just two more weeks and then summer. I can do this. I have to do this.",
        "mood": 2,
        "days_ago": 525
    },
    {
        "content": "Finished spring semester. Got three As and one B. Honestly proud of that considering everything I'm dealing with. The B was in Operating Systems which makes sense because that was the hardest class. But still. 3.3 GPA for the semester brings my overall up a little. Maybe I can actually do this. Maybe I can actually graduate and get a good job and all of this struggle will have been worth something. Two more years. Just two more years.",
        "mood": 4,
        "days_ago": 518
    },
    {
        "content": "Summer work schedule is great. I'm working 40 hours a week and there's no homework. No studying. No projects. Just work and sleep. It's almost relaxing compared to the semester grind. I clock in, do my job, clock out. My brain isn't constantly running in a million directions. I'm actually sleeping six or seven hours a night which feels like luxury. And I'm saving money. Every paycheck I put $200 into savings. Building up that emergency fund. By the end of summer I should have maybe $1500 saved. That's more money than I've ever had at once. It feels good. It feels like progress.",
        "mood": 5,
        "days_ago": 510
    },
    {
        "content": "AC broke in my apartment. It's 95 degrees outside and probably 85 inside. I told my landlord and he said he'll send someone to fix it but it'll be about a week. A week. I'm sleeping with all the windows open and three fans running. It's miserable. I hate this apartment but moving would cost money I don't have. First month rent, last month rent, security deposit - that's like $900 upfront. I don't have that. So I'm stuck here in this hot box apartment with a landlord who doesn't care. Just another thing to deal with. Just another thing on the pile.",
        "mood": 3,
        "days_ago": 495
    },
    {
        "content": "Everyone's posting their summer internships on LinkedIn. Google, Microsoft, Facebook, Amazon. Working on cutting-edge projects. Getting paid $40/hour. Meanwhile I'm stocking shelves at Target for $12/hour. I'm trying not to compare myself to them but it's hard. Their resumes are going to look incredible. They're getting real software engineering experience while I'm scanning barcodes. When we all graduate and start applying for jobs, they're going to have these amazing internships listed and I'm going to have retail experience. How am I supposed to compete with that? The gap between me and my peers just keeps growing and there's nothing I can do about it. I have to work to survive. They get to work to build their resumes. It's not fair but I don't know how to fix it.",
        "mood": 2,
        "days_ago": 485
    },
    {
        "content": "Started learning React on my own. If I can't get fancy internships I'll just build my own projects. Watched YouTube tutorials after work for three hours tonight. Built a simple component. It was actually fun. First time in a while I've coded for enjoyment instead of because I have to for a grade. Maybe I can build a full project this summer. Put it on GitHub, deploy it somewhere, add it to my resume. Show employers I can actually build things even if I don't have internship experience. It's something. It's better than nothing.",
        "mood": 4,
        "days_ago": 475
    },
    {
        "content": "Toothache is getting worse. Pretty sure I need to see a dentist. Whole left side of my mouth hurts when I eat or drink anything cold. Student health insurance doesn't cover dental. I called a local dentist office to ask how much an exam costs. $150 just for the exam. Then whatever treatment costs on top of that. If I need a filling that could be another $200. If I need a root canal it's over $1000. I don't have that money. So I'm just dealing with the pain. Taking ibuprofen every few hours. Avoiding eating on that side of my mouth. Hoping it somehow gets better on its own even though I know that's not how teeth work. Why is everything so expensive? Why is basic healthcare so inaccessible? I'm working and going to school and I still can't afford to take care of basic health problems. The system is broken.",
        "mood": 2,
        "days_ago": 465
    },
    {
        "content": "Finished building my first real project. It's a todo app with React and a Node backend. Has user authentication, database storage, the whole thing. It's pretty basic but it works. Deployed it on Heroku. Added it to my resume and my GitHub. Looking at it makes me feel proud. I built something. Nobody assigned this to me. Nobody graded it. I just made it because I wanted to learn and prove to myself I could do it. Maybe employers will care. Maybe they won't. But I care. It's evidence that I'm more than just my GPA and my lack of internships. I can actually build things.",
        "mood": 4,
        "days_ago": 455
    },
    {
        "content": "Fall semester registration opened today. Got most of my required classes but two of them conflict with my work schedule. Software Engineering is only offered at 3pm on Tuesdays and Thursdays. I work 2-6 those days. I talked to my manager about shifting my schedule. She was understanding but I could tell she's getting tired of me constantly asking for schedule changes. She said she'll try to accommodate me but she can't promise anything. If she can't move my schedule I'll have to either drop the class and delay graduation or quit my job. Both options are terrible. I need that class to graduate on time. I need the job to pay rent. Why does everything have to be so complicated?",
        "mood": 3,
        "days_ago": 445
    },
    {
        "content": "Senior year is starting in a week and I'm panicking. Graduating means I need to find a real job. What if I can't? What if four years of this struggle was for nothing? My student loans are going to start coming due six months after graduation. I don't even know how much I owe total - probably $30,000 at least. How am I supposed to pay that back when I'm already broke? What if I can't find a job that pays enough? What if all those people were right and I should have majored in something more practical? Computer Science is supposed to be a good field but what if I'm not good enough? What if my mediocre GPA and lack of internships mean I can't get hired? I'm spiraling. I know I'm spiraling. But graduation is coming and I feel completely unprepared for real life.",
        "mood": 2,
        "days_ago": 430
    },
    {
        "content": "First day of senior year. Last first day ever. Bought my textbooks. Total was $450. At least this is the last time I'll have to do this. Found a new job opportunity posted on the CS department board. IT helpdesk position on campus. Pays $15/hour instead of the $12 I make now. Applied immediately. It's still on campus which means easy to get to between classes. And it's actual tech work instead of retail. Fixing computers, helping with software issues. Would look way better on my resume. Crossing my fingers I get it.",
        "mood": 4,
        "days_ago": 425
    },
    {
        "content": "I got the IT helpdesk job! Start next week. $15 an hour and it's actually related to my degree. Finally something is going right. Maybe senior year won't be completely terrible. Maybe things are starting to look up. This feels like the first real break I've gotten in years. I'm excited. Actually excited about work for once. This could be the start of things getting better.",
        "mood": 5,
        "days_ago": 418
    },
    {
        "content": "New job is actually great. I'm helping students fix their computers, troubleshooting software issues, helping professors with tech problems. It's real technical work. I'm using actual skills I learned in my classes. And during slow periods I can study or work on homework. My boss doesn't care as long as I help people when they come in. This is so much better than retail. I feel like less of a failure. Like I'm actually building relevant experience. Plus the people I work with are nice. Other CS students, couple of IT professionals. They get it. They understand the struggle. This was a good move.",
        "mood": 5,
        "days_ago": 410
    }
]


def load_demo_data():
    """
    Load demo entries into database WITH EMBEDDINGS.

    Each entry is backdated to create realistic timeline.
    Patterns emerge: anxiety → preparation → success.
    """
    print("\n" + "=" * 70)
    print("Loading Demo Data for Hackathon Presentation")
    print("=" * 70)
    print(f"\nDatabase: {db_path}")
    print(f"Loading {len(demo_entries)} entries with emotional patterns...")
    print()

    # Check if database already has entries
    stats = db.get_stats()
    if stats["total_entries"] > 0:
        print(f"⚠️  Warning: Database already has {stats['total_entries']} entries")
        response = input("Delete existing entries and load demo data? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Cancelled. No changes made.")
            return

        # Clear existing entries
        db.conn.execute("DELETE FROM entries")
        db.conn.commit()
        print("✅ Cleared existing entries\n")

    # Import ML analyzer to generate embeddings and analysis
    print("🔄 Loading ML analyzer with RAG LLM pipeline...")
    from ml.analyzer import Analyzer

    # Initialize with use_llm=False for faster demo data loading
    # (Template-based insights are fine for demo data)
    analyzer = Analyzer(use_llm=False)
    print("✅ ML analyzer loaded\n")

    # Load each demo entry
    for i, entry in enumerate(demo_entries, 1):
        print(f"{i:2d}. Processing entry... ", end="", flush=True)
        
        # Calculate timestamp (backdate by days_ago)
        timestamp = datetime.now() - timedelta(days=entry["days_ago"])

        # Get past entries for analysis (entries loaded so far)
        past_entries = db.get_all_entries_for_analysis()
        
        # Run full ML analysis (generates embedding, insight, summary, etc.)
        analysis = analyzer.analyze_entry(
            entry["content"], 
            past_entries, 
            entry["mood"]
        )
        
        # Prepare analysis for storage (exclude embedding - stored separately)
        analysis_for_db = {
            "insight": analysis["insight"],
            "mood": analysis["mood"],
            "summary": analysis["summary"],
            "mental_state": analysis.get("mental_state", {}),
            "writing_intensity": analysis.get("writing_intensity", {}),
            "sentiment": analysis.get("sentiment", {}),
        }
        
        # Save entry with embedding and full analysis
        entry_id = db.save_entry(
            content=entry["content"],
            mood_rating=entry["mood"],
            embedding=analysis["embedding"],
            analysis=analysis_for_db,
        )

        # Update timestamp to match days_ago
        db.conn.execute(
            "UPDATE entries SET timestamp = ? WHERE id = ?",
            (timestamp.isoformat(), entry_id),
        )
        db.conn.commit()

        # Print progress
        preview = (
            entry["content"][:60] + "..."
            if len(entry["content"]) > 60
            else entry["content"]
        )
        mood_emoji = (
            "😊" if entry["mood"] >= 4 else "😐" if entry["mood"] == 3 else "😔"
        )

        print(
            f"✅ [{entry['days_ago']:2d} days ago] {mood_emoji} Mood: {entry['mood']}/5"
        )
        print(f"    {preview}")
        
        # Show summary if available
        if "summary" in analysis and "title" in analysis["summary"]:
            print(f"    📝 {analysis['summary']['title']}")
        
        print()

    # Show final statistics
    print("=" * 70)
    stats = db.get_stats()
    print(f"✅ Successfully loaded {stats['total_entries']} demo entries")
    print()
    print("📊 Database Statistics:")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Average mood: {stats['avg_mood']}/5")
    print(f"   Mood range: {stats['min_mood']}-{stats['max_mood']}")
    print()
    print("💡 These entries showcase:")
    print("   ✓ Recurring pattern: Anxiety before presentations")
    print("   ✓ What helps: Preparation with Sarah, therapy, exercise")
    print("   ✓ Emotional progression: Anxiety → Action → Success")
    print("   ✓ Self-awareness: User notices patterns over time")
    print("   ✓ Semantic similarity: 'anxious'/'worried'/'nervous' will match")
    print("   ✓ Auto-generated summaries for timeline view")
    print("   ✓ Composite mental state scoring")
    print("   ✓ Multi-factor analysis (sentiment, writing intensity, reflection)")
    print()
    print(f"📁 Database location: {db_path}")
    print()
    print("=" * 70)
    print("✅ Demo data ready for Electron app presentation!")
    print()
    print("🎯 Next steps:")
    print("   1. Run Electron app: cd ../electron && npm start")
    print("   2. Click '📚 View Past Entries' to see timeline with summaries")
    print("   3. Write new entry: 'Nervous about next presentation'")
    print("   4. Watch RAG LLM generate personalized insight!")
    print()
    print("💡 Tip: The app now uses RAG LLM pipeline for natural insights.")
    print("   If you want faster loading, LLM is auto-disabled for demo data.")
    print()

    db.close()


if __name__ == "__main__":
    try:
        load_demo_data()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        db.close()
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        db.close()

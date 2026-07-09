BFI_2_ITEMS = [
    # ── EXTRAVERSION ─────────────────────────
    # Sociability
    ("E", "+", "Outgoing, sociable", [
        "When you enter a tavern, do you tend to mingle or keep to yourself?",
        "Do you naturally engage with others, or wait for them to approach you?",
        "Are you the type to strike up conversation with strangers on the road?",
    ]),
    ("E", "+", "Talkative", [
        "When traveling with others, do you speak often or mostly listen?",
        "Do you tend to explain your thoughts, or keep them short and to the point?",
        "Would people describe you as someone who talks a lot, or only when necessary?",
    ]),
    ("E", "-", "Quiet", [
        "Do you usually stay silent unless something needs to be said?",
        "In a group, are you more of an observer than a speaker?",
        "Would others say you keep your thoughts to yourself?",
    ]),
    ("E", "-", "Introverted", [
        "Do you ever avoid conversation even when it might be useful?",
        "Around unfamiliar people, do you keep your distance?",
        "Do you prefer staying in the background rather than drawing attention?",
    ]),

    # Assertiveness
    ("E", "+", "Assertive", [
        "When decisions need to be made, do you take charge or hold back?",
        "Do you state your intentions clearly, even if others disagree?",
        "Are you comfortable pushing forward when others hesitate?",
    ]),
    ("E", "+", "Dominant, leader", [
        "In dangerous situations, do you naturally take the lead?",
        "Do others tend to follow your direction during a hunt?",
        "When working in a group, do you end up guiding the outcome?",
    ]),
    ("E", "-", "Hard to influence others", [
        "Do you struggle to convince others to follow your advice?",
        "When you speak, do people ignore your guidance?",
        "Do you find it difficult to sway others’ decisions?",
    ]),
    ("E", "-", "Avoids leadership", [
        "Would you rather let someone else lead a mission?",
        "Do you step back when leadership is required?",
        "In a group, do you avoid being the one in command?",
    ]),

    # Energy Level
    ("E", "+", "High energy", [
        "Do you feel constantly ready for the next challenge?",
        "Are you quick to act when something demands attention?",
        "Do you rarely feel worn down by long journeys?",
    ]),
    ("E", "+", "Enthusiastic", [
        "Do you ever feel excitement when taking on a new contract?",
        "When something interests you, does it show in your actions?",
        "Do you approach tasks with eagerness or indifference?",
    ]),
    ("E", "-", "Low excitement", [
        "Do most jobs feel the same to you, without much excitement?",
        "Is it rare for you to feel genuinely eager about something?",
        "Do you approach most situations with a steady, neutral mindset?",
    ]),
    ("E", "-", "Low activity", [
        "Do you prefer conserving your energy rather than constant movement?",
        "Are you slower to act compared to others around you?",
        "Would others describe you as less physically driven?",
    ]),

    # # ── AGREEABLENESS ─────────────────────────
    # # Compassion
    ("A", "+", "Compassionate", [
        "Do you feel for those who suffer, even if they’re strangers?",
        "When someone is hurting, does it affect your decisions?",
        "Do you ever act out of sympathy rather than profit?",
    ]),
    ("A", "+", "Helpful, unselfish", [
        "Do you help others even when there’s nothing to gain?",
        "Would you take on a task purely because someone needs it?",
        "Do you go out of your way to assist those in trouble?",
    ]),
    ("A", "-", "Low sympathy", [
        "Do you find it easy to ignore others’ suffering?",
        "Are you unmoved by most people’s problems?",
        "Do you rarely feel pity for those in need?",
    ]),
    ("A", "-", "Cold, uncaring", [
        "Do people see you as distant or emotionally detached?",
        "Are you often indifferent to others’ feelings?",
        "Would others say you come across as cold?",
    ]),

    # Respectfulness
    ("A", "+", "Respectful", [
        "Do you treat others with basic respect, regardless of who they are?",
        "Even when annoyed, do you keep your conduct measured?",
        "Do you avoid unnecessary insults or hostility?",
    ]),
    ("A", "+", "Polite, courteous", [
        "Do you mind your manners when dealing with others?",
        "Are you careful about how you speak, even in tense moments?",
        "Do you show courtesy, even to difficult people?",
    ]),
    ("A", "-", "Starts arguments", [
        "Do you often provoke conflict when speaking with others?",
        "Are you quick to challenge people openly?",
        "Do disagreements tend to escalate when you’re involved?",
    ]),
    ("A", "-", "Rude", [
        "Do you speak bluntly, even if it offends others?",
        "Are you known for being harsh in conversation?",
        "Do you disregard politeness when it suits you?",
    ]),

    # Trust
    ("A", "+", "Forgiving", [
        "Do you give people a second chance after they’ve wronged you?",
        "Are you willing to let past mistakes go?",
        "Can someone regain your trust once it’s broken?",
    ]),
    ("A", "+", "Assumes best of others", [
        "Do you believe most people mean well?",
        "When unsure, do you lean toward trusting others?",
        "Do you expect honesty unless proven otherwise?",
    ]),
    ("A", "-", "Finds fault", [
        "Do you quickly notice flaws in people’s actions?",
        "Are you often critical of others’ behavior?",
        "Do you assume people are making mistakes?",
    ]),
    ("A", "-", "Suspicious", [
        "Do you assume people may be hiding something?",
        "When offered help, do you question the motive?",
        "Do you expect deception more often than honesty?",
    ]),

    # # ── CONSCIENTIOUSNESS ─────────────────────────
    # # Organization
    ("C", "+", "Systematic", [
        "Do you follow a structured approach when preparing for a hunt?",
        "Do you prefer doing things in a set order?",
        "Are your methods deliberate and organized?",
    ]),
    ("C", "+", "Neat, tidy", [
        "Do you keep your gear well-maintained and in order?",
        "Is your workspace organized or chaotic?",
        "Do you take care to keep things clean?",
    ]),
    ("C", "-", "Disorganized", [
        "Do you often lose track of your tools or supplies?",
        "Is your preparation messy or inconsistent?",
        "Do you struggle to keep things in order?",
    ]),
    ("C", "-", "Leaves a mess", [
        "Do you leave things behind after finishing a task?",
        "Is cleaning up something you tend to ignore?",
        "Do others notice the disorder you leave behind?",
    ]),

    # Productiveness
    ("C", "+", "Efficient", [
        "Do you complete contracts quickly and effectively?",
        "Are you focused on getting things done without delay?",
        "Do you avoid wasting time on unnecessary steps?",
    ]),
    ("C", "+", "Persistent", [
        "Do you stick with a task until it’s finished, no matter how long it takes?",
        "When something proves difficult, do you keep pushing?",
        "Do you see things through to the end?",
    ]),
    ("C", "-", "Lazy", [
        "Do you ever avoid work unless absolutely necessary?",
        "Are you slow to act when effort is required?",
        "Do you put things off more than you should?",
    ]),
    ("C", "-", "Difficulty starting tasks", [
        "Do you hesitate before beginning a task?",
        "Is starting the hardest part for you?",
        "Do you delay action even when you know what to do?",
    ]),

    # Responsibility
    ("C", "+", "Dependable", [
        "Can others rely on you to follow through on your word?",
        "Do you take your commitments seriously?",
        "Are you someone people trust to get the job done?",
    ]),
    ("C", "+", "Reliable", [
        "When you accept a contract, do you always see it through?",
        "Do people count on you without doubt?",
        "Are you consistent in your actions?",
    ]),
    ("C", "-", "Careless", [
        "Do you sometimes overlook important details?",
        "Have your mistakes caused problems for others?",
        "Do you act without thinking things through?",
    ]),
    ("C", "-", "Irresponsible", [
        "Do you ever ignore consequences when making choices?",
        "Have you taken risks that put others in danger?",
        "Do you sometimes act without regard for duty?",
    ]),

    # # ── NEGATIVE EMOTIONALITY ─────────────────────────
    # # Anxiety
    ("N", "+", "Tense", [
        "Do you feel tight or on edge before danger strikes?",
        "Does anticipation ever make you uneasy?",
        "Do you carry tension into uncertain situations?",
    ]),
    ("N", "+", "Worries a lot", [
        "Do you find yourself thinking about what could go wrong?",
        "Are you often concerned about outcomes beyond your control?",
        "Do worries stay with you longer than they should?",
    ]),
    ("N", "-", "Relaxed", [
        "Do you remain calm even under pressure?",
        "Can you keep steady when things go wrong?",
        "Does stress rarely shake you?",
    ]),
    ("N", "-", "Rarely anxious", [
        "Do you face danger without fear taking hold?",
        "Is anxiety something you almost never feel?",
        "Do you stay composed in most situations?",
    ]),

    # Depression
    ("N", "+", "Often sad", [
        "Do you carry a sense of sadness with you?",
        "Do losses weigh heavily on your mind?",
        "Do you often feel low, even without reason?",
    ]),
    ("N", "+", "Feels depressed", [
        "Do you ever feel weighed down by a lingering gloom?",
        "Are there times when nothing seems worth the effort?",
        "Do you struggle with feelings of emptiness?",
    ]),
    ("N", "-", "Stays optimistic", [
        "After failure, do you quickly regain your footing?",
        "Do you believe things will improve after hardship?",
        "Can you stay hopeful despite losses?",
    ]),
    ("N", "-", "Secure with self", [
        "Are you comfortable with who you are?",
        "Do you rarely doubt yourself?",
        "Do you feel steady in your identity?",
    ]),

    # Emotional Volatility
    ("N", "+", "Moody", [
        "Do your moods shift noticeably from one moment to the next?",
        "Are you prone to emotional ups and downs?",
        "Do your feelings change quickly depending on events?",
    ]),
    ("N", "+", "Emotionally reactive", [
        "Do strong emotions come on quickly for you?",
        "Are you easily stirred by what happens around you?",
        "Do your feelings rise faster than you expect?",
    ]),
    ("N", "-", "Emotionally stable", [
        "Do you stay steady regardless of circumstances?",
        "Are your emotions consistent over time?",
        "Do you rarely get shaken emotionally?",
    ]),
    ("N", "-", "Controlled emotions", [
        "Do you keep your feelings in check, even under strain?",
        "Can you suppress emotion when needed?",
        "Do you maintain control over your reactions?",
    ]),

    # # ── OPENNESS ─────────────────────────
    # # Intellectual Curiosity
    ("O", "+", "Curious", [
        "Do you take interest in things beyond your trade?",
        "When you encounter the unknown, do you want to understand it?",
        "Are you drawn to learning new ideas?",
    ]),
    ("O", "+", "Deep thinker", [
        "Do you reflect deeply on the world and your place in it?",
        "Do you spend time considering complex questions?",
        "Are your thoughts often philosophical?",
    ]),
    ("O", "-", "Avoids intellectual discussion", [
        "Do you steer clear of deep or abstract conversations?",
        "Are philosophical topics something you ignore?",
        "Do you prefer practical talk over theoretical ideas?",
    ]),
    ("O", "-", "Low interest in abstract ideas", [
        "Do abstract concepts bore you?",
        "Are you uninterested in ideas that aren’t practical?",
        "Do you dismiss things that can’t be directly applied?",
    ]),

    # Aesthetic Sensitivity
    ("O", "+", "Appreciates art", [
        "Do songs, stories, or poetry ever move you?",
        "Are you drawn to music or tales told by bards?",
        "Do you find meaning in art or storytelling?",
    ]),
    ("O", "+", "Values beauty", [
        "Do you notice beauty in landscapes or crafted works?",
        "Is there value in art beyond usefulness to you?",
        "Do you appreciate things simply for how they look or feel?",
    ]),
    ("O", "-", "Few artistic interests", [
        "Do you ignore art as irrelevant to your work?",
        "Are music and stories unimportant to you?",
        "Do you rarely engage with creative expression?",
    ]),
    ("O", "-", "Finds art boring", [
        "Do you find performances like plays dull?",
        "Are poetic words a waste of time to you?",
        "Do artistic performances fail to hold your interest?",
    ]),

    # Creative Imagination
    ("O", "+", "Inventive", [
        "Do you come up with clever solutions in difficult situations?",
        "When plans fail, do you think of new approaches quickly?",
        "Are you resourceful in unexpected ways?",
    ]),
    ("O", "+", "Original", [
        "Do you rely on your own ideas rather than others’ methods?",
        "Do you approach problems in unique ways?",
        "Are your solutions different from what others expect?",
    ]),
    ("O", "-", "Uncreative", [
        "Do you stick strictly to known methods?",
        "Do you struggle to think of new approaches?",
        "Are you uncomfortable improvising?",
    ]),
    ("O", "-", "Poor imagination", [
        "Do you find it hard to picture possibilities in your mind?",
        "Is imagining alternatives something you avoid?",
        "Do you prefer concrete reality over imagined scenarios?",
    ]),

]
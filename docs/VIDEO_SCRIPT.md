# Two-minute presentation script

Hello, I’m presenting LittleLingo, an English-practice companion designed for children under seven.

The backend uses Python and FastAPI. The browser uses HTML, CSS, and JavaScript, keeping the interface lightweight on phones. Lesson content is separate from dialogue handling, so prompts can be reviewed without rewriting the routing logic.

There are three stages. The first covers early words such as colours, letters, and animals. The second introduces action words and phrases. The third practises short sentences and polite language. A simple mastery rule moves a learner forward after a streak of correct answers.

The chatbot also has four modes: learning, conversation, engagement, and support. It can offer a hint, respond to common feelings, tell a short story or joke, or respect a request for a break. Safety-related phrases receive supportive wording that encourages the child to tell a trusted grown-up.

I chose a deterministic engine instead of calling an LLM on every turn. That avoids model costs and round-trip delays, and makes responses easier to test. The trade-off is that phrase matching is limited and cannot understand every child’s wording.

The prototype does not store chat transcripts, and progress only exists in the browser session. Before production, I would add broader child-language testing, specialist safeguarding review, accessibility checks, caregiver controls, and real end-to-end latency measurements.

Thank you for taking a look at LittleLingo.

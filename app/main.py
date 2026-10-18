from __future__ import annotations
import re
import time
from pathlib import Path
from typing import Literal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="LittleLingo", version="1.1.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
Mode = Literal["learning", "conversation", "engagement", "support"]
LEVELS = {1: ("Little Learner", 3), 2: ("Word Explorer", 4), 3: ("Sentence Star", 5)}

# Keep lesson copy separate from routing logic so content can be reviewed independently.
LESSONS = {
    1: [
        {"question": "Which one is a colour: red or run?", "answers": ("red",), "hint": "Red is a colour. You might see it on an apple. 🍎"},
        {"question": "What sound does a cat make?", "answers": ("meow", "miaow"), "hint": "A cat often says “meow”. 🐱"},
        {"question": "What comes after A and B?", "answers": ("c", "letter c"), "hint": "Say the alphabet slowly: A, B, C."},
        {"question": "Which word can we use to greet a friend?", "answers": ("hello", "hi"), "hint": "We can say “hello” when we meet someone."},
    ],
    2: [
        {"question": "Which word tells us to move: jump or blue?", "answers": ("jump",), "hint": "You can jump up and down. It is something you do."},
        {"question": "Complete the greeting: Good ___.", "answers": ("morning",), "hint": "We often say this when we wake up: good morning."},
        {"question": "What is the opposite of big?", "answers": ("small", "little"), "hint": "A mouse is small. An elephant is big."},
        {"question": "In “the bright sun”, which word describes the sun?", "answers": ("bright",), "hint": "The describing word tells us what the sun is like."},
    ],
    3: [
        {"question": "Finish the sentence: The bird can ___.", "answers": ("fly",), "hint": "A bird uses its wings to fly."},
        {"question": "Which sounds kinder: “Please help me” or “Give it now”?", "answers": ("please help me", "please"), "hint": "“Please” is a kind word to use when asking."},
        {"question": "Choose a word to describe a banana: yellow or running?", "answers": ("yellow",), "hint": "Think about the colour of a ripe banana."},
        {"question": "Finish the sentence: I like to ___ outside.", "answers": ("play", "run"), "hint": "You might play or run when you are outside."},
    ],
}
FEELINGS = {
    "sad": ("support", "I’m sorry you feel sad. 💛 Would you like to talk, draw, or sit quietly for a moment?"),
    "angry": ("support", "Sometimes feelings get very big. Let’s take one slow breath together. Would a short break help?"),
    "worried": ("support", "Thank you for telling me. If something is worrying you, you can talk to a grown-up you trust."),
    "scared": ("support", "That sounds uncomfortable. Please tell a grown-up you trust if something is making you feel scared."),
    "frustrated": ("support", "This one feels tricky, and that’s okay. We can try a hint, an easier question, or a little break."),
    "bored": ("engagement", "Shall we switch it up? We could hear a tiny story, try a silly animal question, or just chat."),
    "happy": ("conversation", "I’m glad! 😊 What was something nice about your day?"),
    "tired": ("support", "Rest matters too. We can pause now. You can come back when you feel ready."),
}
SAFETY_PHRASES = ("someone hurts me", "someone hurt me", "hit me", "touch me", "i am not safe", "i feel unsafe", "scared of someone", "they hurt me")
BREAK_PHRASES = ("i need a break", "stop please", "not now", "i am finished", "i'm finished", "take a break")
HINT_PHRASES = ("hint", "help me", "i don't know", "i dont know", "not sure")

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    level: int = Field(default=1, ge=1, le=3)
    correct_streak: int = Field(default=0, ge=0, le=100)
    turns: int = Field(default=0, ge=0, le=10000)
    lesson_index: int = Field(default=0, ge=0, le=10000)

class ChatResponse(BaseModel):
    reply: str
    mode: Mode
    level: int
    level_title: str
    correct_streak: int
    turns: int
    lesson_index: int
    progress: int
    answered_correctly: bool
    next_question: str
    latency_ms: float

def normalise(text: str) -> str:
    """Ignore case and punctuation when comparing short answers."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text.casefold())).strip()

def lesson_for(level: int, index: int) -> dict:
    lessons = LESSONS[level]
    return lessons[index % len(lessons)]

def detect_feeling(message: str) -> str | None:
    text = normalise(message)
    patterns = {
        "sad": ("i feel sad", "i am sad", "im sad", "feel sad"),
        "angry": ("i feel angry", "i am angry", "im angry", "i feel mad", "i am mad"),
        "worried": ("i feel worried", "i am worried", "im worried"),
        "scared": ("i feel scared", "i am scared", "im scared", "i am afraid", "im afraid"),
        "frustrated": ("this is hard", "too hard", "i give up", "i cant do it", "i can t do it"),
        "bored": ("i am bored", "im bored", "this is boring"),
        "happy": ("i feel happy", "i am happy", "im happy"),
        "tired": ("i am tired", "im tired", "i feel tired", "i am sleepy", "im sleepy"),
    }
    return next((feeling for feeling, examples in patterns.items() if any(x in text for x in examples)), None)

def route_message(message: str, lesson: dict) -> tuple[Mode, str, bool]:
    text = normalise(message)
    # Safety and emotional intent take priority over the quiz matcher.
    if any(phrase in text for phrase in SAFETY_PHRASES):
        return "support", ("I’m glad you told me. You deserve to feel safe. Please tell a trusted grown-up now, "
            "such as your parent, caregiver, or teacher. If you are in danger right now, go to a safe grown-up nearby. 💛"), False
    feeling = detect_feeling(message)
    if feeling:
        mode, reply = FEELINGS[feeling]
        return mode, reply, False
    if any(phrase in text for phrase in BREAK_PHRASES):
        return "support", "Of course. 🌼 We can pause. Come back whenever you’re ready.", False
    if any(phrase in text for phrase in HINT_PHRASES):
        return "learning", lesson["hint"] + " Have a try if you’d like.", False
    if "joke" in text or "story" in text or "chat" in text or "talk" in text:
        if "joke" in text:
            reply = "What do you call a sleeping dinosaur? A dino-snore! 🦕"
        elif "story" in text:
            reply = "A little bird found a seed. She planted it, watered it, and waited. One sunny day, a flower bloomed. 🌱"
        else:
            reply = "Of course, we can chat. 😊 What would you like to tell me?"
        return "engagement", reply, False
    answer = normalise(message)
    if answer in (normalise(option) for option in lesson["answers"]):
        return "learning", "correct", True
    if len(text.split()) >= 6 or "my day" in text or "my friend" in text:
        return "conversation", "I’m listening. 😊 Tell me a little more about that.", False
    return "learning", "not quite", False

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/health")
def health():
    return {"status": "ok", "name": "LittleLingo", "version": "1.1.0"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    started = time.perf_counter()
    level, streak = request.level, request.correct_streak
    turns, lesson_index = request.turns + 1, request.lesson_index
    lesson = lesson_for(level, lesson_index)
    mode, outcome, correct = route_message(request.message, lesson)

    if correct:
        streak += 1
        praise = ("That’s it! 🌟", "You worked that out! High five! 🙌", "Lovely thinking! 🎉")
        reply = praise[streak % len(praise)]
        if streak >= LEVELS[level][1] and level < 3:
            level += 1
            streak, lesson_index = 0, 0
            reply += f" You’re ready for Level {level}, {LEVELS[level][0]}!"
        else:
            lesson_index += 1
    elif mode == "learning":
        streak = max(0, streak - 1)
        reply = "Good try. Mistakes help our brains grow. 💛 " + lesson["hint"]
    else:
        reply = outcome

    next_lesson = lesson_for(level, lesson_index)
    progress = min(100, round(streak / LEVELS[level][1] * 100))
    return ChatResponse(reply=reply, mode=mode, level=level, level_title=LEVELS[level][0],
        correct_streak=streak, turns=turns, lesson_index=lesson_index, progress=progress,
        answered_correctly=correct, next_question=next_lesson["question"],
        latency_ms=round((time.perf_counter() - started) * 1000, 2))

# System design

## Request flow

1. FastAPI validates message length and session fields.
2. The router checks a small safeguarding phrase list first.
3. It checks explicit feelings, break requests, hint requests, and engagement requests.
4. Only a likely lesson response is compared with accepted answers.
5. The API returns a reply, mode, level/streak, next question, and server processing time.

## Learning stages

- L1: letters, colours, animals, greetings.
- L2: action words, phrases, opposites, describing words.
- L3: sentence completion, polite language, descriptions.

Advancement uses a consecutive-correct-answer threshold. This is a prototype heuristic, not a validated assessment of a child's ability.

## Why no LLM in this version?

A curated local engine avoids model round-trip latency and makes the responses predictable and inexpensive. The trade-off is reduced flexibility and shallow intent understanding. If an LLM is introduced later, its output should be bounded by reviewed child-safe rules, output limits, timeouts, and a safe fallback.

## Latency

The API reports Python processing time, not total browser/network latency or hosting cold starts. Test end-to-end latency on the deployed service before claiming the two-second target is met.

## Privacy and safety

The app does not request names or store transcripts in a database. The phrase matcher is limited and must not be presented as a reliable abuse or danger detector. A production release needs child-development and safeguarding review, caregiver controls, and a privacy/legal assessment.

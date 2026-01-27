# Deep Questioning

Techniques for gathering rich project context through conversation.

## Philosophy

Deep questioning follows threads, not checklists. Start open, then dig into what the user says. The goal is understanding, not form-filling.

## Opening

Ask: "What do you want to build?"

Wait for their response. This gives you context to ask intelligent follow-ups.

## Thread-Following Techniques

### Challenge Vagueness

When user says something abstract, push for specifics:

- "A platform for X" → "What's the core action a user takes on this platform?"
- "It should be fast" → "What would feel too slow? What's the critical path?"
- "Easy to use" → "Who's the least technical user? What would confuse them?"

### Make Abstract Concrete

Turn concepts into scenarios:

- "User management" → "Walk me through someone signing up for the first time"
- "Analytics dashboard" → "What's the first number someone looks at when they open it?"
- "API integration" → "Which specific API? What data flows between systems?"

### Surface Assumptions

Find hidden decisions:

- "We need auth" → "Username/password? OAuth? Magic links? Who decides?"
- "Mobile app" → "iOS, Android, or both? Native or cross-platform?"
- "Real-time updates" → "How real-time? Seconds? Sub-second? What happens if delayed?"

### Find Edges

Explore boundaries:

- "What's the smallest version that would be useful?"
- "What would make this project a failure even if it works?"
- "What's explicitly NOT part of this?"

### Reveal Motivation

Understand the why:

- "What problem sparked this idea?"
- "Who asked for this? What do they actually need?"
- "What are you doing today without this tool?"

## Context Checklist

As you converse, mentally track coverage of:

- [ ] **Vision** — The big picture in 1-2 sentences
- [ ] **Core problem** — What pain point this solves
- [ ] **Target users** — Who uses this, their context
- [ ] **Key constraints** — Platform, performance, security, timeline
- [ ] **Tech preferences** — Languages, frameworks, patterns (if any)
- [ ] **Success criteria** — How to know it's working
- [ ] **Non-goals** — What's explicitly out of scope

Don't switch to checklist mode. Weave missing items into natural conversation.

## Decision Gate

When you could write a clear PROJECT.md, ask:

"I think I understand what you're building. Ready to create PROJECT.md, or want to explore more?"

If they want to explore, ask what's unclear or what they want to add.

## Anti-Patterns

- **Interrogation mode** — Firing questions without listening to answers
- **Checklist mode** — Mechanically covering items instead of following threads
- **Assumption mode** — Filling in blanks without asking
- **Validation seeking** — "So you want X, right?" instead of exploring

## Quality Signals

Good questioning produces:

- Specific user scenarios, not abstract features
- Clear constraints, not vague preferences
- Explicit non-goals, not just goals
- User's own words, not your interpretations

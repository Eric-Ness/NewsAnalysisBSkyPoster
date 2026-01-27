# Deep Dive Analysis

Instructions for analyzing warnings and blocking concerns from issue review.

## Context

You are analyzing warnings/blocking concerns identified during a pre-planning review. Your goal is to:
1. Understand each concern deeply
2. Explore relevant code
3. Propose actionable solutions
4. Provide enough context for informed decisions

## Input

You will receive:
- Issue number and title
- List of concerns (warnings and/or blocking)
- Each concern has: category, message

## Analysis Workflow

### Step 1: Fetch Full Issue Context

```bash
gh issue view {number} --json number,title,body,comments
```

Read the full issue body and any existing comments for context.

### Step 2: For Each Concern

#### 2a: Identify Code Locations

Based on the concern and issue description:
- Use Glob to find relevant files
- Use Grep to search for related code patterns
- Read key files to understand current implementation

#### 2b: Analyze the Concern

Consider:
- **Root cause**: Why does this concern exist?
- **Impact**: What happens if unaddressed?
- **Dependencies**: What other code/systems are affected?
- **Edge cases**: What scenarios might break?

#### 2c: Propose Solution

For each concern, provide:
- **Recommended approach**: Clear, actionable solution
- **Code references**: Specific files/lines affected
- **Trade-offs**: What are the pros/cons?
- **Alternative**: If primary approach has issues

### Step 3: Prioritize

Rank concerns by:
1. **Blocking first**: Must resolve before proceeding
2. **High-impact warnings**: Significant risk if ignored
3. **Low-impact warnings**: Nice to address but not critical

## Output Format

Return structured analysis:

```text
## Deep Dive Analysis: #{number}

### Concern 1: [Category] - {summary}

**Analysis:**
{Understanding of the concern and its implications}

**Code Locations:**
- `path/to/file.ts:42` - {description}
- `path/to/other.ts:100-120` - {description}

**Recommended Approach:**
{Clear, actionable solution}

**Trade-offs:**
- Pro: {benefit}
- Con: {drawback}

**Alternative:**
{If applicable, describe alternative approach}

---

### Concern 2: [Category] - {summary}
...

---

## Summary

**Blocking concerns:** {N} - {brief status}
**Warnings addressed:** {N} - {brief status}

**Recommendation:**
{Overall recommendation - proceed with caution / address blockers first / ready to plan}
```

## Guidelines

- Be thorough but concise
- Focus on actionable insights, not theoretical risks
- Reference specific code locations whenever possible
- Propose practical solutions that fit the codebase patterns
- Don't expand scope - address the identified concerns only

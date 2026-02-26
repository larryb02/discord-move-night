# Movie Night Bot — V1 Plan

## Features
- Users can add movies to a nomination list during a set timeframe
- A movie night cycle runs regularly scheduled polls based on the nominated list
- After voting, the winner is announced, pinned, and voters are tagged
- The list clears after each cycle and the process resets

---

## Commands

### `/addmovie <title>`
- Adds a movie to the nomination list
- Only valid during an active nomination window
- Rejects submissions if no movie night is in progress

### `/movienight nomination_window:<duration> voting_window:<duration>`
- Starts the movie night cycle
- Duration format: `1h`, `30m`, `2d`, etc.
- Announces the nomination window and how long users have to submit movies
- Automatically transitions to voting when the nomination window closes
- Announces the winner when the voting window closes

---

## Cycle Flow

1. `/movienight` called — nomination window opens, bot announces it with the deadline
2. Users submit movies via `/addmovie` during the nomination window
3. Nomination window closes — bot creates a Discord native poll from the submitted list
4. Voting window closes — bot:
   - Announces the winning movie
   - Pins the announcement
   - Tags all users who voted
   - Clears the movie list
   - Resets state

---

## Technical Requirements

### Persistence
- Movie list must persist between sessions
- Current cycle state (phase, deadlines, voters) must also persist
- V1: JSON file is sufficient

### State
- `phase`: `idle` | `nominations` | `voting`
- `nomination_deadline`: timestamp
- `voting_deadline`: timestamp
- `movies`: list of submitted titles
- `voters`: list of user IDs who voted

### Scheduling
- `asyncio` tasks to fire phase transitions automatically
- On bot restart, resume in-progress cycle from persisted state

### Permissions
- `Manage Messages` — required for pinning the announcement

### Discord Features
- Native Discord polls for the voting phase
- Ephemeral responses where appropriate (e.g. rejecting `/addmovie` outside nomination window)

---

## Out of Scope for V1
- Multiple simultaneous movie nights
- Per-user movie limits
- Movie deduplication
- Persistent movie history across cycles

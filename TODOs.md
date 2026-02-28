# TODOs

## Known Gaps
- Cycle state is in-memory only — if the bot restarts mid-cycle, the cycle is lost with no cleanup or resumption

## Future Improvements
- Include movie URL in winner announcement so Discord auto-embeds the title, image, and description — requires mapping poll answer text back to the original URL at announcement time
- Finer-grained cancellation and retry logic within the cycle — transient failures (e.g. Discord HTTP errors) shouldn't require restarting the entire cycle from nominations
- Tiebreaker round — when voting ends in a tie, kick off a new mini-cycle with only the tied films
- Backlog — a persistent list of movies that didn't win, available as nominees in future cycles
- Scheduler — fully autonomous mode where cycles run on a recurring interval without manual `/movienight` invocation

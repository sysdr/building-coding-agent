# Reference transcripts — what these actually are

The article's "What ships" section describes these as "real captured runs from the
reference agent." That claim predates this build. The environment that built this zip
holds no model API key, so `instance_a.json` and `instance_b.json` here are captured
from the **offline fixture backend** (`demo_agent.py demo --instance a --fixture`), not
from a real model call.

They're still useful for the "I don't have an API key yet" fallback the article
describes — you can read a full transcript shape (system prompt, tool calls, tool
output, stop condition) without spending anything. What they can't give you is the
genuine uncertainty a real model run has: the fixture agent's moves are scripted, so
there's no actual reasoning to be surprised by.

Run `apr demo --instance a` / `--instance b` with a real `APR_MODEL_API_KEY` for the
experience the article is actually about.

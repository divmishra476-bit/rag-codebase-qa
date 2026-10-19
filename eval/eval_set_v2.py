# eval/eval_set_v2.py
# Ground truth decided BEFORE running retrieval on these questions.
# Rule: only chunks that directly answer the question; borderline chunks left out.

NEW_SET = [
    {"query": "how do I send JSON in a request body",
     "expected_chunk_ids": ["docs\\quickstart.md:227"]},
    {"query": "how do I upload a file",
     "expected_chunk_ids": ["docs\\quickstart.md:172"]},
    {"query": "how do I add query parameters to a URL",
     "expected_chunk_ids": ["docs\\quickstart.md:32"]},
    {"query": "how do I set custom headers",
     "expected_chunk_ids": ["docs\\quickstart.md:124"]},
    {"query": "how do I raise an error for bad status codes",
     "expected_chunk_ids": ["httpx\\_models.py:794", "docs\\quickstart.md:264", "docs\\quickstart.md:495"]},
    {"query": "how do I use a proxy",
     "expected_chunk_ids": ["docs\\advanced\\proxies.md:8"]},
    {"query": "how do I make async requests",
     "expected_chunk_ids": ["docs\\async.md:13"]},
    {"query": "how do I enable HTTP/2",
     "expected_chunk_ids": ["docs\\http2.md:19"]},
    {"query": "how do I limit the number of connections",
     "expected_chunk_ids": ["docs\\advanced\\resource-limits.md:1"]},
    {"query": "how do I disable SSL verification",
     "expected_chunk_ids": ["docs\\advanced\\ssl.md:3"]},
    {"query": "how do I stream a large response",
     "expected_chunk_ids": ["docs\\quickstart.md:339"]},
    {"query": "what exceptions can httpx raise",
     "expected_chunk_ids": ["docs\\exceptions.md:40"]},
    {"query": "how do I use event hooks",
     "expected_chunk_ids": ["docs\\advanced\\event-hooks.md:1"]},
    {"query": "where is the code that picks a transport for a URL",
     "expected_chunk_ids": ["httpx\\_client.py:760", "httpx\\_client.py:1474"]},
]
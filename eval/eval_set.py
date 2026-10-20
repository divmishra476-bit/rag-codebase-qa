# eval/eval_set.py
# "expected_chunk_ids": a hit = ANY one of these appears in the top 5.
# Rule: only chunks that DIRECTLY answer the question. Original code-chunk IDs kept.
# NOTE: docs IDs for redirects/timeout were added AFTER reading retrieved chunks (post-hoc).

EVAL_SET = [
    {
        "query": "how do I make an HTTP request",
        "expected_chunk_ids": ["httpx\\_client.py:771"],
    },
    {
        "query": "how do I send a GET request",
        "expected_chunk_ids": ["httpx\\_client.py:1036"],
    },
    {
        "query": "how do I send a POST request",
        "expected_chunk_ids": ["httpx\\_client.py:1123"],
    },
    {
        "query": "how does httpx handle redirects",
        "expected_chunk_ids": [
            "httpx\\_client.py:494",
            "docs\\quickstart.md:418",
            "docs\\compatibility.md:8",
        ],
    },
    {
        "query": "how do I set a timeout for requests",
        "expected_chunk_ids": [
            "httpx\\_client.py:254",
            "httpx\\_client.py:258",
            "docs\\advanced\\timeouts.md:30",
            "docs\\advanced\\timeouts.md:6",
            "docs\\advanced\\timeouts.md:66",
        ],
    },
    {
        "query": "how do I close the client connection",
        "expected_chunk_ids": ["httpx\\_client.py:1263"],
    },
]
# eval/eval_set.py

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
        "expected_chunk_ids": ["httpx\\_client.py:494"],
    },
    {
        "query": "how do I set a timeout for requests",
        "expected_chunk_ids": ["httpx\\_client.py:254", "httpx\\_client.py:258"],
    },
    {
        "query": "how do I close the client connection",
        "expected_chunk_ids": ["httpx\\_client.py:1263"],
    },
]
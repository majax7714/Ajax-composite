from rgr.generator.formatting import build_feedback_prompt, extract_code


def test_extract_fenced_python():
    text = "Here is my solution:\n```python\ndef add(a, b):\n    return a + b\n```\nDone."
    assert extract_code(text) == "def add(a, b):\n    return a + b"


def test_extract_bare_fence():
    text = "```\ndef f():\n    pass\n```"
    assert extract_code(text) == "def f():\n    pass"


def test_extract_first_of_multiple_blocks():
    text = "```python\nfirst = 1\n```\n```python\nsecond = 2\n```"
    assert extract_code(text) == "first = 1"


def test_unfenced_code_fallback():
    assert extract_code("def f():\n    return 1") == "def f():\n    return 1"


def test_narration_yields_none():
    assert extract_code("I would solve this by iterating over the list.") is None


def test_empty_fence_yields_none():
    assert extract_code("```python\n```") is None


def test_feedback_prompt_contains_prev_and_score():
    prompt = build_feedback_prompt("Write add.", "def add(a,b): return a+b", 0.42)
    assert "def add(a,b): return a+b" in prompt
    assert "0.42" in prompt

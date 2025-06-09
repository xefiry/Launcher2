from configuration import Rule


def test_Rule_eq():
    rules: list[Rule] = [
        Rule("test", "test", ["dummy.exe"]),
        Rule("test", "test", ["dummy.exe"]),
        Rule("diff", "test", ["dummy.exe"]),
        Rule("test", "diff", ["dummy.exe"]),
        Rule("test", "test", ["diff.exe"]),
    ]

    assert rules[0] == rules[1]
    assert rules[0] != rules[2]
    assert rules[0] != rules[3]
    assert rules[0] != rules[4]
    assert rules[0] != 0
    assert rules[0] != "foo"


def test_Rule_check():
    r = Rule("Demo rule", "Description", ["dummy.exe"])

    tests: dict[str, Rule | None] = {
        "Demo": r,
        "demo": r,
        "demo RuLe": r,
        "rule": r,
        "emo": r,
        "emo r": r,
        "Nope": None,
        "demo_rule": None,
    }

    for input, expected in tests.items():
        assert r.check(input) == expected

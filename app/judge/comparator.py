def compare_output(expected: str, actual: str) -> bool:
    expected = expected.replace("\r\n", "\n").rstrip()
    actual = actual.replace("\r\n", "\n").rstrip()
    return expected == actual

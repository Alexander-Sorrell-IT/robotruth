from robotruth.diffparse import parse_diff
from robotruth.scanners.dangerous_primitives import scan


def _add(path, line):
    return parse_diff(f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1,1 +1,2 @@\n keep\n+{line}\n")


def test_flags_added_eval():
    flags = scan(_add("run.js", "const r = " + "ev" + "al(userInput)"), [])
    assert len(flags) == 1 and flags[0].severity == "critical" and flags[0].line == 2


def test_ignores_removed_sink():
    d = parse_diff("diff --git a/x.js b/x.js\n--- a/x.js\n+++ b/x.js\n@@ -1,2 +1,1 @@\n keep\n-const r = " + "ev" + "al(x)\n")
    assert scan(d, []) == []


def test_ignores_comment_with_sink_word():
    assert scan(_add("x.py", "# " + "ev" + "al() is dangerous, never use it"), []) == []


def test_ignores_js_regex_exec():
    # regex.exec(...) is benign and extremely common in JS -> must NOT flag
    assert scan(_add("x.js", "const m = myRegex." + "ex" + "ec(input)"), []) == []


def test_subprocess_safe_form_not_flagged():
    assert scan(_add("x.py", ("sub" + "process") + ".run([cmd], shell=False)"), []) == []


def test_subprocess_shell_true_flagged():
    flags = scan(_add("x.py", ("sub" + "process") + ".run(cmd, shell=True)"), [])
    assert len(flags) == 1


def test_yaml_safe_loader_not_flagged():
    assert scan(_add("x.py", "data = yaml.load(s, Loader=yaml.SafeLoader)"), []) == []


def test_yaml_unsafe_flagged():
    flags = scan(_add("x.py", "data = yaml.load(s)"), [])
    assert len(flags) == 1

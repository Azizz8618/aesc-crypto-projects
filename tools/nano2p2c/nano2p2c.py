#!/usr/bin/env python3
"""Lower nanolang --target c output into the P2C dialect for the BESM-6.

I accept the integer-only part of nanolang's hosted C seed profile. I refuse
constructs I cannot lower faithfully; I never emit a P2C source I cannot
justify against the pas2c compiler's documented dialect.
"""

import re
import sys

USAGE = "usage: nano2p2c.py input.genC [-o output.p2c]"

# Constructs of the hosted C profile that have no faithful P2C lowering here.
REFUSALS = [
    (r"\bdouble\b|\bfloat\b", "binary64 and float values are outside the integer P2C subset"),
    (r"\bconst\s+char\b|\bchar\s*\*", "string values need a packed-array ABI I do not lower"),
    (r"\bnano_cb_\d+_(?:string|scalar|text|float)", "nanolang runtime helpers are not part of P2C"),
    (r"\b(?:malloc|calloc|free|atexit|snprintf|sprintf)\b", "host runtime calls have no P2C equivalent"),
    (r"\bstruct\b|\bunion\b|\bvoid\s*\*", "aggregates and void pointers are refused"),
    (r"\b(?:dlopen|dlsym|fopen|fclose|fgets)\b", "host file and FFI calls are refused"),
    (r"\bstrlen\b", "P2C strlen needs an explicit assembler declaration I do not emit"),
    (r"\b(?:fprintf|stderr|exit)\b", "assert diagnostics use host I/O absent from the integer P2C subset"),
    (r"\bnano_cb_\w+\b", "a nanolang runtime helper would stay undefined in P2C"),
]


def top_level_items(source):
    """Split generated C into top-level declarations, ignoring directives."""
    items = []
    buffer = []
    depth = 0
    for line in source.splitlines():
        stripped = line.strip()
        if not buffer and (not stripped or stripped.startswith("#") or stripped.startswith("typedef")):
            continue
        buffer.append(line)
        code = re.sub(r'"(?:\\.|[^"\\])*"', '""', line)
        depth += code.count("{") - code.count("}")
        if depth == 0 and (stripped.endswith(";") or stripped.endswith("}")):
            items.append("\n".join(buffer))
            buffer = []
    if buffer:
        raise ValueError("I found an unterminated top-level declaration")
    return items


DECL_NAME = re.compile(r"\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:;|\{)", re.S)
ENTRY_NAME = re.compile(r"nano_cb_\d+_entry")


LOCAL_DECL = re.compile(r"^(\s*)(int|unsigned)\s+([A-Za-z_]\w*)\s*=\s*([^;]+);\s*$")
BARE_DECL = re.compile(r"^(\s+)(?:int|unsigned)\s+[A-Za-z_]\w*\s*;\s*$")


def split_local_initializers(text):
    """P2C accepts a load-time initializer only at module scope, and it
    requires declarations before statements in a block.

    NanoLang emits `int total = 0;` inside functions, so I separate the
    declaration from its assignment and hoist declarations to the block head.
    """
    if "{" not in text:
        return text
    lines = []
    for line in text.splitlines():
        match = LOCAL_DECL.match(line)
        if match:
            indent, kind, name, initializer = match.groups()
            lines.append(f"{indent}{kind} {name};")
            lines.append(f"{indent}{name} = {initializer};")
        else:
            lines.append(line)

    opening = next(
        (i for i, line in enumerate(lines) if line.rstrip().endswith("{") and "(" in line),
        None,
    )
    if opening is None:
        return "\n".join(lines)
    body = next((line for line in lines[opening + 1:] if line.strip()), "")
    body_indent = len(body) - len(body.lstrip())
    indices = [
        i for i in range(opening + 1, len(lines))
        if BARE_DECL.match(lines[i]) and len(lines[i]) - len(lines[i].lstrip()) == body_indent
    ]
    declarations = [lines[i] for i in indices]
    kept = [line for i, line in enumerate(lines) if i not in indices]
    return "\n".join(kept[:opening + 1] + declarations + kept[opening + 1:])


def rewrite(text):
    """Map nanolang C spellings onto the P2C dialect."""
    text = re.sub(r"INT64_C\((-?\d+)\)", r"\1", text)
    text = re.sub(r"UINT64_C\((-?\d+)\)", r"\1U", text)
    text = re.sub(r"\(\s*(?:long long|unsigned long long)\s*\)", "", text)
    text = re.sub(r"\(\s*(?:u?int(?:8|16|32|64)_t|size_t)\s*\)", "", text)
    text = re.sub(r"\bint64_t\b", "int", text)
    text = re.sub(r"\buint(?:8|16|32|64)_t\b", "unsigned", text)
    text = re.sub(r"\bsize_t\b", "int", text)
    text = text.replace("%lld", "%d").replace("%llu", "%u").replace("%llx", "%x")
    text = re.sub(r"\bvoid\s+main\s*\([^)]*\)[^{]*\{[^}]*\}", "", text)
    text = text.replace("(void)", "()")
    text = ENTRY_NAME.sub("nano_entry", text)
    text = split_local_initializers(text)
    return text.strip()


def translate(source, origin):
    kept = []
    entry_body = None
    for item in top_level_items(source):
        match = DECL_NAME.search(item)
        if not match:
            continue
        name = match.group(1)
        if name.startswith("nano_cb_") and not ENTRY_NAME.fullmatch(name):
            continue
        if name == "main":
            continue
        lowered = rewrite(item)
        for pattern, reason in REFUSALS:
            found = re.search(pattern, lowered)
            if found:
                raise ValueError(f"I refuse '{found.group(0)}': {reason}")
        for digits in re.findall(r"(?<![\w])\d+(?![\w])", lowered):
            if int(digits) > 1099511627775:
                raise ValueError(
                    f"I refuse {digits}: it exceeds P2C's 41-bit signed range"
                )
        kept.append(lowered)
        if name == "nano_cb_0_entry" or ENTRY_NAME.fullmatch(name):
            entry_body = lowered

    if entry_body is None:
        raise ValueError("I require a nanolang entry function (nano_cb_N_entry)")

    if "printf(" in entry_body:
        wrapper = "void main(int argc, char **argv) { nano_entry(); }"
    else:
        wrapper = 'void main(int argc, char **argv) { printf("%d\\n", nano_entry()); }'

    header = "/*=k9,l0*/\n/* Generated by nano2p2c from %s. Integer P2C dialect for BESM-6. */" % origin
    return header + "\n" + "\n\n".join(kept) + "\n\n" + wrapper + "\n"


def main(argv):
    args = argv[1:]
    output = None
    if "-o" in args:
        index = args.index("-o")
        if index + 1 >= len(args):
            print(USAGE, file=sys.stderr)
            return 2
        output = args[index + 1]
        del args[index:index + 2]
    if len(args) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    origin = args[0]
    try:
        with open(origin, encoding="utf-8") as stream:
            source = stream.read()
        result = translate(source, origin)
    except (OSError, ValueError) as error:
        print(f"nano2p2c: {error}", file=sys.stderr)
        return 1
    if output:
        with open(output, "w", encoding="utf-8") as stream:
            stream.write(result)
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

import re

def parse_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    functions = re.findall(r'function\s+(\w+)\s*\(', code)
    arrow_funcs = re.findall(r'(\w+)\s*=\s*\(.*?\)\s*=>', code)
    variables = re.findall(r'var\s+(\w+)|let\s+(\w+)|const\s+(\w+)', code)

    flat_vars = [v for group in variables for v in group if v]

    return {
        "Classes": [],
        "Functions": list(set(functions + arrow_funcs)),
        "Variables": list(set(flat_vars))
    }

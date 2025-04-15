import ast

def parse_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    tree = ast.parse(code)

    classes, functions, variables = [], [], []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append(target.id)

    return {
        "Classes": classes,
        "Functions": functions,
        "Variables": variables
    }

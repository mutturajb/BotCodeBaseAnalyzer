import os
from parsers import python_parser, java_parser, html_parser, js_parser

PARSERS = {
    '.py': python_parser,
    '.java': java_parser,
    '.html': html_parser,
    '.js': js_parser,
    '.jsx': js_parser,
    '.ts': js_parser,
    '.tsx': js_parser,
}

def get_supported_files(directory):
    supported = []
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in PARSERS:
                supported.append(os.path.relpath(os.path.join(root, file), directory))
    return supported

def analyze_repo(directory, file_path=None):
    files = get_supported_files(directory) if file_path is None else [file_path]
    result = {"Classes": [], "Functions": [], "Variables": []}

    for f in files:
        ext = os.path.splitext(f)[1]
        parser = PARSERS.get(ext)
        if parser:
            full_path = os.path.join(directory, f)
            parsed = parser.parse_file(full_path)
            for key in result:
                result[key].extend(parsed.get(key, []))

    for key in result:
        result[key] = list(set(result[key]))

    return result

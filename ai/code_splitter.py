import tree_sitter_python as tspython
import tree_sitter_javascript as tsjs
from tree_sitter import Language, Parser, TreeCursor


def parse_code_chunks(code:str, code_type:str='py'):
    """
    使用Tree-sitter解析Python代码的主要chunk
    
    :param code: 源代码字符串
    :param code_type: 代码类型
    :return: 解析后的chunks列表
    """
    # 创建解析器并设置语言
    print(code_type)
    if code_type == 'py':
        LANGUAGE = Language(tspython.language())
        QUERY_STRING = """
            (module (function_definition) @function.def)
            (module (class_definition) @class.def)
            (module (expression_statement) @expression)
            (module (import_statement) @import)
            (module (import_from_statement) @from_import)
            (module (decorated_definition) @decoed.def)
            """
        query_prop_list = ['function.def', 'class.def', 'expression', 'import', 'from_import', 'decoed.def']
    elif code_type == 'js' or code_type == 'jsx':
        LANGUAGE = Language(tsjs.language())
        QUERY_STRING = """
            (program (function_declaration) @function.def)
            (program (class_declaration) @class.def)
            (program (expression_statement) @expression)
            (program (import_statement) @import)
            (program (lexical_declaration) @lex.def)
            (program (variable_declaration) @var.def)
            """
        query_prop_list = ['function.def', 'class.def', 'expression', 'import', 'lex.def', 'var.def']
    else:
        return []

    parser = Parser(LANGUAGE)
    TYPE_MAP = {
        "function.def": "function",
        "class.def": "class",
        "expression": "expression",
        "decoed.def": "decoed",
        "import": "import",
        "from_import": "other",
        "lex.def": "other",
        "var.def": "other",
    }

    # 解析代码
    tree = parser.parse(code.encode())
    chunks = []

    query = LANGUAGE.query(QUERY_STRING)

    results = query.matches(tree.root_node)
    # print(len(results))


    for node, capture_group in results:
        chunk_node = capture_group[query_prop_list[node]][0]
        # print(chunk_node.text.decode())
        chunks.append({
            # 'type': chunk_node.type,
            'type': TYPE_MAP[query_prop_list[node]],
            # 'name': name,
            'content': chunk_node.text.decode(),
            'start_line': chunk_node.start_point[0],
            'end_line': chunk_node.end_point[0]
        })

    return chunks

def main():
    from pathlib import Path
    file_path = "jina-api.py"
    with open(Path.cwd() / Path(file_path), "r") as file:
        CODE = file.read()

    # 解析代码chunks
    chunks = parse_code_chunks(CODE, code_type='py')

    # 打印解析结果
    for chunk in chunks:
        print(f"Type: {chunk['type']}")
        # print(f"Name: {chunk['name']}")
        print(f"Lines: {chunk['start_line']} - {chunk['end_line']}")
        print("Full Text:")
        print(chunk['content'])
        print("-" * 40)

if __name__ == "__main__":
    main()
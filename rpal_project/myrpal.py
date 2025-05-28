import sys
from lexer.lexical_analyzer import tokenize
from parser.parser import RPALParser  
from ast.ast import ASTNode 
#from standardizer.standardizer import standardize_ast, print_st

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <-ast | -eval> <source_file.rpal>")
        sys.exit(1)

    mode = sys.argv[1]
    file_path = sys.argv[2]

    try:
        with open(file_path, 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    try:
        tokens = tokenize(source_code)
        parser = RPALParser(tokens)
        ast_root = parser.parse()

        if mode == "-ast":
            ast_root.print_tree()  # Implement print_tree() in ASTNode to match rpal.exe output
        elif mode == "-eval":
            #from cse_machine import evaluate  # if you have a CSE machine module
            #result = evaluate(ast_root)
            #print(result)
            from standardizer.standardizer import standardize
            standardized_ast = standardize(ast_root)

            print("Standardized AST:")
            standardized_ast.print_tree()
        else:
            print("Error: Invalid mode. Use -ast or -eval.")
            sys.exit(1)

    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

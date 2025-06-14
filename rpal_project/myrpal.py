import sys
from lexer.lexical_analyzer import tokenize
from parser.parser import RPALParser
from contextlib import redirect_stdout
import os
def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage:")
        print("  python myrpal.py -ast <source_file.rpal>")
        print("  python myrpal.py -st <source_file.rpal>")
        print("  python myrpal.py <source_file.rpal>")
        sys.exit(1)

    # Handle input mode
    if len(sys.argv) == 3:
        mode = sys.argv[1]
        file_path = sys.argv[2]
        #if mode != "-ast":
            #print("Error: Invalid mode. Use '-ast' or no switch.")
        if mode not in ["-ast", "-st"]:
            print("Error: Invalid mode. Use '-ast', '-st', or no switch.")
            sys.exit(1)
    else:
        mode = "eval"
        file_path = sys.argv[1]

    # Load file
    try:
        with open(file_path, 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    # Tokenize and parse
    try:
        tokens = tokenize(source_code)
        parser = RPALParser(tokens)
        ast_root = parser.parse()

        if mode == "-ast":
            
            # Create 'outputs/' directory if it doesn't exist
            os.makedirs("outputs", exist_ok=True)

            # Extract base name of the file for output naming
            base_filename = os.path.basename(file_path).replace(".rpal", "")
            output_path = f"outputs/ast_{base_filename}.txt"

            ast_root.print_tree()  # AST printing

            # Write AST to file
            with open(output_path, "w") as f:
                with redirect_stdout(f):
                   ast_root.print_tree()
               

            print(f"[✔] AST written to {output_path}")
        elif mode == "-st":
            from standardizer.standardizer import standardize
    
            # Create 'outputs/' directory if it doesn't exist
            os.makedirs("outputs", exist_ok=True)
    
            # Extract base name of the file for output naming
            base_filename = os.path.basename(file_path).replace(".rpal", "")
            output_path = f"outputs/st_{base_filename}.txt"
    
            # Standardize the AST
            standardized_ast = standardize(ast_root)
            standardized_ast.print_tree()  # Print standardized tree to console
    
            
    
    
        else:
            from standardizer.standardizer import standardize
            from cse.csemachine import Result

            standardized_ast = standardize(ast_root)
            result = Result(standardized_ast)
            print(result)  # Output should be just the final value, e.g., 15

    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

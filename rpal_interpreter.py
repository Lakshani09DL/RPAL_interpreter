import sys
import os
from rpal_parser import tokenize, RPALParser, print_ast
from rpal_standardizer import standardize_ast, print_st
from rpal_cse_machine import execute_st, print_result

def read_file(filename):
    """Read RPAL program from file"""
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def interpret_rpal(code, debug=False):
    """Interpret RPAL program"""
    try:
        # Step 1: Tokenize
        tokens = tokenize(code)
        if debug:
            print("=== Tokens ===")
            for token in tokens:
                print(token)
            print()
        
        # Step 2: Parse to AST
        parser = RPALParser(tokens)
        ast = parser.parse()
        if debug:
            print("=== Abstract Syntax Tree ===")
            print_ast(ast)
            print()
        
        # Step 3: Convert AST to Standardized Tree
        st = standardize_ast(ast)
        if debug:
            print("=== Standardized Tree ===")
            print_st(st)
            print()
        
        # Step 4: Execute with CSE Machine
        result = execute_st(st)
        if debug:
            print("=== Result ===")
        print_result(result)
        
        return result
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python rpal_interpreter.py <filename> [-debug]")
        sys.exit(1)
    
    filename = sys.argv[1]
    debug = "-debug" in sys.argv
    
    # Read and interpret RPAL program
    code = read_file(filename)
    interpret_rpal(code, debug)

if __name__ == "__main__":
    main()
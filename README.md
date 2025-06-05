# RPAL_interpreter


## 🚀 Features

- **Lexical Analysis** – Converts RPAL source code into a stream of tokens.
- **Recursive Descent Parser** – Parses tokens and builds an abstract syntax tree (AST).
- **AST Printer** – Outputs the AST in a structured, readable format.
- **CSE Machine** – Evaluates the AST according to RPAL semantics.

## 🛠️ Usage

### 1. **AST Generation**
To generate and print the AST of a `.rpal` file:
```bash
python myrpal.py -ast path/to/program.rpal
```
Prints the AST in RPAL format to the terminal.
Saves a copy to:
```bash
outputs/ast_<filename>.txt
```

### 2. **Evaluation (Default Mode)**
To evaluate a .rpal program and print the output:
```bash
python myrpal.py path/to/program.rpal
```

### 3. **ST Generation**
To generate and print the ST of a `.rpal` file:
```bash
python main.py -st path/to/program.rpal
```

## Makfile Usage
Use the provided Makefile to simplify running tests:
```bash
make ast FILE=tests/test1.rpal   # Show AST for a test file
make run FILE=tests/test1.rpal   # Evaluate and show output
make test                        # Run all test files in /tests
make clean                       # Clean up temporary files
```

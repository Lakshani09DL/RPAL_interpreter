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

### 2. **ST Generation**
To generate and print the ST of a `.rpal` file:
```bash
python myrpal.py -eval path/to/program.rpal



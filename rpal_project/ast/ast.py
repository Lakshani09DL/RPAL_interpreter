class ASTNode:
    def __init__(self, type_name, value=None, children=None):
        self.type = type_name
        self.value = value
        self.children = children if children is not None else []
    
    def add_child(self, child):
        self.children.append(child)
    
    def __str__(self):
        return self.to_string()
    
    def to_string(self, level=0):
        indent = "  " * level
        result = f"{indent}{self.type}"
        if self.value is not None:
            result += f": {self.value}"
        result += "\n"
        
        for child in self.children:
            result += child.to_string(level + 1)
        
        return result
    
    def print_tree(self, indent=0):
        """Print the AST in a readable format"""
        prefix = '  ' * indent
        print(f"{prefix}{self.type}", end='')
        if self.value is not None:
            print(f": {self.value}")
        else:
            print()
        
        for child in self.children:
            child.print_tree(indent + 1)
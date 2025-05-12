class Environment:
    """Environment for CSE machine"""
    def __init__(self, parent=None):
        self.parent = parent
        self.bindings = {}
    
    def lookup(self, name):
        """Look up a variable in the environment"""
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            raise ValueError(f"Variable {name} not found in environment")
    
    def extend(self, name, value):
        """Extend environment with a new binding"""
        self.bindings[name] = value
        return self
    
    def __str__(self):
        return str(self.bindings)

class CSEValue:
    """Value in CSE machine"""
    def __init__(self, type_name, value=None, env=None):
        self.type = type_name
        self.value = value
        self.env = env
    
    def __str__(self):
        if self.type == 'lambda':
            return f"<{self.type}: {self.value}>"
        elif self.type == 'tuple':
            return f"({', '.join(str(v) for v in self.value)})"
        else:
            return str(self.value)

class CSEClosure:
    """Closure in CSE machine"""
    def __init__(self, node, env):
        self.node = node
        self.env = env
    
    def __str__(self):
        return f"<closure: {self.node.type}>"

class CSEMachine:
    """Control-Stack-Environment Machine"""
    def __init__(self):
        self.control = []  # Control stack
        self.stack = []    # Value stack
        self.env = Environment()  # Initial environment
        
        # Initialize standard environment with built-in functions
        self._init_std_env()
    
    def _init_std_env(self):
        """Initialize standard environment with built-in functions"""
        # Y combinator for recursion
        self.env.extend('Y', CSEValue('Y-combinator'))
        
        # Arithmetic operations
        self.env.extend('+', CSEValue('operator', lambda x, y: CSEValue('integer', int(x.value) + int(y.value))))
        self.env.extend('-', CSEValue('operator', lambda x, y: CSEValue('integer', int(x.value) - int(y.value))))
        self.env.extend('*', CSEValue('operator', lambda x, y: CSEValue('integer', int(x.value) * int(y.value))))
        self.env.extend('/', CSEValue('operator', lambda x, y: CSEValue('integer', int(x.value) // int(y.value))))
        self.env.extend('**', CSEValue('operator', lambda x, y: CSEValue('integer', int(x.value) ** int(y.value))))
        self.env.extend('neg', CSEValue('operator', lambda x: CSEValue('integer', -int(x.value))))
        
        # Comparison operations
        self.env.extend('gr', CSEValue('operator', lambda x, y: CSEValue('boolean', x.value > y.value)))
        self.env.extend('ge', CSEValue('operator', lambda x, y: CSEValue('boolean', x.value >= y.value)))
        self.env.extend('ls', CSEValue('operator', lambda x, y: CSEValue('boolean', x.value < y.value)))
        self.env.extend('le', CSEValue('operator', lambda x, y: CSEValue('boolean', x.value <= y.value)))
        self.env.extend('eq', CSEValue('operator', lambda x, y: CSEValue('boolean', x.value == y.value)))
        self.env.extend('ne', CSEValue('operator', lambda x, y: CSEValue('boolean', x.value != y.value)))
        
        # Logical operations
        self.env.extend('and', CSEValue('operator', lambda x, y: CSEValue('boolean', x.value and y.value)))
        self.env.extend('or', CSEValue('operator', lambda x, y: CSEValue('boolean', x.value or y.value)))
        self.env.extend('not', CSEValue('operator', lambda x: CSEValue('boolean', not x.value)))
        
        # Tuple operations
        self.env.extend('aug', CSEValue('operator', lambda x, y: CSEValue('tuple', x.value + [y] if isinstance(x.value, list) else [x, y])))
    
    def execute(self, st_node):
        """Execute standardized tree"""
        # Initialize control with root node
        self.control = [st_node]
        self.stack = []
        
        # Main execution loop
        while self.control:
            # Get next control item
            ctrl = self.control.pop(0)
            
            # Process based on type
            if isinstance(ctrl, tuple) and ctrl[0] == 'apply':
                # Apply function
                self._apply()
            else:
                # Process node
                self._process_node(ctrl)
        
        # Return final result
        if self.stack:
            return self.stack[0]
        return None
    
    def _process_node(self, node):
        """Process a node in the standardized tree"""
        node_type = node.type
        
        if node_type == 'lambda':
            # Create closure
            self.stack.append(CSEClosure(node, self.env))
        
        elif node_type == 'identifier':
            # Look up identifier in environment
            try:
                value = self.env.lookup(node.value)
                self.stack.append(value)
            except ValueError:
                print(f"Error: Undefined variable '{node.value}'")
                self.stack.append(CSEValue('error', f"Undefined variable '{node.value}'"))
        
        elif node_type == 'integer':
            # Push integer value
            self.stack.append(CSEValue('integer', int(node.value)))
        
        elif node_type == 'string':
            # Push string value
            self.stack.append(CSEValue('string', node.value))
        
        elif node_type == 'boolean' or node_type == 'true' or node_type == 'false':
            # Push boolean value
            if node_type == 'true':
                self.stack.append(CSEValue('boolean', True))
            elif node_type == 'false':
                self.stack.append(CSEValue('boolean', False))
            else:
                self.stack.append(CSEValue('boolean', node.value))
        
        elif node_type == 'nil':
            # Push nil value
            self.stack.append(CSEValue('nil', None))
        
        elif node_type == 'tau':
            # Create tuple
            # First process all children
            n = len(node.children)
            self.control.insert(0, ('construct_tuple', n))
            
            # Add children to control in reverse order
            for child in reversed(node.children):
                self.control.insert(0, child)
        
        elif node_type == 'gamma':
            # Function application
            # Process function and argument
            self.control.insert(0, ('apply',))
            
            # Add argument to control
            self.control.insert(0, node.children[1])
            
            # Add function to control
            self.control.insert(0, node.children[0])
        
        elif node_type == '=':
            # Assignment
            # Process right side
            self.control.insert(0, ('assign', node.children[0]))
            
            # Add expression to control
            self.control.insert(0, node.children[1])
        
        elif node_type == ',':
            # Multiple variables
            # Create tuple of identifiers
            ids = []
            for child in node.children:
                if child.type == 'identifier':
                    ids.append(child.value)
            self.stack.append(CSEValue('identifiers', ids))
        
        elif node_type == ('construct_tuple', n):
            # Construct tuple from top n values on stack
            tuple_vals = []
            for _ in range(n):
                tuple_vals.insert(0, self.stack.pop())
            self.stack.append(CSEValue('tuple', tuple_vals))
        
        else:
            # For other node types, just process all children
            for child in node.children:
                self.control.insert(0, child)
    
    def _apply(self):
        """Apply function to argument"""
        # Get function and argument from stack
        arg = self.stack.pop()
        func = self.stack.pop()
        
        if isinstance(func, CSEClosure):
            # Apply closure
            node = func.node
            if node.type == 'lambda':
                # Lambda application
                var_node = node.children[0]
                body_node = node.children[1]
                
                # Create new environment
                new_env = Environment(func.env)
                
                # Bind variable to argument
                if var_node.type == 'identifier':
                    new_env.extend(var_node.value, arg)
                elif var_node.type == ',' and arg.type == 'tuple':
                    # Multiple variable binding
                    for i, name in enumerate(var_node.children):
                        if i < len(arg.value):
                            new_env.extend(name.value, arg.value[i])
                
                # Execute body with new environment
                old_env = self.env
                self.env = new_env
                self.control.insert(0, body_node)
                self.env = old_env
            
            elif node.type == 'Y-combinator':
                # Y combinator for recursion
                if isinstance(arg, CSEClosure):
                    # Create recursive function closure
                    self.stack.append(CSEClosure(arg.node, self.env))
                else:
                    self.stack.append(CSEValue('error', "Y combinator argument must be a closure"))
        
        elif func.type == 'operator':
            # Apply operator
            if func.value and callable(func.value):
                # Built-in operator
                if isinstance(arg, list):
                    # Apply to all elements in list
                    result = func.value(*arg)
                else:
                    result = func.value(arg)
                self.stack.append(result)
            else:
                self.stack.append(CSEValue('error', f"Operator {func.value} is not callable"))
        
        else:
            # Other function types
            if func.type == 'function':
                # Apply function to argument
                if func.value and callable(func.value):
                    result = func.value(arg)
                    self.stack.append(result)
                else:
                    self.stack.append(CSEValue('error', f"Function {func.value} is not callable"))
            else:
                self.stack.append(CSEValue('error', f"Cannot apply {func.type} as a function"))

def execute_st(st_node):
    """Execute standardized tree with CSE machine"""
    machine = CSEMachine()
    result = machine.execute(st_node)
    return result

def print_result(result):
    """Pretty print the result of CSE machine execution"""
    if result.type == 'tuple':
        print(f"({', '.join(str(v) for v in result.value)})")
    else:
        print(result)

if __name__ == "__main__":
    # We'll integrate this with the parser and standardizer in the main program
    pass
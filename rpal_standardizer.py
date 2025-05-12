class STNode:
    """Node in the Standardized Tree"""
    def __init__(self, type_name, value=None):
        self.type = type_name
        self.value = value
        self.children = []
    
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

class RPALStandardizer:
    """Converts AST to Standardized Tree"""
    def __init__(self):
        self.delta_counter = 0
    
    def standardize(self, ast_node):
        """Convert AST to Standardized Tree"""
        return self._standardize_node(ast_node)
    
    def _standardize_node(self, ast_node):
        """Recursively standardize a node"""
        node_type = ast_node.type
        
        # Handle special forms
        if node_type == 'let':
            return self._standardize_let(ast_node)
        elif node_type == 'where':
            return self._standardize_where(ast_node)
        elif node_type == 'fcn_form':
            return self._standardize_fcn_form(ast_node)
        elif node_type == 'lambda':
            return self._standardize_lambda(ast_node)
        elif node_type == 'within':
            return self._standardize_within(ast_node)
        elif node_type == 'rec':
            return self._standardize_rec(ast_node)
        elif node_type == 'and':
            return self._standardize_and(ast_node)
        
        # Standard node processing
        st_node = STNode(node_type, ast_node.value)
        for child in ast_node.children:
            st_node.add_child(self._standardize_node(child))
        
        return st_node
    
    def _standardize_let(self, ast_node):
        """Standardize let expression: let D in E => (lambda V.E) where V is bound to D"""
        # Extract D and E from let expression
        d_node = ast_node.children[0]
        e_node = ast_node.children[1]
        
        # Create gamma node
        gamma_node = STNode('gamma')
        
        # Create lambda node
        lambda_node = STNode('lambda')
        
        # Process D to get bindings
        if d_node.type == '=':
            # Simple variable binding: let x = E1 in E2
            var_node = d_node.children[0]
            binding_node = d_node.children[1]
            
            # Create lambda with the variable
            lambda_node.add_child(self._standardize_node(var_node))
            lambda_node.add_child(self._standardize_node(e_node))
            
            # Create gamma with lambda and binding
            gamma_node.add_child(lambda_node)
            gamma_node.add_child(self._standardize_node(binding_node))
            
            return gamma_node
        elif d_node.type == 'and':
            # Multiple bindings: let x=E1 and y=E2 and ... in E
            return self._standardize_let_and(d_node, e_node)
        elif d_node.type == 'rec':
            # Recursive binding: let rec D in E
            return self._standardize_let_rec(d_node.children[0], e_node)
        else:
            # Handle other complex bindings
            gamma_node.add_child(lambda_node)
            lambda_node.add_child(self._extract_binding_vars(d_node))
            lambda_node.add_child(self._standardize_node(e_node))
            gamma_node.add_child(self._standardize_node(d_node))
            return gamma_node
    
    def _standardize_let_and(self, and_node, expr_node):
        """Standardize let with multiple bindings: let x=E1 and y=E2 and ... in E"""
        # Build tuple of variables and expressions
        vars_list = []
        exprs_list = []
        
        for binding in and_node.children:
            if binding.type == '=':
                vars_list.append(binding.children[0])
                exprs_list.append(binding.children[1])
        
        # Create gamma node for the let expression
        gamma_node = STNode('gamma')
        
        # Create lambda node with all variables
        lambda_node = STNode('lambda')
        
        # Create comma node for multiple variables if needed
        if len(vars_list) > 1:
            comma_node = STNode(',')
            for var_node in vars_list:
                comma_node.add_child(self._standardize_node(var_node))
            lambda_node.add_child(comma_node)
        else:
            lambda_node.add_child(self._standardize_node(vars_list[0]))
        
        # Add expression to lambda
        lambda_node.add_child(self._standardize_node(expr_node))
        
        # Add lambda to gamma
        gamma_node.add_child(lambda_node)
        
        # Create tau node for multiple expressions if needed
        if len(exprs_list) > 1:
            tau_node = STNode('tau')
            for expr_node in exprs_list:
                tau_node.add_child(self._standardize_node(expr_node))
            gamma_node.add_child(tau_node)
        else:
            gamma_node.add_child(self._standardize_node(exprs_list[0]))
        
        return gamma_node
    
    def _standardize_where(self, ast_node):
        """Standardize where expression: E where D => let D in E"""
        e_node = ast_node.children[0]
        d_node = ast_node.children[1]
        
        # Create equivalent let structure
        let_node = STNode('let')
        let_node.add_child(d_node)
        let_node.add_child(e_node)
        
        # Standardize the let expression
        return self._standardize_let(let_node)
    
    def _standardize_fcn_form(self, ast_node):
        """Standardize function form: f x1 x2 ... xn = E => f = lambda x1.lambda x2...lambda xn.E"""
        # Extract function name and parameters
        func_name = ast_node.children[0]
        param_nodes = ast_node.children[1:-1]  # Parameters between name and body
        body_node = ast_node.children[-1]      # Last child is function body
        
        # Create equality node
        eq_node = STNode('=')
        eq_node.add_child(self._standardize_node(func_name))
        
        # Create nested lambdas for each parameter
        current_node = None
        lambda_head = None
        
        for i, param_node in enumerate(param_nodes):
            lambda_node = STNode('lambda')
            lambda_node.add_child(self._standardize_node(param_node))
            
            if i == 0:
                lambda_head = lambda_node
                current_node = lambda_node
            else:
                current_node.add_child(lambda_node)
                current_node = lambda_node
        
        # Add function body to innermost lambda
        if current_node:
            current_node.add_child(self._standardize_node(body_node))
            eq_node.add_child(lambda_head)
        else:
            # No parameters case
            eq_node.add_child(self._standardize_node(body_node))
        
        return eq_node
    
    def _standardize_lambda(self, ast_node):
        """Standardize lambda expression: lambda x.E"""
        st_node = STNode('lambda')
        
        # Add variable binding
        st_node.add_child(self._standardize_node(ast_node.children[0]))
        
        # Add body
        if len(ast_node.children) > 1:
            st_node.add_child(self._standardize_node(ast_node.children[1]))
        
        return st_node
    
    def _standardize_within(self, ast_node):
        """Standardize within expression: D1 within D2 => let D1 in D2"""
        d1_node = ast_node.children[0]
        d2_node = ast_node.children[1]
        
        # Create gamma node
        gamma_node = STNode('gamma')
        
        # Create lambda node
        lambda_node = STNode('lambda')
        
        # Extract variables from D1
        vars_node = self._extract_binding_vars(d1_node)
        
        # Add variables to lambda
        lambda_node.add_child(vars_node)
        
        # Add D2 to lambda
        lambda_node.add_child(self._standardize_node(d2_node))
        
        # Add lambda to gamma
        gamma_node.add_child(lambda_node)
        
        # Add D1 expressions to gamma
        gamma_node.add_child(self._extract_binding_exprs(d1_node))
        
        return gamma_node
    
    def _standardize_rec(self, ast_node):
        """Standardize recursive definition: rec D => Y (lambda vars.expressions)"""
        # Extract binding from rec node
        binding_node = ast_node.children[0]
        
        # Create Y combinator node
        y_node = STNode('identifier', 'Y')
        
        # Create gamma node for Y application
        gamma_node = STNode('gamma')
        gamma_node.add_child(y_node)
        
        # Create lambda for the recursive function
        lambda_node = STNode('lambda')
        
        # Extract variables from binding
        vars_node = self._extract_binding_vars(binding_node)
        lambda_node.add_child(vars_node)
        
        # Extract expressions from binding
        expr_node = self._extract_binding_exprs(binding_node)
        lambda_node.add_child(expr_node)
        
        # Add lambda to gamma
        gamma_node.add_child(lambda_node)
        
        return gamma_node
    
    def _standardize_and(self, ast_node):
        """Standardize and expression: D1 and D2 and ... => (D1,D2,...)"""
        # Create tuple node for multiple bindings
        tau_node = STNode('tau')
        
        # Add each binding to tuple
        for binding in ast_node.children:
            tau_node.add_child(self._standardize_node(binding))
        
        return tau_node
    
    def _extract_binding_vars(self, binding_node):
        """Extract variables from binding node"""
        if binding_node.type == '=':
            return self._standardize_node(binding_node.children[0])
        elif binding_node.type == 'and':
            comma_node = STNode(',')
            for child in binding_node.children:
                if child.type == '=':
                    comma_node.add_child(self._standardize_node(child.children[0]))
            return comma_node
        return STNode('identifier', 'UNKNOWN')
    
    def _extract_binding_exprs(self, binding_node):
        """Extract expressions from binding node"""
        if binding_node.type == '=':
            return self._standardize_node(binding_node.children[1])
        elif binding_node.type == 'and':
            tau_node = STNode('tau')
            for child in binding_node.children:
                if child.type == '=':
                    tau_node.add_child(self._standardize_node(child.children[1]))
            return tau_node
        return STNode('identifier', 'UNKNOWN')

def standardize_ast(ast_node):
    """Convert AST to Standardized Tree"""
    standardizer = RPALStandardizer()
    return standardizer.standardize(ast_node)

def print_st(st_node, indent=0):
    """Print the Standardized Tree in a readable format"""
    prefix = '  ' * indent
    print(f"{prefix}{st_node.type}", end='')
    if st_node.value is not None:
        print(f": {st_node.value}")
    else:
        print()
    
    for child in st_node.children:
        print_st(child, indent + 1)
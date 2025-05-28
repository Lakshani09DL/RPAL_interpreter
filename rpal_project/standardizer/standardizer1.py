from ast.ast import ASTNode

class RPALASTStandardizer:
    """
    Standardizes RPAL AST according to language specifications.
    Handles transformations like let->where conversion, lambda standardization,
    multi-parameter functions, conditional expressions, etc.
    """
    
    def __init__(self):
        self.standardized_tree = None
    
    def standardize(self, ast_root):
        """
        Main standardization method that applies all transformations
        """
        if ast_root is None:
            return None
        
        # Create a deep copy and standardize
        self.standardized_tree = self._deep_copy(ast_root)
        self._standardize_node(self.standardized_tree)
        return self.standardized_tree
    
    def _deep_copy(self, node):
        """Create a deep copy of the AST node"""
        if node is None:
            return None
        
        new_node = ASTNode(node.type, node.value)
        for child in node.children:
            new_node.add_child(self._deep_copy(child))
        return new_node
    
    def _standardize_node(self, node):
        """
        Recursively standardize each node in the AST
        """
        if node is None:
            return
        
        # First standardize all children
        for child in node.children:
            self._standardize_node(child)
        
        # Apply specific standardizations based on node type
        if node.type == "let" or node.type == "let_rec" or node.type == "where":
            self._standardize_let(node)
        elif node.type == "lambda":
            self._standardize_lambda(node)
        elif node.type == "function_form":
            self._standardize_function_form(node)
        elif node.type == "conditional":
            self._standardize_conditional(node)
        elif node.type == "tau":
            self._standardize_tau(node)
        elif node.type == "within":
            self._standardize_within(node)
        elif node.type == "and":
            self._standardize_and(node)
        elif node.type == "rec":
            self._standardize_rec(node)
        elif node.type == "@":
            self._standardize_at(node)
    
    def _standardize_let(self, node):
        """
        Transform let, let rec, and where to gamma applications with lambda
        """
        if node.type == "let":
            definition = node.children[0]
            body = node.children[1]
            
            if definition.type == "=" and len(definition.children) == 2:
                var = definition.children[0]
                expr = definition.children[1]
                # Standardize the expression first
                self._standardize_node(expr)
                lam = ASTNode("lambda", children=[var, body])
                # Transform to gamma application
                node.type = "gamma"
                node.children = [lam, expr]
                # Recursively standardize the new structure
                self._standardize_node(node)
                
            elif definition.type == "fcn_form":
                var = definition.children[0]
                params = definition.children[1:-1]
                expr = definition.children[-1]
                # Create nested lambdas for parameters
                for param in reversed(params):
                    expr = ASTNode("lambda", children=[param, expr])
                lam = ASTNode("lambda", children=[var, body])
                # Transform to gamma application
                node.type = "gamma"
                node.children = [lam, expr]
                # Recursively standardize the new structure
                self._standardize_node(node)
                
            else:
                print(f"[Warning] Unexpected 'let' definition node: {definition.type}")
                
        elif node.type == "let_rec":
            # let rec f = E1 in E2 -> gamma(lambda f . E2, Y(lambda f . E1))
            # where Y is the fixed-point combinator
            definition = node.children[0]
            body = node.children[1]
            
            if definition.type == "=" and len(definition.children) == 2:
                var = definition.children[0]
                expr = definition.children[1]
                
                # Create Y(lambda f . E1) 
                inner_lambda = ASTNode("lambda", children=[var, expr])
                y_combinator = ASTNode("Y")  # Fixed-point combinator
                y_application = ASTNode("gamma", children=[y_combinator, inner_lambda])
                
                # Create lambda f . E2
                outer_lambda = ASTNode("lambda", children=[var, body])
                
                # Final transformation: gamma(lambda f . E2, Y(lambda f . E1))
                node.type = "gamma"
                node.children = [outer_lambda, y_application]
                
                # Recursively standardize the new structure
                self._standardize_node(node)
                
            elif definition.type == "fcn_form":
                # let rec f x y = E1 in E2 
                # -> gamma(lambda f . E2, Y(lambda f . lambda x . lambda y . E1))
                var = definition.children[0]
                params = definition.children[1:-1]
                expr = definition.children[-1]
                
                # Create nested lambdas for parameters: lambda x . lambda y . E1
                nested_lambda = expr
                for param in reversed(params):
                    nested_lambda = ASTNode("lambda", children=[param, nested_lambda])
                
                # Create Y(lambda f . lambda x . lambda y . E1)
                inner_lambda = ASTNode("lambda", children=[var, nested_lambda])
                y_combinator = ASTNode("Y")
                y_application = ASTNode("gamma", children=[y_combinator, inner_lambda])
                
                # Create lambda f . E2
                outer_lambda = ASTNode("lambda", children=[var, body])
                
                # Final transformation
                node.type = "gamma"
                node.children = [outer_lambda, y_application]
                
                # Recursively standardize the new structure
                self._standardize_node(node)
                
            else:
                print(f"[Warning] Unexpected 'let rec' definition node: {definition.type}")
                
        elif node.type == "where":
            body = node.children[0]
            definition = node.children[1]
            
            if definition.type == "=" and len(definition.children) == 2:
                var = definition.children[0]
                expr = definition.children[1]
                # Standardize the expression first
                self._standardize_node(expr)
                lam = ASTNode("lambda", children=[var, body])
                # Transform to gamma application
                node.type = "gamma"
                node.children = [lam, expr]
                # Recursively standardize the new structure
                self._standardize_node(node)
            else:
                print(f"[Warning] Unexpected 'where' definition node: {definition.type}")
    
    def _standardize_lambda(self, node):
        """
        Handle multi-parameter lambda functions
        Transform: lambda x1,x2,...,xn . E -> lambda x1 . (lambda x2 . (... lambda xn . E))
        """
        if len(node.children) < 2:
            return
        
        # Get all parameter nodes (all but the last child which is the body)
        params = node.children[:-1]
        body = node.children[-1]
        
        if len(params) > 1:
            # Create nested lambda structure
            current_lambda = node
            current_lambda.children = [params[0]]  # First parameter
            
            # Create nested lambdas for remaining parameters
            for i in range(1, len(params)):
                inner_lambda = ASTNode("lambda")
                inner_lambda.add_child(params[i])
                current_lambda.add_child(inner_lambda)
                current_lambda = inner_lambda
            
            # Add the body to the innermost lambda
            current_lambda.add_child(body)
    
    def _standardize_function_form(self, node):
        """
        Transform function form to lambda
        f x1 x2 ... xn = E -> f = lambda x1 . lambda x2 . ... lambda xn . E
        """
        if len(node.children) < 2:
            return
        
        function_name = node.children[0]
        params = node.children[1:-1]  # Parameters
        body = node.children[-1]      # Function body
        
        if params:
            # Create nested lambda structure
            lambda_node = ASTNode("lambda")
            lambda_node.add_child(params[0])
            
            current_lambda = lambda_node
            for i in range(1, len(params)):
                inner_lambda = ASTNode("lambda")
                inner_lambda.add_child(params[i])
                current_lambda.add_child(inner_lambda)
                current_lambda = inner_lambda
            
            current_lambda.add_child(body)
            
            # Transform to assignment
            node.type = "="
            node.children = [function_name, lambda_node]
    
    def _standardize_conditional(self, node):
        """
        Ensure conditional has proper structure: -> B T F
        """
        if len(node.children) == 3:
            # Already in correct form
            return
        
        # Handle any malformed conditionals
        if len(node.children) < 3:
            # Add missing parts as needed
            while len(node.children) < 3:
                node.add_child(ASTNode("nil"))
    
    def _standardize_tau(self, node):
        """
        Standardize tuple expressions
        tau E1 E2 ... En -> properly structured tuple
        """
        # Tau nodes are generally already in correct form
        # Just ensure all children are properly standardized
        pass
    
    def _standardize_within(self, node):
        """
        Transform within expressions
        D1 within D2 -> where (where E D2) D1
        """
        if len(node.children) >= 2:
            d1_node = node.children[0]
            d2_node = node.children[1]
            
            # This transformation depends on the specific structure
            # May need adjustment based on your RPAL implementation
            pass
    
    def _standardize_and(self, node):
        """
        Handle simultaneous definitions
        """
        # And nodes typically don't need transformation
        # but ensure proper structure
        pass
    
    def _standardize_rec(self, node):
        """
        Handle recursive definitions
        rec D -> properly structured recursive definition
        """
        # Rec transformations depend on specific implementation
        pass
    
    def _standardize_at(self, node):
        """
        Handle @ (at) expressions for indexing
        E1 @ E2 @ ... @ En
        """
        # At expressions are typically left-associative
        if len(node.children) > 2:
            # Restructure to be left-associative
            self._make_left_associative(node)
    
    def _make_left_associative(self, node):
        """
        Make binary operators left-associative
        """
        if len(node.children) <= 2:
            return
        
        # Create left-associative structure
        op_type = node.type
        first_child = node.children[0]
        remaining_children = node.children[1:]
        
        # Create new left-associative structure
        current_node = ASTNode(op_type)
        current_node.add_child(first_child)
        current_node.add_child(remaining_children[0])
        
        for i in range(1, len(remaining_children)):
            new_node = ASTNode(op_type)
            new_node.add_child(current_node)
            new_node.add_child(remaining_children[i])
            current_node = new_node
        
        # Replace current node's structure
        node.children = current_node.children
    
    def _standardize_binary_ops(self, node):
        """
        Standardize binary operations to be left-associative
        """
        binary_ops = ["+", "-", "*", "/", "**", "eq", "ne", "ls", "le", "gr", "ge", 
                     "or", "&", "aug", "@"]
        
        if node.type in binary_ops and len(node.children) > 2:
            self._make_left_associative(node)
    
    def print_standardized_tree(self):
        """Print the standardized AST"""
        if self.standardized_tree:
            print("Standardized AST:")
            self.standardized_tree.print_tree()
        else:
            print("No standardized tree available. Call standardize() first.")


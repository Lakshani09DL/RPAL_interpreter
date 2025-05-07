from lexer.lexical_analyzer import TokenType, Token, tokenize
from ast.ast import ASTNode

class RPALParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = tokens[0]
    
    def parse(self):
        """Parse the RPAL program and return the AST"""
        return self.parse_E()
    
    def consume(self):
        """Consume current token and advance to the next token"""
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
            self.current_token = self.tokens[self.current_token_index]
    
    def match(self, token_type, value=None):
        """Match current token with expected token type and value"""
        if self.current_token.type == token_type and (value is None or self.current_token.value == value):
            token = self.current_token
            self.consume()
            return token
        else:
            if value:
                expected = f"{token_type.name}: {value}"
            else:
                expected = token_type.name
            found = f"{self.current_token.type.name}: {self.current_token.value}"
            raise SyntaxError(f"Expected {expected}, but found {found}")
    
    def check(self, token_type, value=None):
        """Check if current token matches expected token type and value without consuming it"""
        return (self.current_token.type == token_type and 
                (value is None or self.current_token.value == value))
    
    # Expressions
    def parse_E(self):
        """Parse E production"""
        if self.check(TokenType.KEYWORD, 'let'):
            self.match(TokenType.KEYWORD, 'let')
            d_node = self.parse_D()
            self.match(TokenType.KEYWORD, 'in')
            e_node = self.parse_E()
            let_node = ASTNode('let')
            let_node.add_child(d_node)
            let_node.add_child(e_node)
            return let_node
        elif self.check(TokenType.KEYWORD, 'fn'):
            self.match(TokenType.KEYWORD, 'fn')
            vb_nodes = []
            while True:
                vb_nodes.append(self.parse_Vb())
                if not self.check(TokenType.IDENTIFIER) and not self.check(TokenType.PUNCTUATION, '('):
                    break
            self.match(TokenType.PUNCTUATION, '.')
            e_node = self.parse_E()
            
            lambda_node = ASTNode('lambda')
            # Build nested lambda structure for multiple variables
            current_node = lambda_node
            for i, vb_node in enumerate(vb_nodes):
                current_node.add_child(vb_node)
                if i < len(vb_nodes) - 1:
                    next_lambda = ASTNode('lambda')
                    current_node.add_child(next_lambda)
                    current_node = next_lambda
                else:
                    current_node.add_child(e_node)
            
            return lambda_node
        else:
            return self.parse_Ew()
    
    def parse_Ew(self):
        """Parse Ew production"""
        t_node = self.parse_T()
        if self.check(TokenType.KEYWORD, 'where'):
            self.match(TokenType.KEYWORD, 'where')
            dr_node = self.parse_Dr()
            where_node = ASTNode('where')
            where_node.add_child(t_node)
            where_node.add_child(dr_node)
            return where_node
        return t_node
    
    # Tuple Expressions
    def parse_T(self):
        """Parse T production"""
        ta_nodes = [self.parse_Ta()]
        
        while self.check(TokenType.PUNCTUATION, ','):
            self.match(TokenType.PUNCTUATION, ',')
            ta_nodes.append(self.parse_Ta())
        
        if len(ta_nodes) > 1:
            tau_node = ASTNode('tau')
            for node in ta_nodes:
                tau_node.add_child(node)
            return tau_node
        return ta_nodes[0]
    
    def parse_Ta(self):
        """Parse Ta production"""
        tc_node = self.parse_Tc()
        
        while self.check(TokenType.KEYWORD, 'aug'):
            self.match(TokenType.KEYWORD, 'aug')
            aug_node = ASTNode('aug')
            aug_node.add_child(tc_node)
            aug_node.add_child(self.parse_Tc())
            tc_node = aug_node
        
        return tc_node
    
    def parse_Tc(self):
        """Parse Tc production"""
        b_node = self.parse_B()
        
        if self.check(TokenType.OPERATOR, '->'):
            self.match(TokenType.OPERATOR, '->')
            tc1_node = self.parse_Tc()
            self.match(TokenType.OPERATOR, '|')
            tc2_node = self.parse_Tc()
            arrow_node = ASTNode('->')
            arrow_node.add_child(b_node)
            arrow_node.add_child(tc1_node)
            arrow_node.add_child(tc2_node)
            return arrow_node
        
        return b_node
    
    # Boolean Expressions
    def parse_B(self):
        """Parse B production"""
        bt_node = self.parse_Bt()
        
        while self.check(TokenType.KEYWORD, 'or'):
            self.match(TokenType.KEYWORD, 'or')
            or_node = ASTNode('or')
            or_node.add_child(bt_node)
            or_node.add_child(self.parse_Bt())
            bt_node = or_node
        
        return bt_node
    
    def parse_Bt(self):
        """Parse Bt production"""
        bs_node = self.parse_Bs()
        
        while self.check(TokenType.OPERATOR, '&'):
            self.match(TokenType.OPERATOR, '&')
            and_node = ASTNode('&')
            and_node.add_child(bs_node)
            and_node.add_child(self.parse_Bs())
            bs_node = and_node
        
        return bs_node
    
    def parse_Bs(self):
        """Parse Bs production"""
        if self.check(TokenType.KEYWORD, 'not'):
            self.match(TokenType.KEYWORD, 'not')
            not_node = ASTNode('not')
            not_node.add_child(self.parse_Bp())
            return not_node
        
        return self.parse_Bp()
    
    def parse_Bp(self):
        """Parse Bp production"""
        a_node = self.parse_A()
        
        if self.check(TokenType.KEYWORD, 'gr') or self.check(TokenType.OPERATOR, '>'):
            if self.check(TokenType.KEYWORD, 'gr'):
                self.match(TokenType.KEYWORD, 'gr')
            else:
                self.match(TokenType.OPERATOR, '>')
            gr_node = ASTNode('gr')
            gr_node.add_child(a_node)
            gr_node.add_child(self.parse_A())
            return gr_node
        
        elif self.check(TokenType.KEYWORD, 'ge') or self.check(TokenType.OPERATOR, '>='):
            if self.check(TokenType.KEYWORD, 'ge'):
                self.match(TokenType.KEYWORD, 'ge')
            else:
                self.match(TokenType.OPERATOR, '>=')
            ge_node = ASTNode('ge')
            ge_node.add_child(a_node)
            ge_node.add_child(self.parse_A())
            return ge_node
        
        elif self.check(TokenType.KEYWORD, 'ls') or self.check(TokenType.OPERATOR, '<'):
            if self.check(TokenType.KEYWORD, 'ls'):
                self.match(TokenType.KEYWORD, 'ls')
            else:
                self.match(TokenType.OPERATOR, '<')
            ls_node = ASTNode('ls')
            ls_node.add_child(a_node)
            ls_node.add_child(self.parse_A())
            return ls_node
        
        elif self.check(TokenType.KEYWORD, 'le') or self.check(TokenType.OPERATOR, '<='):
            if self.check(TokenType.KEYWORD, 'le'):
                self.match(TokenType.KEYWORD, 'le')
            else:
                self.match(TokenType.OPERATOR, '<=')
            le_node = ASTNode('le')
            le_node.add_child(a_node)
            le_node.add_child(self.parse_A())
            return le_node
        
        elif self.check(TokenType.KEYWORD, 'eq'):
            self.match(TokenType.KEYWORD, 'eq')
            eq_node = ASTNode('eq')
            eq_node.add_child(a_node)
            eq_node.add_child(self.parse_A())
            return eq_node
        
        elif self.check(TokenType.KEYWORD, 'ne'):
            self.match(TokenType.KEYWORD, 'ne')
            ne_node = ASTNode('ne')
            ne_node.add_child(a_node)
            ne_node.add_child(self.parse_A())
            return ne_node
        
        return a_node
    
    # Arithmetic Expressions
    def parse_A(self):
        """Parse A production"""
        if self.check(TokenType.OPERATOR, '+'):
            self.match(TokenType.OPERATOR, '+')
            return self.parse_At()
        
        elif self.check(TokenType.OPERATOR, '-'):
            self.match(TokenType.OPERATOR, '-')
            neg_node = ASTNode('neg')
            neg_node.add_child(self.parse_At())
            return neg_node
        
        at_node = self.parse_At()
        
        while self.check(TokenType.OPERATOR, '+') or self.check(TokenType.OPERATOR, '-'):
            op = self.current_token.value
            self.consume()
            op_node = ASTNode(op)
            op_node.add_child(at_node)
            op_node.add_child(self.parse_At())
            at_node = op_node
        
        return at_node
    
    def parse_At(self):
        """Parse At production"""
        af_node = self.parse_Af()
        
        while self.check(TokenType.OPERATOR, '*') or self.check(TokenType.OPERATOR, '/'):
            op = self.current_token.value
            self.consume()
            op_node = ASTNode(op)
            op_node.add_child(af_node)
            op_node.add_child(self.parse_Af())
            af_node = op_node
        
        return af_node
    
    def parse_Af(self):
        """Parse Af production"""
        ap_node = self.parse_Ap()
        
        if self.check(TokenType.OPERATOR, '**'):
            self.match(TokenType.OPERATOR, '**')
            exp_node = ASTNode('**')
            exp_node.add_child(ap_node)
            exp_node.add_child(self.parse_Af())
            return exp_node
        
        return ap_node
    
    def parse_Ap(self):
        """Parse Ap production"""
        r_node = self.parse_R()
        
        while self.check(TokenType.OPERATOR, '@'):
            self.match(TokenType.OPERATOR, '@')
            if not self.check(TokenType.IDENTIFIER):
                raise SyntaxError(f"Expected IDENTIFIER after '@', but found {self.current_token.type.name}: {self.current_token.value}")
            id_token = self.match(TokenType.IDENTIFIER)
            at_node = ASTNode('@')
            at_node.add_child(r_node)
            id_node = ASTNode('identifier', id_token.value)
            at_node.add_child(id_node)
            next_r_node = self.parse_R()
            at_node.add_child(next_r_node)
            r_node = at_node
        
        return r_node
    
    # Rators And Rands
    def parse_R(self):
        """Parse R production"""
        rn_node = self.parse_Rn()
        
        while (self.check(TokenType.IDENTIFIER) or 
               self.check(TokenType.INTEGER) or 
               self.check(TokenType.STRING) or 
               self.check(TokenType.KEYWORD, 'true') or 
               self.check(TokenType.KEYWORD, 'false') or 
               self.check(TokenType.KEYWORD, 'nil') or 
               self.check(TokenType.KEYWORD, 'dummy') or 
               self.check(TokenType.PUNCTUATION, '(')):
            gamma_node = ASTNode('gamma')
            gamma_node.add_child(rn_node)
            gamma_node.add_child(self.parse_Rn())
            rn_node = gamma_node
        
        return rn_node
    
    def parse_Rn(self):
        """Parse Rn production"""
        if self.check(TokenType.IDENTIFIER):
            id_token = self.match(TokenType.IDENTIFIER)
            return ASTNode(id_token.value)
        
        elif self.check(TokenType.INTEGER):
            int_token = self.match(TokenType.INTEGER)
            return ASTNode(int_token.value)
        
        elif self.check(TokenType.STRING):
            str_token = self.match(TokenType.STRING)
            # Remove the surrounding quotes from string literal
            string_value = str_token.value[1:-1]
            return ASTNode(f'"{string_value}"')
        
        elif self.check(TokenType.KEYWORD, 'true'):
            self.match(TokenType.KEYWORD, 'true')
            return ASTNode('true')
        
        elif self.check(TokenType.KEYWORD, 'false'):
            self.match(TokenType.KEYWORD, 'false')
            return ASTNode('false')
        
        elif self.check(TokenType.KEYWORD, 'nil'):
            self.match(TokenType.KEYWORD, 'nil')
            return ASTNode('nil')
        
        elif self.check(TokenType.KEYWORD, 'dummy'):
            self.match(TokenType.KEYWORD, 'dummy')
            return ASTNode('dummy')
        
        elif self.check(TokenType.PUNCTUATION, '('):
            self.match(TokenType.PUNCTUATION, '(')
            e_node = self.parse_E()
            self.match(TokenType.PUNCTUATION, ')')
            return e_node
        
        else:
            raise SyntaxError(f"Unexpected token in Rn: {self.current_token.type.name}: {self.current_token.value}")
    
    # Definitions
    def parse_D(self):
        """Parse D production"""
        da_node = self.parse_Da()
        
        if self.check(TokenType.KEYWORD, 'within'):
            self.match(TokenType.KEYWORD, 'within')
            d_node = self.parse_D()
            within_node = ASTNode('within')
            within_node.add_child(da_node)
            within_node.add_child(d_node)
            return within_node
        
        return da_node
    
    def parse_Da(self):
        """Parse Da production"""
        dr_nodes = [self.parse_Dr()]
        
        while self.check(TokenType.KEYWORD, 'and'):
            self.match(TokenType.KEYWORD, 'and')
            dr_nodes.append(self.parse_Dr())
        
        if len(dr_nodes) > 1:
            and_node = ASTNode('and')
            for node in dr_nodes:
                and_node.add_child(node)
            return and_node
        
        return dr_nodes[0]
    
    def parse_Dr(self):
        """Parse Dr production"""
        if self.check(TokenType.KEYWORD, 'rec'):
            self.match(TokenType.KEYWORD, 'rec')
            db_node = self.parse_Db()
            rec_node = ASTNode('rec')
            rec_node.add_child(db_node)
            return rec_node
        
        return self.parse_Db()
    
    def parse_Db(self):
        """Parse Db production"""
        if self.check(TokenType.IDENTIFIER):
            # Check if this is a function definition (fcn_form)
            saved_index = self.current_token_index
            id_token = self.match(TokenType.IDENTIFIER)
            
            # Collect variable bindings if any
            vb_nodes = []
            while self.check(TokenType.IDENTIFIER) or self.check(TokenType.PUNCTUATION, '('):
                vb_nodes.append(self.parse_Vb())
            
            if self.check(TokenType.OPERATOR, '=') and vb_nodes:
                # This is a function definition
                self.match(TokenType.OPERATOR, '=')
                e_node = self.parse_E()
                
                fcn_node = ASTNode('fcn_form')
                id_node = ASTNode('identifier', id_token.value)
                fcn_node.add_child(id_node)
                
                for vb_node in vb_nodes:
                    fcn_node.add_child(vb_node)
                
                fcn_node.add_child(e_node)
                return fcn_node
            else:
                # Reset and try as a regular variable binding
                self.current_token_index = saved_index
                self.current_token = self.tokens[self.current_token_index]
        
        if self.check(TokenType.PUNCTUATION, '('):
            self.match(TokenType.PUNCTUATION, '(')
            d_node = self.parse_D()
            self.match(TokenType.PUNCTUATION, ')')
            return d_node
        
        # Regular variable binding
        vl_node = self.parse_Vl()
        self.match(TokenType.OPERATOR, '=')
        e_node = self.parse_E()
        
        eq_node = ASTNode('=')
        eq_node.add_child(vl_node)
        eq_node.add_child(e_node)
        return eq_node
    
    # Variables
    def parse_Vb(self):
        """Parse Vb production"""
        if self.check(TokenType.IDENTIFIER):
            id_token = self.match(TokenType.IDENTIFIER)
            return ASTNode('identifier', id_token.value)
        
        elif self.check(TokenType.PUNCTUATION, '('):
            self.match(TokenType.PUNCTUATION, '(')
            if self.check(TokenType.PUNCTUATION, ')'):
                self.match(TokenType.PUNCTUATION, ')')
                return ASTNode('()')
            
            vl_node = self.parse_Vl()
            self.match(TokenType.PUNCTUATION, ')')
            return vl_node
        
        else:
            raise SyntaxError(f"Unexpected token in Vb: {self.current_token.type.name}: {self.current_token.value}")
    
    def parse_Vl(self):
        """Parse Vl production"""
        if not self.check(TokenType.IDENTIFIER):
            raise SyntaxError(f"Expected IDENTIFIER in Vl, but found {self.current_token.type.name}: {self.current_token.value}")
        
        id_token = self.match(TokenType.IDENTIFIER)
        id_node = ASTNode('identifier', id_token.value)
        
        if self.check(TokenType.PUNCTUATION, ','):
            id_nodes = [id_node]
            
            while self.check(TokenType.PUNCTUATION, ','):
                self.match(TokenType.PUNCTUATION, ',')
                if not self.check(TokenType.IDENTIFIER):
                    raise SyntaxError(f"Expected IDENTIFIER after ',', but found {self.current_token.type.name}: {self.current_token.value}")
                next_id_token = self.match(TokenType.IDENTIFIER)
                id_nodes.append(ASTNode('identifier', next_id_token.value))
            
            comma_node = ASTNode(',')
            for node in id_nodes:
                comma_node.add_child(node)
            return comma_node
        
        return id_node
'''
def print_ast(ast, indent=0):
    """Print the AST in a readable format"""
    prefix = '  ' * indent
    print(f"{prefix}{ast.type}", end='')
    if ast.value is not None:
        print(f": {ast.value}")
    else:
        print()
    
    for child in ast.children:
        print_ast(child, indent + 1)'''

def parse_rpal_program(code):
    """Parse RPAL program and return the AST"""
    tokens = tokenize(code)
    parser = RPALParser(tokens)
    ast = parser.parse()
    return ast
'''
if __name__ == "__main__":
    # Example RPAL program
    code = """
    let f x = x > 0 -> 'Positive' | 'Negative'
       in print(f(-3))
    """
    
    # Parse and print AST
    ast = parse_rpal_program(code)
    print_ast(ast)'''
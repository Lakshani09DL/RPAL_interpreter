from ast.ast import ASTNode

class Standardizer:
    def standardize(self, node):
        for i, child in enumerate(node.children):
            self.standardize(child)

        match node.type:
            case 'let' if node.children[0].type == '=':
                equal_node, p = node.children
                x, e = equal_node.children
                lambda_node = ASTNode('lambda', children=[x, p])
                node.type = 'gamma'
                node.children = [lambda_node, e]

            case 'where' if node.children[1].type == '=':
                p, equal_node = node.children
                x, e = equal_node.children
                lambda_node = ASTNode('lambda', children=[x, p])
                node.type = 'gamma'
                node.children = [lambda_node, e]

            case 'fcn_form':
                f = node.children[0]
                params = node.children[1:-1]
                e = node.children[-1]
                for p in reversed(params):
                    e = ASTNode('lambda', children=[p, e])
                node.type = '='
                node.children = [f, e]

            case 'gamma' if len(node.children) > 2:
                expr = node.children.pop()
                current = node
                for _ in range(len(node.children) - 1):
                    arg = node.children.pop(1)
                    lambda_node = ASTNode('lambda', children=[arg])
                    current.children.append(lambda_node)
                    current = lambda_node
                current.children.append(expr)

            case 'within' if node.children[0].type == node.children[1].type == '=':
                eq1, eq2 = node.children
                x1, e1 = eq1.children
                x2, e2 = eq2.children
                lambda_node = ASTNode('lambda', children=[x1, e2])
                gamma_node = ASTNode('gamma', children=[lambda_node, e1])
                node.type = '='
                node.children = [x2, gamma_node]

            case '@':
                e1 = node.children.pop(0)
                n = node.children[0]
                gamma1 = ASTNode('gamma', children=[n, e1])
                node.children[0] = gamma1
                node.type = 'gamma'

            case 'and':
                vars = []
                exprs = []
                for eq in node.children:
                    x, e = eq.children
                    vars.append(x)
                    exprs.append(e)
                comma_node = ASTNode(',', children=vars)
                tau_node = ASTNode('tau', children=exprs)
                node.type = '='
                node.children = [comma_node, tau_node]

            case 'rec':
                eq = node.children[0]
                x, e = eq.children
                lambda_node = ASTNode('lambda', children=[x, e])
                ystar_node = ASTNode('<Y*>')
                gamma_node = ASTNode('gamma', children=[ystar_node, lambda_node])
                node.type = '='
                node.children = [x, gamma_node]

            case 'lambda' if len(node.children) > 2:
                params = node.children[:-1]
                e = node.children[-1]
                for p in reversed(params[1:]):
                    e = ASTNode('lambda', children=[p, e])
                node.children = [params[0], e]

        return node

def standardize(ast_root):
    """
    Top-level function to standardize an AST.
    Can be imported via: from standardizer.standardizer import standardize
    """
    Standardizer().standardize(ast_root)
    return ast_root

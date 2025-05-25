from ast.ast import ASTNode

def standardize(node):
    # Handle compound syntactic sugar nodes BEFORE recursive standardization
    if node.type == "let":
        definition = node.children[0]
        body = node.children[1]

        if definition.type == "=" and len(definition.children) == 2:
            var = definition.children[0]
            expr = definition.children[1]
            lam = ASTNode("lambda", children=[var, body])
            return standardize(ASTNode("gamma", children=[lam, expr]))

        elif definition.type == "fcn_form":
            var = definition.children[0]
            params = definition.children[1:-1]
            expr = definition.children[-1]
            for param in reversed(params):
                expr = ASTNode("lambda", children=[param, expr])
            lam = ASTNode("lambda", children=[var, body])
            return standardize(ASTNode("gamma", children=[lam, expr]))

        else:
            print(f"[Warning] Unexpected 'let' definition node: {definition.type}")
            return node

    elif node.type == "where":
        body = node.children[0]
        definition = node.children[1]
        var = definition.children[0]
        expr = definition.children[1]
        lam = ASTNode("lambda", children=[var, body])
        return standardize(ASTNode("gamma", children=[lam, expr]))

    elif node.type == "within":
        outer = node.children[0]
        inner = node.children[1]
        lam = ASTNode("lambda", children=[inner.children[0], inner.children[1]])
        gamma = ASTNode("gamma", children=[lam, outer.children[1]])
        return standardize(ASTNode("=", children=[outer.children[0], gamma]))

    elif node.type == "rec":
        eq = node.children[0]
        var = eq.children[0]
        expr = eq.children[1]
        lam = ASTNode("lambda", children=[var, expr])
        ystar = ASTNode("Y*")
        gamma = ASTNode("gamma", children=[ystar, lam])
        return standardize(ASTNode("=", children=[var, gamma]))

    elif node.type == "and":
        var_nodes = []
        expr_nodes = []
        for eq_node in node.children:
            var_nodes.append(eq_node.children[0])
            expr_nodes.append(eq_node.children[1])
        tau_vars = ASTNode("tau", children=var_nodes)
        tau_exprs = ASTNode("tau", children=expr_nodes)
        return ASTNode("=", children=[tau_vars, tau_exprs])

    elif node.type == "lambda" and node.children[0].type == "tau":
        expr = node.children[1]
        for param in reversed(node.children[0].children):
            expr = ASTNode("lambda", children=[param, expr])
        return standardize(expr)

    elif node.type == "fcn_form":
        var = node.children[0]
        params = node.children[1:-1]
        expr = node.children[-1]
        for param in reversed(params):
            expr = ASTNode("lambda", children=[param, expr])
        lam = ASTNode("lambda", children=[var, expr])
        return standardize(ASTNode("gamma", children=[lam]))

    elif node.type == "@":
        return standardize(ASTNode("gamma", children=node.children))

    # Base case: standardize children for all other (non-sugar) nodes
    for i in range(len(node.children)):
        node.children[i] = standardize(node.children[i])

    return node

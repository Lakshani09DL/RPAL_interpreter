class Environment:
    def __init__(self,number):
        self.name= f"e_{number}"
        self.variables= {}
        self.parent=None
        self.children=[]
    

    def addVar(self, key, value):
        """Add or update a variable in the current environment."""
        if not isinstance(key, str):
            raise ValueError("Variable key must be a string")
        self.variables[key] = value
    
    def addParent(self, parent):
        """Set the parent environment."""
        self.parent = parent

    def addChild(self, child):
        """Add a child environment and inherit variables from parent."""
        self.children.append(child)
        child.variables.update(self.variables)
    
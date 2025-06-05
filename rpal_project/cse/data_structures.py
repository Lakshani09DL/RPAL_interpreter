#Represents lambda expressions with bound variables
class Lambda:
    def __init__(self, number):
        self.number = number
        self.boundedVar = None
        self.environment = None
    def addEnvironment(self, environment):
        self.environment = environment

# Tuple construction handling
class Tau:
    def __init__(self, number):
        self.number = number
        
# Handle -> nodes
class Condition:
    def __init__(self, number):
        self.number = number


class YStar:
    def __init__(self, number):
        self.number = number
        self.boundedVar = None
        self.environment = None 
        
class Stack:
    def __init__(self):
        self.stack = []      
    
    def __getitem__(self, index):
        return self.stack[index]
    
    def __reversed__(self):
        return reversed(self.stack)
    
    def __setitem__(self, index, value):
        self.stack[index] = value
        
    
    # Returns the size of the stack.
    def size(self):
        return len(self.stack)
    
    def push(self, item):
        self.stack.append(item)
    def pop(self):
        if not self.Empty():
            return self.stack.pop()

    
    def Empty(self):
        return len(self.stack) == 0    
       
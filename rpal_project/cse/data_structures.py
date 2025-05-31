class Lambda:
    def __init__(self, number):
        self.number = number
        self.boundedVari = None
        self.environment = None
    def addEnvironment(self, environment):
        self.environment = environment
class Tau:
    def __init__(self, number):
        self.number = number
        
class Condition:
    def __init__(self, number):
        self.number = number

class YStar:
    def __init__(self, number):
        self.number = number
        self.boundedVari = None
        self.environment = None 
        
class Stack:
    def __init__(self, type):
        self.type = type
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

    # Check whether the stack is empty.
    def Empty(self):
        return len(self.stack) == 0    
       
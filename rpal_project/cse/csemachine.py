from ast.ast import ASTNode
from cse.environment import Environment
from cse.data_structures import *


control = []
controlStruc = []
count = 0
environments = [Environment(0)]
stack = Stack()                        
print_present = False
currentEnv= 0
builtInFunctions = ["Order", "Print", "print", "Conc", "Stern", "Stem", "Isinteger", "Istruthvalue", "Isstring", "Istuple", "Isfunction", "ItoS"]


def buildControlStructure(root_node, index):
    global count

    # Ensure controlStruc has enough sublists up to index
    for _ in range(len(controlStruc), index + 1):
        controlStruc.append([])

    match root_node.type:
        case "lambda":
            count += 1
            lambda_node = root_node.children[0]

            new_lambda = Lambda(count)

            if lambda_node.type == ",":
                bounded_vars = []
                for arg_node in lambda_node.children:
                    bounded_vars.append(arg_node.type[4:-1])
                new_lambda.boundedVar = ",".join(bounded_vars)
            else:
                new_lambda.boundedVar = lambda_node.type[4:-1]

            controlStruc[index].append(new_lambda)

            for i in range(1, len(root_node.children)):
                buildControlStructure(root_node.children[i], count)
        case "tau":
            tau_size = len(root_node.children)
            tau_obj = Tau(tau_size)
            controlStruc[index].append(tau_obj)
            for tau_child in root_node.children:
                buildControlStructure(tau_child, index)
        case "->":
            count += 1
            cond1 = Condition(count)
            controlStruc[index].append(cond1)
            buildControlStructure(root_node.children[1], count)

            count += 1
            cond2 = Condition(count)
            controlStruc[index].append(cond2)
            buildControlStructure(root_node.children[2], count)

            controlStruc[index].append("beta")
            buildControlStructure(root_node.children[0], index)


        case _:
            controlStruc[index].append(root_node.type)
            for general_child in root_node.children:
                buildControlStructure(general_child, index)

def parse_token(token_name):
    trimmed_name = token_name[1:-1]
    parts = trimmed_name.split(":")

    if len(parts) == 1:
        value = parts[0]
    else:
        data_type, value = parts[0], parts[1]

        match data_type:
            case "INT":
                return int(value)

            case "ID":
                if value in builtInFunctions:
                    return value
                try:
                    return environments[currentEnv].variables[value]
                except KeyError:
                    print("Undeclared Identifier: " + value)
                    exit(1)

            case "STR":
                return value


    
    match value:
        case "Y*":
            return "Y*"
        case "true":
            return True
        case "false":
            return False
        case "nil":
            return ()
        case _:
            return value


def convert_value(value):
    match value:
        case "Y*":
            return "Y*"
        case "true":
            return True
        case "false":
            return False
        case "nil":
            return ()
        case _:
            return value

def built(function, argument):
    global print_present

    match function:
        case "Order":
            stack.push(len(argument))

        case "Print" | "print":
            print_present = True
            if isinstance(argument, str):
                argument = argument.replace("\\n", "\n").replace("\\t", "\t")
            stack.push(argument)

        case "Conc":
            stack_latter = stack.pop()
            control.pop()
            stack.push(argument + stack_latter)

        case "Stern":
            stack.push(argument[1:])

        case "Stem":
            stack.push(argument[0])

        case "Isinteger":
            stack.push(isinstance(argument, int))

        case "Istruthvalue":
            stack.push(isinstance(argument, bool))

        case "Isstring":
            stack.push(isinstance(argument, str))

        case "Istuple":
            stack.push(isinstance(argument, tuple))

        case "Isfunction":
            return argument in builtInFunctions

        case "ItoS":
            if isinstance(argument, int):
                stack.push(str(argument))
            else:
                print("Error: ItoS function can only accept integers.")
                exit()


def ApplyRules():
    uop = ["neg", "not"]
    op = ["+", "-", "*", "/", "**", "gr", "ge", "ls", "le", "eq", "ne", "or", "&", "aug"]
    

    global control
    global currentEnv

    while(len(control) > 0):
     
        latter = control.pop()

        # Rule 1
        if type(latter) == str and (latter[-1] == ">" and latter[0] == "<" ):
            stack.push(parse_token(latter))
        

    

        # Rule 2
        elif type(latter) == Lambda:
            tempary = Lambda(latter.number)
            tempary.boundedVar = latter.boundedVar
            tempary.addEnvironment(currentEnv)
            stack.push(tempary)

        # Rule 4
        elif (latter == "gamma"):
            stack_latter_1 = stack.pop()
            stack_latter_2 = stack.pop()

            match stack_latter_1:
                # Rule 11: If it's a Lambda
                case Lambda():

                    boundedVar = stack_latter_1.boundedVar
                    lambda_number = stack_latter_1.number
                    parent_environment_number = stack_latter_1.environment
                    currentEnv = len(environments)
                    
                    parent = environments[parent_environment_number]
                    child = Environment(currentEnv)
                    child.addParent(parent)
                    parent.addChild(child)
                    environments.append(child)

                    # Rule 11: Binding variables
                    variablesL = boundedVar.split(",")

                    if len(variablesL) > 1:
                        i = 0
                        while i < len(variablesL):
                            child.addVar(variablesL[i], stack_latter_2[i])
                            i += 1
                    else:
                        child.addVar(boundedVar, stack_latter_2)

                    stack.push(child.name)
                    control.append(child.name)
                    control += controlStruc[lambda_number]

                # Rule 10: If it's a tuple
                case tuple():
                    stack.push(stack_latter_1[stack_latter_2 - 1])

                # Rule 12: If it's "Y*"
                case "Y*":
                    tempary = YStar(stack_latter_2.number)
                    tempary.boundedVar = stack_latter_2.boundedVar
                    tempary.environment = stack_latter_2.environment
                    stack.push(tempary)

                # Rule 13: If it's a YStar instance
                case YStar():
                    tempary = Lambda(stack_latter_1.number)
                    tempary.boundedVar = stack_latter_1.boundedVar
                    tempary.environment = stack_latter_1.environment
                    
                    control.append("gamma")
                    control.append("gamma")
                    stack.push(stack_latter_2)
                    stack.push(stack_latter_1)
                    stack.push(tempary)

                # Built-in functions
                case _ if stack_latter_1 in builtInFunctions:
                    built(stack_latter_1, stack_latter_2)

                        
        # Rule 5
        elif type(latter) == str and (latter[0:2] == "e_"):
            stack_latter = stack.pop()
            stack.pop()
            
            if currentEnv != 0:
                for element in reversed(stack):
                    match element:
                        case str() if element.startswith("e_"):
                            currentEnv = int(element[2:])
                            break

            stack.push(stack_latter)

        # Rule 6
        elif (latter in op):
            rand_1 = stack.pop()
            rand_2 = stack.pop()
            print("DEBUG: rand_1 =", rand_1, "| type:", type(rand_1))
            print("DEBUG: rand_2 =", rand_2, "| type:", type(rand_2))

            match latter:
                case "+":
                    stack.push(rand_1 + rand_2)
                case "-":
                    stack.push(rand_1 - rand_2)
                case "*":
                    stack.push(rand_1 * rand_2)
                case "/":
                    stack.push(rand_1 // rand_2)
                case "**":
                    stack.push(rand_1 ** rand_2)
                case "gr":
                    stack.push(rand_1 > rand_2)
                case "ge":
                    stack.push(rand_1 >= rand_2)
                case "ls":
                    stack.push(rand_1 < rand_2)
                case "le":
                    stack.push(rand_1 <= rand_2)
                case "eq":
                    stack.push(rand_1 == rand_2)
                case "ne":
                    stack.push(rand_1 != rand_2)
                case "or":
                    stack.push(rand_1 or rand_2)
                case "&":
                    stack.push(rand_1 and rand_2)
                case "aug":
                    if isinstance(rand_2, tuple):
                        stack.push(rand_1 + rand_2)
                    else:
                        stack.push(rand_1 + (rand_2,))


        # Rule 7
        elif (latter in uop):
            rand = stack.pop()
            match latter:
                case "not":
                    stack.push(not rand)
                case "neg":
                    stack.push(-rand)


        # Rule 8
        elif (latter == "beta"):
            B = stack.pop()
            else_part = control.pop()
            then_part = control.pop()
            match B:
                case True:
                    control += controlStruc[then_part.number]
                case False:
                    control += controlStruc[else_part.number]

        # Rule 9
        elif type(latter) == Tau:
            n = latter.number
            tau_list = []
            i = 0
            while i < n:
                tau_list.append(stack.pop())
                i += 1

            tau_tuple = tuple(tau_list)
            stack.push(tau_tuple)

        elif (latter == "Y*"):
            stack.push(latter)

    # Lambda expression becomes a lambda closure when its environment is determined.
    if type(stack[0]) == Lambda:
        stack[0] = "[lambda closure: " + str(stack[0].boundedVar) + ": " + str(stack[0].number) + "]"
         
    if type(stack[0]) == tuple:          
         
        i = 0
        while i < len(stack[0]):
            if type(stack[0][i]) == bool:
                stack[0] = list(stack[0])
                stack[0][i] = str(stack[0][i]).lower()
                stack[0] = tuple(stack[0])
            i += 1

                
          
        match len(stack[0]):
            case 1:
                stack[0] = "(" + str(stack[0][0]) + ")"
            case _:
                if any(isinstance(element, str) for element in stack[0]):
                    tempary = "("
                    i = 0
                    while i < len(stack[0]):
                        tempary += str(stack[0][i]) + ", "
                        i += 1
                    tempary = tempary[:-2] + ")"
                    stack[0] = tempary

                
    # The rpal.exe program prints the boolean values in lowercase. Our code must emulate this behaviour.    
    if stack[0] == True or stack[0] == False:
        stack[0] = str(stack[0]).lower()


def print_control_structures(controlStruc):
    for i, cs in enumerate(controlStruc):
        print(f"\nControl Structure [{i}]:")
        for item in cs:
            if isinstance(item, Lambda):
                print(f"  lambda {item.boundedVar} -> {item.number}")
            elif isinstance(item, Tau):
                print(f"  tau({item.size})")
            elif isinstance(item, Condition):
                print(f"  condition {item.number}")
            else:
                print(f"  {item}")

def Result(standardized_tree):
    global control
    buildControlStructure(standardized_tree, 0)
    print_control_structures(controlStruc)
    control.append(environments[0].name)
    control += controlStruc[0]
    
    ApplyRules()
    stack.push(environments[0].name)

    if print_present:
        return stack[0]
import re

# حافظه برای ذخیره متغیرها، توابع، کلاس‌ها و ماژول‌ها
variables = {}
functions = {}
classes = {}
modules = {}

# ارزیابی عبارات
def evaluate(expression, local_vars={}):
    try:
        if isinstance(expression, str):
            # بررسی رشته
            if expression.startswith('"') and expression.endswith('"'):
                return expression[1:-1]
            # ارزیابی متغیرها
            if expression in local_vars:
                return local_vars[expression]
            if expression in variables:
                return variables[expression]
        # ارزیابی عبارات ریاضی
        return eval(expression, {}, {**variables, **local_vars})
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {expression} ({e})")

# اجرای دستور 'say'
def execute_say(command, local_vars):
    match = re.match(r'say\s+(.+)', command)
    if match:
        value = evaluate(match.group(1), local_vars)
        print(value)
    else:
        raise SyntaxError(f"Invalid syntax in 'say': {command}")

# اجرای دستور 'set'
def execute_set(command, local_vars):
    match = re.match(r'set\s+(\w+)\s*=\s*(.+)', command)
    if match:
        var_name = match.group(1)
        value = evaluate(match.group(2), local_vars)
        variables[var_name] = value
    else:
        raise SyntaxError(f"Invalid syntax in 'set': {command}")

# اجرای حلقه 'repeat'
def execute_repeat(command, local_vars):
    match = re.match(r'repeat\s+(\d+)\s*\{\s*(.+)\s*\}', command)
    if match:
        count = int(match.group(1))
        body = match.group(2)
        for _ in range(count):
            interpret(body, local_vars)
    else:
        raise SyntaxError(f"Invalid syntax in 'repeat': {command}")

# اجرای حلقه 'for'
def execute_for(command, local_vars):
    match = re.match(r'for\s+(\w+)\s+in\s+range\((.+)\)\s*\{\s*(.+)\s*\}', command)
    if match:
        var_name = match.group(1)
        range_expr = match.group(2)
        body = match.group(3)
        start, end = map(int, range_expr.split(','))
        for i in range(start, end):
            local_vars[var_name] = i
            interpret(body, local_vars)
    else:
        raise SyntaxError(f"Invalid syntax in 'for': {command}")

# اجرای حلقه 'while'
def execute_while(command, local_vars):
    match = re.match(r'while\s+\((.+)\)\s*\{\s*(.+)\s*\}', command)
    if match:
        condition = match.group(1)
        body = match.group(2)
        while evaluate(condition, local_vars):
            interpret(body, local_vars)
    else:
        raise SyntaxError(f"Invalid syntax in 'while': {command}")

# اجرای عبارت 'if'
def execute_if(command, local_vars):
    match = re.match(r'if\s+\((.+)\)\s*\{\s*(.+)\s*\}\s*(else\s*\{\s*(.+)\s*\})?', command)
    if match:
        condition = evaluate(match.group(1), local_vars)
        if condition:
            interpret(match.group(2), local_vars)
        elif match.group(4):
            interpret(match.group(4), local_vars)
    else:
        raise SyntaxError(f"Invalid syntax in 'if': {command}")

# اجرای تابع 'def'
def execute_def(command):
    match = re.match(r'def\s+(\w+)\((.*?)\)\s*\{\s*(.+)\s*\}', command)
    if match:
        func_name = match.group(1)
        params = match.group(2).split(',')
        body = match.group(3)
        functions[func_name] = (params, body)
    else:
        raise SyntaxError(f"Invalid syntax in 'def': {command}")

# اجرای فراخوانی تابع
def execute_call(command, local_vars):
    match = re.match(r'(\w+)\((.*?)\)', command)
    if match:
        func_name = match.group(1)
        args = match.group(2).split(',')
        if func_name in functions:
            params, body = functions[func_name]
            if len(params) != len(args):
                raise ValueError(f"Function {func_name} expects {len(params)} arguments, got {len(args)}")
            local_vars = {param.strip(): evaluate(arg.strip(), local_vars) for param, arg in zip(params, args)}
            interpret(body, local_vars)
        else:
            raise NameError(f"Function {func_name} is not defined")
    else:
        raise SyntaxError(f"Invalid syntax in function call: {command}")

# اجرای کلاس 'class'
def execute_class(command):
    match = re.match(r'class\s+(\w+)\s*\{\s*(.+)\}', command)
    if match:
        class_name = match.group(1)
        body = match.group(2)
        classes[class_name] = body
    else:
        raise SyntaxError(f"Invalid syntax in 'class': {command}")

# اجرای ایجاد شیء
def execute_new(command, local_vars):
    match = re.match(r'new\s+(\w+)\((.*?)\)', command)
    if match:
        class_name = match.group(1)
        args = match.group(2).split(',')
        if class_name in classes:
            body = classes[class_name]
            local_vars = {f"self.{param.strip()}": evaluate(arg.strip(), local_vars) for param, arg in zip(args, args)}
            interpret(body, local_vars)
        else:
            raise NameError(f"Class {class_name} is not defined")
    else:
        raise SyntaxError(f"Invalid syntax in 'new': {command}")

# اجرای مدیریت خطاها 'try-except'
def execute_try(command, local_vars):
    match = re.match(r'try\s*\{\s*(.+)\s*\}\s*except\s*\{\s*(.+)\s*\}', command)
    if match:
        try_body = match.group(1)
        except_body = match.group(2)
        try:
            interpret(try_body, local_vars)
        except Exception as e:
            interpret(except_body, local_vars)
    else:
        raise SyntaxError(f"Invalid syntax in 'try-except': {command}")

# اجرای ماژول 'import'
def execute_import(command):
    match = re.match(r'import\s+(\w+)', command)
    if match:
        module_name = match.group(1)
        try:
            module = __import__(module_name)
            modules[module_name] = module
        except ImportError:
            raise ImportError(f"Module {module_name} not found")
    else:
        raise SyntaxError(f"Invalid syntax in 'import': {command}")

# اجرای کد
def interpret(line, local_vars={}):
    line = line.strip()
    if line.startswith("say"):
        execute_say(line, local_vars)
    elif line.startswith("set"):
        execute_set(line, local_vars)
    elif line.startswith("repeat"):
        execute_repeat(line, local_vars)
    elif line.startswith("for"):
        execute_for(line, local_vars)
    elif line.startswith("while"):
        execute_while(line, local_vars)
    elif line.startswith("if"):
        execute_if(line, local_vars)
    elif line.startswith("def"):
        execute_def(line)
    elif line.startswith("class"):
        execute_class(line)
    elif line.startswith("new"):
        execute_new(line, local_vars)
    elif line.startswith("try"):
        execute_try(line, local_vars)
    elif line.startswith("import"):
        execute_import(line)
    else:
        execute_call(line, local_vars)

# رابط کاربری
def run():
    print("Choobin Interpreter - وارد کردن کد:")
    while True:
        try:
            code = input(">>> ")
            if code.lower() == "exit":
                break
            interpret(code)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    run()
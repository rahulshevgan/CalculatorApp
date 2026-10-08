from flask import Flask, render_template_string, request, jsonify
import ast
import operator

app = Flask(__name__)

# Safe math expression evaluator using AST
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval(expr):
    """Safely evaluates a basic mathematical string expression."""
    try:
        node = ast.parse(expr, mode='eval').body
        
        def _eval(node):
            if isinstance(node, ast.Num):  # Python < 3.8 back-compat
                return node.n
            elif isinstance(node, ast.Constant):  # Python >= 3.8
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("Unsupported constant type")
            elif isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                op_type = type(node.op)
                if op_type in ALLOWED_OPERATORS:
                    return ALLOWED_OPERATORS[op_type](left, right)
                raise ValueError("Unsupported operator")
            elif isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                op_type = type(node.op)
                if op_type in ALLOWED_OPERATORS:
                    return ALLOWED_OPERATORS[op_type](operand)
                raise ValueError("Unsupported unary operator")
            else:
                raise ValueError("Unsupported expression")

        return _eval(node)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception:
        return "Error: Invalid Expression"


@app.route('/')
def home():
    # Serve index.html content
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression', '')
    
    if not expression:
        return jsonify({'result': '0'})
    
    result = safe_eval(expression)
    
    # Format float integers cleanly (e.g., 5.0 -> 5)
    if isinstance(result, float) and result.is_integer():
        result = int(result)
        
    return jsonify({'result': str(result)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
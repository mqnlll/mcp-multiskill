import argparse
from mcp_multiskill.parser_to_schema import get_parser_json
def cal(a, b, operation):
    if operation == "+":
        result = a + b
    elif operation == "-":
        result = a - b
    else:
        result = 0
    print(f"Result of {a} {operation} {b}: {result}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple calculator.")
    parser.add_argument("--a", type=float, help="First number")
    parser.add_argument("--b", type=float, help="Second number")
    parser.add_argument("--o", choices=["+", "-"], help="Operation to perform")
    if get_parser_json(parser):
        exit(0)
    
    args = parser.parse_args()
    cal(args.a, args.b, args.o)

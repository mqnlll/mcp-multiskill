def get_parser_json(parser):
    import os
    if os.environ.get("PRINT_MCP_SCHEMA"):
        from argparse_to_json import convert_parser_to_json
        schema_json = convert_parser_to_json(parser)
        import json
        print(json.dumps(schema_json, indent=2, ensure_ascii=False))
        return True
    return False
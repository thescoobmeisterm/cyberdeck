def compile_rules(rules):
    compiled = []
    for r in rules:
        expr = r["if"]
        def make_fn(src):
            return lambda ctx, _src=src: eval(_src, {}, ctx)
        compiled.append({"fn": make_fn(expr), "do": r["do"]})
    return compiled

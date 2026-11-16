# MCP Odoo Shell Tool

This addon exposes the `execute_odoo_code` MCP tool. It executes Python in the
current MCP user's Odoo environment after calling `mcp.shell.sandbox.check_code`.

The initial sandbox policy is deliberately permissive:

- `allowed` is always `true`;
- no policy rules are evaluated;
- unrestricted Python imports and Odoo ORM access are available after approval.

Only users in `base.group_system` can execute the tool. The tool is categorized
as `write`, so an MCP key with read-only scope cannot call it.

Callers should assign their return value to `result`:

```python
partners = env['res.partner'].search([], limit=5)
result = partners.read(['name', 'email'])
```

The response contains the sandbox report, the value of `result`, and `stdout`
when the code uses `print()`.

> Warning: the permissive policy makes this tool remote code execution with the
> permissions of the MCP key owner. Install it only where that behavior is
> explicitly intended.

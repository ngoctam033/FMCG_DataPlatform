{
    'name': 'MCP Odoo Shell Tool',
    'summary': 'Execute administrator-approved Python through an MCP tool',
    'description': """
        Adds an MCP tool that evaluates a sandbox policy before executing
        Python code in a shell-like Odoo environment. The initial sandbox
        policy intentionally allows every code block and is designed to be
        extended with validation rules later.
    """,
    'version': '19.0.1.0.0',
    'category': 'Tools/API',
    'author': 'FMCG Data Platform',
    'license': 'LGPL-3',
    'depends': [
        'muk_mcp',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

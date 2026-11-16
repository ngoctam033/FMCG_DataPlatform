from __future__ import annotations

import json

from odoo.exceptions import AccessError
from odoo.tests import common, tagged
from odoo.tests.common import new_test_user

from odoo.addons.muk_mcp.core.registry import invalidate_registry_cache


@tagged('post_install', '-at_install')
class TestMCPShellTool(common.TransactionCase):
    """Cover sandbox approval and shell-like MCP execution."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        invalidate_registry_cache(cls.env)

    @classmethod
    def tearDownClass(cls) -> None:
        invalidate_registry_cache(cls.env)
        super().tearDownClass()

    def _call(self, code: str) -> dict:
        text, _info = self.env['muk_mcp.tool']._call(
            'execute_odoo_code',
            {'code': code},
            self.env,
        )
        return json.loads(text)

    def test_tool_is_registered_as_mcp_write_tool(self):
        tools = self.env['muk_mcp.tool'].get_tools(registry='mcp')
        tool = next(entry for entry in tools if entry['name'] == 'execute_odoo_code')
        self.assertFalse(tool['annotations']['readOnlyHint'])
        self.assertEqual(tool['inputSchema']['required'], ['code'])

    def test_default_sandbox_allows_every_code_block(self):
        report = self.env['mcp.shell.sandbox'].check_code(
            'import os\nresult = os.getcwd()'
        )
        self.assertEqual(report['policy'], 'allow_all')
        self.assertTrue(report['allowed'])
        self.assertEqual(report['rules_checked'], 0)
        self.assertEqual(report['violations'], [])

    def test_executes_imports_and_reads_odoo_data(self):
        partner = self.env['res.partner'].create({'name': 'MCP Shell Partner'})
        response = self._call(
            'import math\n'
            f"partner = env['res.partner'].browse({partner.id})\n"
            "result = {'sqrt': math.sqrt(81), 'name': partner.name}\n"
        )
        self.assertTrue(response['sandbox']['allowed'])
        self.assertEqual(
            response['result'],
            {'sqrt': 9.0, 'name': 'MCP Shell Partner'},
        )

    def test_returns_print_output(self):
        response = self._call("print('hello', 'odoo')\nresult = uid\n")
        self.assertEqual(response['stdout'], 'hello odoo\n')
        self.assertEqual(response['result'], self.env.uid)

    def test_invalid_python_raises_syntax_error_after_sandbox(self):
        with self.assertRaises(SyntaxError):
            self.env['muk_mcp.mixin']._mcp_execute_odoo_code('if True')

    def test_non_admin_user_cannot_execute_code(self):
        user = new_test_user(
            self.env,
            login='mcp_shell_non_admin',
            groups='base.group_user',
        )
        with self.assertRaises(AccessError):
            self.env(user=user)['muk_mcp.mixin']._mcp_execute_odoo_code(
                'result = 1'
            )


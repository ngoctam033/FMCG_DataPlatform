from __future__ import annotations

import builtins
import io
from typing import Any

import odoo
from odoo import api, models
from odoo.exceptions import AccessError

from odoo.addons.muk_mcp.core.tool import mcp_tool


class MCPMixin(models.AbstractModel):
    """Expose unrestricted, sandbox-gated Python execution over MCP."""

    _inherit = 'muk_mcp.mixin'

    @api.model
    def _mcp_shell_namespace(self) -> tuple[dict[str, Any], io.StringIO]:
        """Build the Odoo-shell namespace and an isolated ``print`` buffer."""
        stdout = io.StringIO()

        def shell_print(
            *values: Any,
            sep: str = ' ',
            end: str = '\n',
            file=None,
            flush: bool = False,
        ) -> None:
            if file is not None:
                builtins.print(
                    *values,
                    sep=sep,
                    end=end,
                    file=file,
                    flush=flush,
                )
                return
            stdout.write(sep.join(str(value) for value in values))
            stdout.write(end)

        shell_builtins = dict(vars(builtins))
        shell_builtins['print'] = shell_print
        return (
            {
                '__builtins__': shell_builtins,
                '__name__': '__mcp_odoo_shell__',
                'odoo': odoo,
                'env': self.env,
                'self': self.env.user,
                'cr': self.env.cr,
                'uid': self.env.uid,
                'context': dict(self.env.context),
            },
            stdout,
        )

    @api.model
    @mcp_tool(
        name='execute_odoo_code',
        description=(
            'Execute Python in an Odoo shell-like environment after the '
            'configured sandbox policy approves it. Available variables are '
            'odoo, env, self, cr, uid, and context. Assign the value returned '
            'to the caller to a variable named result.'
        ),
        input_schema={
            'type': 'object',
            'properties': {
                'code': {
                    'type': 'string',
                    'description': (
                        'Python source code to validate and execute. Assign the '
                        'response value to a variable named result.'
                    ),
                },
            },
            'required': ['code'],
        },
        category='write',
        registry='mcp',
    )
    def _mcp_execute_odoo_code(self, code: str) -> dict[str, Any]:
        """Check, compile, and execute Python as the MCP key owner."""
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(
                self.env._(
                    'Only technical administrators may execute Odoo shell code.'
                )
            )

        sandbox = self.env['mcp.shell.sandbox'].check_code(code)
        if not sandbox.get('allowed'):
            raise AccessError(
                sandbox.get('reason')
                or self.env._('The shell sandbox rejected this code.')
            )

        compiled = compile(code, '<mcp:execute_odoo_code>', 'exec')
        namespace, stdout = self._mcp_shell_namespace()
        exec(compiled, namespace, namespace)  # noqa: S102

        response = {
            'sandbox': sandbox,
            'result': namespace.get('result'),
        }
        if output := stdout.getvalue():
            response['stdout'] = output
        return response


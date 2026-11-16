from __future__ import annotations

from typing import Any

from odoo import api, models


class MCPShellSandbox(models.AbstractModel):
    """Policy hook evaluated before code enters the shell executor."""

    _name = 'mcp.shell.sandbox'
    _description = 'MCP Shell Sandbox Policy'

    @api.model
    def check_code(self, code: str) -> dict[str, Any]:
        """Approve code without applying rules.

        Override this method later to add AST, model, method, import, or other
        policy rules. The executor treats ``allowed`` as the authorization
        decision and will not compile or execute rejected code.
        """
        return {
            'allowed': True,
            'policy': 'allow_all',
            'rules_checked': 0,
            'violations': [],
        }


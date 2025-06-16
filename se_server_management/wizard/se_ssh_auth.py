import base64
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class SshAuth(models.TransientModel):
    _name = "se.ssh.auth"
    _description = "Wizard para configurar certificado ssh en los servers"
    _inherit = "server.util"

    strategy = fields.Selection(
        selection=[("generate", _("Generate")), ("upload", _("Upload"))],
        default="generate",
        string="Strategy"
    )
    user_name = fields.Char(string="User Name", trim=False)
    password = fields.Char(string="Password", trim=False)
    server = fields.Many2one("server.server", string="Server")
    ssh_key = fields.Binary(string="SSH Key")
    ssh_password = fields.Char(string="SSH Passphrase", trim=False)

    def connect(self):
        context = {
            "host": self.server.main_hostname,
            "user_name": self.user_name,
            "password": self.password,
            "port": self.server.ssh_port,
        }

        if self.strategy == "generate":
            _logger.info("Testing connection for server %s", self.server.name)
            private_key, public_key = self.create_blob_ssh_key(
                context, name=self.server.name
            )
            self.server.write({
                'ssh_private_key': private_key,
                'ssh_public_key': public_key,
                'ssh_password': base64.b64encode(self.password.encode()).decode() if self.password else False,
                'ssh_init': True
            })

        elif self.strategy == "upload":
            self.server.write({
                'ssh_private_key': base64.b64decode(self.ssh_key),
                'ssh_password': base64.b64encode(self.ssh_password.encode()).decode() if self.ssh_password else False,
                'ssh_init': False
            })

            self.env["ir.attachment"].create({
                "name": f"SSH Key - {self.server.name}",
                "datas": self.server.ssh_private_key,
                "res_model": "server.server",
                "res_id": self.server.id,
                "type": "binary",
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('SSH configuration updated successfully'),
                'sticky': False,
            }
        }
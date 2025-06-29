# -*- coding: utf-8 -*-
import base64
import logging
from odoo import _, fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SshAuth(models.TransientModel):
    _name = "se.ssh.auth"
    _description = "Wizard para configurar certificado ssh en los servers"
    _inherit = "server.util"

    strategy = fields.Selection(
        selection=[
            ("generate", _("Generate")),
            ("upload", _("Upload")),
            ("master", _("Use Master Key"))
        ],
        default="generate",
    )
    user_name = fields.Char(string="User Name")
    password = fields.Char(string="Password")
    server = fields.Many2one("server.server")
    ssh_key = fields.Binary(string="SSH Key")
    ssh_password = fields.Char(string="SSH Passphrase")

    @api.onchange('strategy')
    def _onchange_strategy(self):
        if self.strategy == 'master':
            self.user_name = self.server.user_name
            self.password = ''

    def connect(self):
        if self.strategy == "master":
            if not self.server.use_master_key:
                raise UserError(_("Master key is not enabled for this server"))
            return {
                'type': 'ir.actions.act_window_close',
                'infos': {'message': _("Configured to use master key")}
            }

        context = {
            "host": self.server.main_hostname,
            "user_name": self.user_name,
            "password": self.password,
            "port": self.server.ssh_port,
        }

        if self.strategy == "generate":
            _logger.info("Generating new SSH key...")
            private_key, public_key = self.create_blob_ssh_key(
                context, name=self.server.name
            )
            self._save_key_config(private_key, public_key)

        elif self.strategy == "upload":
            _logger.info("Uploading SSH key...")
            self._validate_uploaded_key()
            self._save_key_config(
                base64.b64decode(self.ssh_key),
                False
            )

        return {
            'type': 'ir.actions.act_window_close',
            'infos': {'message': _("SSH configuration saved successfully")}
        }

    def _save_key_config(self, private_key, public_key):
        """Guarda la configuración de clave en el servidor"""
        self.server.write({
            'ssh_private_key': private_key,
            'ssh_public_key': public_key,
            'ssh_password': base64.b64encode(
                (self.password or '').encode()
            ).decode(),
            'ssh_init': self.strategy == "generate",
            'use_master_key': False  # Desactiva clave maestra si se usa método manual
        })

        if self.strategy == "upload":
            self.env["ir.attachment"].create({
                "name": self.server.name,
                "datas": base64.b64encode(private_key),
                "res_model": "server.server",
                "res_id": self.server.id,
            })

    def _validate_uploaded_key(self):
        """Valida la clave subida"""
        if not self.ssh_key:
            raise UserError(_("Please upload a valid SSH private key"))

        try:
            import paramiko
            from io import StringIO
            key_str = base64.b64decode(self.ssh_key).decode()
            paramiko.RSAKey.from_private_key(StringIO(key_str), password=self.password or None)
        except Exception as e:
            raise UserError(_("Invalid SSH key: %s") % str(e))

    def action_test_connection(self):
        """Prueba de conexión unificada"""
        if self.strategy == "master":
            return self.server.action_test_master_key()
        else:
            context = {
                "host": self.server.main_hostname,
                "port": self.server.ssh_port,
                "user_name": self.user_name or self.server.user_name,
                "password": self.password,
            }
            if self.strategy == "upload" and self.ssh_key:
                context['sshkey'] = base64.b64decode(self.ssh_key)

            ssh_obj, error = self.login_remote(context)
            if error:
                raise UserError(_("Connection failed: %s") % error)
            else:
                ssh_obj.close()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Test'),
                        'message': _('Connection successful!'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
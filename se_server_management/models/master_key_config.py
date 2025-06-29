# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ServerMasterKeyConfig(models.TransientModel):
    _name = 'server.master.key.config'
    _description = 'Configuración de Clave Maestra SSH'

    master_key_path = fields.Char(
        string='Ruta de Clave Privada',
        required=True,
        default='/home/odoo/.ssh/secure_key'
    )
    server_id = fields.Many2one(
        'server.server',
        string='Servidor'
    )

    def action_save_config(self):
        self.ensure_one()
        if self.server_id:
            self.server_id.update_master_key_path(self.master_key_path)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Configuración Guardada',
                'message': 'La ruta de la clave maestra ha sido actualizada correctamente',
                'type': 'success',
                'sticky': False,
            }
        }
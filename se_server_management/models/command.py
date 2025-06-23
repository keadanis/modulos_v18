# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ServerCommand(models.Model):
    _name = "server.command"
    _description = "Server Command"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    command = fields.Text(required=True)
    server_id = fields.Many2one('server.server', string="Server")

    def action_ejecutar(self):
        for record in self:
            if record.server_id:
                record.server_id.custom_sudo(record.command)
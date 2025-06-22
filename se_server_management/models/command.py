# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CommandCommand(models.Model):
    _name = "server.command"
    _description = "Server Command"
    _order = "sequence, id"  # Ordenamiento más robusto

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        index=True,
        help="Drag and drop to reorder"
    )
    name = fields.Char(
        string="Name",
        required=True,
        index=True  # Mejor búsqueda
    )
    command = fields.Text(
        string="Command",
        required=True,
        help="Comando completo a ejecutar en el servidor"
    )

    server_id = fields.Many2one(
        comodel_name="server.server",
        string="Server",
        ondelete="set null"  # Comportamiento mejorado al eliminar
    )

    @api.model
    def create(self, vals):
        """Override para asegurar valores por defecto"""
        if 'sequence' not in vals:
            max_seq = self.search([], order="sequence desc", limit=1)
            vals['sequence'] = max_seq.sequence + 1 if max_seq else 10
        return super(CommandCommand, self).create(vals)

    def action_ejecutar(self):
        """Ejecuta el comando en el servidor asociado"""
        for record in self:
            if record.server_id:
                record.server_id.custom_sudo(record.command)
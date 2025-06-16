# -*- coding: utf-8 -*-
import os
from odoo import _, api, fields, models
from odoo.exceptions import UserError  # Actualizado para Odoo 18 (except_orm está obsoleto)


class Proftpd(models.AbstractModel):
    _name = 'proftpd'
    _inherit = ['server.util']
    _description = 'ProFTPd Configuration'

    def install_proftpd(self, remote, context):
        connect = "SQLConnectInfo " + context['odoo_db'] + "@" + context['odoo_host'] + " " + context['db_user'] + " " + \
                  context['db_pass'] + "\n"
        sql_path = context['module_path'] + '/data/sql.conf'
        modules_path = context['module_path'] + '/data/modules.conf'
        proftpd_path = context['module_path'] + '/data/proftpd.conf'
        depend_cmd = 'sudo apt-get install proftpd-basic proftpd-mod-pgsql -y'
        restart_cmd = 'sudo systemctl restart proftpd.service'

        with open(sql_path, 'r+') as fd:
            contents = fd.readlines()
            contents[5] = connect
            fd.seek(0)
            fd.writelines(contents)

        with open(proftpd_path, 'r+') as fd:
            contents = fd.readlines()
            contents[14] = 'ServerName      "' + context['host'] + '"\n'
            fd.seek(0)
            fd.writelines(contents)

        if remote:
            ssh_obj = self.login_remote(context)
            # instalando dependencias
            self.execute_on_remote_shell(ssh_obj, depend_cmd)
            # Copiando ficheros
            self.copy_remote_file(ssh_obj, modules_path, '/etc/proftpd/modules.conf')
            self.copy_remote_file(ssh_obj, proftpd_path, '/etc/proftpd/proftpd.conf')
            self.copy_remote_file(ssh_obj, sql_path, '/etc/proftpd/sql.conf')
            # Reiniando el servicio
            self.execute_on_remote_shell(ssh_obj, restart_cmd)
        else:
            # instalando dependencias
            self.execute_on_local_shell(depend_cmd)
            # Copiando ficheros
            self.execute_on_local_shell('sudo cp ' + modules_path + ' /etc/proftpd/modules.conf')
            self.execute_on_local_shell('sudo cp ' + proftpd_path + ' /etc/proftpd/proftpd.conf')
            self.execute_on_local_shell('sudo cp ' + sql_path + ' /etc/proftpd/sql.conf')
            # Reiniando el servicio
            self.execute_on_local_shell(restart_cmd)


class ProftpdUser(models.Model):
    _name = 'proftpd.user'
    _description = 'ProFTPd Virtual User'  # Descripción más clara

    name = fields.Char(string='Name', required=True)
    password = fields.Char(string='Password')
    uid = fields.Integer(string='UID')
    gid = fields.Integer(string='GID')
    homedir = fields.Char(string='Home Directory')
    shell = fields.Char(string='Shell')
    server = fields.Many2one('server.server', string='Server')
    server_name = fields.Char(compute='_compute_server_name', string='Server Name', store=True)

    @api.depends('server')
    def _compute_server_name(self):
        for record in self:
            record.server_name = record.server.main_hostname if record.server else False

    def show_passwd(self):
        self.ensure_one()
        raise UserError(_("Password for user '%s':\n%s") % (self.name, self.password))  # Actualizado a UserError


class ProftpdGroup(models.Model):
    _name = 'proftpd.group'
    _description = 'ProFTPd User Group'

    name = fields.Char(string='Group Name')
    gid = fields.Integer(string='GID')
    members = fields.Char(string='Members')
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"

    is_user_validator = fields.Boolean(string="Est Validateur",compute="_compute_is_user_validator")
    validated = fields.Boolean(string="Demande validé", default=False)

    def _compute_is_user_validator(self):
        for record in self:
            record.is_user_validator = self.env.user.paiement_validator

    def send_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Envoyer demande'),
            'res_model': 'account.move.request',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(self.env.ref('complexe_validation.custom_view_send_payment_request_account_move').id, 'form')],
            'view_id': self.env.ref('complexe_validation.custom_view_send_payment_request_account_move').id,
            'target': 'new',
            'context': self.env.context,
        }

    def new_post_move(self):
        for record in self:
            move_request_id = self.env['account.move.request'].sudo().search([('validator_id','=', self.env.user.id), ('move_id', '=', record.id), ('validated','=', False)], order="id DESC", limit=1)
            if move_request_id:
                record.write({'validated': True})
                move_request_id.sudo().write({'validated': True})
                move_request_id.send_validation_request_mail()

class AccountMoveRequest(models.Model):
    _name = "account.move.request"

    validator_id = fields.Many2one(string="Validateur", comodel_name="res.users", copy=False, domain='[("paiement_validator", "=", True)]')
    move_id = fields.Many2one(string="Facture", comodel_name="account.move", copy=False)
    validated = fields.Boolean(string="Demande Validé", default=False)

    def send_move_req(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        active_id = self.env.context.get('move')
        if active_id:
            move_id = self.env['account.move'].sudo().browse(int(active_id))
            self.sudo().write({'move_id': move_id})
        else:
            move_id = False
        template = self.env.ref("complexe_validation.send_account_move_request_email_template")
        template_values = {
            'email_from': 'pounasatu@gmail.com',
            'email_to': self.validator_id.email,
            'email_cc': False,
            'auto_delete': True,
            'partner_to': self.validator_id.partner_id.id,
            'scheduled_date': False,
        }

        template.write(template_values)
        context = {
            'lang': self.env.user.lang,
            'current_user': self.env.user,
            'move_id': move_id,
            'move_partner_id': move_id.partner_id,
            'base_url': base_url,
        }
        with self.env.cr.savepoint():
            template.with_context(context).send_mail(self.id, force_send=True, raise_exception=True)
            values = template.generate_email(self.id)
        return True

    def send_validation_request_mail(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        template = self.env.ref("complexe_validation.send_validation_move_request_email_template")
        requester = self.create_uid
        template_values = {
            'email_from': 'pounasatu@gmail.com',
            'email_to': requester.email,
            'email_cc': False,
            'auto_delete': True,
            'partner_to': requester.partner_id.id,
            'scheduled_date': False,
        }

        template.write(template_values)
        context = {
            'lang': self.env.user.lang,
            'requester': requester,
            'move_id': self.move_id,
            'base_url': base_url,
        }
        with self.env.cr.savepoint():
            template.with_context(context).send_mail(self.id, force_send=True, raise_exception=True)
            values = template.generate_email(self.id)
        return True
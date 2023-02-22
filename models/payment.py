# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_user_validator = fields.Boolean(string="Est Validateur",compute="_compute_is_user_validator")
    validated = fields.Boolean(string="Demande validé", default=False)

    def _compute_is_user_validator(self):
        for record in self:
            record.is_user_validator = self.env.user.paiement_validator

    def send_paiement_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Envoyer demande'),
            'res_model': 'account.payment.request',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(self.env.ref('complexe_validation.custom_view_send_payment_request').id, 'form')],
            'view_id': self.env.ref('complexe_validation.custom_view_send_payment_request').id,
            'target': 'new',
            'context': self.env.context,
        }

    def new_post(self):
        for record in self:
            payment_request_id = self.env['account.payment.request'].sudo().search([('validator_id','=', self.env.user.id), ('payment_id', '=', record.id), ('validated','=', False)], order="id DESC", limit=1)
            if payment_request_id:
                record.write({'validated': True})
                payment_request_id.sudo().write({'validated': True})
                payment_request_id.send_validation_request_mail()


class AccountPaymentRequest(models.Model):
    _name="account.payment.request"

    validator_id = fields.Many2one(string="Validateur", comodel_name="res.users", copy=False, domain='[("paiement_validator", "=", True)]')
    payment_id = fields.Many2one(string="Payment", comodel_name="account.payment", copy=False)
    validated = fields.Boolean(string="Demande Validé", default=False)

    def send_req(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        active_id = self.env.context.get('active_id')
        if active_id:
            payment_id = self.env['account.payment'].sudo().browse(int(active_id))
            self.sudo().write({'payment_id': payment_id})
        else:
            payment_id = False
        template = self.env.ref("complexe_validation.send_paiement_request_email_template")
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
            'payment_id': payment_id,
            'payment_partner_id': payment_id.partner_id,
            'base_url': base_url,
        }
        with self.env.cr.savepoint():
            template.with_context(context).send_mail(self.id, force_send=True, raise_exception=True)
            values = template.generate_email(self.id)
        return True

    def send_validation_request_mail(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        template = self.env.ref("complexe_validation.send_validation_request_email_template")
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
            'payment_id': self.payment_id,
            'base_url': base_url,
        }
        with self.env.cr.savepoint():
            template.with_context(context).send_mail(self.id, force_send=True, raise_exception=True)
            values = template.generate_email(self.id)
        return True
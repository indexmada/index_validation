# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResUsers(models.Model):
	_inherit = "res.users"

	paiement_validator = fields.Boolean(string="Validateur de paiement")
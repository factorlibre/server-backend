# © 2024 FactorLibre - Aritz Olea <aritz.olea@factorlibre.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, tools
from odoo.osv import expression
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval


class IrRule(models.Model):
    _inherit = "ir.rule"

    and_restriction_for_groups = fields.Boolean(string="AND restriction for groups")

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        res = super()._compute_domain(model_name, mode=mode)
        restriction_domains = []
        if not self.env.su:
            rules = self._get_rules(model_name, mode=mode)
            eval_context = self._eval_context()
            for rule in rules.sudo().filtered(lambda r: r.and_restriction_for_groups):
                dom = (
                    safe_eval(rule.domain_force, eval_context)
                    if rule.domain_force
                    else []
                )
                dom = expression.normalize_domain(dom)
                restriction_domains.append(dom)
        return expression.AND(restriction_domains + [res])

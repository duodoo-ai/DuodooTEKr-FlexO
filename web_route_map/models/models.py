# -*- coding: utf-8 -*-


from odoo import _, api, models
from lxml.builder import E
from odoo.exceptions import UserError


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _get_default_map_view(self):
        view = E.route_map()


        if 'partner_id' in self._fields:
            view.set('res_partner', 'partner_id')
        else:
            raise UserError(_("You need to set a Contact field on this model to use the Map View"))

        # if "latitude" not in self._fields:
        #     raise UserError(_("You need to set the 'latitude' field on this model to use the route map view"))
        # elif "longitude" in self._fields:
        #     raise UserError(_("You need to set the 'longitude' field on this model to use the route map view"))

        return view

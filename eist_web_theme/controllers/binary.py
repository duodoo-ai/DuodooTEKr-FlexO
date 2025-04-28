# -*- coding: utf-8 -*-

import base64
import io
import functools
import logging

try:
    from werkzeug.utils import send_file
except ImportError:
    from odoo.tools._vendor.send_file import send_file


import odoo
import odoo.modules.registry
from odoo import SUPERUSER_ID, _, http
from odoo.addons.base.models.assetsbundle import ANY_UNIQUE
from odoo.exceptions import AccessError, UserError
from odoo.http import request, Response
from odoo.tools import file_open, file_path, replace_exceptions
from odoo.tools.image import image_guess_size_from_field_name
from odoo.tools.mimetypes import guess_mimetype


from odoo.addons.web.controllers.binary import Binary

_logger = logging.getLogger(__name__)


class WebThemeBinary(Binary):
    @http.route(
        [
            "/web/binary/company_square_logo",
            "/company_square_logo",
            "/company_square_logo.png",
        ],
        type="http",
        auth="none",
        cors="*",
    )
    def company_square_logo(self, dbname=None, **kw):
        imgname = "square_logo"
        imgext = ".png"
        dbname = request.db
        uid = (request.session.uid if dbname else None) or odoo.SUPERUSER_ID

        if not dbname:
            response = http.Stream.from_path(
                file_path("eist_web_theme/static/img/square_logo.png")
            ).get_response()
        else:
            try:
                # create an empty registry
                registry = odoo.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    company = int(kw["company"]) if kw and kw.get("company") else False
                    if company:
                        cr.execute(
                            """SELECT square_logo_web, write_date
                                        FROM res_company
                                       WHERE id = %s
                                   """,
                            (company,),
                        )
                    else:
                        cr.execute(
                            """SELECT c.square_logo_web, c.write_date
                                        FROM res_users u
                                   LEFT JOIN res_company c
                                          ON c.id = u.company_id
                                       WHERE u.id = %s
                                   """,
                            (uid,),
                        )
                    row = cr.fetchone()
                    if row and row[0]:
                        image_base64 = base64.b64decode(row[0])
                        image_data = io.BytesIO(image_base64)
                        mimetype = guess_mimetype(image_base64, default="image/png")
                        imgext = "." + mimetype.split("/")[1]
                        if imgext == ".svg+xml":
                            imgext = ".svg"
                        response = send_file(
                            image_data,
                            request.httprequest.environ,
                            download_name=imgname + imgext,
                            mimetype=mimetype,
                            last_modified=row[1],
                            response_class=Response,
                        )
                    else:
                        response = http.Stream.from_path(
                            file_path("eist_web_theme/static/img/square_logo.png")
                        ).get_response()
            except Exception:
                response = http.Stream.from_path(
                    file_path(f"eist_web_theme/static/img/{imgname}{imgext}")
                ).get_response()

        return response

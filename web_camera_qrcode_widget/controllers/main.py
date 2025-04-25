# -*- coding: utf-8 -*-

import odoo.http as http
import os
# import cv2

from base64 import b64decode, b64encode
from odoo.tools.image import image_data_uri, base64_to_image,image_to_base64
from PIL import Image, ImageFont, ImageDraw
from pyzbar.pyzbar import decode
from io import BytesIO
import base64

class WebCameraQrController(http.Controller):
    @http.route(
        [
            "/web/multiple_qrcode_scanner/capture",
        ],
        type="json",
        auth="none",
        cors="*",
        methods=["GET", "POST"],
    )
    def capture_qrcode_cameras(self, **kw):  
        image = base64_to_image(kw["base64_source_str"].split("base64,")[1])
        image_data = decode(image)
        draw = ImageDraw.Draw(image)
        for code in decode(image):
            rect = code.rect
            draw.rectangle(
                (
                    (rect.left, rect.top),
                    (rect.left + rect.width, rect.top + rect.height)
                ),
                outline='#0080ff'
            )
            draw.polygon(code.polygon, outline='#e945ff')
        base64_img = image_to_base64(image, 'PNG')
        # print(image_data)
        return {
            "base64_img": "data:image/png;base64,%s" % base64_img.decode(),
            "image_data": image_data
        }

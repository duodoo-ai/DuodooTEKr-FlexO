# -*- coding: utf-8 -*-

{
    "name": "Web Camera QRCode Widget",
    "author": "RStudio",
    "category": "Hidden",
    "summary": "Odoo Community Edition QR code and barcode Camera widgit.",
    "version": "18.0.0.1",
    "description": """ 
Odoo Community Edition QR code and barcode Camera widgit.
======================================================
Please read the document carefully.
""",
    "depends": ["web", "barcodes",],
    "external_dependencies": {
        "python": [
            # "opencv-contrib-python",
            # "pyzxing",
            "pyzbar",
        ],
    },
    "assets":{
        "web.assets_qweb": [
            "web_camera_qrcode_widget/static/src/**/*.xml",
        ],
        "web.assets_backend":[
            "/web_camera_qrcode_widget/static/src/js/code.js",
            "/web_camera_qrcode_widget/static/src/scss/qr.scss",
        ],
    },
    "images": ["images/main_screenshot.png"],
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "price": 30,
    "currency": "EUR",
    "bootstrap": True, 
}

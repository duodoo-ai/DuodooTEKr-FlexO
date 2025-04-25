==============================================
Web Camera QRCode Widget
==============================================


Note:
----------------------------------------------
* When using the WebRTC API, the browser requires HTTPS. Any page that uses this library should be served via HTTPS.  
* Chrome is recommended.

----



How to install:
----------------------------------------------
1) Click on the menu "Apps".
2) Select "Extra" in the filter popup menu.
3) Enter "Web QRCode Widget" in the search input box.
4) Please install the module "Web QRCode Widget" in the search results.

----

How to use in form view:
----------------------------------------------
* You can directly modify the form view in odoo debug mode.
* You can inherit the view and use position="attributes" to add widget="qr_code" to the field.

**Example1:Modify the form view in debug mode**

::

    <field name="arch" type="xml">
        <form string="View name">
            <field name="barcode" widget="qr_code" />
        </form>
    </field>

**Example2:Inherit the view to add attributes to the field**

::

    <xpath expr="//field[@name='barcode']" position="attributes">
        <attribute name="widget">qr_code</attribute>
    </xpath>

----





Bugs and requirements:
----------------------------------------------

You can send an email to rain.wen@outlook.com to submit bugs and requirements to me.

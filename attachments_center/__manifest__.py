# Copyright (C) 2020-2023 Artem Shurshilov <shurshilov.a@yandex.ru>
# Odoo Proprietary License v1.0

# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).

# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).

# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.

# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
{
    "name": "DMS attachment and document module with directory,tags,export, numbering",
    "summary": " \
DMS \
document module document extension add directory adds directory for ir.attachment model \
export attachment export attachments exports attachments document exports document export \
document export \
attachment and document module with directory and tags document Attchment \
creation directory and folder by model record object models records objects \
security group access control \
document management system dms alfresco similar document number diretory number \
file number file sequence document search file store filestore dms document management system \
dms document document/directories document/directories/directories directory Form View document number \
document sequence document sequence document numbering document directory document folder folder \
directory attachment number attach number document attach number document numbering document number \
number attachment odoo document attachment number filestore file store file number files number \
folder document folders attachment unique number reference unique number \
version control versions control file version control files version files version control \
documents tags documents download documents zip documents numbering documents versions \
",
    "author": "EURO ODOO, Shurshilov Artem",
    "maintainer": "EURO ODOO",
    "website": "https://eurodoo.com",
    "live_test_url": "https://eurodoo.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Document Management",
    "version": "16.10.0.7",
    "license": "OPL-1",
    "price": 13.0,
    "currency": "EUR",
    "images": ["images/preview.png"],
    # any module necessary for this one to work correctly
    "depends": ["base", "web"],
    # always loaded
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/ir_attachment.xml",
        "views/ir_attachment_action.xml",
        "views/menu.xml",
        "views/ir_attachment_tag.xml",
        "views/ir_attachment_category.xml",
        "views/ir_attachment_history.xml",
        "views/res_config_settings_views.xml",
        "data/sequence.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "attachments_center/static/**/*",
        ],
    },
}

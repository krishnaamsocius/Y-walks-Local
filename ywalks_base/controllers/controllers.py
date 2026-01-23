# from odoo import http


# class YwalksBase(http.Controller):
#     @http.route('/ywalks_base/ywalks_base', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ywalks_base/ywalks_base/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ywalks_base.listing', {
#             'root': '/ywalks_base/ywalks_base',
#             'objects': http.request.env['ywalks_base.ywalks_base'].search([]),
#         })

#     @http.route('/ywalks_base/ywalks_base/objects/<model("ywalks_base.ywalks_base"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ywalks_base.object', {
#             'object': obj
#         })


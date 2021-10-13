(function () {
	'use strict';

	frappe.ui.form.on('Branch', {
		refresh: function (frm) {
			if (frm.doc.shopee_shop_id) {
				frm.add_custom_button('Refresh from Shopee', function () {
					frappe.call({
						method: 'shopee_open_api.apis.shop.reload_shop_details_from_shopee',
						args: {
							branch_name: frm.doc.name,
						},
						callback: function (r) {
							frm.refresh();
						},
					});
				});
			}
		},
	});

	frappe.listview_settings['Branch'] = {
		onload: function (listview) {
			this.add_button(['Add from Shopee'], 'warning', function () {
				frappe.call({
					method: 'shopee_open_api.auth.get_authorize_url',
					callback: function (r) {
						var authorizeUrl = r['message'];
						window.open(authorizeUrl, '_self');
					},
				});
			});

			this.add_button(['Remove Shopee Branch'], 'danger', function () {
				frappe.call({
					method: 'shopee_open_api.auth.get_unauthorize_url',
					callback: function (r) {
						var unauthorizeUrl = r['message'];
						window.open(unauthorizeUrl, '_self');
					},
				});
			});
		},

		add_button: function add_button(name, type, action, wrapper_class) {
			if ( wrapper_class === void 0 ) wrapper_class = '.page-actions';

			var button = document.createElement('button');
			button.classList.add('btn', 'btn-' + type, 'btn-sm', 'ml-2');
			button.innerHTML = name;
			button.onclick = action;
			document.querySelector(wrapper_class).prepend(button);
		},
	};

}());
//# sourceMappingURL=branch_modification.js.map

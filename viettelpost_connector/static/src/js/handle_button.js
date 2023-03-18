/** @odoo-module **/

import ListController from 'web.ListController';
import FormController from 'web.FormController';
FormController.include({
    events: Object.assign({}, FormController.prototype.events, {
        'click .o_get_debts': '_onClickGetDebs',
    }),
    init: function () {
        this._super.apply(this, arguments);
    },
   _onClickGetDebs: function (e) {
        e.preventDefault();
        var self = this;
        var state = self.renderer.state;
        var partnerId = state.data.partner_id.data.id;
        var yearOfPaymentPeriod = state.data.year_of_payment_period;
        var monthOfPaymentPeriod = state.data.month_of_payment_period;
        return this._rpc({
            model: 'account.payment.wizard',
            method: 'get_debts',
            kwargs: {
                partnerId: partnerId,
                yearOfPaymentPeriod: yearOfPaymentPeriod,
                monthOfPaymentPeriod: monthOfPaymentPeriod
            }
        }).then(function(result) {
            console.log(self)
            self.renderer.state.data.incurred_customer_debts = new Intl.NumberFormat('vi-VN').format(result.incurred_customer_debts)
            self.renderer.state.data.payment_amount = new Intl.NumberFormat('vi-VN').format(result.payment_amount)
//            var incurredCustomerDebtsInput = $("input[name='incurred_customer_debts']");
//            var paymentAmount = $("input[name='payment_amount']");
//            incurredCustomerDebtsInput.val(new Intl.NumberFormat('vi-VN').format(result.incurred_customer_debts));
//            paymentAmount.val(result.payment_amount);
        });
   }
});

ListController.include({
    events: Object.assign({}, ListController.prototype.events, {
        'click .o_button_sync_province': '_onClickSyncProvince',
        'click .o_button_sync_district': '_onClickSyncDistrict',
        'click .o_button_sync_ward': '_onClickSyncWard',
        'click .o_button_sync_office': '_onClickSyncOffice',
        'click .o_button_sync_service': '_onClickSyncService',
        'click .o_button_sync_extend_service': '_onClickSyncExtendService',
        'click .o_button_sync_store': '_onClickSyncStore',
        'click .o_button_create_store': '_onClickCreateStore',
        'click .o_button_register_payment': '_onClickRegisterPayment',
        'click .o_get_debts': '_onClickGetDebts',
    }),
    _onClickSyncProvince: function (e) {
        var self = this;
        return this._rpc({
            model: 'viettelpost.province',
            method: 'sync_province'
        }).then(function(result) {
            self.do_action(result);
        }).then(function(result) {
            self.do_action({
                'type': 'ir.actions.client',
                'tag': 'reload'
            });
        });
    },
    _onClickSyncDistrict: function (e) {
        var self = this;
        return this._rpc({
            model: 'viettelpost.district',
            method: 'sync_district'
        }).then(function(result) {
            self.do_action(result);
        }).then(function(result) {
            self.do_action({
                'type': 'ir.actions.client',
                'tag': 'reload'
            });
        });
    },
    _onClickSyncWard: function (e) {
        var self = this;
        return this._rpc({
            model: 'viettelpost.ward',
            method: 'sync_ward'
        }).then(function(result) {
            self.do_action(result);
        }).then(function(result) {
            self.do_action({
                'type': 'ir.actions.client',
                'tag': 'reload'
            });
        });
    },
    _onClickSyncService: function (e) {
        var self = this;
        return this._rpc({
            model: 'viettelpost.service',
            method: 'sync_service'
        }).then(function(result) {
            self.do_action(result);
        }).then(function(result) {
            self.do_action({
                'type': 'ir.actions.client',
                'tag': 'reload'
            });
        });
    },
    _onClickSyncOffice: function (e) {
        var self = this;
        return this._rpc({
            model: 'viettelpost.office',
            method: 'sync_office'
        }).then(function(result) {
            self.do_action(result);
        }).then(function(result) {
            self.do_action({
                'type': 'ir.actions.client',
                'tag': 'reload'
            });
        });
    },
    _onClickSyncStore: function (e) {
        var self = this;
        return this._rpc({
            model: 'viettelpost.store',
            method: 'sync_store'
        }).then(function(result) {
            self.do_action(result);
        }).then(function(result) {
            self.do_action({
                'type': 'ir.actions.client',
                'tag': 'reload'
            });
        });
    },
    _onClickCreateStore: function (e) {
        var self = this;
        return this._rpc({
            model: 'create.store.wizard',
            method: 'create_store'
        }).then(function(result) {
            self.do_action(result);
        });
    },
    _onClickSyncExtendService: function (e) {
        var self = this;
        return this._rpc({
            model: 'viettelpost.service',
            method: 'sync_extend_services'
        }).then(function(result) {
            self.do_action(result);
        }).then(function(result) {
            self.do_action({
                'type': 'ir.actions.client',
                'tag': 'reload'
            });
        });
    },
    _onClickRegisterPayment: function (e) {
        var self = this;
        return this._rpc({
            model: 'account.payment.wizard',
            method: 'action_register_payment'
        }).then(function(result) {
            self.do_action(result);
        });
    },
});
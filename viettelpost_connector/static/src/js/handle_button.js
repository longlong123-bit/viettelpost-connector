/** @odoo-module **/

import ListController from "web.ListController";

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
    }
});
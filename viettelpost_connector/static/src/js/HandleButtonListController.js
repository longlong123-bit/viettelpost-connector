/** @odoo-module **/

import { useService } from '@web/core/utils/hooks';
import { ListController } from "@web/views/list/list_controller";

export class HandleButtonListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.actionService = useService('action');
        this.rpc = useService("rpc");
    }
    async onClickSyncProvince() {
        const action = await this.orm.call('vtp.country.province', 'sync_province');
        this.actionService.doAction(action, {
            onClose: () => {
                this.actionService.doAction({
                'type': 'ir.actions.client',
                'tag': 'reload'})
            },
        });
    }
    async onClickSyncDistrict() {
        const action = await this.orm.call('vtp.country.district', 'sync_district');
        this.actionService.doAction(action, {
            onClose: () => {
                this.actionService.doAction({
                'type': 'ir.actions.client',
                'tag': 'reload'})
            },
        });
    }
    async onClickSyncWard() {
        const action = await this.orm.call('vtp.country.ward', 'sync_ward');
        this.actionService.doAction(action, {
            onClose: () => {
                this.actionService.doAction({
                'type': 'ir.actions.client',
                'tag': 'reload'})
            },
        });
    }
    async onClickSyncService() {
        const action = await this.orm.call('viettelpost.service', 'sync_service');
        this.actionService.doAction(action, {
            onClose: () => {
                this.actionService.doAction({
                'type': 'ir.actions.client',
                'tag': 'reload'})
            },
        });
    }
    async onClickSyncOffice() {
        const action = await this.orm.call('viettelpost.office', 'sync_office');
        this.actionService.doAction(action, {
            onClose: () => {
                this.actionService.doAction({
                'type': 'ir.actions.client',
                'tag': 'reload'})
            },
        });
    }
    async onClickSyncStore() {
        const action = await this.orm.call('viettelpost.store', 'sync_store');
        this.actionService.doAction(action, {
            onClose: () => {
                this.actionService.doAction({
                'type': 'ir.actions.client',
                'tag': 'reload'})
            },
        });
    }
    async onClickCreateStore() {
        const action = await this.orm.call('create.store.wizard', 'create_store');
        this.actionService.doAction(action, {
            onClose: () => {
                this.actionService.doAction({
                'type': 'ir.actions.client',
                'tag': 'reload'})
            },
        });
    }
    async onClickSyncExtendService(e) {
        const action = await this.orm.call('viettelpost.service', 'sync_extend_services');
        this.actionService.doAction(action, {
            onClose: () => {
                this.actionService.doAction({
                'type': 'ir.actions.client',
                'tag': 'reload'})
            },
        });
    }
}
console.log("QRScanner Component Loading..."); // 确认文件加载

odoo.define('odoo_maintenance.QRScanner', function (require) {
    "use strict";

    console.log("Component Initialization Started"); // 调试点1

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');
    var ajax = require('web.ajax');
    var _t = core._t;

    // 使用更兼容的Instascan库
    var QRScanner = Widget.extend({
        template: 'QRScannerTemplate',
        jsLibs: [
            '/odoo_maintenance/static/src/js/instascan.min.js'
        ],

        init: function(parent, options) {
            this._super.apply(this, arguments);
            console.log("Scanner Initialized"); // 调试点2
            this.scanner = null;
            this.videoElement = null;
        },

        willStart: function() {
            return Promise.all([
                ajax.loadJS('/odoo_maintenance/static/src/js/instascan.min.js'),
                this._super.apply(this, arguments)
            ]);
        },

        start: function() {
            this._prepareScanner();
            console.log("Scanner Started"); // 调试点3
            this.$('.start-scan').on('click', this.proxy('_onStartScan'));
            return this._super.apply(this, arguments);
        },

        _prepareScanner: function() {
            var self = this;
            this.videoElement = document.createElement('video');
            this.$('.scanner-container').append(this.videoElement);

            this.scanner = new Instascan.Scanner({
                video: this.videoElement,
                mirror: false,
                backgroundScan: true
            });

            this.scanner.addListener('scan', function(content) {
                self._processScanResult(content);
            });
        },

        _processScanResult: function(content) {
            var match = content.match(/EQUIPMENT:(\d+)/);
            if (match) {
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'maintenance.inspection',
                    views: [[false, 'form']],
                    context: {
                        default_equipment_id: parseInt(match[1])
                    }
                });
                this.destroy();
            } else {
                Dialog.alert(this, _t("无效二维码"), _t("请扫描有效的设备二维码"));
            }
        },

        _onStartScan: function() {
            var self = this;
            Instascan.Camera.getCameras().then(function(cameras) {
                if (cameras.length > 0) {
                    self.scanner.start(cameras[0]);
                } else {
                    Dialog.alert(self, _t("摄像头未找到"), _t("请检查设备摄像头权限"));
                }
            }).catch(function(error) {
                Dialog.alert(self, _t("摄像头错误"), error);
            });
        },

        destroy: function() {
            if (this.scanner) {
                this.scanner.stop();
            }
            this._super.apply(this, arguments);
        }
    });

    // 确保组件正确注册到动作注册表
    core.action_registry.add('open_qr_scanner', QRScanner); // ← 名称必须完全一致
    console.log("Registration Completed:",
        core.action_registry.map.has('open_qr_scanner')); // 应输出true

    return QRScanner;
});
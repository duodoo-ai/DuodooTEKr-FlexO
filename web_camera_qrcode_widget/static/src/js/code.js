odoo.define('web.web_camera_qrcode_widget', function (require) {
    "use strict";
    var core = require('web.core');
    var utils = require('web.utils');
    var config = require('web.config');
    var fieldRegistry = require('web.field_registry');
    var FieldChar = require('web.basic_fields').FieldChar;
    var Dialog = require('web.Dialog');
    var _t = core._t;
    var QWeb = core.qweb;
    var WEB_CAMERA_QRCODE_WIDGET_COOKIE = 'web_camera_qrcode_widget_default_camera';
    // var audio = new Audio('/web_camera_qrcode_widget/static/audio/beep.mp3');

    var QRCode = FieldChar.extend({
        template: 'QRCode',
        className: 'o_field_qr_code',
        jsLibs: [
            '/web_camera_qrcode_widget/static/lib/zxing-library/zxing-library.js'
        ],
        init: function (parent) {
            var self = this;
            this._super.apply(this, arguments);
            this.option_need_confirm = true; //需要确认扫码结果，默认为true
            this.option_autoplay = true; //自动启动摄像头，默认为true
            this.option_identify_multiple = false; //识别多个，默认为 false
            this.option_select_multiple = false; //选择多个，默认为 false
            this.has_error = false;
            this.error_msg = "";
            this.barcode_parser = parent.barcode_parser;
            core.bus.on('barcode_scanned', this, function (barcode) {
                this.use_scanner(barcode);
            });
            navigator.mediaDevices.ondevicechange = event => {
                self.updateDeviceList();
            }
        },
        start: function () {
            var self = this;
            if (self.option_identify_multiple) {
                self.camera_res = navigator.mediaDevices.enumerateDevices()
                    .then((mediaDevices) => {
                        var videoInputDevices = mediaDevices.filter(device => device.kind === 'videoinput');
                        return {
                            "devices": self.recodingDevice(videoInputDevices),
                            "has_error": false,
                            "error_msg": "",
                        };
                    })
                    .catch((err) => {
                        console.error(err)
                        return {
                            "devices": {},
                            "has_error": true,
                            "error_msg": err,
                        };
                    });
            } else {
                self.codeReader = new ZXing.BrowserMultiFormatReader();
                self.camera_res = self.codeReader.listVideoInputDevices()
                    .then((videoInputDevices) => {
                        return {
                            "devices": self.recodingDevice(videoInputDevices),
                            "has_error": false,
                            "error_msg": "",
                        };
                    })
                    .catch((err) => {
                        console.error(err)
                        return {
                            "devices": {},
                            "has_error": true,
                            "error_msg": err,
                        };
                    });
            }
            return this._super.apply(this, arguments).then(this.initCameraAndCookice.bind(this));
        },
        recodingDevice: function (devices) {
            // Safari不允许非ASCII码作为cookie的值存储
            // 存储cookie时，需要使用 encodeURI 编码，
            // 读取cookie时，需要使用 decodeURI 解码。
            let newVideoList = new Array();
            devices.forEach((element) => {
                newVideoList.push({
                    "deviceId": element.deviceId,
                    "groupId": element.groupId,
                    "kind": element.kind,
                    "label": encodeURI(element.label),
                });
            });
            return newVideoList;
        },
        updateDeviceList: function () {
            //每当媒体设备（例如相机，麦克风或扬声器）连接到系统或从系统中移除时，devicechange 事件就会被发送到 MediaDevices  实例。
            var self = this;
            navigator.mediaDevices.enumerateDevices()
                .then((mediaDevices) => {
                    var videoInputDevices = mediaDevices.filter(device => device.kind === 'videoinput');

                    let newVideoList = new Array();
                    videoInputDevices.forEach((element) => {
                        newVideoList.push({
                            "deviceId": element.deviceId,
                            "groupId": element.groupId,
                            "kind": element.kind,
                            "label": encodeURI(element.label),
                        });
                    });
                    self.videoList = newVideoList;
                    self.setDefaultCookie();
                    if (!self.dialog.isDestroyed() && !config.device.isMobile) {
                        self.camera_source.empty();
                        self.initCameraSelect();
                    }
                });
        },

        initCameraAndCookice: async function () {
            var self = this;
            const cookie = self.getCameraCookie();
            const data = await Promise.resolve(self.camera_res);
            const devices = data.devices;
            const has_error = data.has_error;
            const error_msg = data.error_msg;
            if (has_error) {
                self.has_error = true;
                self.error_msg = error_msg;
            } else {
                self.has_error = false;
                self.error_msg = "";

                if (devices.length > 0) {
                    self.videoList = devices;

                    if ($.isEmptyObject(cookie)) {
                        // cookie 为空 设置默认值
                        self.option_autoplay = true;
                        self.option_need_confirm = true;
                        self.option_horizontal = false;
                        self.option_vertical = false;
                        self.option_identify_multiple = false;
                        self.option_select_multiple = false;
                        self.option_use_back_camera = true;
                        self.defaultCameraId = self.videoList[0].deviceId;
                        self.defaultCameraName = decodeURI(self.videoList[0].label);
                        self.setDefaultCookie();
                    } else {
                        if (!self.cookieDefaultIsExistInVideoList()) {
                            // COOKIE中的默认摄像头 不在本地设备列表中
                            // 重新设置 缓存中的默认摄像头
                            self.defaultCameraId = self.videoList[0].deviceId;
                            self.defaultCameraName = decodeURI(self.videoList[0].label);
                        } else {
                            // COOKIE中的默认摄像头 在本地设备列表中
                            // 设置默认摄像头为 cookie中的数据
                            self.defaultCameraId = self.getCameraCookie()["defaultCamera"]["id"];
                            self.defaultCameraName = decodeURI(self.getCameraCookie()["defaultCamera"]["name"]);
                        }

                        self.videoList = self.getCameraCookie()["list"];
                        self.option_autoplay = self.getCameraCookie()["option_autoplay"];
                        self.option_need_confirm = self.getCameraCookie()["option_need_confirm"];
                        self.option_horizontal = self.getCameraCookie()["option_horizontal"];
                        self.option_vertical = self.getCameraCookie()["option_vertical"];
                        self.option_identify_multiple = self.getCameraCookie()["option_identify_multiple"];
                        self.option_select_multiple = self.getCameraCookie()["option_select_multiple"];
                        self.option_use_back_camera = self.getCameraCookie()["option_use_back_camera"];
                    }
                }
                // console.log("cookie", self.getCameraCookie());
            };
        },

        //#region cookie

        getCameraCookie: function () {
            // 获取cookie中的默认摄像头
            var self = this;
            var cookie = utils.get_cookie(WEB_CAMERA_QRCODE_WIDGET_COOKIE);
            if (cookie === undefined || cookie === null || cookie === "") {
                return new Object();
            } else {
                cookie = JSON.parse(cookie);
                if (!self.hasKey("id", cookie["defaultCamera"])) {
                    cookie["defaultCamera"]["id"] = "";
                }
                return cookie;
            }
        },

        setDefaultCookie: function () {
            // 设置cookie中的默认摄像头
            let list = {};
            let defaultCameraId = "";
            if (this.videoList != undefined && this.videoList.length > 0) {
                list = this.videoList;
            }
            // Safari不允许非ASCII码作为cookie的值存储
            // 存储cookie时，需要使用 encodeURI 编码，
            // 读取cookie时，需要使用 decodeURI 解码。
            this.qr_config = {
                "defaultCamera": {
                    "id": this.defaultCameraId,
                    "name": encodeURI(this.defaultCameraName),
                },
                "list": list,
                "option_autoplay": this.option_autoplay,
                "option_need_confirm": this.option_need_confirm,
                "option_horizontal": this.option_horizontal,
                "option_vertical": this.option_vertical,
                "option_identify_multiple": this.option_identify_multiple,
                "option_select_multiple": this.option_select_multiple,
                "option_use_back_camera": this.option_use_back_camera,
            }
            utils.set_cookie(WEB_CAMERA_QRCODE_WIDGET_COOKIE, JSON.stringify(this.qr_config), 60 * 60 * 24 * 30); // 30 day cookie
        },
        cookieDefaultIsExistInVideoList: function () {
            //判断缓存的defaultCameraId是否存在当前设备本地连接的摄像头列表中
            var self = this;
            var list = self.getCameraCookie()["list"];
            var list_str = JSON.stringify(list);

            var default_camera_id = self.getCameraCookie()["defaultCamera"]["id"];
            if (list_str == undefined || default_camera_id == undefined) {
                return false;
            } else {
                return list_str.indexOf(default_camera_id) !== -1;
            }
        },
        hasKey(key, obj) {
            if (obj.hasOwnProperty(key)) {
                return true;
            } else {
                return false;
            }
        },
        //#endregion

        //#region widget
        _renderEdit: function () {
            var $input = this.$el.find('input');
            setTimeout(function () {
                //设置焦点
                $input.focus();
            }, 1000)
            // this.$loading = this.$el.find('.loading');

            if (this.value === null || this.value === "" || this.value === false) {
                return this._super($input.val(""));
            } else {
                return this._super($input.val(this.value));
            }
        },
        _prepareInput: function ($input) {
            var self = this;
            var $button = this.$el.find("button.o_show_camera_button");
            $button.click(function () {
                self.open_scan_dialog();
            })
            return $.when($input, this._super.apply(this, arguments));
        },
        _setValue: function () {
            var $input = this.$el.find('input');
            return this._super($input.val());
        },
        //#endregion

        //#region dialog
        open_scan_dialog: function () {
            var self = this;
            self.scanResult = null;
            var size = 'medium';

            var content = QWeb.render('QRCode.Camera.Body', {
                browser_type: self.browserType,
                isApp: self.isApp,
                isMobile: config.device.isMobile,
                multiple: self.option_identify_multiple,
                use_back_camera: self.option_use_back_camera,
            });
            // 
            if (self.option_identify_multiple && !config.device.isMobile) {
                size = 'extra-large';
            }
            self.$el.find("button[class*='o_show_camera_button']").prop('disabled', true); //禁用 --变灰，且不能调用点击事件
            self.$el.find(".loading").removeClass("o_hidden");

            self.checkBrowserType();
            var dialog_title = this.browserType;
            // var dialog_title = this.browserType + ": " + _t("QR code and Bar code Scanning");
            this.dialog = new Dialog(self, {
                size: size, //'extra-large', 'large', 'medium', 'small'
                dialogClass: 'o_act_window',
                title: dialog_title,
                // buttons: self.getButtons(),
                renderHeader: false,
                // renderFooter: true,
                footerTemplate: "QRCode.Camera.Footer",
                onForceClose: function () {
                    //使用键盘ESC按键时，关闭摄像头
                    self.closeDialog();
                },
                $content: content,
                // $footer: footer,
            });
            this.dialog.opened().then(function (res) {
                self.initScanDialog();
            });
            self.dialog.open();
        },
        initScanDialog: function () {
            var self = this;
            this.modal_body = this.dialog.$modal.find(".modal-body");
            this.scan_result_value = this.modal_body.find(".scan_result_value");

            this.audio = document.getElementById("sacn_success_beep");
            this.audio.loop = false;

            this.scannerLaser = this.modal_body.find(".scanner-laser");
            this.dialog.$modal.find("footer").css({
                "padding": "4px 16px"
            });

            this.dialog.$footer.empty();
            var $footer = QWeb.render('QRCode.Camera.Footer', {
                multiple: self.option_identify_multiple,
                isMobile: config.device.isMobile,
            });
            this.dialog.$footer.append($footer);

            this.initFooterButton();
            this.scan_info = this.dialog.$footer.find(".scan_info");

            var header_button = this.dialog.$modal.find("header").find("button");
            header_button.click(function () {
                self.closeDialog();
            });

            self.initOption();
            self.scan_info.text(_t("The camera is being initialized. . .")).addClass("text-info").removeClass("text-danger").removeClass("text-success");
            self.initCameraSelect();

            self.start_button.click(function () {
                self.startReader();
            });
            self.stop_button.click(function () {
                self.stopReader();
            });
        },
        toggleScanDialog: function () {
            var self = this;
            self.dialog.destroy();
            self.open_scan_dialog();
        },
        initCameraSelect: async function () {
            var self = this;
            this.sourceSelectPanel = this.modal_body.find("#sourceSelectPanel");
            this.camera_source = this.modal_body.find(".camera-select");
            if (self.videoList != undefined && self.videoList.length >= 1) {
                //设置下拉菜单
                self.sourceSelectPanel.removeClass("o_hidden");
                self.videoList.forEach((element) => {
                    var option;
                    if (element.deviceId === self.defaultCameraId) {
                        option = new Option(decodeURI(element.label), element.deviceId, true, true);
                    } else {
                        option = new Option(decodeURI(element.label), element.deviceId);
                    }
                    self.camera_source.append(option);
                })

                // 下拉菜单选中默认值
                self.camera_source.change(function () {
                    // let oldDefaultCameraId = self.defaultCameraId;
                    self.defaultCameraId = $(this).children('option:selected').val();
                    self.defaultCameraName = $(this).children('option:selected').text();
                    // if (oldDefaultCameraId !== self.defaultCameraId) {

                    // }
                    self.setDefaultCookie();
                    self.toggleReader();
                });

                self.scan_info.text(_t("The camera is initialized successfully!")).addClass("text-info").removeClass("text-danger").removeClass("text-success");
                if (self.option_autoplay) {
                    self.start_button.prop('disabled', true); //禁用 --变灰，且不能调用事件
                    self.stop_button.prop('disabled', false); //启用

                    self.startReader();
                } else {
                    self.start_button.prop('disabled', false); //启用
                    self.stop_button.prop('disabled', true); //禁用 --变灰，且不能调用事件
                    self.scan_info.text(_("The camera has not started yet. Please click the start button.")).addClass("text-warning").removeClass("text-info").removeClass("text-success");
                }
                self.initCameraButtons();
            } else {
                // 无本地设备数量;
                self.scan_info.text(_t("Startup failed: no cameras were found.")).removeClass("text-info").addClass("text-danger").removeClass("text-success");
                self.scannerLaser.addClass("o_hidden");
                self.camera_source.prop('disabled', true); //禁用 --变灰，且不能调用事件
                self.start_button.prop('disabled', true); //禁用 --变灰，且不能调用事件
                self.stop_button.prop('disabled', true); //禁用 --变灰，且不能调用
            }
        },
        initOption: function () {
            var self = this;
            this.start_button = this.modal_body.find(".scancode_start");
            this.stop_button = this.modal_body.find(".scancode_stop");
            this.show_options_button = this.modal_body.find(".show_or_hide_options_panel");
            if (config.device.isMobile) {
                this.show_options_button.find("span").addClass("o_hidden");
            }

            this.option_autoplay_el = self.modal_body.find("#option_autoplay");
            this.option_autoplay_el.prop("checked", self.option_autoplay);
            $(self.option_autoplay_el).change(function () {
                self.option_autoplay = $(this).prop("checked");
                self.setDefaultCookie();
            });

            this.option_need_confirm_el = self.modal_body.find("#option_need_confirm");
            this.option_need_confirm_el.prop("checked", self.option_need_confirm);
            $(self.option_need_confirm_el).change(function () {
                self.option_need_confirm = $(this).prop("checked");
                if (self.option_need_confirm) {
                    self.confirmButton.removeClass("o_hidden");
                } else {
                    self.confirmButton.addClass("o_hidden");
                }
                if (self.scanResult !== null) {
                    self.updateResult();
                    self.closeDialog();
                }
                self.setDefaultCookie();
            });

            this.option_flip_horizontal_el = self.modal_body.find("#option_flip_horizontal");
            this.option_flip_horizontal_el.prop("checked", self.option_horizontal);
            $(self.option_flip_horizontal_el).change(function () {
                self.option_horizontal = $(this).prop("checked");
                self.set_flip();
                self.setDefaultCookie();
            });

            this.option_flip_vertical_el = self.modal_body.find("#option_flip_vertical");
            this.option_flip_vertical_el.prop("checked", self.option_vertical);
            $(self.option_flip_vertical_el).change(function () {
                self.option_vertical = $(this).prop("checked");
                self.set_flip();
                self.setDefaultCookie();
            });
            self.set_flip();

            this.option_identify_multiple_el = self.modal_body.find("#option_identify_multiple");
            this.option_identify_multiple_el.prop("checked", self.option_identify_multiple);
            $(self.option_identify_multiple_el).change(function () {
                self.option_identify_multiple = $(this).prop("checked");
                self.setDefaultCookie();
                self.toggleScanDialog();
            });
            // if (self.option_identify_multiple) {
            //     self.modal_body.find(".control_need_confirm").addClass("o_hidden");
            // } else {
            //     self.modal_body.find(".control_need_confirm").removeClass("o_hidden");
            // }

            this.option_select_multiple_el = self.modal_body.find("#option_select_multiple");
            this.option_select_multiple_el.prop("checked", self.option_select_multiple);
            $(self.option_select_multiple_el).change(function () {
                self.option_select_multiple = $(this).prop("checked");
                self.setDefaultCookie();
            });

            this.option_use_back_camera_el = self.modal_body.find("#option_use_back_camera");
            this.user_back_camera_span = self.modal_body.find(".user_back_camera");
            this.option_use_back_camera_el.prop("checked", self.option_use_back_camera);
            $(self.option_use_back_camera_el).change(function () {
                self.option_use_back_camera = $(this).prop("checked");
                if (config.device.isMobile && self.option_use_back_camera) {
                    self.user_back_camera_span.removeClass("o_hidden");
                    self.camera_source.addClass("o_hidden");

                } else {
                    self.user_back_camera_span.addClass("o_hidden");
                    self.camera_source.removeClass("o_hidden");
                }
                self.setDefaultCookie();
                self.toggleReader();
            });
        },
        initCameraButtons: function () {
            var self = this;
            var camera_widget_options_panel = this.dialog.$modal.find("#camera_widget_options");
            var options_button = this.modal_body.find(".show_or_hide_options_panel");
            var options_button_icon = options_button.find("i");
            var options_button_text = options_button.find("span");

            $(camera_widget_options_panel).on('show.bs.collapse', function () {
                options_button_icon.addClass("fa-angle-double-up").removeClass("fa-angle-double-down");
                options_button_text.html(_t("Hide"));
            })
            $(camera_widget_options_panel).on('hide.bs.collapse', function () {
                options_button_icon.addClass("fa-angle-double-down").removeClass("fa-angle-double-up");
                options_button_text.html(_t("Show"));
            })
        },
        setControlButtons: function (state) {
            var self = this;
            if (state) {
                // 启动了摄像头
                self.start_button.prop('disabled', true); //禁用 --变灰，且不能调用点击事件
                self.stop_button.prop('disabled', false); //启用
                // self.camera_source.prop('disabled', false); //启用
            } else {
                // 关闭了摄像头
                self.start_button.prop('disabled', false); //启用
                self.stop_button.prop('disabled', true); //禁用 --变灰，且不能调用点击事件
            }
        },
        set_flip: function () {
            //设置翻转
            var self = this;

            if (self.option_horizontal && self.option_vertical) {
                self.dialog.$modal.find("#scancode-video").attr("class", "").addClass("video-flip-both");
            } else if (self.option_horizontal) {
                self.dialog.$modal.find("#scancode-video").attr("class", "").addClass("video-flip-horizontal");
            } else if (self.option_vertical) {
                self.dialog.$modal.find("#scancode-video").attr("class", "").addClass("video-flip-vertically");
            } else {
                self.dialog.$modal.find("#scancode-video").attr("class", "").addClass("video-no-flip");
            }
        },
        initFooterButton: function () {
            var self = this;

            // 拍摄按钮
            self.captureButton = self.dialog.$footer.find("button[name='capture']");
            self.captureButton.click(function () {
                self.captureMultipleCodeReader();
            });

            // 重新拍摄按钮
            self.reRaptureButton = self.dialog.$footer.find("button[name='recapture']")
            self.reRaptureButton.click(function () {
                self.againCaptureMultipleCodeReader(true);
            });
            if (config.device.isMobile) {
                self.reRaptureButton.addClass("o_hidden");
            }

            // 确认按钮
            self.confirmButton = self.dialog.$footer.find("button[name='confirm']")

            if (self.option_need_confirm) {
                self.confirmButton.removeClass("o_hidden");
            } else {
                self.confirmButton.addClass("o_hidden");
            }
            self.confirmButton.click(function () {
                if (self.scanResult === null || self.scanResult === "") {
                    self.scan_info.removeClass("text-success").addClass(
                        "text-warning");
                    self.scan_info.text(_t(
                        "No scan was performed or no scan results were selected."));
                } else {
                    self.scan_info.removeClass("text-warning").addClass(
                        "text-success");
                    self.updateResult();
                    self.closeDialog();
                }
            });

            //取消按钮
            self.cancelButton = self.dialog.$footer.find("button[name='cancel']")
            self.cancelButton.click(function () {
                self.closeDialog();
            });
        },
        closeDialog: function () {
            var self = this;
            self.stopReader();
            // self.$input.find("button[name*='o_show_camera_button']").prop('disabled', false); //启用
            self.$el.find(".loading").addClass("o_hidden");
            self.$el.find("button[class*='o_show_camera_button']").prop('disabled', false); //启用

            this.dialog.$modal.modal('hide');
        },
        updateResult: function () {
            var self = this;
            this.$el.find('input').val(self.scanResult);
            this._setValue(); //设置值
        },
        //#endregion

        //#region Reader

        startReader: function () {
            var self = this;
            self.scan_info.text(_t("Start camera...")).addClass("text-info").removeClass("text-danger").removeClass("text-success");

            if (self.option_identify_multiple) {
                let constraints = {
                    video: {
                        deviceId: self.getCameraCookie()["defaultCamera"]["id"]
                    },
                    audio: false
                };
                if (config.device.isMobile && self.option_use_back_camera) {
                    self.camera_source.addClass("o_hidden");
                    let front = false;
                    constraints = {
                        video: {
                            facingMode: (front ? "user" : "environment")
                        }
                    };
                }
                navigator.mediaDevices.getUserMedia(constraints)
                    .then(function (mediaStream) {
                        self.scannerLaser.removeClass("o_hidden");
                        let video = document.getElementById("scancode-video");
                        self.multipleMediaStream = mediaStream;
                        video.srcObject = mediaStream;
                        video.onloadedmetadata = function (e) {
                            video.play();
                            self.setControlButtons(true);
                        };
                    })
                    .catch(function (err) {
                        console.log(err.name + ": " + err.message);
                        self.scan_result_value.text(err.message);

                        self.scan_info.text(_t("Startup failed:" + err.message)).removeClass("text-info").addClass("text-danger").removeClass("text-success");
                        self.scannerLaser.addClass("o_hidden");
                    });
            } else {
                self.codeReader.listVideoInputDevices()
                    .then(() => {
                        let defaultCameraId = self.defaultCameraId;
                        if (config.device.isMobile && self.option_use_back_camera) {
                            self.camera_source.addClass("o_hidden");
                            defaultCameraId = "";
                        }
                        self.codeReader.decodeFromVideoDevice(defaultCameraId, 'scancode-video', (result, err) => {
                            if (result) {
                                self.scan_result_value.text(result.text);
                                self.scanResult = result.text;

                                self.scan_info.text(_t("Scan the code successfully, Format:") + self.getZXingFormat(result.format)).addClass("text-success").removeClass("text-danger").removeClass("text-warning");

                                self.scannerLaser.fadeOut(0.5);
                                setTimeout(function () {
                                    self.scannerLaser.fadeIn(0.5);
                                });

                                self.audio.play();
                                if (!self.option_need_confirm) {
                                    //不需要确认扫码结果
                                    self.audio.addEventListener('ended', function () {
                                        self.updateResult();
                                        self.closeDialog();
                                    }, false);
                                }
                            }
                            if (err && !(err instanceof ZXing.NotFoundException)) {
                                console.error(err);
                                self.scan_result_value.text(err);
                                self.scan_info.text(_t("Startup failed:" + err)).removeClass("text-info").addClass("text-danger").removeClass("text-success");
                                self.scannerLaser.addClass("o_hidden");
                            }
                        });
                    })
                    .catch((err) => {
                        console.error(err)
                    })
            }

            if (self.option_identify_multiple) {
                self.scan_info.text(_t("Started successfully. Please click the capture button."))
            } else {
                self.scan_info.text(_t("Started successfully. Please scan the code..."))
            }
            self.scan_info.removeClass("text-info").removeClass("text-danger").removeClass("text-warning").addClass("text-success");
        },
        stopReader: function () {
            var self = this;
            self.scannerLaser.addClass("o_hidden");
            if (self.option_identify_multiple) {
                let canvas = document.getElementById("scancode-canvas");
                let $canvas = $(canvas);
                if ($canvas.length > 0) {
                    let ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    let mask = document.getElementById("scancode-mask");
                    let $mask = $(mask);
                    let $rectangles = $mask.find(".scancode-rectangles");
                    $rectangles.find(".rectangle").remove();
                }
                if (self.multipleMediaStream) {
                    self.multipleMediaStream.getTracks().forEach(function (track) {
                        track.stop();
                    });
                }

            } else {
                if (self.codeReader) {
                    self.codeReader.reset();
                }
            }
            self.scan_result_value.text("");
            self.scannerLaser.addClass("o_hidden");

            self.setControlButtons(false);
            self.scan_info.text(_("The camera stops working.")).addClass("text-warning").removeClass("text-info").removeClass("text-success");
        },
        toggleReader: function () {
            var self = this;
            self.stopReader();
            self.startReader();
        },
        captureMultipleCodeReader: function () {
            this.audio.play();
            var self = this;

            self.scannerLaser.fadeOut(0.5);
            setTimeout(function () {
                self.scannerLaser.fadeIn(0.5);
            });

            let video = document.getElementById("scancode-video");
            let canvas = document.getElementById("scancode-canvas");
            canvas.style.height = video.clientHeight;
            canvas.style.width = video.clientWidth;
            let mask = document.querySelector("#scancode-mask");

            canvas.width = video.clientWidth;
            canvas.height = video.clientHeight;
            let ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, video.clientWidth, video.clientHeight);

            //将canvas图像转换为base64字符串，设置格式以及压缩比例
            let base64_source_str = canvas.toDataURL('image/png', 100 / 100);

            self.scan_result_value.text("");
            self.scanResult = null;
            self._rpc({
                route: '/web/multiple_qrcode_scanner/capture',
                params: {
                    base64_source_str: base64_source_str,
                }
            }).then(function (res) {
                if (res["image_data"].length > 0) {
                    let img = new Image()
                    img.height = video.clientHeight;
                    img.width = video.clientWidth;
                    img.src = res["base64_img"];
                    img.onload = () => {
                        ctx.drawImage(img, 0, 0, video.clientWidth, video.clientHeight);
                    };
                    var info_srt = _.str.sprintf(_t("Successfully scanned %s data, please select data."), res["image_data"].length);
                    if (self.option_select_multiple) {
                        info_srt = _.str.sprintf(_t("Successfully scanned %s data."), res["image_data"].length);
                    }
                    self.scan_info.text(info_srt).addClass("text-success").removeClass("text-warning").removeClass("text-danger");
                    self.draw_multiple_selection_box(res["image_data"])
                } else {
                    // 清除矩形框
                    let $mask = $(mask);
                    $mask.find(".rectangle").remove();
                    // self.reRaptureButton.removeClass("o_hidden");
                    self.scan_info.text(_t("Unrecognized, please recapture!")).addClass("text-danger").removeClass("text-warning").removeClass("text-success");
                }
                if (config.device.isMobile) {
                    let video_parent = video.parentNode;
                    let canvas_parent = canvas.parentNode;

                    $(canvas_parent).css({
                        "height": video_parent.clientHeight + "px",
                        "width": video_parent.clientWidth + "px"
                    });
                    $(video_parent).addClass("o_hidden");
                    $(canvas_parent).removeClass("o_hidden");


                    self.captureButton.addClass("o_hidden");
                    self.reRaptureButton.removeClass("o_hidden");
                }
            });

        },
        againCaptureMultipleCodeReader: function () {
            var self = this;
            self.captureButton.removeClass("o_hidden");
            self.reRaptureButton.addClass("o_hidden");

            self.modal_body.find(".o_camera_widget_camera_multiple").removeClass("o_hidden");
            self.modal_body.find(".o_camera_widget_camera_multiple_result").addClass("o_hidden");
        },
        draw_multiple_selection_box: function (data) {
            var self = this;
            let canvas = document.getElementById("scancode-canvas");
            let mask = document.getElementById("scancode-mask");
            let $mask = $(mask);
            $mask.css({
                "height": canvas.height,
                "width": canvas.width
            });
            let $rectangles = $mask.find(".scancode-rectangles");

            $rectangles.find(".rectangle").remove();
            // $rectangles.empty();
            let codes = "";
            data.forEach(function (rectangle, index) {
                let $rectangle = $("<div class='rectangle' data-code='" + rectangle[0] + "' data-format='" + rectangle[1] + "'/>");
                $rectangle.css({
                    "left": rectangle[2][0],
                    "top": rectangle[2][1],
                    "width": rectangle[2][2],
                    "height": rectangle[2][3],
                });


                if (self.option_select_multiple) {
                    let $icon = $("<i class='fa fa-check-circle-o fa-2x '/>")
                    $rectangle.addClass("active");
                    $rectangle.append($icon);
                    let code = rectangle[0] + ",";
                    if (index == data.length - 1) {
                        code = rectangle[0];
                    }
                    codes += code;
                    self.scan_result_value.text(codes);
                    self.scanResult = codes;
                } else {
                    $rectangle.click(function (ev) {
                        let code = ev.target.dataset.code;
                        let format = ev.target.dataset.format;
                        let $icon = $mask.find("i");
                        $icon.remove();
                        $(ev.target).siblings().removeClass("active");
                        $(ev.target).addClass("active");

                        self.scan_result_value.text(code);
                        self.scanResult = code;
                        self.scan_info.text(_t("You have selected data in the format ") + format).addClass("text-success").removeClass("text-danger").removeClass("text-warning");
                        self.set_active_rectangle(ev);
                        if (!self.option_need_confirm) {
                            //不需要确认扫码结果
                            self.updateResult();
                            self.closeDialog();
                        }

                    })
                }
                $rectangles.append($rectangle);
            })
        },
        set_active_rectangle: function (ev) {
            let $icon = $("<i class='fa fa-check-circle-o fa-2x '/>")
            $(ev.target).append($icon);
        },
        //#endregion

        //#region 使用扫描枪
        set_barcode_parser: function (barcode_parser) {
            this.barcode_parser = barcode_parser;
        },
        use_scanner: function (code) {
            var self = this;

            if (!code) {
                return;
            }

            if (self.option_need_confirm) {
                // self.scan_result_value.textContent = code;
                self.scan_result_value.text(code);
                self.scanResult = code;
            } else {
                //不需要确认扫码结果
                this.$el.find('input').val(code);
                // self.updateResult();
            }

            core.bus.off('barcode_scanned', this, this.use_scanner);
        },
        //#endregion

        //#region 工具函数
        checkBrowserType() {
            var self = this;
            // 判断是否手机设备
            if (!config.device.isMobile) {
                // 非手机设备
                this.browserType = _("PC browser");
            } else {
                // 手机设备
                this.browserType = _("Mobile browser");
            }

        },
        convertBoolean: function (value) {
            switch (value) {
                case false:
                    return false;
                    break;
                case undefined:
                    return true;
                    break;
                case null:
                    return true;
                    break;
                case 0:
                    return false;
                    break;
                case -0:
                    return false;
                    break;
                case NaN:
                    return true;
                    break;
                case "":
                    return true;
                    break;
                default:
                    return true;
            }
        },
        getZXingFormat: function (value) {
            switch (value) {
                case 0:
                    return "AZTEC";
                    break;
                case 1:
                    return "CODABAR";
                    break;
                case 2:
                    return "CODE_39";
                    break;
                case 3:
                    return "CODE_93";
                    break;
                case 4:
                    return "CODE_128";
                    break;
                case 5:
                    return "DATA_MATRIX";
                    break;
                case 6:
                    return "PDF_417";
                    break;
                case 7:
                    return "EAN_13";
                    break;
                case 8:
                    return "ITF";
                    break;
                case 9:
                    return "MAXICODE";
                    break;
                case 10:
                    return "PDF_417";
                    break;
                case 11:
                    return "QR_CODE";
                    break;
                case 12:
                    return "RSS_14";
                    break;
                case 13:
                    return "RSS_EXPANDED";
                    break;
                case 14:
                    return "UPC_A";
                    break;
                case 15:
                    return "UPC_E";
                    break;
                case 16:
                    return "UPC_EAN_EXTENSION";
                    break;
                default:
                    return _("unknown");
            }
        },
        //#endregion
    });

    fieldRegistry.add('qr_code', QRCode);
    return {
        QRCode: QRCode
    };
});
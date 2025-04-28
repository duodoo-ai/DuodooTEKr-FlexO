/** @odoo-module **/

import { sprintf } from "@web/core/utils/strings";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { AssetsLoadingError, loadCSS, loadJS } from '@web/core/assets';
import { useService } from "@web/core/utils/hooks";
const { Component, onMounted, onWillStart, useState, useRef } = owl;


export class DisplayTencentMapDialog extends Component {
    setup() {
        this.orm = useService("orm");
        this.notificationService = useService("notification");

        this.api_url = sprintf("%s&key=%s", this.props.api_url, this.props.key);
        this.key = this.props.key;
        this.address = this.props.address;
        this.resModel = this.props.resModel;
        this.resId = this.props.resId;
        this.resFields = this.props.resFields;
        this.city = this.props.city;

        this.keyword_input = useRef("keywordRef");
        this.mapRef = useRef("mapRef");

        this.marker = null;

        this.state = useState({
            resModel: this.props.resModel,
            resId: this.props.resId,
            shouldLoadMap: false,
            keyword: this.props.address,
            coordinates_selected: false,
            latitude: 0,
            longitude: 0,
        });

        onWillStart(async () => {
            try {
                await Promise.all([
                    loadJS(this.api_url),
                    // loadJS(this.lib_url),
                    // loadJS(this.service_url),
                ])
                this.state.shouldLoadMap = true;
            } catch (error) {
                if (!(error instanceof AssetsLoadingError)) {
                    throw error;
                }
            }
        });
        onMounted(() => {
            if (this.state.shouldLoadMap) {
                this.initMap();

                this.searchByKeyword();
            }
        });
    }

    onClickSearch() {
        // this.map.destroy();
        this.state.keyword = this.keyword_input.el.value;
        this.searchByKeyword()
    }

    onInputKeydown(ev) {
        switch (ev.key) {
            case "Enter":
                ev.preventDefault();
                ev.stopPropagation();
                this.state.keyword = this.keyword_input.el.value;
                this.searchByKeyword()
                break;
            // case "Escape":
            //     ev.preventDefault();
            //     ev.stopPropagation();
            //     this.state.isEditing = false;
            //     break;
        }
    }

    initMap() {
        const self = this;

        // 初始化地图
        this.map = new TMap.Map(this.mapRef.el, {
            zoom: 10, // 初始缩放级别
            center: new TMap.LatLng(39.908802, 116.397502), // 初始中心点坐标,默认北京天安门
        });

        // 获取缩放控件实例
        this.control = this.map.getControl(TMap.constants.DEFAULT_CONTROL_ID.ZOOM);
        this.control.setNumVisible(true) // 缩放控件显示缩放级别

        // 新建一个地点搜索类
        this.search = new TMap.service.Search({ pageSize: 10 });

        // 新建一个点标记管理类
        this.markers = new TMap.MultiMarker({
            map: this.map,
            geometries: [],
        });

        // 新建一个正逆地址解析类
        this.geocoder = new TMap.service.Geocoder();

        this.infoWindowList = Array(10); // 保存10个infoWindow实例

        // 改变地图中心点到目标城市坐标
        this.geocoder.getLocation({ address: this.city })
            .then((result) => {
                this.markers.updateGeometries([
                    {
                        id: 'main',
                        position: result.result.location, // 将得到的坐标位置用点标记标注在地图上
                    },
                ]);
                this.map.setCenter(result.result.location);
            });

        // 绑定点击事件
        this.map.on('click', (ev) => {
            self.onClickCreateMarker(ev)
        })
    }

    searchByKeyword() {
        /*
        文档 https://lbs.qq.com/webDemoCenter/glAPI/glServiceLib/search
        */
        const self = this;


        this.infoWindowList.forEach((infoWindow) => {
            infoWindow.close();
        });
        this.infoWindowList.length = 0;
        this.markers.setGeometries([]);

        // 在地图显示范围内以给定的关键字搜索地点
        this.search
            .searchRectangle({
                keyword: this.state.keyword,
                bounds: self.map.getBounds(),
            })
            .then((result) => {
                result.data.forEach((item, index) => {
                    var geometries = this.markers.getGeometries();
                    var infoWindow = new TMap.InfoWindow({
                        map: self.map,
                        position: item.location,
                        content: sprintf(`<h3>${item.title}</h3><p>%s${item.address}</p>`, _t("Address:")),
                        offset: { x: 0, y: -50 },
                    }); // 新增信息窗体显示地标的名称与地址、电话等信息
                    infoWindow.close();
                    self.infoWindowList[index] = infoWindow;
                    geometries.push({
                        id: String(index), // 点标注数据数组
                        position: item.location,
                    });
                    this.markers.updateGeometries(geometries); // 绘制地点标注
                    this.markers.on('click', (e) => {
                        self.infoWindowList[Number(e.geometry.id)].open();
                    }); // 点击标注显示信息窗体
                });
            });
    }

    onClickCreateMarker(ev) {
        this.state.latitude = ev.latLng.getLat().toFixed(6);
        this.state.longitude = ev.latLng.getLng().toFixed(6);
        this.state.coordinates_selected = true;

        if (this.marker) {
            this.marker.setMap(null);
            this.marker = null;
        }

        if (!this.marker) {
            this.marker = new TMap.MultiMarker({
                id: 'marker-layer',
                map: this.map,
                styles: {
                    "marker": new TMap.MarkerStyle({
                        "width": 64,
                        "height": 64,
                        "anchor": { x: 32, y: 64 },
                        "src": '/esit_geolocalize/static/img/marker-succes.png'
                    })
                },
                geometries: [{
                    "id": '1', //第1个点标记
                    "styleId": 'marker',
                    "position": new TMap.LatLng(this.state.latitude, this.state.longitude),
                    "properties": {
                        "title": "marker"
                    }
                }]
            });
        }
    }

    onConfirm() {
        try {
            this.orm.call(this.resModel, "write", [[this.resId], {
                "latitude": this.state.latitude,
                "longitude": this.state.longitude,
            }])
            this.notificationService.add(_t("Successfully located"), {
                title: _t("Success"),
                type: "success",
                sticky: true,
                buttons: [
                    {
                        name: _t("Refresh"),
                        primary: true,
                        onClick: () => browser.location.reload(),
                    },
                ],
            });
        } catch (error) {
            this.notificationService.add(error, {
                title: _t("Error"),
                type: "warning",
                sticky: true,
            });
        } finally {
            this.props.close();
        }
    }
}

DisplayTencentMapDialog.components = {
    Dialog
};
DisplayTencentMapDialog.template = "esit_geolocalize.DisplayTencentMapDialog";
DisplayTencentMapDialog.title = _t("Locate on the Tencent map");
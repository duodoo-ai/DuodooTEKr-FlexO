/** @odoo-module */

/*
腾讯位置服务文档：折线-动态箭头
https://lbs.qq.com/webDemoCenter/glAPI/glPolyline/arrowAnimation
*/
import { _t } from '@web/core/l10n/translation';
import { session } from '@web/session';
import { sprintf } from '@web/core/utils/strings';
import { AssetsLoadingError, loadCSS, loadJS } from '@web/core/assets';
import { useService } from '@web/core/utils/hooks';
import { Component, onMounted, onWillStart, onPatched, onWillUpdateProps, useState, useRef } from '@odoo/owl';
import { renderToString, renderToElement, renderToMarkup } from '@web/core/utils/render';

export class TencentProjectRouteMap extends Component {
    static template = 'project.TencentProjectRouteMap';
    static props = {
        projects: { type: Array, optional: true },
        isLargeScreen: { type: Boolean, optional: true },
        key: { type: String, optional: true },
        zoom: { type: Number, optional: true },
    };
    static defaultProps = {
        isLargeScreen: false,
    };
    setup() {
        this.orm = useService('orm');
        // this.action = useService("action");
        this.rootRef = useRef('rootRef');
        this.mapRef = useRef('mapRef');

        this.project_config = session['project'];
        this.normal_state_color = this.project_config['pipeline']['normal_state_color'] || '#00ff00';
        this.exception_state_color = this.project_config['pipeline']['exception_state_color'] || '#ffa500';
        this.large_screen_title = this.project_config['large_screen']['title'] || _t('Smart water supply operation system');
        this.large_screen_background_color = this.project_config['large_screen']['background_color'] || '#004b7a';

        this.state = useState({
            displayList: window.localStorage.getItem('project_route_map.displayList') === 'false' ? false : true || true,
            enableCollision: true,
            displayDistance: true,
            mapZoomThresholdList: [10,11, 12, 13, 14, 15],
            mapZoomThreshold: window.localStorage.getItem('project_route_map.mapZoomThreshold') || 12,
            shouldLoadMap: false,
            zoom: this.props.zoom,
            projects: this.props.projects,
        });

        this.busService = this.env.services.bus_service;
        this.busService.subscribe('online_sync_pipeline_node', (notification) => {
            this.updatePipelineNodeData(notification.project_id, notification.location_id, notification.node_data);
        });

        onWillStart(async () => {
            const tencent_api_url = sprintf(
                'https://map.qq.com/api/gljs?v=1.exp&libraries=service,geocoder,drawing,geometry,autocomplete,convertor&key=%s',
                this.props.key
            );
            // console.log("加载腾讯地图", tencent_api_url)
            try {
                await Promise.all([loadJS(tencent_api_url)]);
                this.state.shouldLoadMap = true;
            } catch (error) {
                if (!(error instanceof AssetsLoadingError)) {
                    throw error;
                }
            }
        });
        onWillUpdateProps(async (newProps) => {
            this.state.projects = newProps.projects;
        });
        onPatched(async () => {});
        onMounted(() => {
            if (this.state.shouldLoadMap) {
                this.initMap();
                // this.renderMap()
            }
        });
    }

    async getLocations() {
        return await this.orm.call('project.project', 'get_locations_by_project_ids', [this.state.resIds]);
    }

    /**
     * 显示列表视图
     * @param {*} ev
     */
    onChangeDisplayList(ev) {
        this.state.displayList = ev.target.checked;
        window.localStorage.setItem('project_route_map.displayList', ev.target.checked);

        const projectPouteMapElement = this.rootRef.el.parentElement;
        const listViewElement = this.rootRef.el.parentElement.previousElementSibling;

        if (!this.state.displayList) {
            // 隐藏列表元素
            listViewElement.classList.add('d-none');
        } else {
            // 显示列表元素
            listViewElement.classList.remove('d-none');
        }
        // 切换地图容器的宽度
        projectPouteMapElement.classList.toggle('w-50', this.state.displayList);
        projectPouteMapElement.classList.toggle('w-100', !this.state.displayList);
    }

    onChangeMapZoomThreshold(ev) {
        this.state.mapZoomThreshold = ev.target.value;

        window.localStorage.setItem('project_route_map.mapZoomThreshold', ev.target.value);
    }

    /**
     * 启用地图碰撞
     * @param {*} ev
     */
    onChangeEnableCollision(ev) {
        this.state.enableCollision = ev.target.checked;

        // 同时更新两个图层的碰撞状态
        this.markers.enableCollision = this.state.enableCollision;
        this.markerLabelLayer.enableCollision = this.state.enableCollision;

        // 强制刷新图层
        this.markers.setGeometries(this.state.markerGeometries);
        this.markerLabelLayer.setGeometries(this.markerLabelGeometries);
    }

    /**
     * 显示线条的长度
     * @param {*} ev
     */
    onChangedisplayDistance(ev) {
        this.state.displayDistance = ev.target.checked;
    }

    /*
    初始化地图
     */
    async initMap() {
        if (!this.state.displayList && !this.props.isLargeScreen) {
            const projectPouteMapElement = this.rootRef.el.parentElement;
            projectPouteMapElement.classList.toggle('w-50', this.state.displayList);
            projectPouteMapElement.classList.toggle('w-100', !this.state.displayList);

            const listViewElement = this.rootRef.el.parentElement.previousElementSibling;
            listViewElement.classList.add('d-none');
        }

        // 新建一个正逆地址解析类
        this.geocoder = new TMap.service.Geocoder();

        // 新建一个行政区划类
        this.district = new TMap.service.District({
            polygon: 2, // 返回行政区划边界的类型
        });

        this.center = new TMap.LatLng(39.908802, 116.397502); //初始中心点坐标  默认北京天安门
        //初始化地图

        this.map = new TMap.Map(this.mapRef.el, {
            zoom: this.state.zoom || 6,
            center: this.center, // 初始中心点坐标  默认北京天安门
            mapStyleId: 'style1',
        });

        // if (this.props.isLargeScreen) {
        //     // 设置为夜间模式
        //     this.map.setMapStyleId('style1');
        // }

        // 获取缩放控件实例
        this.control = this.map.getControl(TMap.constants.DEFAULT_CONTROL_ID.ZOOM);
        this.control.setNumVisible(true); // 缩放控件显示缩放级别

        // 添加地图缩放监听事件
        this.map.on('zoom_changed', () => {
            const currentZoom = this.map.getZoom();
            this.state.zoom = currentZoom; // 更新组件状态
            this.handleZoomChange(); // 触发缩放处理
        });

        // 新建 `infoWindow` 实例   用于显示信息
        this.infoWindowList = Array();

        // 设置地图中心点
        this.setMapCenter();

        // 生成线路图（标记、折线、信息窗口）
        await this.generateRouteMap();
    }

    /*
    根据国家和城市获取地图中心点坐标
     */
    setMapCenter() {
        // 合并项目中的坐标数据数组
        let location_list = []; // 坐标数据数组
        let district_list = []; // 地区数据数组

        this.state.projects.forEach((project) => {
            district_list.push(...project.locations);
            const locations = project.locations;
            locations.forEach((location) => {
                location_list.push([location['latitude'], location['longitude']]);
            });
        });

        // 根据坐标数据数组 计算中心坐标
        // 过滤无效坐标（纬度/经度为 0 的数据）
        const validLocations = location_list.filter(([lat, lng]) => lat !== 0 && lng !== 0);

        if (validLocations.length > 0) {
            // 如果有有效坐标，计算平均坐标并设置地图中心点
            const averageCoordinate = this.computeAverageLocation(validLocations);
            this.map.setCenter(averageCoordinate); //设置地图中心点

            // this.map.setCenter(new TMap.LatLng(39.908802, 116.397502));//坐标为天安门
        } else {
            // 如果没有有效坐标，获取城市、州\省, 国家的数量
            // TODO 此处代码待完善
            const countryCount = [...new Set(district_list.map((loc) => loc.country))].length;
            const stateCount = [...new Set(district_list.map((loc) => loc.state))].length;
            const cityCount = [...new Set(district_list.map((loc) => loc.city))].length;
            console.log('国家数量:', countryCount, '省份数量:', stateCount, '城市数量:', cityCount);
            let region_name = '';
            let district_level = '';
            if (cityCount === 1 && district_list[0].city !== '') {
                // 城市数量为 1，获取城市的中心坐标
                region_name = district_list[0].city;
            } else if (stateCount === 1 && district_list[0].state !== '') {
                // 省份数量为 1，获取省份的中心坐标
                region_name = district_list[0].state;
            } else if (countryCount === 1 && district_list[0].country !== '') {
                // 国家数量为 1，获取国家的中心坐标
                region_name = district_list[0].country;
            } else {
                // TODO 其他情况，获取所有坐标的中心坐标
            }

            this.setMapCenterByName(region_name);
        }
    }

    /**
     * 生成线路图（折线、标记、信息窗口）
     */
    async generateRouteMap() {
        // 1.生成折线
        this.generatePolyline();

        // 2.生成标记
        this.generateMarker();

        // 3.生成项目名称和公里数文本标记
        this.generateMarkerLabel();

        // 4.生成信息窗口
        await this.generateInfoWindow();
    }

    /**
     * 1.生成动态箭头折线
     */
    generatePolyline() {
        // 创建包含多个几何路径的数组
        this.geometries = this.state.projects.map((project, index) => {
            // 将每个项目的坐标转换为 TMap.LatLng 对象
            const paths = project.locations.map((loc) => new TMap.LatLng(loc.latitude, loc.longitude));

            return {
                id: 'pl_' + index, //折线唯一标识，删除时使用
                styleId: 'normal_state_animation', //绑定样式名
                paths: paths,
                properties: {
                    projectId: project.id, // 附加项目 ID 属性
                    index: index, // 折线索引号
                },
            };
        });

        // 创建多折线图层（替换原单一折线）
        this.polylineLayer = new TMap.MultiPolyline({
            map: this.map,
            styles: {
                //折线样式定义
                normal_state_animation: new TMap.PolylineStyle({
                    color: this.normal_state_color, //线填充色
                    borderWidth: 2, //边线宽度
                    borderColor: this.adjustColorBrightness(this.normal_state_color, -10), //边线颜色
                    width: 8, //折线宽度
                    showArrow: true,
                    arrowOptions: {
                        width: 6, // 箭头图标宽度
                        height: 5, // 箭头图标高度
                        space: 50, // 箭头图标之间的孔隙长度
                        animSpeed: 50, // 箭头动态移动的速度 单位 (像素/秒)
                    },
                }),
                abnormal_state_animation: new TMap.PolylineStyle({
                    color: '#3777FF', //线填充色
                    width: 1, //折线宽度
                    borderWidth: 1, //边线宽度
                    borderColor: '#FFF', //边线颜色
                    lineCap: 'butt', //线端头方式
                }),
            },
            geometries: this.geometries, // 传入所有折线几何数据
        });
    }

    /**
     * 2.生成 Marker 标记
     */
    generateMarker() {
        const self = this;
        // 创建标记几何数据数组
        this.state.markerGeometries = [];

        this.state.projects.forEach((project, projectIndex) => {
            project.locations.forEach((location, locationIndex) => {
                if (location.latitude && location.longitude) {
                    let projectNodeGeometrie = {
                        id: `marker_${project.id}_${location.id}`, // 唯一标识
                        position: new TMap.LatLng(location.latitude, location.longitude),
                        properties: {
                            projectId: project.id,
                            locationId: location.id,
                            locationSequence: location.sequence,
                            locationName: location.name || _t('Unnamed location'),
                            locationLength: location.length,
                            address: location.address,
                            real_input_traffic: location.real_input_traffic,
                            real_output_traffic: location.real_output_traffic,
                            status: location.status,
                        },
                        styleId: location.status === 'normal' ? 'normal_location_marker' : 'exception_location_marker', // 使用统一样式
                        rank: project.locations.length - locationIndex, //文本碰撞时的优先级，值越大优先级越高
                    };
                    if (locationIndex === 0 || locationIndex === project.locations.length - 1) {
                        // 起点 和 终点
                        projectNodeGeometrie = {
                            id: `marker_${project.id}_${location.id}`, // 唯一标识
                            position: new TMap.LatLng(location.latitude, location.longitude),
                            properties: {
                                projectId: project.id,
                                locationId: location.id,
                                locationSequence: location.sequence,
                                locationName: location.name || _t('Unnamed location'),
                                locationLength: location.length,
                                address: location.address,
                                real_input_traffic: location.real_input_traffic,
                                real_output_traffic: location.real_output_traffic,
                                status: location.status,
                            },
                            styleId: location.status === 'normal' ? 'normal_location_point_marker' : 'exception_location_point_marker', // 使用统一样式
                            rank: project.locations.length - locationIndex, //文本碰撞时的优先级，值越大优先级越高
                        };
                    }

                    this.state.markerGeometries.push(projectNodeGeometrie);
                }
            });
        });

        // 创建多标记图层
        this.markers = new TMap.MultiMarker({
            map: this.map,
            styles: {
                normal_location_point_marker: new TMap.MarkerStyle({
                    width: 18, // 图标宽度
                    height: 18, // 图标高度
                    anchor: { x: 9, y: 9 }, // 图标锚点
                    src: '/rtx_project/static/img/map/tencentmap/green_node_point.png',
                    enableRelativeScale: false, // 是否开启相对缩放
                }),
                exception_location_point_marker: new TMap.MarkerStyle({
                    width: 18, // 图标宽度
                    height: 18, // 图标高度
                    anchor: { x: 9, y: 9 }, // 图标锚点
                    src: '/rtx_project/static/img/map/tencentmap/red_node_point.png',
                    enableRelativeScale: false, // 是否开启相对缩放
                }),
                normal_location_marker: new TMap.MarkerStyle({
                    width: 14, // 图标宽度
                    height: 14, // 图标高度
                    anchor: { x: 7, y: 7 }, // 图标锚点
                    src: '/rtx_project/static/img/map/tencentmap/green_node.png',
                    enableRelativeScale: false, // 是否开启相对缩放
                }),
                exception_location_marker: new TMap.MarkerStyle({
                    width: 14, // 图标宽度
                    height: 14, // 图标高度
                    anchor: { x: 7, y: 7 }, // 图标锚点
                    src: '/rtx_project/static/img/map/tencentmap/red_node.png',
                    enableRelativeScale: false, // 是否开启相对缩放
                }),
            },
            enableCollision: this.state.enableCollision, // 开启碰撞
            // enableAutoRotate: true, // 开启自动旋转
            // autoRotateSpeed: 10, // 自动旋转速度
            geometries: this.state.markerGeometries,
        });

        let infoWindow = null;

        // 绑定鼠标划入事件
        this.markers.on('mouseover', (ev) => {
            if (self.state.zoom < self.state.mapZoomThreshold) {
                infoWindow = self.mouseoverHandler(ev);
            }
        });

        // 绑定鼠标划出事件
        this.markers.on('mouseout', () => {
            if (self.state.zoom < self.state.mapZoomThreshold && infoWindow) {
                self.mouseoutHandler(infoWindow);
            }
        });
    }

    /**
     * 3.生成文本标记
     */
    generateMarkerLabel() {
        this.markerLabelGeometries = [];
        let labelCount = this.state.projects.length;
        this.state.projects.forEach((project, projectIndex) => {
            // 每条线路节点上显示的文本标记
            const nodeCount = project.locations.length;
            labelCount += nodeCount;
            project.locations.forEach((location, locationIndex) => {
                if (location.latitude && location.longitude) {
                    const projectNodeGeometrie = {
                        id: `label_project_node_${project.id}_${locationIndex}`, // 唯一标识
                        position: new TMap.LatLng(location.latitude, location.longitude),
                        content: location.name, // 标注文本
                        styleId: 'project_node', // 使用统一样式
                        rank: project.locations.length - locationIndex, //文本碰撞时的优先级，值越大优先级越高
                    };
                    this.markerLabelGeometries.push(projectNodeGeometrie);
                    if (locationIndex === 0) {
                        // 起点
                        const startProjectNodeGeometrie = {
                            id: `label_project_node_start_${project.id}_${locationIndex}`, // 唯一标识
                            position: new TMap.LatLng(location.latitude, location.longitude),
                            content: _t('0km'), // 标注文本
                            styleId: 'project_start_km', // 使用统一样式
                            rank: project.locations.length - locationIndex, //文本碰撞时的优先级，值越大优先级越高
                        };
                        this.markerLabelGeometries.push(startProjectNodeGeometrie);
                    } else if (locationIndex === project.locations.length - 1) {
                        // 终点
                        const endProjectNodeGeometrie = {
                            id: `label_project_node_start_${project.id}_${locationIndex}`, // 唯一标识
                            position: new TMap.LatLng(location.latitude, location.longitude),
                            content: this.computeProjectDistance(project), // 根据项目坐标集合计算长度
                            styleId: 'project_end_km', // 使用统一样式
                            rank: project.locations.length - locationIndex, //文本碰撞时的优先级，值越大优先级越高
                        };
                        this.markerLabelGeometries.push(endProjectNodeGeometrie);
                    }
                }
            });

            // 每条路线上方显示的文本标记
            const projectCenterCoordinate = this.computeAverageLocation(project.locations.map((loc) => [loc.latitude, loc.longitude])); // 计算项目中心坐标
            const projectGeometrie = {
                id: `label_project_${project.id}`, // 唯一标识
                position: projectCenterCoordinate,
                styleId: 'project_label', // 使用统一样式
                content: project.name, // 标注文本
                rank: labelCount - projectIndex, //文本碰撞时的优先级，值越大优先级越高
            };
            this.markerLabelGeometries.push(projectGeometrie);
        });

        // 创建多文本标记图层
        this.markerLabelLayer = new TMap.MultiLabel({
            map: this.map,
            styles: {
                project_label: new TMap.LabelStyle({
                    color: '#3777FF', // 颜色属性
                    size: 18, // 文字大小属性
                    offset: { x: 0, y: -50 }, // 文字偏移属性单位为像素
                    angle: 0, // 文字旋转属性
                    alignment: 'center', // 文字水平对齐属性
                    verticalAlignment: 'middle', // 文字垂直对齐属性
                }),
                project_node: new TMap.LabelStyle({
                    color: '#000000', // 颜色属性
                    size: 12, // 文字大小属性
                    offset: { x: 0, y: -15 }, // 文字偏移属性单位为像素
                    angle: 0, // 文字旋转属性
                    alignment: 'center', // 文字水平对齐属性
                    verticalAlignment: 'middle', // 文字垂直对齐属性
                }),
                project_start_km: new TMap.LabelStyle({
                    color: '#000000', // 颜色属性
                    size: 14, // 文字大小属性
                    offset: { x: 0, y: 15 }, // 文字偏移属性单位为像素
                    angle: 0, // 文字旋转属性
                    alignment: 'center', // 文字水平对齐属性
                    verticalAlignment: 'middle', // 文字垂直对齐属性
                }),
                project_end_km: new TMap.LabelStyle({
                    color: '#000000', // 颜色属性
                    size: 14, // 文字大小属性
                    offset: { x: 0, y: 15 }, // 文字偏移属性单位为像素
                    angle: 0, // 文字旋转属性
                    alignment: 'center', // 文字水平对齐属性
                    verticalAlignment: 'middle', // 文字垂直对齐属性
                }),
            },
            geometries: this.markerLabelGeometries,
            enableCollision: this.state.enableCollision, // 开启碰撞
        });
    }

    /**
     * 4.生成信息窗口
     */
    async generateInfoWindow() {
        const self = this;
        this.state.markerGeometries.forEach((geometry) => {
            const geometry_id = geometry.id;
            const ids = geometry_id.split('_');
            const projectId = ids[1];
            const project = this.state.projects.find((project) => project.id === parseInt(projectId));
            const position = geometry.position;

            // 渲染信息窗口内容
            const contentElement = renderToString('project.ProjectRouteMapInfoWindow', {
                geometry_id: geometry_id,
                title: geometry.properties['locationName'],
                distance: this.computeProjectDistanceByLocation(project, geometry.properties),
                real_input_traffic: geometry.properties['real_input_traffic'],
                real_output_traffic: geometry.properties['real_output_traffic'],
                status: geometry.properties['status'],
                normal_state_color: this.normal_state_color,
                exception_state_color: this.exception_state_color,
            });

            // 创建新的信息窗口实例
            const infoWindow = new TMap.InfoWindow({
                map: this.map, // 添加地图实例
                enableCustom: true,
                position: position,
                content: contentElement,
                offset: { x: 0, y: -32 },
                zIndex: 100,
            });

            this.infoWindowList.push(infoWindow);
            infoWindow.close(); // 初始时关闭
        });
    }

    /**
     * 显示所有的信息窗口
     */
    showAllInfoWindows() {
        // 先关闭所有信息窗口
        this.hideAllInfoWindows();

        // 按顺序显示信息窗口
        this.state.markerGeometries.forEach((geometry, index) => {
            // 查找对应位置的信息窗口
            const existingInfoWindow = this.infoWindowList.find((infoWindow) => {
                const windowPosition = infoWindow.getPosition();
                const geometryPosition = geometry.position;
                return windowPosition.lat === geometryPosition.lat && windowPosition.lng === geometryPosition.lng;
            });

            if (existingInfoWindow) {
                // 更新信息窗口位置和地图实例
                existingInfoWindow.setMap(this.map);
                existingInfoWindow.setPosition(geometry.position);

                // 延迟显示信息窗口，避免同时显示导致的重叠
                setTimeout(() => {
                    existingInfoWindow.open();
                }, index * 100);
            }
        });
    }

    /**
     * 显示单个信息窗口
     */
    showInfoWindow(geometry) {
        const existingInfoWindow = this.infoWindowList.find((infoWindow) => {
            const windowPosition = infoWindow.getPosition();
            const geometryPosition = geometry.position;
            return windowPosition.lat === geometryPosition.lat && windowPosition.lng === geometryPosition.lng;
        });

        if (existingInfoWindow) {
            // 更新信息窗口位置和地图实例
            existingInfoWindow.setMap(this.map);
            existingInfoWindow.setPosition(geometry.position);
            existingInfoWindow.open();
        }
        return existingInfoWindow;
    }

    /**
     * 关闭所有的信息窗口
     */
    hideAllInfoWindows() {
        this.infoWindowList.forEach((infoWindow) => {
            infoWindow.close();
        });
    }

    /*
    根据名称设置地图中心点坐标
    */
    setMapCenterByName(name) {
        const self = this;
        console.log('setMapCenterByName', name);
        this.geocoder.getLocation({ address: name }).then((result) => {
            self.map.setCenter(result.result.location);
        });
    }

    /**
     * 节流函数
     * @param {*} fn
     * @param {*} delay
     * @returns
     */
    throttle(fn, delay) {
        let timer = null;
        return function (...args) {
            if (!timer) {
                timer = setTimeout(() => {
                    fn.apply(this, args);
                    timer = null;
                }, delay);
            }
        };
    }

    /**
     * 使用节流函数包装 handleZoomChange，提高了性能，减少了不必要的 DOM 操作
     * 信息窗口的显示和隐藏会更加平滑，不会因为频繁的缩放操作而导致性能问题。
     * 处理地图缩放事件
     */
    handleZoomChange = this.throttle(function () {
        const self = this;
        let infoWindow = null;

        if (this.state.zoom >= this.state.mapZoomThreshold) {
            this.showAllInfoWindows();

            // 移除绑定鼠标划入事件
            this.markers.off('mouseover', (ev) => {
                if (self.state.zoom < self.state.mapZoomThreshold) {
                    infoWindow = self.mouseoverHandler(ev);
                }
            });
            // 移除鼠标划出事件
            this.markers.off('mouseout', () => {
                if (self.state.zoom < self.state.mapZoomThreshold && infoWindow) {
                    self.mouseoutHandler(infoWindow);
                }
            });
        } else {
            this.hideAllInfoWindows();

            // 绑定鼠标划入事件
            this.markers.on('mouseover', (ev) => {
                if (self.state.zoom < self.state.mapZoomThreshold) {
                    infoWindow = self.mouseoverHandler(ev);
                }
            });

            // 绑定鼠标划出事件
            this.markers.on('mouseout', () => {
                if (self.state.zoom < self.state.mapZoomThreshold && infoWindow) {
                    self.mouseoutHandler(infoWindow);
                }
            });
        }
    }, 200);

    clickHandler(ev) {
        this.showInfoWindow(ev.geometry);
    }

    mouseoverHandler(ev) {
        // console.log("鼠标划入事件", ev);
        const infoWindow = this.showInfoWindow(ev.geometry);
        return infoWindow;
    }

    mouseoutHandler(infoWindow) {
        if (infoWindow) {
            infoWindow.close();
        }
    }

    // ---------------------------------------------
    // 方法
    // ---------------------------------------------
    /**
     * 更新管道节点数据
     */
    updatePipelineNodeData(project_id, location_id, node_data) {
        const id = `marker_${project_id}_${location_id}`;
        const data = this.markers.getGeometryById(id);

        let newData = data;
        Object.entries(node_data).forEach(([key, value]) => {
            newData['properties'][key] = value;
            if (key === 'status') {
                // 获取原 styles
                const oldStyleId = data['styleId'];
                if (oldStyleId.includes('point')) {
                    // 是端点
                    if (newData['properties'][key] === 'normal') {
                        newData['styleId'] = 'normal_location_point_marker';
                    } else {
                        newData['styleId'] = 'exception_location_point_marker';
                    }
                } else {
                    // 是中间点
                    if (newData['properties'][key] === 'normal') {
                        newData['styleId'] = 'normal_location_marker';
                    } else {
                        newData['styleId'] = 'exception_location_marker';
                    }
                }
            }
        });

        // Object.assign(data, {
        //     position: center,
        // });
        this.markers.updateGeometries([data]);
    }

    /**
    计算项目的平均坐标
     */
    computeProjectAverageCoordinate(project) {
        // 计算项目的平均坐标
        const total = project.locations.reduce(
            (acc, location) => {
                acc.lat += location.latitude;
                acc.lng += location.longitude;
                return acc;
            },
            { lat: 0, lng: 0 }
        );

        const avgLat = total.lat / project.locations.length;
        const avgLng = total.lng / project.locations.length;

        return new TMap.LatLng(avgLat, avgLng);
    }

    /**
    根据项目坐标集合计算长度（单位：公里）
     */
    computeProjectDistance(project) {
        let totalDistance = 0;
        const locations = project.locations;

        // 确保至少 2 个坐标点才能计算长度
        if (locations.length < 2) return '0.00' + _t('km');

        // 遍历所有相邻坐标点
        for (let i = 1; i < locations.length; i++) {
            const startPoint = new TMap.LatLng(locations[i - 1].latitude, locations[i - 1].longitude);
            const endPoint = new TMap.LatLng(locations[i].latitude, locations[i].longitude);
            const path = [startPoint, endPoint];
            // 使用TMap几何计算方法获取精确距离（单位：米）
            const distance = TMap.geometry.computeDistance(path);
            totalDistance += distance;
        }

        // 更新项目的总长度
        this.orm.call('project.project', 'set_project_length', [project.id, (totalDistance / 1000).toFixed(2)]);

        // 转换为公里并保留两位小数
        return (totalDistance / 1000).toFixed(2) + _t('km');
    }

    /**
    根据项目和坐标计算当前坐标长度（单位：公里）
     */
    computeProjectDistanceByLocation(project, locationData) {
        let totalDistance = 0.0;
        const locations = project.locations;
        if (locationData.locationSequence === 1) {
            totalDistance = 0.0;
        } else if (locations.length < 2) {
            // 确保至少2个坐标点才能计算长度
            totalDistance = 0.0;
        } else {
            // 查找坐标在项目中的索引，根据索引计算长度
            const locationIndex = locations.findIndex((loc) => loc.id === locationData.locationId);

            if (locationIndex === -1) {
                return '0.00';
            } else {
                // 遍历所有相邻坐标点
                for (let i = 1; i <= locationIndex; i++) {
                    const startPoint = new TMap.LatLng(locations[i - 1].latitude, locations[i - 1].longitude);
                    const endPoint = new TMap.LatLng(locations[i].latitude, locations[i].longitude);
                    const path = [startPoint, endPoint];

                    // 使用TMap几何计算方法获取精确距离（单位：米）
                    const distance = TMap.geometry.computeDistance(path);

                    totalDistance += distance;
                }
                // 转换为公里并保留两位小数
                totalDistance = (totalDistance / 1000).toFixed(2);
            }
        }
        this.orm.call('project.map.location', 'set_project_location_length', [locationData.locationId, totalDistance]);
        return totalDistance.toString();
    }

    /**
    计算有效坐标的平均值
     */
    computeAverageLocation(validLocations) {
        // 计算有效坐标的平均值
        const total = validLocations.reduce(
            (acc, [lat, lng]) => {
                acc.lat += lat;
                acc.lng += lng;
                return acc;
            },
            { lat: 0, lng: 0 }
        );

        const avgLat = total.lat / validLocations.length;
        const avgLng = total.lng / validLocations.length;

        return new TMap.LatLng(avgLat, avgLng);
    }

    /**
     * 将十六进制颜色值转换为 RGB 数组
     * @param {string} hex 十六进制颜色值，如 "#RRGGBB"
     * @returns {number[]} RGB 数组，如 [r, g, b]
     */
    hexToRgb(hex) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return [r, g, b];
    }

    /**
     * 将 RGB 数组转换为十六进制颜色值
     * @param {number[]} rgb RGB 数组，如 [r, g, b]
     * @returns {string} 十六进制颜色值，如 "#RRGGBB"
     */
    rgbToHex(rgb) {
        const r = Math.round(rgb[0]).toString(16).padStart(2, '0');
        const g = Math.round(rgb[1]).toString(16).padStart(2, '0');
        const b = Math.round(rgb[2]).toString(16).padStart(2, '0');
        return `#${r}${g}${b}`;
    }

    /**
     * 调整颜色的亮度
     * @param {string} color 输入的颜色值，可以是十六进制或 RGB 格式
     * @param {number} percentage 调整的百分比，正数为变亮，负数为变暗
     * @returns {string} 调整后的颜色值，十六进制格式
     */
    adjustColorBrightness(color, percentage) {
        let rgb;
        if (color.startsWith('#')) {
            rgb = this.hexToRgb(color);
        } else if (color.startsWith('rgb')) {
            const match = color.match(/\d+/g);
            rgb = match.map(Number);
        } else {
            throw new Error('Unsupported color format');
        }

        const factor = 1 + percentage / 100;
        const newRgb = rgb.map((value) => {
            const newValue = value * factor;
            return Math.min(255, Math.max(0, newValue));
        });

        return this.rgbToHex(newRgb);
    }
}

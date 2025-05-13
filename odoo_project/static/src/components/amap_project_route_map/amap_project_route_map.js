import { _t } from '@web/core/l10n/translation';
import { session } from '@web/session';
import { AssetsLoadingError, loadCSS, loadJS } from '@web/core/assets';
import { renderToString } from '@web/core/utils/render';
import { Component, onMounted, onWillStart, useState, useRef, useEffect } from '@odoo/owl';
import { useService } from '@web/core/utils/hooks';
import { adjustColorBrightness } from '@web_route_map/utils/colors';
import { aMpaCalculateTotalDistance } from '@web_route_map/utils/map/amap/calculate';

export class AmapProjectRouteMap extends Component {
    static template = 'project.AmapProjectRouteMap';
    static props = {
        projects: { type: Array, optional: true },
        isLargeScreen: { type: Boolean, optional: true },
        key: { type: String, optional: true },
        zoom: { type: Number, optional: true },
        center: { type: Array, optional: true },
    };
    static defaultProps = {
        isLargeScreen: false,
    };

    setup() {
        this.orm = useService('orm');
        this.rootRef = useRef('rootRef');
        this.mapRef = useRef('mapRef');

        this.amap_jsapi_key = session['amap_jsapi_key'] || '';
        this.amap_map_style = this.props.isLargeScreen ? session['amap_map_style'] : 'normal';
        // console.log('session', session);
        // console.log('this.amap_jsapi_key', this.amap_jsapi_key);
        // console.log('this.amap_map_style', this.amap_map_style);
        this.project_config = session['project'];
        this.normal_state_color = this.project_config['pipeline']['normal_state_color'] || '#00ff00';
        this.exception_state_color = this.project_config['pipeline']['exception_state_color'] || '#ffa500';

        this.markerLayer = null; // 初始化 markerLayer

        // 定义标记样式
        this.markerStyles = {
            // 正常起始终点样式
            normal_location_point_marker: {
                type: 'image',
                image: '/odoo_project/static/img/map/amap/green_node_point.png',
                size: [24, 24],
                anchor: 'center',
                zIndex: 100,
            },
            // 异常起始终端样式
            exception_location_point_marker: {
                type: 'image',
                image: '/odoo_project/static/img/map/amap/red_node_point.png',
                size: [24, 24],
                anchor: 'center',
                zIndex: 100,
            },
            // 正常中间点样式
            normal_location_dot_marker: {
                type: 'image',
                image: '/odoo_project/static/img/map/amap/green_dots.png',
                size: [16, 16],
                anchor: 'center',
                zIndex: 90,
            },
            // 异常中间点样式
            exception_location_dot_marker: {
                type: 'image',
                image: '/odoo_project/static/img/map/amap/red_dots.png',
                size: [16, 16],
                anchor: 'center',
                zIndex: 90,
            },
        };

        this.state = useState({
            displayList: window.localStorage.getItem('project_route_map.displayList') === 'false' ? false : true || true,
            enableCollision: true,
            displayDistance: true,
            mapZoomThresholdList: [10, 11, 12, 13, 14, 15],
            mapZoomThreshold: window.localStorage.getItem('project_route_map.mapZoomThreshold') || 11,
            shouldLoadMap: false,
            zoom: this.props.zoom,
            projects: this.props.projects,
            projectMarkers: new Map(),
            infoOverlays: new Map(), // 存储覆盖物
            exception_nodes: [],
            exception_overlays: new Map(), // 存储异常节点的覆盖物
        });

        // 监听异常节点列表变化
        useEffect(
            () => {
                this._handleExceptionNodesChange();
            },
            () => [this.state.exception_nodes]
        );

        // 订阅后端消息
        this.busService = this.env.services.bus_service;
        this.busService.subscribe('online_sync_pipeline_node', (notification) => {
            this.updatePipelineNodeData(notification.project_id, notification.location_id, notification.node_data);
        });

        onWillStart(async () => {
            try {
                // 加载高德地图主API
                await loadJS(
                    `https://webapi.amap.com/maps?v=2.0&key=${this.amap_jsapi_key}&plugin=AMap.Geocoder,AMap.DistrictSearch,AMap.MoveAnimation`
                );
                // 加载UI组件库
                await loadJS('https://webapi.amap.com/ui/1.1/main.js?v=1.1.1');
                // 加载Loca库
                await loadJS(`https://webapi.amap.com/loca?key=${this.amap_jsapi_key}&v=2.0.0`);
            } catch (error) {
                console.error('地图脚本加载失败:', error);
                if (!(error instanceof AssetsLoadingError)) {
                    throw error;
                }
            }

            // 等待Loca加载完成
            await new Promise((resolve) => {
                if (window.Loca) {
                    resolve();
                } else {
                    window._AMapSecurityConfig = {
                        securityJsCode: this.amap_jsapi_key,
                    };
                    const checkLoca = () => {
                        if (window.Loca) {
                            resolve();
                        } else {
                            setTimeout(checkLoca, 100);
                        }
                    };
                    checkLoca();
                }
            });
        });

        onMounted(() => {
            this.initMap();
        });
    }

    /**
     * 处理异常节点列表变化
     */
    _handleExceptionNodesChange() {
        // 移除所有现有的异常节点覆盖物
        this.state.exception_overlays.forEach((overlay) => {
            overlay.setMap(null);
        });
        this.state.exception_overlays.clear();

        // 为每个异常节点创建新的覆盖物，不考虑缩放级别
        this.state.exception_nodes.forEach((node) => {
            // 在标记图层中查找对应的标记
            let targetMarker = null;
            this.markerLayer.eachLayer((marker) => {
                const extData = marker.getExtData();
                if (extData.projectId === node.projectId && extData.locationId === node.locationId) {
                    targetMarker = marker;
                }
            });

            if (targetMarker) {
                const position = targetMarker.getPosition();
                const overlayId = `exception_${node.projectId}_${node.locationId}`;

                const overlay = this.createInfoOverlay({
                    content: this.getInfoWindowContent({
                        ...node.data,
                        showCloseButton: true,
                    }),
                    position: position,
                    offset: [0, -30],
                    onClose: () => this.handleInfoWindowClose(overlayId),
                });

                overlay.setMap(this.map);
                this.state.exception_overlays.set(overlayId, overlay);
            }
        });
    }

    /**
     * 获取信息窗体的内容
     */
    getInfoWindowContent(props) {
        const content = renderToString('project.ProjectRouteMapInfoWindow', {
            ...props,
            title: props.locationName || _t('Unknown'),
            showCloseButton: props.showCloseButton || false,
            distance: props.distance || '0',
            locationName: props.locationName,
            locationSequence: props.locationSequence,
            address: props.address || _t('Unknown'),
            real_input_traffic: props.real_input_traffic || '0',
            real_output_traffic: props.real_output_traffic || '0',
            status: props.status,
            status_class: props.status === 'normal' ? 'text-success' : 'text-danger',
            status_color: props.status_color,
            normal_state_color: this.normal_state_color,
            exception_state_color: this.exception_state_color,
        });
        return content;
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
     * 设置标记点的鼠标事件
     */
    setupMarkerEvents() {
        // 移除所有现有的覆盖物
        this.state.infoOverlays.forEach((overlay) => {
            overlay.setMap(null);
        });
        this.state.infoOverlays.clear();

        this.markerLayer.eachLayer((marker) => {
            // 移除现有的事件监听
            marker.off('mouseover').off('mouseout');

            // 只在缩放级别小于阈值时添加事件
            if (this.state.zoom < this.state.mapZoomThreshold) {
                marker.on('mouseover', () => {
                    const markerData = marker.getExtData();
                    const position = marker.getPosition();
                    const infoWindow = new AMap.InfoWindow({
                        content: this.getInfoWindowContent({
                            ...markerData,
                            showCloseButton: false,
                        }),
                        offset: new AMap.Pixel(0, -30),
                        isCustom: true,
                        anchor: 'bottom-center',
                        position: position,
                    });
                    infoWindow.open(this.map, position);
                });

                marker.on('mouseout', () => {
                    this.map.clearInfoWindow();
                });
            }
        });
    }

    /**
     * 处理地图缩放事件
     */
    handleZoomChange() {
        const newZoom = this.map.getZoom();
        const wasAboveThreshold = this.state.zoom >= this.state.mapZoomThreshold;
        const isAboveThreshold = newZoom >= this.state.mapZoomThreshold;

        this.state.zoom = newZoom;

        // 只有当跨越阈值时才切换显示模式
        if (wasAboveThreshold !== isAboveThreshold) {
            // 移除所有现有的覆盖物
            this.state.infoOverlays.forEach((overlay) => {
                overlay.setMap(null);
            });
            this.state.infoOverlays.clear();

            // 移除所有事件监听
            this.markerLayer.eachLayer((marker) => {
                marker.off('mouseover').off('mouseout');
            });

            if (isAboveThreshold) {
                // 缩放级别 >= 阈值：显示所有节点的固定覆盖物
                this.markerLayer.eachLayer((marker) => {
                    const markerData = marker.getExtData();
                    const position = marker.getPosition();
                    const overlayId = `marker_${markerData.projectId}_${markerData.locationId}`;

                    const overlay = this.createInfoOverlay({
                        content: this.getInfoWindowContent({
                            ...markerData,
                            showCloseButton: true,
                        }),
                        position: position,
                        offset: [0, -30],
                        onClose: () => this.handleInfoWindowClose(overlayId),
                    });

                    overlay.setMap(this.map);
                    this.state.infoOverlays.set(overlayId, overlay);
                });
            } else {
                // 缩放级别 < 阈值：使用鼠标悬停事件
                this.setupMarkerEvents();
            }
        }

        // 更新所有覆盖物位置
        this.updateAllOverlaysPosition();
    }

    /**
     * 初始化地图
     */
    async initMap() {
        if (!this.state.displayList && !this.props.isLargeScreen) {
            const projectPouteMapElement = this.rootRef.el.parentElement;
            projectPouteMapElement.classList.toggle('w-50', this.state.displayList);
            projectPouteMapElement.classList.toggle('w-100', !this.state.displayList);

            const listViewElement = this.rootRef.el.parentElement.previousElementSibling;
            listViewElement.classList.add('d-none');
        }
        try {
            // 设置地图容器的canvas属性
            const mapContainer = this.mapRef.el;
            const canvas = document.createElement('canvas');
            canvas.getContext('2d', { willReadFrequently: true });
            mapContainer.appendChild(canvas);

            this.map = new AMap.Map(mapContainer, {
                zoom: this.state.zoom || 6,
                center: [116.405285, 39.904989],
                showIndoorMap: false,
                viewMode: '2D', //地图模式
                mapStyle: `amap://styles/${this.amap_map_style}`,
            });

            // 等待地图加载完成
            await new Promise((resolve) =>
                this.map.on('complete', () => {
                    // 确保所有canvas元素都设置willReadFrequently
                    mapContainer.querySelectorAll('canvas').forEach((canvas) => {
                        const ctx = canvas.getContext('2d', { willReadFrequently: true });
                    });
                    resolve();
                })
            );

            // 等待UI库加载完成
            await new Promise((resolve) => {
                if (window.AMapUI) {
                    resolve();
                } else {
                    window.onAMapUILoaded = resolve;
                }
            });

            // 使用UI组件
            AMapUI.loadUI(['control/BasicControl'], (BasicControl) => {
                /*
                lt,    left top, 左上角
                lm，   left middle, 左侧中部
                lb，   left bottom, 左下角
                ct，   center top, 中上
                cb，   center bottom, 中下
                rt，   right top, 右上角
                rm，   right middle, 右侧中部
                rb，   right bottom 右下角
                */
                this.zoomCtrl = new BasicControl.Zoom({
                    showZoomNum: true,
                    position: 'rm',
                });
                this.map.addControl(this.zoomCtrl);
                this.map.on('zoomend', this.handleZoomChange.bind(this));
            });

            // 初始化地理编码服务
            this.geocoder = new AMap.Geocoder({
                radius: 1000,
            });

            // 初始化行政区查询服务
            this.district = new AMap.DistrictSearch({
                subdistrict: 1,
                showbiz: false,
                extensions: 'all',
            });

            await this.setMapCenter();
            await this.generateRouteMap();
        } catch (e) {
            console.error('地图初始化失败:', e);
        }
    }

    /**
     * 设置地图中心点
     */
    async setMapCenter() {
        if (this.props.center) {
            this.map.setCenter(this.props.center);
            return;
        }

        if (this.props.projects && this.props.projects.length > 0) {
            const validProjects = this.props.projects.filter((project) => project.latitude && project.longitude);

            if (validProjects.length > 0) {
                const sumCoords = validProjects.reduce(
                    (acc, project) => {
                        acc.latitude += parseFloat(project.latitude);
                        acc.longitude += parseFloat(project.longitude);
                        return acc;
                    },
                    { latitude: 0, longitude: 0 }
                );

                const centerPoint = [sumCoords.longitude / validProjects.length, sumCoords.latitude / validProjects.length];

                this.map.setCenter(centerPoint);
            }
        }
    }

    /**
     * 计算并设置地图中心点
     */
    calculateAndSetMapCenter() {
        if (this.state.markerList && this.state.markerList.length > 0) {
            // 计算所有坐标的平均值
            const sum = this.state.markerList.reduce(
                (acc, marker) => {
                    acc.lng += marker.position[0];
                    acc.lat += marker.position[1];
                    return acc;
                },
                { lng: 0, lat: 0 }
            );

            const centerPoint = [sum.lng / this.state.markerList.length, sum.lat / this.state.markerList.length];
            this.map.setCenter(centerPoint);
        }
    }

    /**
     * 创建带流动效果的折线
     */
    createFlowingPolyline(path, projectName) {
        if (!Array.isArray(path) || path.length < 2) {
            console.warn('路径点数组无效或格式不正确');
            return;
        }

        // 创建基础折线
        const polyline = new AMap.Polyline({
            path: path,
            strokeWeight: 10,
            strokeColor: adjustColorBrightness(this.normal_state_color, -10),
            strokeStyle: 'solid',
            showDir: true,
            dirColor: '#ffffff',
            isOutline: true,
            outlineColor: '#ffffff',
            outlineWidth: 2,
            zIndex: 10,
        });

        // 创建项目名称标签
        if (projectName) {
            // 计算所有节点的中心坐标
            let sumLng = 0;
            let sumLat = 0;
            path.forEach((point) => {
                sumLng += point.getLng();
                sumLat += point.getLat();
            });
            const centerPoint = new AMap.LngLat(sumLng / path.length, sumLat / path.length);

            // 计算路线主要走向
            const startPoint = path[0];
            const endPoint = path[path.length - 1];
            const longitudeDiff = Math.abs(endPoint.getLng() - startPoint.getLng());
            const latitudeDiff = Math.abs(endPoint.getLat() - startPoint.getLat());

            // 根据走向设置文字方向和样式
            let isVertical = false;
            let labelText = projectName;
            let offsetX = 0;
            let offsetY = 0;

            if (longitudeDiff > latitudeDiff) {
                // 东西走向，横向显示
                isVertical = false;
                offsetX = 0;
                offsetY = -60; // 向上偏移60px
                labelText = projectName;
            } else {
                // 南北走向，纵向显示
                isVertical = true;
                offsetX = 60; // 向右偏移60px
                offsetY = 0;
                // 将文字转为纵向排列
                labelText = projectName.split('').join('\n');
            }

            const projectLabel = new AMap.Text({
                text: labelText,
                position: centerPoint, // 使用计算出的中心点
                anchor: 'center',
                offset: new AMap.Pixel(offsetX, offsetY), // 根据方向设置不同的偏移量
                style: {
                    backgroundColor: 'transparent',
                    borderWidth: '0',
                    textAlign: 'center',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    color: '#333',
                    lineHeight: isVertical ? '1.2em' : 'normal', // 纵向显示时调整行高
                    padding: isVertical ? '10px 5px' : '5px 10px', // 根据方向调整内边距
                    whiteSpace: isVertical ? 'pre-line' : 'nowrap', // 纵向显示时允许换行
                },
            });
            this.map.add(projectLabel);
        }

        // 创建Loca实例
        const loca = new window.Loca.Container({
            map: this.map,
        });

        // 创建数据源
        const geo = new window.Loca.GeoJSONSource({
            data: {
                type: 'FeatureCollection',
                features: [
                    {
                        type: 'Feature',
                        properties: {},
                        geometry: {
                            type: 'LineString',
                            coordinates: path.map((point) => [point.getLng(), point.getLat()]),
                        },
                    },
                ],
            },
        });

        // 创建流线图层
        const lineLayer = new window.Loca.PulseLineLayer({
            zIndex: 11,
            opacity: 0.8,
            visible: true,
        });

        lineLayer.setSource(geo);
        lineLayer.setStyle({
            lineWidth: 6,
            lineColor: adjustColorBrightness(this.normal_state_color, -20),
            interval: 0.5,
            duration: 2000,
            trailLength: 0.5,
            flowLength: 0.5,
        });

        // 添加到地图
        this.map.add([polyline]);
        loca.add(lineLayer);
        loca.animate.start();

        return polyline;
    }

    /**
     * 更新所有覆盖物的位置
     */
    updateAllOverlaysPosition() {
        // 更新普通覆盖物位置
        this.state.infoOverlays.forEach((overlay) => {
            overlay.updatePosition();
        });

        // 更新异常节点覆盖物位置
        this.state.exception_nodes.forEach((node) => {
            const overlayId = `exception_${node.projectId}_${node.locationId}`;
            const overlay = this.state.exception_overlays.get(overlayId);
            if (overlay) {
                overlay.updatePosition();
            }
        });
    }

    /**
     * 生成线路图
     */
    async generateRouteMap() {
        if (!this.props.projects || this.props.projects.length === 0) {
            return;
        }

        // 1. 清理地图和覆盖物
        this.map.clearMap();
        this.state.infoOverlays.forEach((overlay) => {
            overlay.setMap(null);
        });
        this.state.infoOverlays.clear();

        // 2. 清理并重新初始化 markerLayer
        if (this.markerLayer) {
            this.markerLayer.clearLayers();
            this.markerLayer.setMap(null);
        }
        this.markerLayer = new AMap.LayerGroup();
        this.markerLayer.setMap(this.map);

        // 3. 准备标记数据
        this.state.markerList = [];
        this.state.projectMarkers = new Map();
        this.state.exception_nodes = [];

        // 4. 创建所有标记点的数据
        this.props.projects.forEach((project) => {
            const projectMarkers = [];

            project.locations.forEach((location, locationIndex) => {
                if (location.latitude && location.longitude) {
                    const markerData = {
                        id: `marker_${project.id}_${location.id}`,
                        position: [parseFloat(location.longitude), parseFloat(location.latitude)],
                        properties: {
                            projectId: project.id,
                            locationId: location.id,
                            locationSequence: location.sequence,
                            locationName: location.name || _t('Unnamed location'),
                            locationLength: location.length,
                            address: location.address,
                            real_input_traffic: location.real_input_traffic || '0',
                            real_output_traffic: location.real_output_traffic || '0',
                            status: location.status,
                            status_color: location.status === 'normal' ? this.normal_state_color : this.exception_state_color,
                            water_flow: location.water_flow || '0',
                            pressure: location.pressure || '0',
                            temperature: location.temperature || '0',
                            distance: '0',
                        },
                        styleId:
                            location.status === 'normal'
                                ? locationIndex === 0 || locationIndex === project.locations.length - 1
                                    ? 'normal_location_point_marker'
                                    : 'normal_location_dot_marker'
                                : locationIndex === 0 || locationIndex === project.locations.length - 1
                                ? 'exception_location_point_marker'
                                : 'exception_location_dot_marker',
                    };

                    this.state.markerList.push(markerData);
                    projectMarkers.push(markerData);

                    // 如果状态异常，添加到异常节点列表
                    if (location.status !== 'normal') {
                        this.state.exception_nodes.push({
                            projectId: project.id,
                            locationId: location.id,
                            data: markerData.properties,
                        });
                    }
                }
            });

            if (projectMarkers.length > 0) {
                this.state.projectMarkers.set(project.id, projectMarkers);
            }
        });

        // 5. 计算并设置地图中心点
        this.calculateAndSetMapCenter();

        // 6. 创建标记实例并添加标签
        this.state.markerList.forEach((markerData) => {
            const marker = new AMap.Marker({
                position: new AMap.LngLat(markerData.position[0], markerData.position[1]),
                icon: new AMap.Icon({
                    image: this.markerStyles[markerData.styleId].image,
                    size: new AMap.Size(...this.markerStyles[markerData.styleId].size),
                    imageSize: new AMap.Size(...this.markerStyles[markerData.styleId].size),
                }),
                offset: new AMap.Pixel(
                    -this.markerStyles[markerData.styleId].size[0] / 2,
                    -this.markerStyles[markerData.styleId].size[1] / 2
                ),
                zIndex: this.markerStyles[markerData.styleId].zIndex,
                cursor: 'pointer',
            });

            // 设置扩展数据
            marker.setExtData(markerData.properties);

            // 添加节点名称标签
            marker.setLabel({
                content: markerData.properties.locationName,
                direction: 'top',
                offset: new AMap.Pixel(0, -10),
                anchor: 'bottom-center',
                style: {
                    backgroundColor: 'transparent',
                    borderWidth: '0',
                    fontSize: '12px',
                    fontWeight: '500',
                    color: markerData.properties.status_color,
                    padding: '0',
                    textAlign: 'center',
                },
            });

            this.markerLayer.addLayer(marker);
        });

        // 7. 为每个项目创建连线和距离标注
        this.state.projectMarkers.forEach((projectMarkers, projectId) => {
            if (projectMarkers.length > 1) {
                const project = this.props.projects.find((p) => p.id === projectId);
                // 按照序号排序标记点
                const sortedMarkers = projectMarkers.sort((a, b) => a.properties.locationSequence - b.properties.locationSequence);
                const path = sortedMarkers.map((marker) => new AMap.LngLat(marker.position[0], marker.position[1]));

                // 创建带流动效果的折线
                this.createFlowingPolyline(path, project.name);

                // 计算总距离
                const totalDistance = aMpaCalculateTotalDistance(AMap, path);

                // 更新每个标记点的距离信息
                let accumulatedDistance = 0;
                for (let i = 0; i < sortedMarkers.length; i++) {
                    if (i > 0) {
                        const prevPoint = path[i - 1];
                        const currentPoint = path[i];
                        accumulatedDistance +=
                            AMap.GeometryUtil.distance(
                                [prevPoint.getLng(), prevPoint.getLat()],
                                [currentPoint.getLng(), currentPoint.getLat()]
                            ) / 1000;
                    }
                    sortedMarkers[i].properties.distance = accumulatedDistance.toFixed(2);
                }

                // 添加起点"0KM"和终点距离标注
                const startLabel = new AMap.Text({
                    text: '0KM',
                    position: path[0],
                    anchor: 'center',
                    offset: new AMap.Pixel(0, 20),
                    style: {
                        backgroundColor: 'transparent',
                        borderWidth: '0',
                        textAlign: 'center',
                        fontSize: '12px',
                        fontWeight: '500',
                        color: '#333',
                    },
                });

                const endLabel = new AMap.Text({
                    text: `${totalDistance}KM`,
                    position: path[path.length - 1],
                    anchor: 'center',
                    offset: new AMap.Pixel(0, 20),
                    style: {
                        backgroundColor: 'transparent',
                        borderWidth: '0',
                        textAlign: 'center',
                        fontSize: '12px',
                        fontWeight: '500',
                        color: '#333',
                    },
                });

                this.map.add([startLabel, endLabel]);
            }
        });

        // 8. 设置初始事件 - 修改这部分
        if (this.state.zoom < this.state.mapZoomThreshold) {
            this.setupMarkerEvents();
        }

        // 9. 监听地图移动事件，包括平移、缩放等
        this.map.on('mapmove', () => {
            this.updateAllOverlaysPosition();
        });

        this.map.on('moveend', () => {
            this.updateAllOverlaysPosition();
        });

        this.map.on('zoomend', () => {
            this.handleZoomChange();
            this.updateAllOverlaysPosition();
        });

        // 10. 调整视图以包含所有标记点
        this.map.setFitView();
    }

    /**
     * 更新管道节点数据
     */
    updatePipelineNodeData(project_id, location_id, node_data) {
        // 确保 markerLayer 已初始化
        if (!this.markerLayer) {
            console.warn('MarkerLayer not initialized');
            return;
        }

        // 在标记图层中查找对应的标记
        let targetMarker = null;
        this.markerLayer.eachLayer((marker) => {
            const extData = marker.getExtData();
            if (extData.projectId === project_id && extData.locationId === location_id) {
                targetMarker = marker;
            }
        });

        if (!targetMarker) {
            console.warn(`未找到标记点: project_id=${project_id}, location_id=${location_id}`);
            return;
        }

        // 获取当前标记的扩展数据
        const extData = targetMarker.getExtData();
        const oldStatus = extData.status;

        // 更新扩展数据
        Object.entries(node_data).forEach(([key, value]) => {
            extData[key] = value;
        });

        // 特殊处理状态变更
        if (node_data.status !== undefined) {
            const newStatus = node_data.status;
            extData.status = newStatus;
            extData.status_color = newStatus === 'normal' ? this.normal_state_color : this.exception_state_color;

            // 更新标记图标
            const isEndpoint =
                extData.locationSequence === 1 ||
                extData.locationSequence === this.props.projects.find((p) => p.id === project_id).locations.length;

            const iconUrl =
                newStatus === 'normal'
                    ? isEndpoint
                        ? this.markerStyles.normal_location_point_marker.image
                        : this.markerStyles.normal_location_dot_marker.image
                    : isEndpoint
                    ? this.markerStyles.exception_location_point_marker.image
                    : this.markerStyles.exception_location_dot_marker.image;

            const iconSize = isEndpoint ? [24, 24] : [16, 16];

            targetMarker.setIcon(
                new AMap.Icon({
                    image: iconUrl,
                    size: new AMap.Size(...iconSize),
                    imageSize: new AMap.Size(...iconSize),
                })
            );

            // 更新标签颜色
            targetMarker.setLabel({
                content: extData.locationName,
                direction: 'top',
                offset: new AMap.Pixel(0, -10),
                anchor: 'bottom-center',
                style: {
                    backgroundColor: 'transparent',
                    borderWidth: '0',
                    fontSize: '12px',
                    fontWeight: '500',
                    color: extData.status_color,
                    padding: '0',
                    textAlign: 'center',
                },
            });

            // 处理异常节点列表
            const exceptionNodeIndex = this.state.exception_nodes.findIndex(
                (node) => node.projectId === project_id && node.locationId === location_id
            );

            if (newStatus === 'normal') {
                // 如果状态恢复正常，从异常节点列表中移除
                if (exceptionNodeIndex !== -1) {
                    const newExceptionNodes = [...this.state.exception_nodes];
                    newExceptionNodes.splice(exceptionNodeIndex, 1);
                    this.state.exception_nodes = newExceptionNodes;
                }
            } else {
                // 如果状态变为异常
                const nodeData = {
                    projectId: project_id,
                    locationId: location_id,
                    data: { ...extData },
                };

                if (exceptionNodeIndex === -1) {
                    // 如果不在列表中，添加到异常节点列表
                    this.state.exception_nodes = [...this.state.exception_nodes, nodeData];
                } else {
                    // 如果已在列表中，更新数据
                    const newExceptionNodes = [...this.state.exception_nodes];
                    newExceptionNodes[exceptionNodeIndex] = nodeData;
                    this.state.exception_nodes = newExceptionNodes;
                }
            }
        }

        // 更新标记的扩展数据
        targetMarker.setExtData(extData);
    }

    /**
     * 处理信息窗体关闭事件
     */
    handleInfoWindowClose(overlayId) {
        const overlay = this.state.exception_overlays.get(overlayId);
        if (overlay) {
            overlay.setMap(null);
            this.state.exception_overlays.delete(overlayId);
        }
    }

    /**
     * 创建信息窗体覆盖物
     */
    createInfoOverlay(options) {
        const dom = document.createElement('div');
        dom.className = 'amap-info-window';
        dom.style.position = 'absolute';
        dom.innerHTML = options.content;
        dom.style.transform = 'translate(-50%, -100%)';
        dom.style.zIndex = '100';
        dom.style.transition = 'left 0.3s, top 0.3s';

        // 添加关闭按钮的点击事件
        const closeButton = dom.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                if (options.onClose) {
                    options.onClose();
                }
            });
        }

        const overlay = {
            dom: dom,
            content: options.content,
            position: options.position,
            offset: options.offset || [0, -30],
            map: null,
            onClose: options.onClose,

            setMap: function (map) {
                if (map) {
                    this.map = map;
                    map.getContainer().appendChild(this.dom);
                    this.updatePosition();
                } else {
                    if (this.dom.parentNode) {
                        this.dom.parentNode.removeChild(this.dom);
                    }
                    this.map = null;
                }
            },

            setPosition: function (position) {
                this.position = position;
                this.updatePosition();
            },

            updatePosition: function () {
                if (this.dom && this.position && this.map) {
                    const pixel = this.map.lngLatToContainer(this.position);
                    const mapContainer = this.map.getContainer();
                    const mapBounds = {
                        width: mapContainer.offsetWidth,
                        height: mapContainer.offsetHeight,
                    };

                    const overlayWidth = this.dom.offsetWidth;
                    const overlayHeight = this.dom.offsetHeight;

                    // 基础位置计算（中心对齐）
                    let left = pixel.x;
                    let top = pixel.y + this.offset[1];

                    // 确保覆盖物完全在视野内
                    // 水平方向调整
                    if (left - overlayWidth / 2 < 0) {
                        left = overlayWidth / 2;
                    } else if (left + overlayWidth / 2 > mapBounds.width) {
                        left = mapBounds.width - overlayWidth / 2;
                    }

                    // 垂直方向调整
                    if (top < 0) {
                        top = pixel.y - this.offset[1]; // 如果上方空间不足，显示在下方
                    } else if (top + overlayHeight > mapBounds.height) {
                        top = mapBounds.height - overlayHeight;
                    }

                    // 应用位置
                    this.dom.style.left = left + 'px';
                    this.dom.style.top = top + 'px';
                }
            },
        };

        return overlay;
    }
}

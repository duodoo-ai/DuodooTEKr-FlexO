/**
 * 高德地图计算两个坐标点之间的距离（单位：米）
 * @param {Object} AMap 高德地图实例
 * @param {Array} point1 [longitude, latitude]
 * @param {Array} point2 [longitude, latitude]
 * @returns {number} 距离（米）
 */
export function aMapCalculateDistance(AMap, point1, point2) {
    return AMap.GeometryUtil.distance(point1, point2);
}

/**
 * 高德地图计算项目路线的总长度（单位：千米）
 * @param {Object} AMap 高德地图实例
 * @param {Array} points 路线上的所有点 [[longitude, latitude], ...]
 * @returns {number} 总长度（千米）
 */
export function aMpaCalculateTotalDistance(AMap, points) {
    let totalDistance = 0;
    for (let i = 0; i < points.length - 1; i++) {
        totalDistance += aMapCalculateDistance(AMap, points[i], points[i + 1]);
    }
    return (totalDistance / 1000).toFixed(2); // 转换为千米并保留两位小数
}

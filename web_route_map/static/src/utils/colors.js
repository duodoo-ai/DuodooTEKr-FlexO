/**
 * 将十六进制颜色值转换为 RGB 数组
 * @param {string} hex 十六进制颜色值，如 "#RRGGBB"
 * @returns {number[]} RGB 数组，如 [r, g, b]
 */
export function hexToRgb(hex) {
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
export function rgbToHex(rgb) {
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
export function adjustColorBrightness(color, percentage) {
    let rgb;
    if (color.startsWith('#')) {
        rgb = hexToRgb(color);
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

    return rgbToHex(newRgb);
}

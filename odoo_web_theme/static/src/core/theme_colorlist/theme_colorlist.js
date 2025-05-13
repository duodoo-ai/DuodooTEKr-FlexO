import { ThemeColorList } from '@eist_web_theme/core/theme_colorlist/theme_colorlist';
import { patch } from '@web/core/utils/patch';
import { _t } from "@web/core/l10n/translation";

patch(ThemeColorList, {
    COLORS: [
        _t('Dark blue'), // 0.深蓝色
        _t('Brown'), // 1.褐色
    ],
});

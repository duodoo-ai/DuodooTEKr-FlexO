import { ThemeColorPickerField } from '@eist_web_theme/views/fields/theme_color_picker/theme_color_picker';
import { patch } from '@web/core/utils/patch';

patch(ThemeColorPickerField, {
    RECORD_COLORS: [0, 1, 2],
});

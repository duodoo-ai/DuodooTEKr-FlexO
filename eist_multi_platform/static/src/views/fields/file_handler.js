import { FileUploader } from '@web/views/fields/file_handler';
import { patch } from '@web/core/utils/patch';
import { getDataURLFromFile } from '@web/core/utils/urls';

patch(FileUploader.props, {
    ...FileUploader.props,
    resModel: { type: String, optional: true },
});
patch(FileUploader.prototype, {
    async onFileChange(ev) {
        // console.log('onFileChange------------', this.props.resModel);
        if (this.props.resModel === 'res.multi_platform.apps') {
            if (!ev.target.files.length) {
                return;
            }
            const { target } = ev;
            for (const file of ev.target.files) {
                this.state.isUploading = true;
                const data = await getDataURLFromFile(file);
                if (!file.size) {
                    console.warn(`Error while uploading file : ${file.name}`);
                    this.notification.add(_t('There was a problem while uploading your file.'), {
                        type: 'danger',
                    });
                }
                try {
                    await this.props.onUploaded({
                        name: file.name,
                        size: file.size,
                        type: file.type,
                        data: data.split(',')[1],
                        objectUrl: file.type === 'application/pdf' ? URL.createObjectURL(file) : null,
                    });
                } finally {
                    this.state.isUploading = false;
                }
            }
            target.value = null;
            if (this.props.multiUpload && this.props.onUploadComplete) {
                this.props.onUploadComplete({});
            }
        } else {
            return await super.onFileChange(...arguments);
        }
    },
});

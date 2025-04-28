/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';
import { FileUploader } from '@web/views/fields/file_handler';
import { standardWidgetProps } from '@web/views/widgets/standard_widget_props';
import { Component, useState } from '@odoo/owl';
import { _t } from '@web/core/l10n/translation';
import { checkFileSize, DEFAULT_MAX_FILE_SIZE } from '@web/core/utils/files';
import { sprintf } from '@web/core/utils/strings';

export class AppFileUploader extends Component {
    static template = 'eist_multi_platform.AppFileUploader';
    static components = {
        FileUploader,
    };
    static props = {
        ...standardWidgetProps,
        record: { type: Object, optional: true },
        slots: { type: Object, optional: true },
        resModel: { type: String, optional: true },
    };
    static defaultProps = {
        acceptedFileExtensions: '.exe,.apk',
        fileUploadClass: 'btn-info',
    };

    setup() {
        this.orm = useService('orm');
        this.action = useService('action');
        this.notification = useService('notification');
        this.dialog = useService('dialog');
        this.http = useService('http');
        this.state = useState({
            uploading: false,
            progress: 0,
            forceUpdate: false,
        });
    }

    /**
     * 将文件块转换为 base64
     * @param {Blob|File} chunk 文件块数据
     * @returns {Promise<string>}
     */
    async chunkToBase64(chunk) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(chunk);
        });
    }

    /**
     * 检查版本是否存在
     * @param {string} filename 文件名
     * @returns {Promise<Object|null>} 返回已存在的记录或null
     */
    async checkVersionExists(filename) {
        try {
            const result = await this.orm.call('res.multi_platform.apps', 'check_version_exists', [filename]);
            return result;
        } catch (error) {
            console.error(_t('Failed to check the version:'), error);
            return null;
        }
    }

    /**
     * 分片上传应用大文件
     * @param {Object} fileData 文件数据对象
     */
    async uploadAppFileInChunks(fileData) {
        console.log('文件数据', fileData);
        try {
            console.log('大文件分片上传', file.size);
            const chunkSize = DEFAULT_MAX_FILE_SIZE; // Odoo 默认最大文件上传大小
            const totalChunks = Math.ceil(file.size / chunkSize);
            console.log('上传会话ID', sessionId);
            console.log('总分片数', totalChunks);
            let currentChunk = 0;

            // 分片上传
            while (currentChunk < totalChunks) {
                const start = currentChunk * chunkSize;
                const end = Math.min(start + chunkSize, file.size);
                const chunk = file.slice(start, end);

                // 将分片转换为base64
                const base64Chunk = await this.chunkToBase64(chunk);
                const chunkContent = base64Chunk.split(',')[1];
                console.log('分片内容（base64编码）', totalChunks);
                console.log('文件名', file.name);

                // 上传分片
                await this.orm.call('res.multi_platform.apps', 'upload_chunk', [], {
                    session_id: sessionId,
                    chunk_index: currentChunk,
                    total_chunks: totalChunks,
                    chunk_content: chunkContent,
                    filename: file.name,
                    force_update: this.state.forceUpdate,
                });

                // 更新进度
                currentChunk++;
                this.state.progress = Math.round((currentChunk / totalChunks) * 100);
            }

            // 完成上传
            const result = await this.orm.call('res.multi_platform.apps', 'complete_upload', [], {
                session_id: sessionId,
                filename: file.name,
                force_update: this.state.forceUpdate,
            });

            if (result) {
                this.notification.add(_t('Upload successful'), {
                    type: 'success',
                });

                if (result.type === 'ir.actions.act_window') {
                    await this.action.doAction(result);
                }
            }
        } catch (error) {
            this.notification.add(error.message || _t('Upload failed'), {
                type: 'danger',
            });
            console.error('Upload failed:', error);
        } finally {
            this.state.uploading = false;
            this.state.progress = 0;
            this.state.forceUpdate = false;
        }
    }

    /**
     * 处理文件选择
     * @param {Object} fileData 文件数据对象
     */
    async onFileUploaded(fileData) {
        console.log('文件数据对象', fileData);
        try {
            if (!fileData || !fileData.data) {
                throw new Error(_t('Invalid file data'));
            }

            
            // 检查文件扩展名，获取平台类型
            const ext = fileData.name.split('.').pop().toLowerCase();
            console.log('文件扩展名', ext);
            let platform;
            switch (ext) {
                case 'exe':
                    platform = 'windows';
                    break;
                case 'apk':
                    platform = 'android';
                    break;
                default:
                    throw new Error(_t('Unsupported file types'));
            }

            console.log('文件上传大小', fileData.size);
            console.log('Odoo 默认最大文件上传大小', DEFAULT_MAX_FILE_SIZE);
            // 根据文件大小决定是否需要分片
            if (fileData.size <= DEFAULT_MAX_FILE_SIZE) {
                console.log('直接上传', fileData.size);
                // 小文件直接上传
                const base64Content = await this.chunkToBase64(file);
                const content = base64Content.split(',')[1];

                // 上传文件
                const result = await this.orm.call('res.multi_platform.apps', 'upload_small_file', [], {
                    session_id: sessionId,
                    file_content: content,
                    filename: file.name,
                    force_update: this.state.forceUpdate,
                });

                this.state.progress = 100;

                if (result) {
                    this.notification.add(_t('Upload successful'), {
                        type: 'success',
                    });

                    if (result.type === 'ir.actions.act_window') {
                        await this.action.doAction(result);
                    }
                }
            } else {
                await this.uploadAppFileInChunks(fileData);
            }
        } catch (error) {
            console.error('File upload failed:', error);
            this.notification.add(error.message || _t('Upload failed'), {
                type: 'danger',
            });
        } finally {
        }
    }
}

export const appFileUploader = {
    component: AppFileUploader,
};

registry.category('view_widgets').add('app_file_uploader', appFileUploader);

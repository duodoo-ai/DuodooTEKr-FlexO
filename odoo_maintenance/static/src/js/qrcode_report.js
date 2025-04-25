document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM Loaded");

    // 状态选择
    document.querySelectorAll('.status-btn').forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.status-btn').forEach(b =>
                    b.classList.remove('active'));
                this.classList.add('active');
                document.querySelector('input[name="status"]').value =
                    this.dataset.status;
            });
        } else {
            console.error("Status button not found");
        }
    });

    // 图片上传
    const cameraInput = document.getElementById('cameraInput');
    if (cameraInput) {
        cameraInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const img = document.getElementById('imagePreview');
                    if (img) {
                        img.src = event.target.result;
                        img.classList.remove('d-none');
                    } else {
                        console.error("Image preview element not found");
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    } else {
        console.error("Camera input element not found");
    }

    // 表单提交
    const inspectionForm = document.getElementById('inspectionForm');
    if (inspectionForm) {
        inspectionForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const imageFile = document.getElementById('cameraInput').files[0];

            if (imageFile) {
                const reader = new FileReader();
                reader.readAsDataURL(imageFile);
                reader.onload = () => {
                    formData.append('image', reader.result);
                    submitForm(formData);
                };
            } else {
                submitForm(formData);
            }
        });
    } else {
        console.error("Inspection form element not found");
    }

    async function submitForm(formData) {
        try {
            const response = await odoo.jsonRpc(
                '/equipment/submit_inspection',
                'call',
                Object.fromEntries(formData.entries())
            );

            if (response.success) {
                window.location.href = `/web#id=${response.inspection_id}&model=equipment.inspection&view_type=form`;
            } else {
                console.error("Form submission failed:", response);
            }
        } catch (error) {
            console.error("Error submitting form:", error);
        }
    }
});
// static/js/preview.js

document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const selectFileBtn = document.getElementById("select-file-btn");
    const previewContainer = document.getElementById("preview-container");
    const uploadPrompt = document.getElementById("upload-prompt");
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    fileNameDisplay.style.display = 'none';

    // Use a Map to store staged files, making it easy to avoid duplicates.
    const stagedFiles = new Map();

    // When the "Select file" button is clicked, trigger the hidden file input
    selectFileBtn.addEventListener("click", () => {
        fileInput.click();
    });

    // Listen for file selection through the file input
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            addFilesToStage(fileInput.files);
        }
    });

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone when a file is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drop-zone--over'), false);
    });

    // Remove highlight when file leaves the drop zone
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('drop-zone--over'), false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        if (dt.files.length > 0) {
            addFilesToStage(dt.files);
        }
    }, false);

    /**
     * Creates a reasonably unique ID for a file object based on its properties.
     * @param {File} file The file object.
     * @returns {string} A unique identifier for the file.
     */
    const getFileId = (file) => {
        return `${file.name}-${file.size}-${file.lastModified}`;
    };

    /**
     * Adds new files to the staging area, avoiding duplicates.
     * @param {FileList} files The files to add.
     */
    function addFilesToStage(files) {
        Array.from(files).forEach(file => {
            const fileId = getFileId(file);
            if (!stagedFiles.has(fileId)) {
                stagedFiles.set(fileId, file);
            }
        });
        updateFileInputAndRenderPreviews();
    }

    /**
     * Syncs the file input with our staged files and re-renders the previews.
     */
    function updateFileInputAndRenderPreviews() {
        // Create a new FileList and assign it to the input
        const dataTransfer = new DataTransfer();
        stagedFiles.forEach(file => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;

        // Re-render the previews
        renderPreviews(Array.from(stagedFiles.values()));
    }

    /**
     * Handles multiple files and generates previews for each.
     * @param {File[]} files The files to render previews for.
     */
    function renderPreviews(files) {
        // Hide the prompt and clear any old previews
        uploadPrompt.style.display = 'none';
        previewContainer.innerHTML = '';

        files.forEach(file => {
            const fileId = getFileId(file);
            const filePreview = document.createElement('div');
            filePreview.className = 'file-preview';
            filePreview.title = file.name; // Show filename on hover
            filePreview.dataset.fileId = fileId; // Associate preview with a unique file ID

            // Create the overlay
            const overlay = document.createElement('div');
            overlay.className = 'overlay';

            const fileName = document.createElement('div');
            fileName.className = 'file-name';
            fileName.textContent = file.name;

            const fileSize = document.createElement('div');
            fileSize.className = 'file-size';
            fileSize.textContent = `${(file.size / 1024).toFixed(2)} KB`; // Convert size to KB

            overlay.appendChild(fileName);
            overlay.appendChild(fileSize);

            // Append the overlay to the preview
            filePreview.appendChild(overlay);

            // 🖼️ For an image file
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    const img = document.createElement('img');
                    img.src = event.target.result;
                    filePreview.appendChild(img);
                    addRemoveButton(filePreview);
                };
                reader.readAsDataURL(file);

            // 📜 For a PDF file
            } else if (file.type === 'application/pdf') {
                const reader = new FileReader();
                const pdfjsLib = window['pdfjs-dist/build/pdf'];
                reader.onload = function (event) {
                    const typedarray = new Uint8Array(event.target.result);
                    pdfjsLib.getDocument(typedarray).promise.then(function (pdf) {
                        pdf.getPage(1).then(function (page) {
                            const canvas = document.createElement('canvas');
                            const context = canvas.getContext('2d');
                            const viewport = page.getViewport({ scale: 0.4 });
                            canvas.height = viewport.height;
                            canvas.width = viewport.width;

                            const renderContext = { canvasContext: context, viewport: viewport };
                            const renderTask = page.render(renderContext);

                            renderTask.promise.then(function () {
                                filePreview.appendChild(canvas);
                                addRemoveButton(filePreview);
                            });
                        });
                    }, function (reason) {
                        console.error(reason);
                        filePreview.innerHTML = '<p>Error loading PDF preview.</p>';
                    });
                };
                reader.readAsArrayBuffer(file);

            // 📁 For any other file
            } else {
                const otherFileDiv = document.createElement('div');
                otherFileDiv.className = 'file-info';
                otherFileDiv.innerHTML = `<span class="icon">📁</span><p>${file.name}</p>`;
                filePreview.appendChild(otherFileDiv);
                addRemoveButton(filePreview);
            }

            previewContainer.appendChild(filePreview);
        });

        // Add a button to select more files if some are already staged
        const addMoreContainer = document.getElementById('add-more-container');
        if (addMoreContainer) addMoreContainer.remove();

        if (files.length > 0) {
            const container = document.createElement('div');
            container.id = 'add-more-container';
            container.className = 'text-center mt-3';
            container.innerHTML = `<button type="button" id="select-more-files-btn" class="btn" style="background-color: rgba(128, 128, 128, 0.114);">Select more files</button>`;
            dropZone.appendChild(container);

            document.getElementById('select-more-files-btn').addEventListener('click', () => fileInput.click());
        }
    }

    /**
     * Helper function to create and add the remove button.
     */
    function addRemoveButton(filePreview) {
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'remove-file-btn';
        removeBtn.innerHTML = '&times;';
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent the drop zone click event

            const previewToRemove = e.target.closest('.file-preview');
            const fileIdToRemove = previewToRemove.dataset.fileId;

            // Remove the file from our staging map
            stagedFiles.delete(fileIdToRemove);

            // Re-sync the input and re-render the previews
            updateFileInputAndRenderPreviews();

            // If no files are left, reset the drop zone to its initial state
            if (stagedFiles.size === 0) {
                resetDropZone();
            }
        });
        filePreview.appendChild(removeBtn);
    }

    /**
     * Resets the drop zone to its initial state.
     */
    function resetDropZone() {
        stagedFiles.clear();
        // Reset the file input by creating an empty FileList
        fileInput.files = new DataTransfer().files;
        previewContainer.innerHTML = '';
        fileNameDisplay.textContent = '';
        fileNameDisplay.style.display = 'none';
        uploadPrompt.style.display = 'block';

        // Remove the "Select more files" button if it exists
        const addMoreContainer = document.getElementById('add-more-container');
        if (addMoreContainer) addMoreContainer.remove();
    }
});
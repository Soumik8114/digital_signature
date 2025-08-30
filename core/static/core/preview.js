// static/js/preview.js

document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const selectFileBtn = document.getElementById("select-file-btn");
    const previewContainer = document.getElementById("preview-container");
    const uploadPrompt = document.getElementById("upload-prompt");
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    fileNameDisplay.style.display = 'none';

    // When the "Select file" button is clicked, trigger the hidden file input
    selectFileBtn.addEventListener("click", () => {
        fileInput.click();
    });

    // Listen for file selection through the file inputcon
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
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
            // Set the dropped file to our file input element
            fileInput.files = dt.files;
            handleFile(dt.files[0]);
        }
    }, false);

    /**
    * Handles the selected file and generates a preview.
    * @param {File} file The file selected by the user.
    */
    function handleFile(file) {
        // Hide the prompt and clear any old preview immediately
        uploadPrompt.style.display = 'none';
        previewContainer.innerHTML = '<p>Loading preview...</p>'; // Optional: Show a loading message

        // 🖼️ For an image file
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (event) {
                // KEY FIX: All DOM manipulation happens *inside* onload
                previewContainer.innerHTML = ''; // Clear loading message

                const img = document.createElement('img');
                img.src = event.target.result;
                previewContainer.appendChild(img);

                addRemoveButton();
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

                        // KEY FIX: Wait for the render to complete before appending to DOM
                        renderTask.promise.then(function () {
                            previewContainer.innerHTML = ''; // Clear loading message        
                            fileNameDisplay.textContent = `File: ${file.name}`;
                            fileNameDisplay.style.display = 'block';
                            previewContainer.appendChild(canvas,);
                            addRemoveButton();
                        });
                    });
                }, function (reason) {
                    // PDF loading error
                    console.error(reason);
                    previewContainer.innerHTML = '<p>Error loading PDF preview.</p>';
                });
            };
            reader.readAsArrayBuffer(file);

            // 📁 For any other file
        } else {
            previewContainer.innerHTML = ''; // Clear loading message
            const otherFileDiv = document.createElement('div');
            otherFileDiv.className = 'file-info';
            otherFileDiv.innerHTML = `<span class="icon">📁</span><p>${file.name}</p>`;
            previewContainer.appendChild(otherFileDiv);
            addRemoveButton();
        }
    }

    /**
     * Helper function to create and add the remove button.
     */
    function addRemoveButton() {
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'remove-file-btn';
        removeBtn.innerHTML = '&times;';
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            resetDropZone();
        });
        previewContainer.appendChild(removeBtn);
    }

    /**
     * Resets the drop zone to its initial state.
     */
    function resetDropZone() {
        fileInput.value = null;
        previewContainer.innerHTML = '';
        fileNameDisplay.textContent = '';
        fileNameDisplay.style.display = 'none';
        uploadPrompt.style.display = 'block';
    }
});
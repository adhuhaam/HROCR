// Upload functionality with drag and drop
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const filePreview = document.getElementById('filePreview');
    const processingStatus = document.getElementById('processingStatus');
    
    let selectedFile = null;
    
    // Drag and drop events
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        if (!dropZone.contains(e.relatedTarget)) {
            dropZone.classList.remove('drag-over');
        }
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });
    
    // Form submission
    uploadForm.addEventListener('submit', function(e) {
        if (!selectedFile) {
            e.preventDefault();
            alert('Please select a file first.');
            return;
        }
        
        // Show processing status
        processingStatus.style.display = 'block';
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    });
    
    function handleFileSelection(file) {
        // Validate file type
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            alert('Invalid file type. Please select a PNG, JPG, JPEG, or PDF file.');
            return;
        }
        
        // Validate file size (16MB limit)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            alert('File is too large. Please select a file smaller than 16MB.');
            return;
        }
        
        selectedFile = file;
        
        // Update file input
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        
        // Show file preview
        showFilePreview(file);
        
        // Enable submit button
        submitBtn.disabled = false;
    }
    
    function showFilePreview(file) {
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileIcon = document.getElementById('fileIcon');
        
        // Update file info
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        // Update icon based on file type
        if (file.type === 'application/pdf') {
            fileIcon.className = 'fas fa-file-pdf fa-2x me-3 text-danger';
        } else {
            fileIcon.className = 'fas fa-file-image fa-2x me-3 text-success';
        }
        
        // Show preview and hide drop zone content
        document.querySelector('.drop-zone-content').style.display = 'none';
        filePreview.style.display = 'block';
        
        // Add selected state to drop zone
        dropZone.classList.add('file-selected');
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Clear file function (global for onclick)
    window.clearFile = function() {
        selectedFile = null;
        fileInput.value = '';
        
        // Hide preview and show drop zone content
        filePreview.style.display = 'none';
        document.querySelector('.drop-zone-content').style.display = 'block';
        
        // Remove selected state
        dropZone.classList.remove('file-selected');
        
        // Disable submit button
        submitBtn.disabled = true;
    };
});

// filemanager.js - Enhanced File Manager JavaScript

class FileManager {
    constructor() {
        this.currentPath = '/';
        this.currentPage = 1;
        this.itemsPerPage = 20;
        this.selectedFiles = new Set();
        this.files = [];
        this.filteredFiles = [];
        this.currentFile = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadFiles();
    }

    initializeElements() {
        // File list and controls
        this.fmList = document.getElementById('fm-list');
        this.searchInput = document.getElementById('search');
        this.typeFilter = document.getElementById('type-filter');
        this.refreshBtn = document.getElementById('refresh');
        
        // Breadcrumb
        this.breadcrumb = document.getElementById('breadcrumb');
        
        // Multi-select
        this.multiActions = document.getElementById('multi-actions');
        this.selectedCount = document.getElementById('selected-count');
        this.deleteSelectedBtn = document.getElementById('delete-selected');
        this.clearSelectionBtn = document.getElementById('clear-selection');
        
        // Buttons
        this.uploadBtn = document.getElementById('upload-btn');
        this.createFolderBtn = document.getElementById('create-folder-btn');
        this.uploadEmptyBtn = document.getElementById('upload-empty');
        
        // Modals
        this.modalUpload = document.getElementById('modal-upload');
        this.modalCreateFolder = document.getElementById('modal-create-folder');
        this.modalRename = document.getElementById('modal-rename');
        this.modalDelete = document.getElementById('modal-delete');
        this.modalInfo = document.getElementById('modal-info');
        
        // Upload elements
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.uploadProgress = document.getElementById('upload-progress');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.uploadStartBtn = document.getElementById('upload-start');
        this.uploadCancelBtn = document.getElementById('upload-cancel');
        
        // Create folder elements
        this.folderNameInput = document.getElementById('folder-name-input');
        this.createFolderCancelBtn = document.getElementById('create-folder-cancel');
        this.createFolderSaveBtn = document.getElementById('create-folder-save');
        
        // Rename elements
        this.renameInput = document.getElementById('rename-input');
        this.renameCancelBtn = document.getElementById('rename-cancel');
        this.renameSaveBtn = document.getElementById('rename-save');
        
        // Delete elements
        this.deleteMessage = document.getElementById('delete-message');
        this.deleteCancelBtn = document.getElementById('delete-cancel');
        this.deleteConfirmBtn = document.getElementById('delete-confirm');
        
        // Info elements
        this.infoCloseBtn = document.getElementById('info-close');
        
        // Pagination
        this.pagination = document.getElementById('pagination');
        this.prevPageBtn = document.getElementById('prev-page');
        this.nextPageBtn = document.getElementById('next-page');
        this.pageInfo = document.getElementById('page-info');
        
        // Mini player
        this.miniPlayer = document.getElementById('mini-player');
        this.miniMediaArea = document.getElementById('mini-media-area');
        this.miniCloseBtn = document.getElementById('mini-close');
        this.miniPlayBtn = document.getElementById('mini-play');
        this.miniPrevBtn = document.getElementById('mini-prev');
        this.miniNextBtn = document.getElementById('mini-next');
        
        // States
        this.loadingIndicator = document.getElementById('loading');
        this.emptyState = document.getElementById('empty-state');
        
        // Toast container
        this.toastContainer = document.getElementById('toast-container');
    }

    bindEvents() {
        // Search and filter
        this.searchInput.addEventListener('input', () => this.filterFiles());
        this.typeFilter.addEventListener('change', () => this.filterFiles());
        this.refreshBtn.addEventListener('click', () => this.loadFiles());
        
        // Upload
        this.uploadBtn.addEventListener('click', () => this.showUploadModal());
        this.uploadEmptyBtn.addEventListener('click', () => this.showUploadModal());
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        this.fileInput.addEventListener('change', () => this.handleFileSelect());
        this.uploadStartBtn.addEventListener('click', () => this.startUpload());
        this.uploadCancelBtn.addEventListener('click', () => this.hideUploadModal());
        
        // Create folder
        this.createFolderBtn.addEventListener('click', () => this.showCreateFolderModal());
        this.createFolderSaveBtn.addEventListener('click', () => this.createFolder());
        this.createFolderCancelBtn.addEventListener('click', () => this.hideCreateFolderModal());
        
        // Multi-select
        this.deleteSelectedBtn.addEventListener('click', () => this.deleteSelectedFiles());
        this.clearSelectionBtn.addEventListener('click', () => this.clearSelection());
        
        // Rename
        this.renameSaveBtn.addEventListener('click', () => this.renameFile());
        this.renameCancelBtn.addEventListener('click', () => this.hideRenameModal());
        
        // Delete
        this.deleteConfirmBtn.addEventListener('click', () => this.confirmDelete());
        this.deleteCancelBtn.addEventListener('click', () => this.hideDeleteModal());
        
        // Info
        this.infoCloseBtn.addEventListener('click', () => this.hideInfoModal());
        
        // Pagination
        this.prevPageBtn.addEventListener('click', () => this.previousPage());
        this.nextPageBtn.addEventListener('click', () => this.nextPage());
        
        // Mini player
        this.miniCloseBtn.addEventListener('click', () => this.hideMiniPlayer());
        this.miniPlayBtn.addEventListener('click', () => this.togglePlayPause());
        this.miniPrevBtn.addEventListener('click', () => this.playPrevious());
        this.miniNextBtn.addEventListener('click', () => this.playNext());
        
        // Close modals on background click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideAllModals();
                }
            });
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    // ======================================
    // FILE MANAGEMENT
    // ======================================

    async loadFiles() {
        this.showLoading();
        
        try {
            const response = await fetch(`/api/files?path=${encodeURIComponent(this.currentPath)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.files = data.files || [];
            this.renderFiles();
            
        } catch (error) {
            console.error('Error loading files:', error);
            this.showToast('Gagal memuat file', 'error');
        } finally {
            this.hideLoading();
        }
    }

    renderFiles() {
        // Apply filters
        this.filterFiles();
        
        // Calculate pagination
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const filesToShow = this.filteredFiles.slice(startIndex, endIndex);
        
        // Clear file list
        this.fmList.innerHTML = '';
        
        if (filesToShow.length === 0) {
            this.showEmptyState();
            this.hidePagination();
            return;
        }
        
        this.hideEmptyState();
        
        // Render files
        filesToShow.forEach(file => {
            const fileElement = this.createFileElement(file);
            this.fmList.appendChild(fileElement);
        });
        
        // Update pagination
        this.updatePagination();
    }

    createFileElement(file) {
        const fileDiv = document.createElement('div');
        fileDiv.className = `file-item ${this.selectedFiles.has(file.id) ? 'selected' : ''}`;
        fileDiv.dataset.id = file.id;
        fileDiv.dataset.type = file.type;
        fileDiv.dataset.path = file.path;
        
        const fileIcon = this.getFileIcon(file);
        const fileSize = this.formatFileSize(file.size);
        
        fileDiv.innerHTML = `
            <input type="checkbox" class="file-checkbox" ${this.selectedFiles.has(file.id) ? 'checked' : ''}>
            <div class="file-icon">${fileIcon}</div>
            <div class="file-name" title="${file.name}">${file.name}</div>
            <div class="file-size">${fileSize}</div>
            <div class="file-actions">
                <button class="file-action-btn" data-action="info" title="Info">
                    <i class="fas fa-info-circle"></i>
                </button>
                ${file.type !== 'folder' ? `
                    <button class="file-action-btn" data-action="preview" title="Preview">
                        <i class="fas fa-play"></i>
                    </button>
                ` : ''}
                <button class="file-action-btn" data-action="rename" title="Rename">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="file-action-btn" data-action="delete" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        // Add event listeners
        fileDiv.addEventListener('click', (e) => {
            if (e.target.type !== 'checkbox' && !e.target.closest('.file-action-btn')) {
                if (file.type === 'folder') {
                    this.navigateToFolder(file.path);
                } else {
                    this.previewFile(file);
                }
            }
        });
        
        const checkbox = fileDiv.querySelector('.file-checkbox');
        checkbox.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleFileSelection(file.id, checkbox.checked);
        });
        
        fileDiv.querySelectorAll('.file-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                this.handleFileAction(action, file);
            });
        });
        
        return fileDiv;
    }

    getFileIcon(file) {
        const icons = {
            folder: 'fas fa-folder',
            mp3: 'fas fa-music',
            video: 'fas fa-video',
            image: 'fas fa-image',
            pdf: 'fas fa-file-pdf',
            document: 'fas fa-file-word',
            text: 'fas fa-file-alt',
            zip: 'fas fa-file-archive',
            default: 'fas fa-file'
        };
        
        if (file.type === 'folder') return `<i class="${icons.folder}"></i>`;
        
        const extension = file.name.split('.').pop().toLowerCase();
        
        if (['mp3', 'wav', 'ogg', 'flac'].includes(extension)) {
            return `<i class="${icons.mp3}"></i>`;
        } else if (['mp4', 'avi', 'mkv', 'mov', 'wmv'].includes(extension)) {
            return `<i class="${icons.video}"></i>`;
        } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(extension)) {
            return `<i class="${icons.image}"></i>`;
        } else if (extension === 'pdf') {
            return `<i class="${icons.pdf}"></i>`;
        } else if (['doc', 'docx', 'odt'].includes(extension)) {
            return `<i class="${icons.document}"></i>`;
        } else if (['txt', 'rtf'].includes(extension)) {
            return `<i class="${icons.text}"></i>`;
        } else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) {
            return `<i class="${icons.zip}"></i>`;
        } else {
            return `<i class="${icons.default}"></i>`;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0 || bytes === undefined) return '0 B';
        
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    // ======================================
    // NAVIGATION & BREADCRUMB
    // ======================================

    navigateToFolder(path) {
        this.currentPath = path;
        this.currentPage = 1;
        this.selectedFiles.clear();
        this.updateMultiSelectUI();
        this.updateBreadcrumb();
        this.loadFiles();
    }

    updateBreadcrumb() {
        this.breadcrumb.innerHTML = '';
        
        // Add home button
        const homeLink = document.createElement('a');
        homeLink.href = '#';
        homeLink.className = 'breadcrumb-home';
        homeLink.innerHTML = '<i class="fas fa-home"></i> Root';
        homeLink.addEventListener('click', (e) => {
            e.preventDefault();
            this.navigateToFolder('/');
        });
        this.breadcrumb.appendChild(homeLink);
        
        // Build path segments
        const segments = this.currentPath.split('/').filter(segment => segment !== '');
        let currentPath = '';
        
        segments.forEach((segment, index) => {
            const separator = document.createElement('span');
            separator.className = 'breadcrumb-separator';
            separator.textContent = '/';
            this.breadcrumb.appendChild(separator);
            
            currentPath += '/' + segment;
            
            const link = document.createElement('a');
            link.href = '#';
            link.textContent = segment;
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToFolder(currentPath);
            });
            
            this.breadcrumb.appendChild(link);
        });
    }

    // ======================================
    // FILTERING & SEARCH
    // ======================================

    filterFiles() {
        const searchTerm = this.searchInput.value.toLowerCase();
        const filterType = this.typeFilter.value;
        
        this.filteredFiles = this.files.filter(file => {
            // Apply search filter
            if (searchTerm && !file.name.toLowerCase().includes(searchTerm)) {
                return false;
            }
            
            // Apply type filter
            if (filterType !== 'all') {
                if (filterType === 'folder' && file.type !== 'folder') {
                    return false;
                } else if (filterType !== 'folder') {
                    const extension = file.name.split('.').pop().toLowerCase();
                    
                    switch (filterType) {
                        case 'mp3':
                            if (!['mp3', 'wav', 'ogg', 'flac'].includes(extension)) return false;
                            break;
                        case 'video':
                            if (!['mp4', 'avi', 'mkv', 'mov', 'wmv'].includes(extension)) return false;
                            break;
                        case 'image':
                            if (!['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(extension)) return false;
                            break;
                        case 'document':
                            if (!['pdf', 'doc', 'docx', 'txt', 'rtf'].includes(extension)) return false;
                            break;
                        case 'upload':
                            // Custom logic for uploads folder if needed
                            break;
                    }
                }
            }
            
            return true;
        });
        
        this.currentPage = 1;
        this.renderFiles();
    }

    // ======================================
    // MULTI-SELECT
    // ======================================

    toggleFileSelection(fileId, selected) {
        if (selected) {
            this.selectedFiles.add(fileId);
        } else {
            this.selectedFiles.delete(fileId);
        }
        
        this.updateMultiSelectUI();
    }

    updateMultiSelectUI() {
        const count = this.selectedFiles.size;
        
        if (count > 0) {
            this.multiActions.classList.remove('hidden');
            this.selectedCount.textContent = `${count} item dipilih`;
        } else {
            this.multiActions.classList.add('hidden');
        }
        
        // Update file items visual state
        document.querySelectorAll('.file-item').forEach(item => {
            const fileId = item.dataset.id;
            if (this.selectedFiles.has(fileId)) {
                item.classList.add('selected');
                item.querySelector('.file-checkbox').checked = true;
            } else {
                item.classList.remove('selected');
                item.querySelector('.file-checkbox').checked = false;
            }
        });
    }

    clearSelection() {
        this.selectedFiles.clear();
        this.updateMultiSelectUI();
    }

    // ======================================
    // FILE OPERATIONS
    // ======================================

    handleFileAction(action, file) {
        switch (action) {
            case 'info':
                this.showFileInfo(file);
                break;
            case 'preview':
                this.previewFile(file);
                break;
            case 'rename':
                this.showRenameModal(file);
                break;
            case 'delete':
                this.showDeleteModal(file);
                break;
        }
    }

    async createFolder() {
        const folderName = this.folderNameInput.value.trim();
        
        if (!folderName) {
            this.showToast('Nama folder tidak boleh kosong', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/folders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    path: this.currentPath,
                    name: folderName
                })
            });
            
            if (response.ok) {
                this.showToast('Folder berhasil dibuat', 'success');
                this.hideCreateFolderModal();
                this.loadFiles();
            } else {
                throw new Error('Gagal membuat folder');
            }
        } catch (error) {
            console.error('Error creating folder:', error);
            this.showToast('Gagal membuat folder', 'error');
        }
    }

    async renameFile() {
        const newName = this.renameInput.value.trim();
        
        if (!newName) {
            this.showToast('Nama file tidak boleh kosong', 'error');
            return;
        }
        
        if (!this.currentFile) return;
        
        try {
            const response = await fetch('/api/files/rename', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    oldPath: this.currentFile.path,
                    newName: newName
                })
            });
            
            if (response.ok) {
                this.showToast('File berhasil diubah nama', 'success');
                this.hideRenameModal();
                this.loadFiles();
            } else {
                throw new Error('Gagal mengubah nama file');
            }
        } catch (error) {
            console.error('Error renaming file:', error);
            this.showToast('Gagal mengubah nama file', 'error');
        }
    }

    async deleteSelectedFiles() {
        if (this.selectedFiles.size === 0) return;
        
        const fileNames = Array.from(this.selectedFiles).map(id => {
            const file = this.files.find(f => f.id === id);
            return file ? file.name : '';
        }).filter(name => name !== '');
        
        this.showDeleteModal(null, fileNames);
    }

    async confirmDelete() {
        let paths = [];
        
        if (this.currentFile) {
            // Single file deletion
            paths = [this.currentFile.path];
        } else if (this.selectedFiles.size > 0) {
            // Multiple files deletion
            paths = Array.from(this.selectedFiles).map(id => {
                const file = this.files.find(f => f.id === id);
                return file ? file.path : '';
            }).filter(path => path !== '');
        }
        
        if (paths.length === 0) return;
        
        try {
            const response = await fetch('/api/files/delete', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ paths })
            });
            
            if (response.ok) {
                this.showToast('File berhasil dihapus', 'success');
                this.hideDeleteModal();
                this.selectedFiles.clear();
                this.updateMultiSelectUI();
                this.loadFiles();
            } else {
                throw new Error('Gagal menghapus file');
            }
        } catch (error) {
            console.error('Error deleting files:', error);
            this.showToast('Gagal menghapus file', 'error');
        }
    }

    // ======================================
    // UPLOAD FUNCTIONALITY
    // ======================================

    showUploadModal() {
        this.hideAllModals();
        this.modalUpload.classList.remove('hidden');
        this.resetUploadForm();
    }

    hideUploadModal() {
        this.modalUpload.classList.add('hidden');
        this.resetUploadForm();
    }

    resetUploadForm() {
        this.fileInput.value = '';
        this.uploadProgress.classList.add('hidden');
        this.progressFill.style.width = '0%';
        this.progressText.textContent = '0%';
        this.uploadStartBtn.disabled = true;
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.style.background = 'rgba(108, 142, 255, 0.2)';
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadArea.style.background = '';
        
        const files = e.dataTransfer.files;
        this.handleFiles(files);
    }

    handleFileSelect() {
        const files = this.fileInput.files;
        this.handleFiles(files);
    }

    handleFiles(files) {
        if (files.length > 0) {
            this.uploadStartBtn.disabled = false;
            // In a real implementation, you might want to show file names
        }
    }

    async startUpload() {
        const files = this.fileInput.files;
        
        if (files.length === 0) {
            this.showToast('Pilih file terlebih dahulu', 'error');
            return;
        }
        
        this.uploadProgress.classList.remove('hidden');
        this.uploadStartBtn.disabled = true;
        
        const formData = new FormData();
        formData.append('path', this.currentPath);
        
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
        
        try {
            const response = await fetch('/api/files/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                this.showToast('File berhasil diupload', 'success');
                this.hideUploadModal();
                this.loadFiles();
            } else {
                throw new Error('Upload gagal');
            }
        } catch (error) {
            console.error('Error uploading files:', error);
            this.showToast('Upload gagal', 'error');
        } finally {
            this.uploadProgress.classList.add('hidden');
        }
        
        // Simulate progress (in real implementation, use XMLHttpRequest with progress events)
        this.simulateUploadProgress();
    }

    simulateUploadProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            this.progressFill.style.width = `${progress}%`;
            this.progressText.textContent = `${progress}%`;
            
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 100);
    }

    // ======================================
    // FILE PREVIEW
    // ======================================

    previewFile(file) {
        const extension = file.name.split('.').pop().toLowerCase();
        
        this.miniMediaArea.innerHTML = '';
        
        if (['mp3', 'wav', 'ogg', 'flac'].includes(extension)) {
            this.previewAudio(file);
        } else if (['mp4', 'avi', 'mkv', 'mov', 'wmv'].includes(extension)) {
            this.previewVideo(file);
        } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(extension)) {
            this.previewImage(file);
        } else {
            this.showToast('Format file tidak didukung untuk preview', 'info');
            return;
        }
        
        this.showMiniPlayer();
    }

    previewAudio(file) {
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = `/api/files/preview?path=${encodeURIComponent(file.path)}`;
        
        this.miniMediaArea.appendChild(audio);
        this.currentMedia = audio;
    }

    previewVideo(file) {
        const video = document.createElement('video');
        video.controls = true;
        video.src = `/api/files/preview?path=${encodeURIComponent(file.path)}`;
        video.style.width = '100%';
        
        this.miniMediaArea.appendChild(video);
        this.currentMedia = video;
    }

    previewImage(file) {
        const img = document.createElement('img');
        img.src = `/api/files/preview?path=${encodeURIComponent(file.path)}`;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '200px';
        
        this.miniMediaArea.appendChild(img);
        this.currentMedia = null;
    }

    showMiniPlayer() {
        this.miniPlayer.classList.remove('hidden');
    }

    hideMiniPlayer() {
        this.miniPlayer.classList.add('hidden');
        if (this.currentMedia) {
            this.currentMedia.pause();
            this.currentMedia = null;
        }
    }

    togglePlayPause() {
        if (this.currentMedia) {
            if (this.currentMedia.paused) {
                this.currentMedia.play();
                this.miniPlayBtn.innerHTML = '<i class="fas fa-pause"></i>';
            } else {
                this.currentMedia.pause();
                this.miniPlayBtn.innerHTML = '<i class="fas fa-play"></i>';
            }
        }
    }

    playPrevious() {
        // Implementation for playing previous file in the list
        this.showToast('Fitur sebelumnya belum diimplementasikan', 'info');
    }

    playNext() {
        // Implementation for playing next file in the list
        this.showToast('Fitur selanjutnya belum diimplementasikan', 'info');
    }

    // ======================================
    // MODAL MANAGEMENT
    // ======================================

    showCreateFolderModal() {
        this.hideAllModals();
        this.modalCreateFolder.classList.remove('hidden');
        this.folderNameInput.value = '';
        this.folderNameInput.focus();
    }

    hideCreateFolderModal() {
        this.modalCreateFolder.classList.add('hidden');
    }

    showRenameModal(file) {
        this.hideAllModals();
        this.currentFile = file;
        this.modalRename.classList.remove('hidden');
        this.renameInput.value = file.name;
        this.renameInput.focus();
        this.renameInput.select();
    }

    hideRenameModal() {
        this.modalRename.classList.add('hidden');
        this.currentFile = null;
    }

    showDeleteModal(file, fileNames = null) {
        this.hideAllModals();
        this.currentFile = file;
        this.modalDelete.classList.remove('hidden');
        
        if (file) {
            this.deleteMessage.textContent = `Apakah Anda yakin ingin menghapus "${file.name}"?`;
        } else if (fileNames && fileNames.length > 0) {
            if (fileNames.length === 1) {
                this.deleteMessage.textContent = `Apakah Anda yakin ingin menghapus "${fileNames[0]}"?`;
            } else {
                this.deleteMessage.textContent = `Apakah Anda yakin ingin menghapus ${fileNames.length} file?`;
            }
        }
    }

    hideDeleteModal() {
        this.modalDelete.classList.add('hidden');
        this.currentFile = null;
    }

    showFileInfo(file) {
        this.hideAllModals();
        this.currentFile = file;
        
        document.getElementById('info-name').textContent = file.name;
        document.getElementById('info-type').textContent = file.type === 'folder' ? 'Folder' : 'File';
        document.getElementById('info-size').textContent = this.formatFileSize(file.size);
        document.getElementById('info-modified').textContent = new Date(file.modified).toLocaleString();
        document.getElementById('info-path').textContent = file.path;
        
        this.modalInfo.classList.remove('hidden');
    }

    hideInfoModal() {
        this.modalInfo.classList.add('hidden');
        this.currentFile = null;
    }

    hideAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    // ======================================
    // PAGINATION
    // ======================================

    updatePagination() {
        const totalPages = Math.ceil(this.filteredFiles.length / this.itemsPerPage);
        
        if (totalPages <= 1) {
            this.hidePagination();
            return;
        }
        
        this.showPagination();
        this.pageInfo.textContent = `Halaman ${this.currentPage} dari ${totalPages}`;
        
        this.prevPageBtn.disabled = this.currentPage === 1;
        this.nextPageBtn.disabled = this.currentPage === totalPages;
    }

    showPagination() {
        this.pagination.classList.remove('hidden');
    }

    hidePagination() {
        this.pagination.classList.add('hidden');
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.renderFiles();
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.filteredFiles.length / this.itemsPerPage);
        
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.renderFiles();
        }
    }

    // ======================================
    // UI STATE MANAGEMENT
    // ======================================

    showLoading() {
        this.loadingIndicator.classList.remove('hidden');
        this.fmList.classList.add('hidden');
    }

    hideLoading() {
        this.loadingIndicator.classList.add('hidden');
        this.fmList.classList.remove('hidden');
    }

    showEmptyState() {
        this.emptyState.classList.remove('hidden');
        this.fmList.classList.add('hidden');
    }

    hideEmptyState() {
        this.emptyState.classList.add('hidden');
        this.fmList.classList.remove('hidden');
    }

    // ======================================
    // TOAST NOTIFICATIONS
    // ======================================

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="${icons[type] || icons.info}"></i>
            <span>${message}</span>
        `;
        
        this.toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    // ======================================
    // KEYBOARD SHORTCUTS
    // ======================================

    handleKeyboard(e) {
        // Escape key closes modals and mini player
        if (e.key === 'Escape') {
            this.hideAllModals();
            this.hideMiniPlayer();
        }
        
        // Ctrl+A for select all (only when not in input)
        if (e.ctrlKey && e.key === 'a' && !e.target.matches('input, textarea')) {
            e.preventDefault();
            this.selectAllFiles();
        }
        
        // Delete key for deleting selected files
        if (e.key === 'Delete' && this.selectedFiles.size > 0) {
            e.preventDefault();
            this.deleteSelectedFiles();
        }
    }

    selectAllFiles() {
        this.filteredFiles.forEach(file => {
            this.selectedFiles.add(file.id);
        });
        this.updateMultiSelectUI();
    }
}

// ======================================
// INITIALIZATION
// ======================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize File Manager
    window.fileManager = new FileManager();
    
    // Additional initialization for neon effects if needed
    if (typeof initNeon === 'function') {
        initNeon();
    }
});
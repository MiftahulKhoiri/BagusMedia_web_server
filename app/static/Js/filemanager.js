// filemanager.js - Compatible with Your API

class FileManager {
    constructor() {
        this.currentType = 'all';
        this.selectedFiles = new Set();
        this.files = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadFiles();
    }

    initializeElements() {
        // File list and controls from original HTML
        this.fmList = document.getElementById('fm-list');
        this.searchInput = document.getElementById('search');
        this.typeFilter = document.getElementById('type-filter');
        this.refreshBtn = document.getElementById('refresh');
        
        // Modals from original HTML
        this.modalRename = document.getElementById('modal-rename');
        this.renameInput = document.getElementById('rename-input');
        this.renameCancelBtn = document.getElementById('rename-cancel');
        this.renameSaveBtn = document.getElementById('rename-save');
        
        // Mini player from original HTML
        this.miniPlayer = document.getElementById('mini-player');
        this.miniMediaArea = document.getElementById('mini-media-area');
        this.miniCloseBtn = document.getElementById('mini-close');
        
        // Current file for operations
        this.currentFile = null;
        
        // Create loading indicator dynamically
        this.createLoadingIndicator();
    }

    createLoadingIndicator() {
        this.loadingIndicator = document.createElement('div');
        this.loadingIndicator.className = 'loading-indicator';
        this.loadingIndicator.innerHTML = `
            <i class="fas fa-spinner fa-spin"></i>
            <p>Memuat file...</p>
        `;
        this.loadingIndicator.style.display = 'none';
        this.fmList.appendChild(this.loadingIndicator);
    }

    bindEvents() {
        // Original events
        this.searchInput.addEventListener('input', () => this.filterFiles());
        this.typeFilter.addEventListener('change', (e) => {
            this.currentType = e.target.value;
            this.loadFiles();
        });
        this.refreshBtn.addEventListener('click', () => this.loadFiles());
        
        // Rename modal events
        this.renameSaveBtn.addEventListener('click', () => this.renameFile());
        this.renameCancelBtn.addEventListener('click', () => this.hideRenameModal());
        
        // Mini player events
        this.miniCloseBtn.addEventListener('click', () => this.hideMiniPlayer());
        
        // Close modals on background click
        this.modalRename.addEventListener('click', (e) => {
            if (e.target === this.modalRename) {
                this.hideRenameModal();
            }
        });
    }

    async loadFiles() {
        this.showLoading();
        
        try {
            // Using your existing endpoint structure
            const response = await fetch(`/api/files?type=${this.currentType}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.files = data.files || [];
            this.renderFiles();
            
        } catch (error) {
            console.error('Error loading files:', error);
            this.showMessage('Gagal memuat file', 'error');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        this.loadingIndicator.style.display = 'block';
    }

    hideLoading() {
        this.loadingIndicator.style.display = 'none';
    }

    renderFiles() {
        this.fmList.innerHTML = '';
        
        if (this.files.length === 0) {
            this.showEmptyState();
            return;
        }
        
        this.files.forEach(file => {
            const fileElement = this.createFileElement(file);
            this.fmList.appendChild(fileElement);
        });
    }

    createFileElement(file) {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item';
        fileDiv.dataset.type = file.is_folder ? 'folder' : 'file';
        
        const fileIcon = this.getFileIcon(file);
        const fileSize = file.size || '';
        
        fileDiv.innerHTML = `
            <div class="file-icon">${fileIcon}</div>
            <div class="file-name" title="${file.name}">${file.name}</div>
            <div class="file-size">${fileSize}</div>
            <div class="file-actions">
                ${!file.is_folder ? `
                    <button class="file-action-btn" data-action="preview" title="Preview">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="file-action-btn" data-action="download" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                ` : ''}
                <button class="file-action-btn" data-action="rename" title="Rename">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="file-action-btn" data-action="delete" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            ${file.thumbnail ? `
                <div class="file-thumbnail">
                    <img src="${file.thumbnail}" alt="${file.name}" style="max-width: 100px; max-height: 60px;">
                </div>
            ` : ''}
        `;
        
        // Add event listeners
        fileDiv.addEventListener('click', (e) => {
            if (!e.target.closest('.file-action-btn')) {
                if (file.is_folder) {
                    // Folder click - you might want to implement folder navigation
                    this.showMessage('Navigasi folder belum diimplementasikan', 'info');
                } else {
                    this.previewFile(file);
                }
            }
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
        
        if (file.is_folder) return `<i class="${icons.folder}"></i>`;
        
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

    filterFiles() {
        const searchTerm = this.searchInput.value.toLowerCase();
        
        const filteredFiles = this.files.filter(file => {
            // Apply search filter
            if (searchTerm && !file.name.toLowerCase().includes(searchTerm)) {
                return false;
            }
            return true;
        });
        
        this.renderFilteredFiles(filteredFiles);
    }

    renderFilteredFiles(filteredFiles) {
        this.fmList.innerHTML = '';
        
        if (filteredFiles.length === 0) {
            this.showEmptyState();
            return;
        }
        
        filteredFiles.forEach(file => {
            const fileElement = this.createFileElement(file);
            this.fmList.appendChild(fileElement);
        });
    }

    showEmptyState() {
        this.fmList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-folder-open"></i>
                <h3>Folder Kosong</h3>
                <p>Tidak ada file di folder ini</p>
            </div>
        `;
    }

    handleFileAction(action, file) {
        switch (action) {
            case 'preview':
                this.previewFile(file);
                break;
            case 'download':
                this.downloadFile(file);
                break;
            case 'rename':
                this.showRenameModal(file);
                break;
            case 'delete':
                this.deleteFile(file);
                break;
        }
    }

    previewFile(file) {
        // Determine file type for preview
        const extension = file.name.split('.').pop().toLowerCase();
        
        this.miniMediaArea.innerHTML = '';
        
        if (['mp3', 'wav', 'ogg', 'flac'].includes(extension)) {
            this.previewAudio(file);
        } else if (['mp4', 'avi', 'mkv', 'mov', 'wmv'].includes(extension)) {
            this.previewVideo(file);
        } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(extension)) {
            this.previewImage(file);
        } else {
            this.showMessage('Format file tidak didukung untuk preview', 'info');
            return;
        }
        
        this.showMiniPlayer();
    }

    previewAudio(file) {
        const audio = document.createElement('audio');
        audio.controls = true;
        // Use the path from your API response or construct download URL
        audio.src = file.path || `/filemanager/download?folder=${file.folder_key}&filename=${encodeURIComponent(file.name)}`;
        
        this.miniMediaArea.appendChild(audio);
        this.currentMedia = audio;
    }

    previewVideo(file) {
        const video = document.createElement('video');
        video.controls = true;
        video.src = file.path || `/filemanager/download?folder=${file.folder_key}&filename=${encodeURIComponent(file.name)}`;
        video.style.width = '100%';
        
        this.miniMediaArea.appendChild(video);
        this.currentMedia = video;
    }

    previewImage(file) {
        const img = document.createElement('img');
        img.src = file.path || `/filemanager/download?folder=${file.folder_key}&filename=${encodeURIComponent(file.name)}`;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '200px';
        
        this.miniMediaArea.appendChild(img);
        this.currentMedia = null;
    }

    downloadFile(file) {
        // Use your existing download endpoint
        const downloadUrl = `/filemanager/download?folder=${file.folder_key}&filename=${encodeURIComponent(file.name)}`;
        window.open(downloadUrl, '_blank');
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

    showRenameModal(file) {
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

    async renameFile() {
        const newName = this.renameInput.value.trim();
        
        if (!newName) {
            this.showMessage('Nama file tidak boleh kosong', 'error');
            return;
        }
        
        if (!this.currentFile) return;
        
        try {
            // Using your existing rename endpoint
            const response = await fetch('/api/rename-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    folder: this.currentFile.folder_key,
                    old_name: this.currentFile.name,
                    new_name: newName
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.status === 'ok') {
                this.showMessage('File berhasil diubah nama', 'success');
                this.hideRenameModal();
                this.loadFiles();
            } else {
                throw new Error(result.error || 'Gagal mengubah nama file');
            }
        } catch (error) {
            console.error('Error renaming file:', error);
            this.showMessage(error.message, 'error');
        }
    }

    async deleteFile(file) {
        if (!confirm(`Apakah Anda yakin ingin menghapus "${file.name}"?`)) {
            return;
        }
        
        try {
            // Using your existing delete endpoint
            const response = await fetch('/api/delete-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    folder: file.folder_key,
                    filename: file.name
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.status === 'ok') {
                this.showMessage('File berhasil dihapus', 'success');
                this.loadFiles();
            } else {
                throw new Error(result.error || 'Gagal menghapus file');
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            this.showMessage(error.message, 'error');
        }
    }

    showMessage(message, type = 'info') {
        // Simple message display - you can enhance this with toast notifications later
        alert(`${type.toUpperCase()}: ${message}`);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.fileManager = new FileManager();
});
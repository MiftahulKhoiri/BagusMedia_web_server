// filemanager.js - Enhanced and Compatible with Your API

class FileManager {
    constructor() {
        this.currentType = 'all';
        this.selectedFiles = new Set();
        this.files = [];
        this.filteredFiles = [];
        this.currentFile = null;
        this.currentMedia = null;
        this.isPlaying = false;
        
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
        this.currentPath = document.getElementById('current-path');
        this.fileCount = document.getElementById('file-count');
        
        // Multi-select
        this.multiActions = document.getElementById('multi-actions');
        this.selectedCount = document.getElementById('selected-count');
        this.deleteSelectedBtn = document.getElementById('delete-selected');
        this.clearSelectionBtn = document.getElementById('clear-selection');
        
        // Modals
        this.modalRename = document.getElementById('modal-rename');
        this.modalDelete = document.getElementById('modal-delete');
        this.modalInfo = document.getElementById('modal-info');
        
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
        
        // Mini player
        this.miniPlayer = document.getElementById('mini-player');
        this.miniMediaArea = document.getElementById('mini-media-area');
        this.miniCloseBtn = document.getElementById('mini-close');
        this.miniPlayBtn = document.getElementById('mini-play');
        this.miniPrevBtn = document.getElementById('mini-prev');
        this.miniNextBtn = document.getElementById('mini-next');
        this.miniTitle = document.getElementById('mini-title');
        
        // Toast container
        this.toastContainer = document.getElementById('toast-container');
        
        // Create loading indicator
        this.createLoadingIndicator();
    }

    createLoadingIndicator() {
        this.loadingIndicator = document.createElement('div');
        this.loadingIndicator.className = 'loading-indicator';
        this.loadingIndicator.innerHTML = `
            <i class="fas fa-spinner fa-spin"></i>
            <p>Memuat file...</p>
        `;
        this.fmList.appendChild(this.loadingIndicator);
    }

    bindEvents() {
        // Search and filter
        this.searchInput.addEventListener('input', () => this.filterFiles());
        this.typeFilter.addEventListener('change', (e) => {
            this.currentType = e.target.value;
            this.updatePathInfo();
            this.loadFiles();
        });
        this.refreshBtn.addEventListener('click', () => this.loadFiles());
        
        // Multi-select
        this.deleteSelectedBtn.addEventListener('click', () => this.deleteSelectedFiles());
        this.clearSelectionBtn.addEventListener('click', () => this.clearSelection());
        
        // Rename modal
        this.renameSaveBtn.addEventListener('click', () => this.renameFile());
        this.renameCancelBtn.addEventListener('click', () => this.hideRenameModal());
        
        // Delete modal
        this.deleteConfirmBtn.addEventListener('click', () => this.confirmDelete());
        this.deleteCancelBtn.addEventListener('click', () => this.hideDeleteModal());
        
        // Info modal
        this.infoCloseBtn.addEventListener('click', () => this.hideInfoModal());
        
        // Mini player
        this.miniCloseBtn.addEventListener('click', () => this.hideMiniPlayer());
        this.miniPlayBtn.addEventListener('click', () => this.togglePlayPause());
        
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
        
        // Select all with Ctrl+A
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'a') {
                e.preventDefault();
                this.selectAllFiles();
            }
        });
    }

    async loadFiles() {
        this.showLoading();
        
        try {
            const response
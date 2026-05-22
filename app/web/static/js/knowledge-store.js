/**
 * 知识库状态管理 Store — v2（加载状态 + 缓存 + 防抖）
 * 替代 Zustand，localStorage 持久化 + 事件驱动
 */

const KnowledgeStore = {
  STORAGE_KEY: 'panda_knowledge_store',

  _state: {
    files: [],
    activeFileId: null,
    learningTarget: null,
    isLoading: false,        // 正在加载知识库内容
    isImporting: false,      // 正在导入文件
    importQueue: 0,          // 排队中的导入任务数
    error: null,             // { message, details? }
  },

  _listeners: [],
  _debounceTimer: null,

  /** 从 localStorage 恢复状态 */
  init() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        this._state.files = parsed.files || [];
        this._state.activeFileId = parsed.activeFileId || null;
        this._state.learningTarget = parsed.learningTarget || null;
      }
    } catch (e) {
      console.warn('[Store] init failed:', e);
    }
    this._notify();
  },

  _persist() {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify({
        files: this._state.files,
        activeFileId: this._state.activeFileId,
        learningTarget: this._state.learningTarget,
      }));
    } catch (e) {
      console.warn('[Store] persist failed:', e);
    }
  },

  _notify() {
    this._listeners.forEach(fn => fn({ ...this._state }));
    document.dispatchEvent(new CustomEvent('knowledge-store-change', {
      detail: { ...this._state },
    }));
  },

  /** 防抖通知：高频操作时合并渲染 */
  _notifyDebounced(delay = 50) {
    clearTimeout(this._debounceTimer);
    this._debounceTimer = setTimeout(() => this._notify(), delay);
  },

  subscribe(fn) {
    this._listeners.push(fn);
    return () => { this._listeners = this._listeners.filter(f => f !== fn); };
  },

  getState() { return { ...this._state }; },

  /** 设置当前学习上下文（学习→练习链路） */
  setLearningTarget(fileId, fileName, chapter) {
    this._state.learningTarget = { fileId, fileName, chapter: chapter || null };
    this._persist();
    this._notify();
  },

  /** 清除学习上下文 */
  clearLearningTarget() {
    this._state.learningTarget = null;
    this._persist();
    this._notify();
  },

  /** 获取学习上下文 */
  getLearningTarget() {
    return this._state.learningTarget;
  },

  /** 设置加载状态 */
  setLoading(v) {
    this._state.isLoading = v;
    this._notifyDebounced();
  },

  /** 设置导入状态 */
  setImporting(v, queueSize = 0) {
    this._state.isImporting = v;
    this._state.importQueue = queueSize;
    this._notifyDebounced();
  },

  /** 设置错误 */
  setError(message, details = '') {
    this._state.error = { message, details };
    this._notify();
  },

  /** 清除错误 */
  clearError() {
    this._state.error = null;
    this._notifyDebounced();
  },

  /** 设置文件列表（从后端同步） */
  setFiles(files) {
    this._state.files = files;
    if (this._state.activeFileId && !files.find(f => f.id === this._state.activeFileId)) {
      this._state.activeFileId = null;
    }
    this._persist();
    this._notify();
  },

  /** 新增文件（去重） */
  addFile(file) {
    if (!this._state.files.find(f => f.id === file.id)) {
      this._state.files = [...this._state.files, file];
      this._persist();
      this._notify();
    }
  },

  /** 移除文件 */
  removeFile(fileId) {
    this._state.files = this._state.files.filter(f => f.id !== fileId);
    if (this._state.activeFileId === fileId) this._state.activeFileId = null;
    this._persist();
    this._notify();
  },

  /** 设置激活文件（带加载状态） */
  setActiveFile(fileId) {
    this.clearError();

    if (fileId && !this._state.files.find(f => f.id === fileId)) {
      this.setError(`文件 ${fileId} 不存在`);
      return;
    }

    this._state.activeFileId = fileId;
    this._persist();

    // 模拟加载就绪（实际后端会在 chat 时懒加载）
    if (fileId) {
      this.setLoading(true);
      // 延迟释放加载状态（给前端渲染时间）
      clearTimeout(this._loadingTimer);
      this._loadingTimer = setTimeout(() => {
        this.setLoading(false);
      }, 300);
    } else {
      this._notify();
    }
  },

  /** 带确认的异步激活（用于导入后自动激活） */
  async setActiveFileAsync(fileId) {
    this.setActiveFile(fileId);
    // 等待后端确认数据就绪
    this.setLoading(true);
    try {
      const resp = await fetch('/api/knowledge-store/active');
      const data = await resp.json();
      if (!data.exists) {
        this.setError('知识库未能加载，请重试');
      }
    } catch (e) {
      this.setError('知识库连接失败', e.message);
    } finally {
      this.setLoading(false);
    }
  },

  clearActiveFile() {
    this._state.activeFileId = null;
    this._persist();
    this._notify();
  },

  getActiveFile() {
    if (!this._state.activeFileId) return null;
    return this._state.files.find(f => f.id === this._state.activeFileId) || null;
  },
};

KnowledgeStore.init();

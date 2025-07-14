/**
 * 任务管理器 - 新版本 (添加了新类和功能)
 */

/**
 * 任务优先级枚举
 */
class Priority {
    static LOW = 'low';
    static MEDIUM = 'medium';
    static HIGH = 'high';
    static URGENT = 'urgent';
    
    static values() {
        return [this.LOW, this.MEDIUM, this.HIGH, this.URGENT];
    }
    
    static isValid(priority) {
        return this.values().includes(priority);
    }
}

/**
 * 任务分类类
 */
class Category {
    constructor(name, color = '#007bff') {
        this.name = name;
        this.color = color;
        this.createdAt = new Date().toISOString();
    }
    
    toString() {
        return this.name;
    }
}

/**
 * 任务统计类
 */
class TaskStatistics {
    constructor(tasks) {
        this.tasks = tasks;
    }
    
    getTotalCount() {
        return this.tasks.length;
    }
    
    getCompletedCount() {
        return this.tasks.filter(task => task.completed).length;
    }
    
    getPendingCount() {
        return this.tasks.filter(task => !task.completed).length;
    }
    
    getCompletionRate() {
        const total = this.getTotalCount();
        return total === 0 ? 0 : (this.getCompletedCount() / total * 100).toFixed(2);
    }
    
    getTasksByPriority() {
        const stats = {};
        Priority.values().forEach(priority => {
            stats[priority] = this.tasks.filter(task => task.priority === priority).length;
        });
        return stats;
    }
    
    getTasksByCategory() {
        const stats = {};
        this.tasks.forEach(task => {
            const categoryName = task.category ? task.category.name : '未分类';
            stats[categoryName] = (stats[categoryName] || 0) + 1;
        });
        return stats;
    }
}

class TaskManager {
    constructor() {
        this.tasks = [];
        this.categories = new Map();
        this.nextId = 1;
        this._initializeDefaultCategories();
    }
    
    /**
     * 初始化默认分类
     */
    _initializeDefaultCategories() {
        this.addCategory('工作', '#dc3545');
        this.addCategory('学习', '#28a745');
        this.addCategory('个人', '#007bff');
    }
    
    /**
     * 添加分类
     * @param {string} name - 分类名称
     * @param {string} color - 分类颜色
     * @returns {Category} 新创建的分类
     */
    addCategory(name, color = '#007bff') {
        if (this.categories.has(name)) {
            throw new Error(`分类 "${name}" 已存在`);
        }
        
        const category = new Category(name, color);
        this.categories.set(name, category);
        return category;
    }
    
    /**
     * 获取分类
     * @param {string} name - 分类名称
     * @returns {Category|null} 分类对象或null
     */
    getCategory(name) {
        return this.categories.get(name) || null;
    }
    
    /**
     * 获取所有分类
     * @returns {Array} 分类列表
     */
    getAllCategories() {
        return Array.from(this.categories.values());
    }
    
    /**
     * 添加任务 - 增强版本
     * @param {string} title - 任务标题
     * @param {string} description - 任务描述
     * @param {string} priority - 任务优先级
     * @param {string} categoryName - 分类名称
     * @param {Date} dueDate - 截止日期
     * @returns {Object} 新创建的任务
     */
    addTask(title, description = '', priority = Priority.MEDIUM, categoryName = null, dueDate = null) {
        if (!title || title.trim().length === 0) {
            throw new Error('任务标题不能为空');
        }
        
        if (!Priority.isValid(priority)) {
            throw new Error(`无效的优先级: ${priority}`);
        }
        
        let category = null;
        if (categoryName) {
            category = this.getCategory(categoryName);
            if (!category) {
                throw new Error(`分类 "${categoryName}" 不存在`);
            }
        }
        
        const task = {
            id: this.nextId++,
            title: title.trim(),
            description: description.trim(),
            priority: priority,
            category: category,
            dueDate: dueDate,
            completed: false,
            createdAt: new Date().toISOString(),
            completedAt: null,
            tags: []
        };
        
        this.tasks.push(task);
        return task;
    }
    
    /**
     * 为任务添加标签
     * @param {number} taskId - 任务ID
     * @param {string} tag - 标签
     * @returns {boolean} 是否操作成功
     */
    addTagToTask(taskId, tag) {
        const task = this.getTaskById(taskId);
        if (task && !task.tags.includes(tag)) {
            task.tags.push(tag);
            return true;
        }
        return false;
    }
    
    /**
     * 获取所有任务
     * @returns {Array} 任务列表
     */
    getAllTasks() {
        return [...this.tasks];
    }
    
    /**
     * 根据ID获取任务
     * @param {number} id - 任务ID
     * @returns {Object|null} 任务对象或null
     */
    getTaskById(id) {
        return this.tasks.find(task => task.id === id) || null;
    }
    
    /**
     * 根据优先级筛选任务
     * @param {string} priority - 优先级
     * @returns {Array} 任务列表
     */
    getTasksByPriority(priority) {
        return this.tasks.filter(task => task.priority === priority);
    }
    
    /**
     * 根据分类筛选任务
     * @param {string} categoryName - 分类名称
     * @returns {Array} 任务列表
     */
    getTasksByCategory(categoryName) {
        return this.tasks.filter(task => 
            task.category && task.category.name === categoryName
        );
    }
    
    /**
     * 获取即将到期的任务
     * @param {number} days - 天数
     * @returns {Array} 任务列表
     */
    getTasksDueSoon(days = 7) {
        const now = new Date();
        const futureDate = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
        
        return this.tasks.filter(task => {
            if (!task.dueDate || task.completed) return false;
            const dueDate = new Date(task.dueDate);
            return dueDate >= now && dueDate <= futureDate;
        });
    }
    
    /**
     * 标记任务完成
     * @param {number} id - 任务ID
     * @returns {boolean} 是否操作成功
     */
    markTaskCompleted(id) {
        const task = this.getTaskById(id);
        if (task && !task.completed) {
            task.completed = true;
            task.completedAt = new Date().toISOString();
            return true;
        }
        return false;
    }
    
    /**
     * 删除任务
     * @param {number} id - 任务ID
     * @returns {boolean} 是否删除成功
     */
    deleteTask(id) {
        const index = this.tasks.findIndex(task => task.id === id);
        if (index !== -1) {
            this.tasks.splice(index, 1);
            return true;
        }
        return false;
    }
    
    /**
     * 获取任务统计信息
     * @returns {TaskStatistics} 统计对象
     */
    getStatistics() {
        return new TaskStatistics(this.tasks);
    }
}

// 使用示例
function main() {
    const manager = new TaskManager();
    
    // 添加自定义分类
    manager.addCategory('健康', '#fd7e14');
    
    // 添加一些任务
    const task1 = manager.addTask('学习JavaScript', '深入学习JavaScript语言特性', Priority.HIGH, '学习');
    const task2 = manager.addTask('写代码', '完成项目开发', Priority.MEDIUM, '工作');
    const task3 = manager.addTask('锻炼身体', '每天运动30分钟', Priority.LOW, '健康', new Date('2024-01-15'));
    
    // 添加标签
    manager.addTagToTask(task1.id, 'frontend');
    manager.addTagToTask(task1.id, 'programming');
    manager.addTagToTask(task2.id, 'project');
    
    console.log('所有任务:');
    manager.getAllTasks().forEach(task => {
        const categoryName = task.category ? task.category.name : '未分类';
        const tags = task.tags.length > 0 ? ` [${task.tags.join(', ')}]` : '';
        console.log(`- [${task.priority.toUpperCase()}] ${task.title} (${categoryName})${tags}: ${task.completed ? '已完成' : '未完成'}`);
    });
    
    // 标记第一个任务完成
    manager.markTaskCompleted(task1.id);
    console.log(`\n任务 "${task1.title}" 已标记为完成`);
    
    // 显示统计信息
    const stats = manager.getStatistics();
    console.log('\n任务统计:');
    console.log(`总任务数: ${stats.getTotalCount()}`);
    console.log(`已完成: ${stats.getCompletedCount()}`);
    console.log(`待完成: ${stats.getPendingCount()}`);
    console.log(`完成率: ${stats.getCompletionRate()}%`);
    
    console.log('\n按优先级统计:');
    const priorityStats = stats.getTasksByPriority();
    Object.entries(priorityStats).forEach(([priority, count]) => {
        console.log(`  ${priority}: ${count}`);
    });
    
    console.log('\n按分类统计:');
    const categoryStats = stats.getTasksByCategory();
    Object.entries(categoryStats).forEach(([category, count]) => {
        console.log(`  ${category}: ${count}`);
    });
}

// 如果直接运行此文件
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TaskManager, Priority, Category, TaskStatistics };
} else {
    main();
} 
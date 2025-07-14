/**
 * 简单任务管理器 - 原始版本
 */

class TaskManager {
    constructor() {
        this.tasks = [];
        this.nextId = 1;
    }
    
    /**
     * 添加任务
     * @param {string} title - 任务标题
     * @param {string} description - 任务描述
     * @returns {Object} 新创建的任务
     */
    addTask(title, description = '') {
        if (!title || title.trim().length === 0) {
            throw new Error('任务标题不能为空');
        }
        
        const task = {
            id: this.nextId++,
            title: title.trim(),
            description: description.trim(),
            completed: false,
            createdAt: new Date().toISOString()
        };
        
        this.tasks.push(task);
        return task;
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
     * 标记任务完成
     * @param {number} id - 任务ID
     * @returns {boolean} 是否操作成功
     */
    markTaskCompleted(id) {
        const task = this.getTaskById(id);
        if (task) {
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
}

// 使用示例
function main() {
    const manager = new TaskManager();
    
    // 添加一些任务
    const task1 = manager.addTask('学习JavaScript', '深入学习JavaScript语言特性');
    const task2 = manager.addTask('写代码', '完成项目开发');
    
    console.log('所有任务:');
    manager.getAllTasks().forEach(task => {
        console.log(`- ${task.title}: ${task.description} (${task.completed ? '已完成' : '未完成'})`);
    });
    
    // 标记第一个任务完成
    manager.markTaskCompleted(task1.id);
    console.log(`\n任务 "${task1.title}" 已标记为完成`);
    
    // 显示更新后的任务列表
    console.log('\n更新后的任务:');
    manager.getAllTasks().forEach(task => {
        console.log(`- ${task.title}: ${task.completed ? '已完成' : '未完成'}`);
    });
}

// 如果直接运行此文件
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TaskManager };
} else {
    main();
} 
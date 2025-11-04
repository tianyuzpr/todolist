document.addEventListener('DOMContentLoaded', function() {
    // 计时器存储对象
    const timers = {};
    
    // 获取所有任务复选框
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    
    // 为每个复选框添加点击事件监听器
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = parseInt(this.getAttribute('data-id'));
            toggleTaskStatus(taskId, this);
        });
    });
    
    // 添加新任务按钮事件
    const addTaskBtn = document.getElementById('addTaskBtn');
    const addTaskModal = document.getElementById('addTaskModal');
    const closeBtns = document.querySelectorAll('.close-btn');
    const confirmAddTaskBtn = document.getElementById('confirmAddTask');
    
    addTaskBtn.addEventListener('click', function() {
        addTaskModal.style.display = 'block';
    });
    
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });
    
    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
    
    // 确认添加任务
    confirmAddTaskBtn.addEventListener('click', function() {
        const title = document.getElementById('newTaskTitle').value;
        const duration = parseInt(document.getElementById('newTaskDuration').value);
        
        if (title && duration > 0) {
            addNewTask(title, duration);
            document.getElementById('newTaskTitle').value = '';
            document.getElementById('newTaskDuration').value = '';
            addTaskModal.style.display = 'none';
        }
    });
    
    // 删除任务按钮事件
    const deleteBtns = document.querySelectorAll('.delete-btn');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = parseInt(this.getAttribute('data-id'));
            deleteTask(taskId);
        });
    });
    
    // 重命名任务按钮事件
    const renameBtns = document.querySelectorAll('.rename-btn');
    const renameTaskModal = document.getElementById('renameTaskModal');
    const confirmRenameTaskBtn = document.getElementById('confirmRenameTask');
    let currentRenameTaskId = null;
    
    renameBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            currentRenameTaskId = parseInt(this.getAttribute('data-id'));
            const taskTitle = document.querySelector(`.task-title[data-id="${currentRenameTaskId}"]`).textContent;
            document.getElementById('renameTaskTitle').value = taskTitle;
            renameTaskModal.style.display = 'block';
        });
    });
    
    // 确认重命名任务
    confirmRenameTaskBtn.addEventListener('click', function() {
        const newTitle = document.getElementById('renameTaskTitle').value;
        if (newTitle && currentRenameTaskId !== null) {
            renameTask(currentRenameTaskId, newTitle);
            renameTaskModal.style.display = 'none';
        }
    });
    
    // 修改任务时长事件
    const durationInputs = document.querySelectorAll('.duration-input');
    durationInputs.forEach(input => {
        input.addEventListener('change', function() {
            const taskId = parseInt(this.getAttribute('data-id'));
            const duration = parseInt(this.value) || 0;
            updateTaskDuration(taskId, duration);
        });
    });
    
    // 开始/暂停计时按钮事件
    const startTimerBtns = document.querySelectorAll('.start-timer-btn');
    startTimerBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = parseInt(this.getAttribute('data-id'));
            toggleTaskTimer(taskId, this);
        });
    });
    
    // 切换任务状态的函数
    function toggleTaskStatus(taskId, checkbox) {
        // 发送POST请求到服务器
        fetch(`/toggle-task/${taskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // 更新UI上的统计数据
            document.getElementById('totalTasks').textContent = data.total_tasks;
            document.getElementById('pendingTasks').textContent = data.pending_tasks;
            document.getElementById('completedTasks').textContent = data.completed_tasks;
            document.getElementById('completionRate').textContent = `${data.completion_rate}%`;
            
            // 更新任务项的样式
            const taskItem = checkbox.closest('.task-item');
            if (checkbox.checked) {
                taskItem.classList.add('completed');
            } else {
                taskItem.classList.remove('completed');
            }
        })
        .catch(error => {
            console.error('切换任务状态失败:', error);
            // 如果出错，恢复复选框状态
            checkbox.checked = !checkbox.checked;
        });
    }
    
    // 添加新任务的函数
    function addNewTask(title, duration) {
        fetch('/add-task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ title, duration })
        })
        .then(response => response.json())
        .then(newTask => {
            // 刷新页面以显示新任务
            location.reload();
        })
        .catch(error => {
            console.error('添加任务失败:', error);
        });
    }
    
    // 删除任务的函数
    function deleteTask(taskId) {
        if (confirm('确定要删除这个任务吗？')) {
            fetch(`/delete-task/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // 停止该任务的计时器（如果正在计时）
                if (timers[taskId]) {
                    clearInterval(timers[taskId]);
                    delete timers[taskId];
                }
                
                // 更新UI上的统计数据
                document.getElementById('totalTasks').textContent = data.total_tasks;
                document.getElementById('pendingTasks').textContent = data.pending_tasks;
                document.getElementById('completedTasks').textContent = data.completed_tasks;
                document.getElementById('completionRate').textContent = `${data.completion_rate}%`;
                
                // 从DOM中移除任务项
                const taskItem = document.querySelector(`.task-item input[data-id="${taskId}"]`).closest('.task-item');
                taskItem.remove();
            })
            .catch(error => {
                console.error('删除任务失败:', error);
            });
        }
    }
    
    // 重命名任务的函数
    function renameTask(taskId, newTitle) {
        fetch(`/rename-task/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ title: newTitle })
        })
        .then(response => response.json())
        .then(() => {
            // 更新UI上的任务标题
            document.querySelector(`.task-title[data-id="${taskId}"]`).textContent = newTitle;
        })
        .catch(error => {
            console.error('重命名任务失败:', error);
        });
    }
    
    // 更新任务时长的函数
    function updateTaskDuration(taskId, duration) {
        fetch(`/update-duration/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ duration })
        })
        .then(response => response.json())
        .then(() => {
            // 更新UI上的计时器显示
            if (!timers[taskId]) {
                document.querySelector(`.timer-display[data-id="${taskId}"]`).textContent = `${duration}:00`;
            }
        })
        .catch(error => {
            console.error('更新任务时长失败:', error);
        });
    }
    
    // 切换任务计时器的函数
    // 添加全局的音频对象引用，用于控制提示音
    let endSound = null;
    
    // 播放结束提示音
    function playEndSound() {
    // 创建新的音频对象
    endSound = new Audio('/sounds/end.mp3');
    endSound.loop = true; // 设置为循环播放，直到用户关闭
    endSound.play().catch(error => {
    console.error('播放提示音失败:', error);
    });
    }
    
    // 停止提示音
    function stopEndSound() {
    if (endSound) {
    endSound.pause();
    endSound.currentTime = 0;
    endSound = null;
    }
    }
    
    // 创建闹钟提醒模态框
    function createAlarmModal(taskId) {
    // 检查是否已存在闹钟模态框，如果有则移除
    const existingModal = document.getElementById('alarmModal');
    if (existingModal) {
    existingModal.remove();
    }
    
    // 获取任务标题
    const taskTitle = document.querySelector(`.task-title[data-id="${taskId}"]`).textContent;
    
    // 创建模态框元素
    const modal = document.createElement('div');
    modal.id = 'alarmModal';
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.style.zIndex = '1000'; // 确保在其他元素之上
    
    // 创建模态框内容
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    modalContent.style.backgroundColor = '#fefefe';
    modalContent.style.margin = '15% auto';
    modalContent.style.padding = '20px';
    modalContent.style.border = '1px solid #888';
    modalContent.style.width = '300px';
    modalContent.style.textAlign = 'center';
    modalContent.style.borderRadius = '8px';
    
    // 创建标题
    const title = document.createElement('h2');
    title.textContent = '任务时间到！';
    
    // 创建消息
    const message = document.createElement('p');
    message.textContent = `"${taskTitle}" 任务的时间到了！`;
    
    // 创建关闭按钮
    const closeButton = document.createElement('button');
    closeButton.textContent = '关闭闹钟';
    closeButton.className = 'close-btn';
    closeButton.style.backgroundColor = '#4CAF50';
    closeButton.style.color = 'white';
    closeButton.style.border = 'none';
    closeButton.style.padding = '10px 20px';
    closeButton.style.textAlign = 'center';
    closeButton.style.textDecoration = 'none';
    closeButton.style.display = 'inline-block';
    closeButton.style.fontSize = '16px';
    closeButton.style.margin = '10px 2px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.borderRadius = '4px';
    
    // 添加关闭按钮点击事件
    closeButton.addEventListener('click', function() {
    stopEndSound();
    modal.style.display = 'none';
    });
    
    // 添加到模态框
    modalContent.appendChild(title);
    modalContent.appendChild(message);
    modalContent.appendChild(closeButton);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // 点击模态框外部关闭
    modal.addEventListener('click', function(event) {
    if (event.target === modal) {
    stopEndSound();
    modal.style.display = 'none';
    }
    });
    }
    
    // 修改计时结束时的行为
    // 查找toggleTaskTimer函数中时间到的部分，替换alert为createAlarmModal
    function toggleTaskTimer(taskId, button) {
        const durationInput = document.querySelector(`.duration-input[data-id="${taskId}"]`);
        const timerDisplay = document.querySelector(`.timer-display[data-id="${taskId}"]`);
        const taskItem = button.closest('.task-item');
        
        // 如果计时器已存在，则停止计时
        if (timers[taskId]) {
            clearInterval(timers[taskId]);
            delete timers[taskId];
            button.textContent = '开始';
            button.classList.remove('pause');
            taskItem.classList.remove('timing');
            
            // 保存剩余时间
            const timeRemaining = parseTimeDisplay(timerDisplay.textContent);
            fetch(`/update-timing/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ is_timing: false, time_remaining: timeRemaining })
            });
        } else {
            // 否则开始计时
            let remainingMinutes = parseInt(durationInput.value) || 0;
            let remainingSeconds = 0;
            
            // 尝试从显示中获取剩余时间
            const displayTime = timerDisplay.textContent;
            if (displayTime.includes(':')) {
                const parts = displayTime.split(':');
                remainingMinutes = parseInt(parts[0]) || 0;
                remainingSeconds = parseInt(parts[1]) || 0;
            }
            
            if (remainingMinutes > 0 || remainingSeconds > 0) {
                button.textContent = '暂停';
                button.classList.add('pause');
                taskItem.classList.add('timing');
                
                // 保存计时状态
                fetch(`/update-timing/${taskId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ is_timing: true })
                });
                
                // 开始计时器
                timers[taskId] = setInterval(() => {
                    if (remainingSeconds === 0) {
                        if (remainingMinutes === 0) {
                            // 时间到，播放提示音
                            playEndSound();
                            clearInterval(timers[taskId]);
                            delete timers[taskId];
                            button.textContent = '开始';
                            button.classList.remove('pause');
                            taskItem.classList.remove('timing');
                            
                            // 显示可关闭的闹钟模态框，而不是alert
                            createAlarmModal(taskId);
                            return;
                        }
                        remainingMinutes--;
                        remainingSeconds = 59;
                    } else {
                        remainingSeconds--;
                    }
                    
                    // 更新显示
                    timerDisplay.textContent = `${remainingMinutes}:${remainingSeconds.toString().padStart(2, '0')}`;
                }, 1000);
            }
        }
    }
    
    // 解析时间显示为分钟数
    function parseTimeDisplay(display) {
        if (display.includes(':')) {
            const parts = display.split(':');
            const minutes = parseInt(parts[0]) || 0;
            const seconds = parseInt(parts[1]) || 0;
            return minutes + seconds / 60;
        }
        return parseInt(display) || 0;
    }
    
    // 初始化时恢复计时状态
    document.querySelectorAll('.task-item.timing').forEach(taskItem => {
        const taskId = parseInt(taskItem.querySelector('.task-checkbox').getAttribute('data-id'));
        const startBtn = taskItem.querySelector('.start-timer-btn');
        toggleTaskTimer(taskId, startBtn);
    });
});
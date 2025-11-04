from flask import Flask, jsonify, send_file # type: ignore
import flask # type: ignore 勿删 用于在安装了多个版本python上的电脑忽略警告
import json
import os
from datetime import datetime
import logging
import requests

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 模拟任务数据
TASKS_FILE = 'tasks.json'
# 任务数量限制
MAX_TASKS = 8

# 51开发板通信设置
# 注意：需要安装pyserial库: pip install pyserial
SERIAL_PORT = 'COM6'  # 根据实际端口修改
BAUD_RATE = 9600

# 初始化任务数据
def init_tasks():
    try:
        if not os.path.exists(TASKS_FILE):
            logger.info(f"任务文件 {TASKS_FILE} 不存在，创建默认任务数据")
            tasks = [
                {'id': 1, 'title': '完成项目计划', 'completed': True, 'duration': 0, 'is_timing': False, 'time_remaining': 0},
                {'id': 2, 'title': '编写代码', 'completed': False, 'duration': 0, 'is_timing': False, 'time_remaining': 0},
                {'id': 3, 'title': '测试功能', 'completed': False, 'duration': 0, 'is_timing': False, 'time_remaining': 0},
                {'id': 4, 'title': '部署应用', 'completed': False, 'duration': 0, 'is_timing': False, 'time_remaining': 0},
                {'id': 5, 'title': '撰写文档', 'completed': False, 'duration': 0, 'is_timing': False, 'time_remaining': 0}
            ]
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            logger.info(f"默认任务数据已创建，包含 {len(tasks)} 个任务")
        
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        logger.info(f"成功加载任务数据，共 {len(tasks)} 个任务")
        return tasks
    except Exception as e:
        logger.error(f"初始化任务数据失败: {str(e)}", exc_info=True)
        # 返回空列表作为兜底
        return []

# 发送完成率数据到51开发板
def send_completion_rate_to_board(completion_rate):
    try:
        import serial
        import time
        import serial.tools.list_ports
        
        logger.info(f"准备发送完成率数据到51开发板: {completion_rate}%")
        
        # 检查端口是否存在
        ports = serial.tools.list_ports.comports()
        logger.debug(f"可用串口列表: {[port.device for port in ports]}")
        port_available = any(port.device == SERIAL_PORT for port in ports)
        
        if not port_available:
            logger.warning(f"端口 {SERIAL_PORT} 不存在，无法与51开发板通信")
            return False
        
        # 创建串口连接，添加超时和重试机制
        retry_count = 3
        success = False
        
        while retry_count > 0 and not success:
            try:
                logger.debug(f"尝试连接 {SERIAL_PORT}，波特率 {BAUD_RATE}，剩余重试次数: {retry_count}")
                with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
                    time.sleep(1)  # 增加等待时间，确保串口完全初始化
                    logger.debug("串口已打开，等待初始化完成")
                    
                    # 确保完成率在有效范围内
                    completion_rate = max(0, min(100, completion_rate))
                    logger.debug(f"修正后的完成率: {completion_rate}%")
                    
                    # 发送完成率数据（格式：Pxx
                    # 修改数据格式，确保开发板能正确解析
                    command = f"P{completion_rate}\n"
                    ser.write(command.encode())
                    print(f"已发送完成率数据: {command.strip()}")
                    
                    # 等待响应
                    time.sleep(0.1)  # 短暂延迟等待响应
                    if ser.in_waiting > 0:
                        response = ser.readline().decode().strip()
                        if response:
                            print(f"51开发板响应: {response}")
                            success = True
            except serial.SerialException as e:
                retry_count -= 1
                logger.error(f"串口通信异常: {str(e)}，剩余重试次数: {retry_count}")
                if retry_count == 0:
                    logger.error(f"与51开发板通信失败，已达到最大重试次数")
                time.sleep(0.5)
        
        logger.info(f"完成率数据发送{'成功' if success else '失败'}")
        return success
    except ImportError:
        logger.warning("未安装pyserial库，无法与51开发板通信。请运行 'pip install pyserial' 安装")
        return False
    except Exception as e:
        logger.error(f"与51开发板通信过程中发生未预期错误: {str(e)}", exc_info=True)
        return False

@app.route("/")
def index():
    logger.info("接收到首页请求")
    tasks = init_tasks()
    
    # 计算任务统计数据 - 修复完成率计算
    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task['completed']])
    pending_tasks = total_tasks - completed_tasks
    
    # 确保使用浮点数除法计算完成率
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = int(round((completed_tasks / total_tasks) * 100))
    
    logger.info(f"任务统计数据 - 总任务数: {total_tasks}, 已完成: {completed_tasks}, 待完成: {pending_tasks}, 完成率: {completion_rate}%")
    
    # 发送完成率到数码管显示
    send_result = send_completion_rate_to_board(completion_rate)
    logger.debug(f"向51开发板发送完成率结果: {'成功' if send_result else '失败'}")
    
    return flask.render_template(
        "index.html",
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        completion_rate=completion_rate,
        tasks=tasks,
        max_tasks=MAX_TASKS
    )

# 修改任务状态的API
@app.route('/toggle-task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    logger.info(f"接收到切换任务状态请求，任务ID: {task_id}")
    tasks = init_tasks()
    
    task_found = False
    for task in tasks:
        if task['id'] == task_id:
            old_status = task['completed']
            task['completed'] = not task['completed']
            task_found = True
            logger.info(f"任务 {task_id} ({task['title']}) 状态已切换: {'已完成' if old_status else '未完成'} -> {'已完成' if task['completed'] else '未完成'}")
            break
    
    if not task_found:
        logger.warning(f"任务ID {task_id} 不存在")
        return jsonify({'error': f'任务ID {task_id} 不存在'}), 404
    
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    logger.info(f"任务数据已保存到 {TASKS_FILE}")
    
    # 重新计算统计数据 - 修复完成率计算
    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task['completed']])
    pending_tasks = total_tasks - completed_tasks
    
    # 确保使用浮点数除法计算完成率
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = int(round((completed_tasks / total_tasks) * 100))
    
    logger.info(f"更新后的任务统计 - 总任务数: {total_tasks}, 已完成: {completed_tasks}, 完成率: {completion_rate}%")
    
    # 发送完成率到数码管显示
    send_completion_rate_to_board(completion_rate)
    
    return jsonify({
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': completion_rate
    })

# 添加新任务的API
@app.route('/add-task', methods=['POST'])
def add_task():
    logger.info("接收到添加新任务请求")
    tasks = init_tasks()
    
    # 检查是否达到任务数量上限
    if len(tasks) >= MAX_TASKS:
        logger.warning(f"任务数量已达到上限 {MAX_TASKS} 个，拒绝添加新任务")
        return jsonify({'error': f'任务数量已达到上限{MAX_TASKS}个'}), 400
    
    try:
        data = request.get_json()
        logger.debug(f"添加新任务的请求数据: {data}")
        
        # 验证请求数据
        if not data or 'title' not in data or not data['title'].strip():
            logger.warning("添加任务请求缺少有效的标题")
            return jsonify({'error': '任务标题不能为空'}), 400
        
        # 获取新任务的ID
        new_id = max([task['id'] for task in tasks]) + 1 if tasks else 1
        
        new_task = {
            'id': new_id,
            'title': data['title'],
            'completed': False,
            'duration': data.get('duration', 0),
            'is_timing': False,
            'time_remaining': data.get('duration', 0)
        }
        
        tasks.append(new_task)
        logger.info(f"新任务已添加 - ID: {new_id}, 标题: {data['title']}")
        
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        logger.info(f"新任务已保存到 {TASKS_FILE}")
        
        # 计算统计数据 - 修复完成率计算
        total_tasks = len(tasks)
        completed_tasks = len([task for task in tasks if task['completed']])
        
        # 确保使用浮点数除法计算完成率
        completion_rate = 0
        if total_tasks > 0:
            completion_rate = int(round((completed_tasks / total_tasks) * 100))
        
        logger.info(f"添加新任务后的完成率: {completion_rate}%")
        
        # 发送完成率到数码管显示
        send_completion_rate_to_board(completion_rate)
        
        return jsonify(new_task)
    except Exception as e:
        logger.error(f"添加新任务过程中发生错误: {str(e)}", exc_info=True)
        return jsonify({'error': '添加任务失败'}), 500

# 删除任务的API
@app.route('/delete-task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    logger.info(f"接收到删除任务请求，任务ID: {task_id}")
    tasks = init_tasks()
    
    task_to_delete = next((task for task in tasks if task['id'] == task_id), None)
    if not task_to_delete:
        logger.warning(f"任务ID {task_id} 不存在，无法删除")
        return jsonify({'error': f'任务ID {task_id} 不存在'}), 404
    
    tasks = [task for task in tasks if task['id'] != task_id]
    logger.info(f"任务已删除 - ID: {task_id}, 标题: {task_to_delete['title']}")
    
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    logger.info(f"任务数据已更新到 {TASKS_FILE}")
    
    # 重新计算统计数据 - 修复完成率计算
    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task['completed']])
    pending_tasks = total_tasks - completed_tasks
    
    # 确保使用浮点数除法计算完成率
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = int(round((completed_tasks / total_tasks) * 100))
    
    logger.info(f"删除任务后的完成率: {completion_rate}%")
    
    # 发送完成率到数码管显示
    send_completion_rate_to_board(completion_rate)
    
    return jsonify({
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': completion_rate
    })

# 重命名任务的API
@app.route('/rename-task/<int:task_id>', methods=['PUT'])
def rename_task(task_id):
    tasks = init_tasks()
    data = request.get_json()
    
    for task in tasks:
        if task['id'] == task_id:
            task['title'] = data['title']
            break
    
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    return jsonify({'success': True})

# 修改任务耗时的API
@app.route('/update-duration/<int:task_id>', methods=['PUT'])
def update_duration(task_id):
    tasks = init_tasks()
    data = request.get_json()
    
    for task in tasks:
        if task['id'] == task_id:
            task['duration'] = data['duration']
            if not task['is_timing']:
                task['time_remaining'] = data['duration']
            break
    
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    return jsonify({'success': True})

# 更新任务计时状态的API
@app.route('/update-timing/<int:task_id>', methods=['PUT'])
def update_timing(task_id):
    tasks = init_tasks()
    data = request.get_json()
    
    for task in tasks:
        if task['id'] == task_id:
            task['is_timing'] = data['is_timing']
            if 'time_remaining' in data:
                task['time_remaining'] = data['time_remaining']
            break
    
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    return jsonify({'success': True})

# 获取音频文件
@app.route('/sounds/end.mp3')
def get_end_sound():
    logger.info("接收到获取音频文件请求")
    # 确保音频文件存在
    sound_path = os.path.join('static', 'sounds', 'end.mp3')
    if not os.path.exists(sound_path):
        logger.warning(f"音频文件 {sound_path} 不存在，创建占位文件")
        os.makedirs(os.path.dirname(sound_path), exist_ok=True)
        with open(sound_path, 'w') as f:
            f.write('Audio placeholder')
        logger.info(f"音频占位文件已创建: {sound_path}")
    else:
        logger.debug(f"音频文件 {sound_path} 已存在")
    
    try:
        logger.info(f"准备发送音频文件: {sound_path}")
        return send_file(sound_path, mimetype='audio/mpeg')
    except Exception as e:
        logger.error(f"发送音频文件失败: {str(e)}", exc_info=True)
        return jsonify({'error': '获取音频文件失败'}), 500


if __name__ == '__main__':
    for task in init_tasks():
        requests.post(f'http://localhost:80/update-duration/{task["id"]}', json={'duration': task['duration']})
    logger.info(f"TodoList应用启动 - 调试模式: {app.debug}, 端口: 80, 主机: 0.0.0.0")
    app.run(debug = True, port = 80, host = "0.0.0.0")
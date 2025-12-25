from flask import Flask, render_template, request, jsonify, session
import requests
import json
import threading
import time
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = 'nenu_course_selection_key'

class CourseSelectionSystem:
    def __init__(self):
        self.base_url = "https://bkjx.nenu.edu.cn"
        self.monitoring_threads = {}
        self.notifications = []  # 通知列表
        self.notification_lock = threading.Lock()  # 通知线程安全锁
        
    def parse_cookies(self, cookies_str):
        """解析cookie字符串为字典"""
        cookies_dict = {}
        for cookie in cookies_str.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookies_dict[key] = value
        return cookies_dict
        
    def make_request_with_cookies(self, cookies_str, url, method='POST', data=None, headers=None):
        """使用指定的cookie发送请求"""
        try:
            cookies_dict = self.parse_cookies(cookies_str)
            
            # 创建新的session，不使用持久化的session
            session = requests.Session()
            session.cookies.update(cookies_dict)
            
            if method.upper() == 'POST':
                response = session.post(url, data=data, headers=headers)
            else:
                response = session.get(url, headers=headers)
                
            return response
        except Exception as e:
            return None
        
    def validate_cookies(self, cookies_str):
        """验证cookie是否有效"""
        # 发送一个简单的请求来验证cookie
        test_url = f"{self.base_url}/new/student/xsxk/xklx/02/hzkc"
        response = self.make_request_with_cookies(cookies_str, test_url, 'POST', {"page": 1, "rows": 1})
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                return "total" in data  # 如果返回了total字段，说明cookie有效
            except:
                return False
        return False
    
    def search_courses(self, cookies_str, course_type, page=1, rows=60, **filters):
        if not cookies_str:
            return {"error": "请提供Cookie"}
            
        course_types = {
            "public_jingyue": "08",
            "major_jingyue": "07", 
            "public_benbu": "06",
            "major_benbu": "02"
        }
        
        if course_type not in course_types:
            return {"error": "无效的课程类型"}
            
        url = f"{self.base_url}/new/student/xsxk/xklx/{course_types[course_type]}/hzkc"
        
        params = {
            "kkyxdm": filters.get('kkyxdm', ''),
            "xqdm": filters.get('xqdm', ''),
            "nd": filters.get('nd', ''),
            "zydm": filters.get('zydm', ''),
            "kcdldm": filters.get('kcdldm', ''),
            "xq": filters.get('xq', ''),
            "jc": filters.get('jc', ''),
            "kcxx": filters.get('kcxx', ''),
            "kcfl": filters.get('kcfl', ''),
            "hasme": filters.get('hasme', 0),
            "page": page,
            "rows": rows,
            "sort": "kcmc",
            "order": "asc"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/xsxk.html?xklxdm={course_types[course_type]}#",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        try:
            response = self.make_request_with_cookies(cookies_str, url, 'POST', params, headers)
            if response and response.status_code == 200:
                return response.json()
            else:
                return {"error": f"请求失败: {response.status_code if response else '网络异常'}"}
        except Exception as e:
            return {"error": f"请求异常: {str(e)}"}
    
    def select_course(self, cookies_str, course_type, kcrwdm, kcmc):
        if not cookies_str:
            return {"error": "请提供Cookie"}
            
        course_types = {
            "public_jingyue": "08",
            "major_jingyue": "07",
            "public_benbu": "06", 
            "major_benbu": "02"
        }
        
        if course_type not in course_types:
            return {"error": "无效的课程类型"}
            
        url = f"{self.base_url}/new/student/xsxk/xklx/{course_types[course_type]}/add"
        
        data = {
            "kcrwdm": kcrwdm,
            "kcmc": kcmc,
            "qz": -1,
            "hlct": 0
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/xsxk.html?xklxdm={course_types[course_type]}#",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        try:
            response = self.make_request_with_cookies(cookies_str, url, 'POST', data, headers)
            if response and response.status_code == 200:
                result = response.json()
                return result
            else:
                return {"error": f"选课失败: {response.status_code if response else '网络异常'}"}
        except Exception as e:
            return {"error": f"选课异常: {str(e)}"}
    
    def query_course_sections(self, cookies_str, course_type, kcptdm, page=1, rows=50):
        """查询课程的不同老师班次"""
        if not cookies_str:
            return {"error": "请提供Cookie"}
            
        course_types = {
            "public_jingyue": "08",
            "major_jingyue": "07",
            "public_benbu": "06", 
            "major_benbu": "02"
        }
        
        if course_type not in course_types:
            return {"error": "无效的课程类型"}
            
        url = f"{self.base_url}/new/student/xsxk/xklx/{course_types[course_type]}/kxkc"
        
        data = {
            "kcptdm": kcptdm,
            "hasme": 0,
            "page": page,
            "rows": rows,
            "sort": "kcrwdm",
            "order": "asc"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/xsxk.html?xklxdm={course_types[course_type]}#",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        try:
            response = self.make_request_with_cookies(cookies_str, url, 'POST', data, headers)
            if response and response.status_code == 200:
                result = response.json()
                return result
            else:
                return {"error": f"查询班次失败: {response.status_code if response else '网络异常'}"}
        except Exception as e:
            return {"error": f"查询班次异常: {str(e)}"}
    
    def start_monitoring(self, cookies_str, course_type, kcrwdm, kcmc, interval=5):
        thread_id = f"{course_type}_{kcrwdm}"
        
        if thread_id in self.monitoring_threads:
            self.add_notification(f"课程 {kcmc} 已在监控中", "warning")
            return {"error": "该课程已在监控中"}
        
        def monitor():
            start_time = time.time()
            check_count = 0
            
            while thread_id in self.monitoring_threads:
                check_count += 1
                self.monitoring_threads[thread_id]["last_check"] = time.time()
                
                result = self.select_course(cookies_str, course_type, kcrwdm, kcmc)
                
                if result.get("code") == 0:
                    # 选课成功
                    success_message = f"🎉 抢课成功！课程：{kcmc}"
                    self.add_notification(success_message, "success")
                    
                    self.monitoring_threads[thread_id]["status"] = "success"
                    self.monitoring_threads[thread_id]["result"] = result
                    del self.monitoring_threads[thread_id]
                    break
                    
                elif "名额已满" in str(result.get("message", "")):
                    # 名额已满，继续监控
                    if check_count % 10 == 0:  # 每10次检查报告一次状态
                        self.add_notification(f"监控中：{kcmc} - 第{check_count}次检查，名额已满", "info")
                    time.sleep(interval)
                    
                elif "选课成功" in str(result.get("message", "")):
                    # 选课成功（其他成功消息）
                    success_message = f"🎉 抢课成功！课程：{kcmc}"
                    self.add_notification(success_message, "success")
                    
                    self.monitoring_threads[thread_id]["status"] = "success"
                    self.monitoring_threads[thread_id]["result"] = result
                    del self.monitoring_threads[thread_id]
                    break
                    
                else:
                    # 其他错误，继续监控
                    if check_count % 10 == 0:  # 每10次检查报告一次状态
                        error_message = f"⚠️ 监控中：{kcmc} - 第{check_count}次检查，遇到错误: {result.get('message', '未知错误')}"
                        self.add_notification(error_message, "warning")
                    time.sleep(interval)
        
        self.monitoring_threads[thread_id] = {
            "thread": threading.Thread(target=monitor, daemon=True),
            "status": "running",
            "course_type": course_type,
            "kcrwdm": kcrwdm,
            "kcmc": kcmc,
            "start_time": time.time(),
            "last_check": time.time()
        }
        
        self.monitoring_threads[thread_id]["thread"].start()
        
        start_message = f"🔍 开始监控课程：{kcmc}"
        self.add_notification(start_message, "info")
        
        return {"success": True, "thread_id": thread_id, "message": start_message}
    
    def stop_monitoring(self, thread_id):
        if thread_id in self.monitoring_threads:
            course_name = self.monitoring_threads[thread_id].get("kcmc", "未知课程")
            del self.monitoring_threads[thread_id]
            
            stop_message = f"⏹️ 已停止监控：{course_name}"
            self.add_notification(stop_message, "info")
            
            return {"success": True, "message": stop_message}
        
        return {"error": "未找到该监控任务"}
    
    def get_monitoring_status(self):
        # 序列化监控状态，确保可以JSON化
        serialized_status = {}
        for thread_id, task in self.monitoring_threads.items():
            serialized_status[thread_id] = {
                "status": task.get("status", "unknown"),
                "course_type": task.get("course_type", ""),
                "kcrwdm": task.get("kcrwdm", ""),
                "kcmc": task.get("kcmc", ""),
                "start_time": task.get("start_time", time.time()),
                "last_check": task.get("last_check", time.time())
            }
        return serialized_status
    
    def add_notification(self, message, level="info"):
        """添加通知"""
        with self.notification_lock:
            notification = {
                "id": len(self.notifications),
                "message": message,
                "level": level,
                "timestamp": time.time(),
                "time_str": time.strftime("%H:%M:%S")
            }
            self.notifications.append(notification)
            # 保持最多50条通知
            if len(self.notifications) > 50:
                self.notifications = self.notifications[-50:]
    
    def get_notifications(self):
        """获取通知列表"""
        with self.notification_lock:
            return self.notifications.copy()
    
    def clear_notifications(self):
        """清空通知"""
        with self.notification_lock:
            self.notifications = []

# 创建全局实例
course_system = CourseSelectionSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login_type = data.get('type')
    
    if login_type == 'cookie':
        cookies = data.get('cookies', '')
        if cookies:
            course_system.set_cookies(cookies)
            return jsonify({"success": True, "message": "Cookie登录成功"})
        else:
            return jsonify({"success": False, "message": "请输入Cookie"})
    
    elif login_type == 'password':
        username = data.get('username')
        password = data.get('password')
        if username and password:
            success = course_system.login_with_password(username, password)
            if success:
                return jsonify({"success": True, "message": "账号密码登录成功"})
            else:
                return jsonify({"success": False, "message": "登录失败"})
        else:
            return jsonify({"success": False, "message": "请输入账号密码"})
    
    return jsonify({"success": False, "message": "无效的登录类型"})

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    course_type = data.get('course_type')
    page = data.get('page', 1)
    rows = data.get('rows', 60)
    cookies = data.get('cookies', '')
    
    filters = {}
    for key in ['kkyxdm', 'xqdm', 'nd', 'zydm', 'kcdldm', 'xq', 'jc', 'kcxx', 'kcfl']:
        if key in data:
            filters[key] = data[key]
    
    result = course_system.search_courses(cookies, course_type, page, rows, **filters)
    return jsonify(result)

@app.route('/sections', methods=['POST'])
def query_sections():
    data = request.json
    course_type = data.get('course_type')
    kcptdm = data.get('kcptdm')
    page = data.get('page', 1)
    rows = data.get('rows', 50)
    cookies = data.get('cookies', '')
    
    result = course_system.query_course_sections(cookies, course_type, kcptdm, page, rows)
    return jsonify(result)

@app.route('/select', methods=['POST'])
def select():
    data = request.json
    course_type = data.get('course_type')
    kcrwdm = data.get('kcrwdm')
    kcmc = data.get('kcmc')
    cookies = data.get('cookies', '')
    
    result = course_system.select_course(cookies, course_type, kcrwdm, kcmc)
    return jsonify(result)

@app.route('/monitor/start', methods=['POST'])
def start_monitor():
    data = request.json
    course_type = data.get('course_type')
    kcrwdm = data.get('kcrwdm')
    kcmc = data.get('kcmc')
    interval = data.get('interval', 5)
    cookies = data.get('cookies', '')
    
    result = course_system.start_monitoring(cookies, course_type, kcrwdm, kcmc, interval)
    return jsonify(result)

@app.route('/monitor/stop', methods=['POST'])
def stop_monitor():
    data = request.json
    thread_id = data.get('thread_id')
    
    result = course_system.stop_monitoring(thread_id)
    return jsonify(result)

@app.route('/monitor/status')
def monitor_status():
    status = course_system.get_monitoring_status()
    return jsonify(status)

@app.route('/notifications')
def get_notifications():
    notifications = course_system.get_notifications()
    return jsonify(notifications)

@app.route('/notifications/clear', methods=['POST'])
def clear_notifications():
    course_system.clear_notifications()
    return jsonify({"success": True, "message": "通知已清空"})

# 移除重复的cookie更新端点，统一使用登录端点

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
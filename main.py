import requests
import time
import urllib3
import threading
import datetime
import json

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 课程信息（示例ID，实际使用时替换）
COURSES = [
  {
    "clazzId": "202520262ae2221205401",
    "secretVal": "REDACTED_SECRET_VAL_1",
    "clazzType": "TJKC"
  },
  {
    "clazzId": "202520262ae2221103701",
    "secretVal": "REDACTED_SECRET_VAL_2",
    "clazzType": "TJKC"
  },
  {
    "clazzId": "202520262ae2221107301",
    "secretVal": "REDACTED_SECRET_VAL_3",
    "clazzType": "TJKC"
  }
]

# 请求头模板
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es-ES;q=0.5,es;q=0.4",
    "Authorization": "YOUR_AUTHORIZATION_TOKEN_HERE",  # ← 替换为你自己的有效Token
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "route=xxxx; Authorization=YOUR_AUTHORIZATION_TOKEN_HERE",  # ← 替换
    "Host": "icourses.jlu.edu.cn",
    "Origin": "https://icourses.jlu.edu.cn",
    "Referer": "https://icourses.jlu.edu.cn/xsxk/elective/grablessons?batchId=YOUR_BATCH_ID",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
    "batchId": "YOUR_BATCH_ID",  # ← 替换为当前选课批次ID
    "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

# 全局控制
stop_all = threading.Event()
completed_courses = set()
completed_lock = threading.Lock()

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S") + f".{now.microsecond // 1000:03d}"

def build_request_body(course):
    return f"clazzType={course['clazzType']}&clazzId={course['clazzId']}&secretVal={course['secretVal']}"

def grab_course(course):
    url = "https://icourses.jlu.edu.cn/xsxk/sc/clazz/addxk"
    data = build_request_body(course)
    
    try:
        custom_headers = HEADERS.copy()
        for header in ["Content-Length", "Host", "Connection"]:
            custom_headers.pop(header, None)
        custom_headers["Content-Length"] = str(len(data))
            
        response = requests.post(
            url,
            headers=custom_headers,
            data=data,
            verify=False,
            timeout=(0.7, 1.1)
        )
        
        try:
            result = response.json()
        except json.JSONDecodeError:
            result = {
                "status_code": response.status_code,
                "text": response.text[:200] + "..." if len(response.text) > 200 else response.text
            }
            
        current_time = get_current_time()
        status = "✅ SUCCESS" if response.status_code == 200 and result.get("code") == 200 else "❌ FAILED"
        class_id_short = course['clazzId'][-4:]
        msg = result.get("msg", "无消息")
        print(f"[{current_time}] {status} | 课ID: {class_id_short} | 响应: {msg}")
        
        if response.status_code == 200 and result.get("code") == 200:
            return {"success": True, "data": result}
        return {"success": False, "data": result}
        
    except Exception as e:
        current_time = get_current_time()
        print(f"[{current_time}] ⚠️ 异常: {str(e)}")
        return {"success": False, "error": str(e)}

def course_worker(course):
    clazz_id = course['clazzId']
    class_id_short = clazz_id[-4:]
    print(f"▶️ 启动课程 {class_id_short} 的抢课线程 (类型: {course['clazzType']})")
    fail_count = 0
    
    while not stop_all.is_set():
        with completed_lock:
            if clazz_id in completed_courses:
                break
        
        result = grab_course(course)
        
        if result["success"] is True:
            with completed_lock:
                completed_courses.add(clazz_id)
            current_time = get_current_time()
            print("\n" + "="*60)
            print(f"[{current_time}] 🎉 课程 {clazz_id} 抢课成功!")
            print(f"响应: {result['data'].get('msg', '成功')}")
            print("="*60)
            break
        else:
            fail_count += 1
            time.sleep(0.12)
    
    current_time = get_current_time()
    print(f"[{current_time}] ⏹️ 课程 {class_id_short} 线程退出 (失败次数: {fail_count})")

def main():
    global stop_all, completed_courses
    stop_all.clear()
    with completed_lock:
        completed_courses.clear()
    
    start_time = get_current_time()
    print("="*60)
    print("吉林大学抢课脚本 (全课程并行版)")
    print(f"开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标课程: {len(COURSES)}门")
    print("="*60)
    
    threads = []
    for course in COURSES:
        t = threading.Thread(target=course_worker, args=(course,), name=f"Course-{course['clazzId'][-4:]}")
        t.daemon = True
        threads.append(t)
        t.start()
        time.sleep(0.02)
    
    try:
        while len(completed_courses) < len(COURSES) and not stop_all.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        current_time = get_current_time()
        print(f"\n[{current_time}] 🛑 用户中断，准备退出...")
        stop_all.set()
    
    for t in threads:
        t.join(timeout=1.0)
    
    end_time = get_current_time()
    print("\n" + "="*60)
    print(f"[{end_time}] 所有课程处理完毕，抢课流程结束")
    print(f"✅ 成功/跳过课程数: {len(completed_courses)} / {len(COURSES)}")
    print("="*60)

if __name__ == "__main__":
    print("\n" + "!"*60)
    print("⚠️  请确保已替换以下内容：")
    print("   - HEADERS 中的 Authorization 和 Cookie")
    print("   - batchId")
    print("   - COURSES 中的 secretVal")
    print("!"*60)
    
    TARGET_TIME = "2025-12-24 09:00:00"  # 根据实际选课时间修改
    print(f"\n🕒 等待选课开始... (目标时间: {TARGET_TIME})")
    
    while True:
        current_dt = datetime.datetime.now()
        target_dt = datetime.datetime.strptime(TARGET_TIME, "%Y-%m-%d %H:%M:%S")
        
        if current_dt >= target_dt:
            current_time = get_current_time()
            print(f"\n[{current_time}] ⏰ 到达目标时间，启动抢课流程!")
            main()
            break
        else:
            remaining_seconds = int((target_dt - current_dt).total_seconds())
            current_display = current_dt.strftime("%Y-%m-%d %H:%M:%S")
            if remaining_seconds <= 10:
                print(f"\r🔥 即将开始! 剩余: {remaining_seconds}秒", end="", flush=True)
            else:
                print(f"\r倒计时: {remaining_seconds}秒 (当前: {current_display})", end="", flush=True)
            time.sleep(0.5)

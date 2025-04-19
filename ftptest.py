
from ftplib import FTP
import readline as readline



# 自动补全函数
def completer(text, state):
	options = [cmd for cmd in COMMANDS.keys() if cmd.startswith(text)]
	if state < len(options):
		return options[state]
	return None
def zsh(COMMANDS):
	# 设置自动补全
	readline.parse_and_bind("tab: complete")
	readline.set_completer(completer)

	# 主循环
	while True:
		try:
			# 获取用户输入
			user_input = input('> ').strip()

			# 根据输入替换为完整命令
			if user_input in COMMANDS:
				user_input = COMMANDS[user_input]

			# 模拟执行命令
			if user_input == 'ls':
				print("Running: ls")
				# 这里可以替换为实际的 ls 命令逻辑
			elif user_input == 'cd':
				print("Running: cd")
				# 这里可以替换为实际的 cd 命令逻辑
			else:
				print(f"Unknown command: {user_input}")

		except KeyboardInterrupt:
			print("\nExiting...")
			break
		except EOFError:
			print("\nExiting...")
			break

def test_ftp_connection():
	try:
		# 创建FTP连接
		ftp = FTP()
		# 连接到服务器
		ftp.connect('124.16.111.141', 21)
		# 登录
		ftp.login('jinyue', 'jy@2024')

		print("FTP连接成功!")
		print("当前目录:", ftp.pwd())


# 调用下载函数
		print("\n可下载的文件列表:")
		ftpdir = ftp.nlst()

 		# 将ftpdir转换为commands字典
		commands = {}
		for i, file in enumerate(ftpdir, 1):
			commands[str(i)] = file
			commands[file] = file

		for i, file in enumerate(ftpdir, 1):
			print(f"{i}. {file}")
		zsh(commands)
		filename = input("\n请输入要下载的文件名: ")
		try:
			# 创建一个临时文件对象来接收数据
			with open('temp.txt', 'wb') as temp_file:
				# 使用RETR命令下载文件
				ftp.retrbinary(f'RETR {filename}', temp_file.write)

			# 读取并显示文件内容
			with open('temp.txt', 'r') as f:
				content = f.read()
				print("\n文件内容:")
				print(content)

		except Exception as e:
			print(f"下载失败: {str(e)}")
	except Exception as e:
		print(f"FTP连接失败: {str(e)}")
		ftp.quit()

if __name__ == '__main__':
	test_ftp_connection()


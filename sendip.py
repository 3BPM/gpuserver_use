#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IP 地址监控与邮件通知脚本
功能：检测本机公网IP变化，并通过邮件通知指定收件人
"""

import os
import socket
import smtplib
import logging
from email.mime.text import MIMEText
from email.utils import formatdate
import urllib.request
import ssl
from typing import List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ip_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IPMonitor:
    def __init__(self):
        self.ip_file = "/var/lib/ip_monitor/current_ip.txt"
        self._ensure_ip_file()

    def _ensure_ip_file(self):
        """确保IP存储文件存在"""
        os.makedirs(os.path.dirname(self.ip_file), exist_ok=True)
        if not os.path.exists(self.ip_file):
            with open(self.ip_file, 'w') as f:
                f.write('')

    def check_network(self, retries: int = 3, delay: int = 5) -> bool:
        """检查网络连接"""
        test_url = "http://connectivitycheck.gstatic.com/generate_204"
        for attempt in range(retries):
            try:
                urllib.request.urlopen(test_url, timeout=5)
                logger.info("Network connectivity confirmed")
                return True
            except Exception as e:
                logger.warning(f"Network check failed (attempt {attempt + 1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
        logger.error("Network unavailable after multiple attempts")
        return False

    def get_public_ip(self) -> str:
        """获取当前公网IP地址"""
        try:
            # 使用更可靠的IP查询服务
            with urllib.request.urlopen("https://api.ipify.org", timeout=10) as response:
                if response.status == 200:
                    return response.read().decode('utf-8').strip()
                raise Exception(f"API returned status {response.status}")
        except Exception as e:
            logger.error(f"Failed to get public IP: {str(e)}")
            # 备用方案：通过DNS查询
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except Exception as fallback_e:
                logger.error(f"Fallback IP detection failed: {str(fallback_e)}")
                raise

    def send_notification(self, ip_address: str) -> bool:
        """发送邮件通知"""
        smtp_config = {
            'server': 'smtp.qq.com',
            'port': 465,
            'from_email': os.getenv('FROM_EMAIL'),
            'auth_code': os.getenv('AUTH_CODE'),
            'to_emails': ['robertcjy@qq.com'],  # 可添加更多收件人
            'subject': f'IP Address Update - {socket.gethostname()}'
        }

        if not all(smtp_config.values()):
            logger.error("Missing email configuration in environment variables")
            return False

        message = f"""
        Host: {socket.gethostname()}
        Time: {formatdate(localtime=True)}
        New IP Address: {ip_address}
        """

        msg = MIMEText(message.strip(), 'plain', 'utf-8')
        msg['From'] = smtp_config['from_email']
        msg['To'] = ', '.join(smtp_config['to_emails'])
        msg['Subject'] = smtp_config['subject']
        msg['Date'] = formatdate(localtime=True)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                smtp_config['server'],
                smtp_config['port'],
                context=context
            ) as server:
                server.login(smtp_config['from_email'], smtp_config['auth_code'])
                server.sendmail(
                    smtp_config['from_email'],
                    smtp_config['to_emails'],
                    msg.as_string()
                )
            logger.info("Notification email sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def run(self):
        """主执行逻辑"""
        if not self.check_network():
            return

        try:
            current_ip = self.get_public_ip()
            logger.info(f"Current IP: {current_ip}")

            # 读取之前存储的IP
            previous_ip = ''
            if os.path.exists(self.ip_file):
                with open(self.ip_file, 'r') as f:
                    previous_ip = f.read().strip()

            # 比较IP是否变化
            if current_ip != previous_ip:
                logger.info(f"IP changed from {previous_ip} to {current_ip}")
                if self.send_notification(current_ip):
                    # 只有邮件发送成功才更新IP记录
                    with open(self.ip_file, 'w') as f:
                        f.write(current_ip)
            else:
                logger.info("IP address unchanged")
        except Exception as e:
            logger.error(f"Error in main execution: {str(e)}")

if __name__ == '__main__':
    import time
    start_time = time.time()
    
    monitor = IPMonitor()
    monitor.run()
    
    logger.info(f"Execution completed in {time.time() - start_time:.2f} seconds")

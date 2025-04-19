import socket  
import uuid  
import re  

def get_host_info():  
    hostname = socket.gethostname()   
    # 获取所有非回环IP  
    ips = [ip for ip in socket.gethostbyname_ex(hostname)[2] if not ip.startswith("127.")]   
    ip = ips[0] if ips else "N/A"  
    # 格式化MAC地址  
    mac_raw = uuid.getnode()   
    mac = ":".join([f"{mac_raw >> i & 0xff:02x}" for i in range(0, 8*6, 8)][::-1])  
    return hostname, ip, mac  
def match(input_str):  
    hostname, ip, mac = get_host_info()
    # 匹配输入类型
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", input_str):
        try:
            remote_hostname = socket.gethostbyaddr(input_str)[0]
            if input_str == ip:
                print(f"主机名: {hostname}\nMAC地址: {mac}")
            else:
                print(f"IP {input_str} 属于主机: {remote_hostname}")
        except socket.herror:
            print("无法解析该IP地址")
    elif re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", input_str):
        if input_str.lower() == mac.lower():
            print(f"主机名: {hostname}\nIP地址: {ip}")
        else:
            # MAC地址只能查询本地
            print("输入的MAC不属于本机")
    else:
        try:
            remote_ip = socket.gethostbyname(input_str)
            if input_str.lower() == hostname.lower():
                print(f"IP地址: {ip}\nMAC地址: {mac}")
            else:
                print(f"主机名 {input_str} 的IP地址为: {remote_ip}")
        except socket.gaierror:
            print("无法解析该主机名")
if __name__ == "__main__":  
    import sys  
    input_arg = sys.argv[1] if len(sys.argv) > 1 else ""  
    match(input_arg)  
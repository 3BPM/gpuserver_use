import grp
import pwd
from collections import defaultdict
import subprocess

def get_all_groups():
    """获取系统中所有组"""
    return grp.getgrall()

def get_user_groups():
    """获取所有用户及其所属的组"""
    user_groups = defaultdict(list)
    groups = get_all_groups()

    # 获取所有用户
    users = pwd.getpwall()

    # 遍历每个用户，获取其所属的组
    for user in users:
        username = user.pw_name
        # 获取用户的主组
        primary_gid = user.pw_gid
        primary_group = grp.getgrgid(primary_gid).gr_name
        user_groups[username].append(primary_group)

        # 获取用户的附加组
        for group in groups:
            if username in group.gr_mem:
                user_groups[username].append(group.gr_name)

    return user_groups

def print_tree():
    """以树形结构打印用户和组的关系"""
    user_groups = get_user_groups()

    print("Ubuntu 用户组关系树:")
    print("├─系统用户")

    # 按用户名排序
    for username in sorted(user_groups.keys()):
        groups = user_groups[username]
        if len(groups) > 0:
            print(f"│  ├─{username}")
            for i, group in enumerate(sorted(groups)):
                if i == len(groups) - 1:
                    print(f"│  │  └─{group}")
                else:
                    print(f"│  │  ├─{group}")

def main():
    print_tree()

if __name__ == "__main__":
    main()


#!/bin/python3
import os
import pwd
import grp

def print_group_tree():
    for group in grp.getgrall():
        print(group.gr_name)
        for user in pwd.getpwall():
            if user.pw_gid == group.gr_gid:
                print(f"  └── {user.pw_name}")

print_group_tree()

#!/bin/python3
import os
import pwd
import grp

def print_group_tree():
    for group in grp.getgrall():
        print(f"Group: {group.gr_name} (GID: {group.gr_gid})")
        for user in pwd.getpwall():
            if user.pw_gid == group.gr_gid:
                print(f"  └── {user.pw_name} (UID: {user.pw_uid})")

print_group_tree()

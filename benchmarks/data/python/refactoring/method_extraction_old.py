#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户管理系统 - 重构前版本 (包含长方法)
"""

import re
from typing import List, Dict, Optional


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        """初始化"""
        self.users: List[Dict] = []
        self.current_id = 1
    
    def create_user(self, name: str, email: str, age: int) -> Dict:
        """创建用户 - 包含复杂验证逻辑的长方法"""
        # 验证用户名
        if not name or len(name.strip()) == 0:
            raise ValueError("用户名不能为空")
        if len(name) < 2:
            raise ValueError("用户名长度至少为2个字符")
        if len(name) > 50:
            raise ValueError("用户名长度不能超过50个字符")
        if not re.match(r'^[a-zA-Z\u4e00-\u9fa5][a-zA-Z\u4e00-\u9fa5\s]*$', name):
            raise ValueError("用户名只能包含字母、汉字和空格")
        
        # 验证邮箱
        if not email or len(email.strip()) == 0:
            raise ValueError("邮箱不能为空")
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("邮箱格式不正确")
        
        # 检查邮箱是否已存在
        for user in self.users:
            if user['email'] == email:
                raise ValueError("邮箱已存在")
        
        # 验证年龄
        if not isinstance(age, int):
            raise ValueError("年龄必须是整数")
        if age < 0:
            raise ValueError("年龄不能为负数")
        if age > 150:
            raise ValueError("年龄不能超过150岁")
        
        # 创建用户对象
        user = {
            'id': self.current_id,
            'name': name.strip(),
            'email': email.strip().lower(),
            'age': age,
            'status': 'active',
            'created_at': __import__('datetime').datetime.now().isoformat()
        }
        
        # 保存用户
        self.users.append(user)
        self.current_id += 1
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱获取用户"""
        for user in self.users:
            if user['email'] == email.lower():
                return user
        return None
    
    def list_users(self) -> List[Dict]:
        """列出所有用户"""
        return self.users.copy()


def main():
    """主函数"""
    manager = UserManager()
    
    try:
        user1 = manager.create_user("张三", "zhangsan@example.com", 25)
        user2 = manager.create_user("李四", "lisi@example.com", 30)
        
        print("创建的用户:")
        for user in manager.list_users():
            print(f"  {user['name']} ({user['email']}) - {user['age']}岁")
            
    except ValueError as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main() 
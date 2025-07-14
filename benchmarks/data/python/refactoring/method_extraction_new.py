#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户管理系统 - 重构后版本 (提取了方法)
"""

import re
import datetime
from typing import List, Dict, Optional


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        """初始化"""
        self.users: List[Dict] = []
        self.current_id = 1
    
    def create_user(self, name: str, email: str, age: int) -> Dict:
        """创建用户 - 重构后的简洁方法"""
        # 验证输入参数
        self._validate_name(name)
        self._validate_email(email)
        self._validate_age(age)
        
        # 检查邮箱唯一性
        self._check_email_uniqueness(email)
        
        # 创建和保存用户
        user = self._create_user_object(name, email, age)
        self._save_user(user)
        
        return user
    
    def _validate_name(self, name: str) -> None:
        """验证用户名"""
        if not name or len(name.strip()) == 0:
            raise ValueError("用户名不能为空")
        if len(name) < 2:
            raise ValueError("用户名长度至少为2个字符")
        if len(name) > 50:
            raise ValueError("用户名长度不能超过50个字符")
        if not re.match(r'^[a-zA-Z\u4e00-\u9fa5][a-zA-Z\u4e00-\u9fa5\s]*$', name):
            raise ValueError("用户名只能包含字母、汉字和空格")
    
    def _validate_email(self, email: str) -> None:
        """验证邮箱格式"""
        if not email or len(email.strip()) == 0:
            raise ValueError("邮箱不能为空")
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("邮箱格式不正确")
    
    def _validate_age(self, age: int) -> None:
        """验证年龄"""
        if not isinstance(age, int):
            raise ValueError("年龄必须是整数")
        if age < 0:
            raise ValueError("年龄不能为负数")
        if age > 150:
            raise ValueError("年龄不能超过150岁")
    
    def _check_email_uniqueness(self, email: str) -> None:
        """检查邮箱唯一性"""
        normalized_email = email.strip().lower()
        for user in self.users:
            if user['email'] == normalized_email:
                raise ValueError("邮箱已存在")
    
    def _create_user_object(self, name: str, email: str, age: int) -> Dict:
        """创建用户对象"""
        return {
            'id': self.current_id,
            'name': name.strip(),
            'email': email.strip().lower(),
            'age': age,
            'status': 'active',
            'created_at': datetime.datetime.now().isoformat()
        }
    
    def _save_user(self, user: Dict) -> None:
        """保存用户"""
        self.users.append(user)
        self.current_id += 1
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱获取用户"""
        normalized_email = email.lower()
        for user in self.users:
            if user['email'] == normalized_email:
                return user
        return None
    
    def list_users(self) -> List[Dict]:
        """列出所有用户"""
        return self.users.copy()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[Dict]:
        """更新用户信息 - 新增方法"""
        user = self._find_user_by_id(user_id)
        if not user:
            return None
        
        # 更新允许的字段
        updatable_fields = ['name', 'age']
        for field, value in kwargs.items():
            if field in updatable_fields:
                if field == 'name':
                    self._validate_name(value)
                elif field == 'age':
                    self._validate_age(value)
                user[field] = value
        
        return user
    
    def _find_user_by_id(self, user_id: int) -> Optional[Dict]:
        """根据ID查找用户"""
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None


def main():
    """主函数"""
    manager = UserManager()
    
    try:
        user1 = manager.create_user("张三", "zhangsan@example.com", 25)
        user2 = manager.create_user("李四", "lisi@example.com", 30)
        
        print("创建的用户:")
        for user in manager.list_users():
            print(f"  {user['name']} ({user['email']}) - {user['age']}岁")
        
        # 测试更新功能
        updated_user = manager.update_user(user1['id'], age=26)
        if updated_user:
            print(f"\n更新后的用户: {updated_user['name']} - {updated_user['age']}岁")
            
    except ValueError as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main() 
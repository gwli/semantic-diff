#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
示例代码 - 新版本
一个改进的计算器类，增加了新功能和错误处理
"""

import math
import logging
from typing import List, Union


class AdvancedCalculator:
    """改进的计算器类，支持更多功能"""
    
    def __init__(self, enable_logging: bool = False):
        """
        初始化计算器
        
        Args:
            enable_logging: 是否启用日志记录
        """
        self.operation_history = []
        self.previous_result = 0
        self.logger = None
        
        if enable_logging:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
    
    def _log_operation(self, operation: str, result: float):
        """记录操作日志"""
        if self.logger:
            self.logger.info(f"执行操作: {operation}, 结果: {result}")
    
    def add(self, x: float, y: float) -> float:
        """
        加法运算
        
        Args:
            x: 第一个数
            y: 第二个数
            
        Returns:
            两数之和
        """
        result = x + y
        operation = f"{x} + {y} = {result}"
        self.operation_history.append(operation)
        self.previous_result = result
        self._log_operation(operation, result)
        return result
    
    def subtract(self, x: float, y: float) -> float:
        """
        减法运算
        
        Args:
            x: 被减数
            y: 减数
            
        Returns:
            两数之差
        """
        result = x - y
        operation = f"{x} - {y} = {result}"
        self.operation_history.append(operation)
        self.previous_result = result
        self._log_operation(operation, result)
        return result
    
    def multiply(self, x: float, y: float) -> float:
        """
        乘法运算
        
        Args:
            x: 第一个数
            y: 第二个数
            
        Returns:
            两数之积
        """
        result = x * y
        operation = f"{x} * {y} = {result}"
        self.operation_history.append(operation)
        self.previous_result = result
        self._log_operation(operation, result)
        return result
    
    def divide(self, x: float, y: float) -> float:
        """
        除法运算，增强错误处理
        
        Args:
            x: 被除数
            y: 除数
            
        Returns:
            两数之商
            
        Raises:
            ZeroDivisionError: 当除数为0时
        """
        if y == 0:
            raise ZeroDivisionError("除数不能为零")
        
        result = x / y
        operation = f"{x} / {y} = {result}"
        self.operation_history.append(operation)
        self.previous_result = result
        self._log_operation(operation, result)
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """
        幂运算
        
        Args:
            base: 底数
            exponent: 指数
            
        Returns:
            幂运算结果
        """
        result = base ** exponent
        operation = f"{base} ^ {exponent} = {result}"
        self.operation_history.append(operation)
        self.previous_result = result
        self._log_operation(operation, result)
        return result
    
    def square_root(self, number: float) -> float:
        """
        平方根运算，重命名并改进
        
        Args:
            number: 要开方的数
            
        Returns:
            平方根结果
            
        Raises:
            ValueError: 当输入负数时
        """
        if number < 0:
            raise ValueError("负数不能开平方根")
        
        result = math.sqrt(number)
        operation = f"sqrt({number}) = {result}"
        self.operation_history.append(operation)
        self.previous_result = result
        self._log_operation(operation, result)
        return result
    
    def factorial(self, n: int) -> int:
        """
        新增：阶乘运算
        
        Args:
            n: 要计算阶乘的数
            
        Returns:
            阶乘结果
            
        Raises:
            ValueError: 当输入负数时
        """
        if n < 0:
            raise ValueError("负数不能计算阶乘")
        
        result = math.factorial(n)
        operation = f"{n}! = {result}"
        self.operation_history.append(operation)
        self.previous_result = result
        self._log_operation(operation, result)
        return result
    
    def percentage(self, value: float, percent: float) -> float:
        """
        新增：百分比计算
        
        Args:
            value: 基数
            percent: 百分比
            
        Returns:
            百分比计算结果
        """
        result = (value * percent) / 100
        operation = f"{percent}% of {value} = {result}"
        self.operation_history.append(operation)
        self.previous_result = result
        self._log_operation(operation, result)
        return result
    
    def get_operation_history(self) -> List[str]:
        """
        获取操作历史（重命名方法）
        
        Returns:
            操作历史列表的副本
        """
        return self.operation_history.copy()
    
    def clear_all(self):
        """
        清除所有数据（重命名并扩展功能）
        """
        self.operation_history.clear()
        self.previous_result = 0
        if self.logger:
            self.logger.info("计算器数据已清除")
    
    def get_previous_result(self) -> float:
        """
        获取上一次计算结果（重命名方法）
        
        Returns:
            上一次的计算结果
        """
        return self.previous_result
    
    def chain_operation(self, operation: str, value: float) -> float:
        """
        新增：链式操作，使用上一次结果
        
        Args:
            operation: 操作符 (+, -, *, /)
            value: 操作数
            
        Returns:
            计算结果
        """
        if operation == '+':
            return self.add(self.previous_result, value)
        elif operation == '-':
            return self.subtract(self.previous_result, value)
        elif operation == '*':
            return self.multiply(self.previous_result, value)
        elif operation == '/':
            return self.divide(self.previous_result, value)
        else:
            raise ValueError(f"不支持的操作: {operation}")


def demonstrate_calculator():
    """演示改进的计算器功能"""
    # 创建带日志的计算器
    calc = AdvancedCalculator(enable_logging=True)
    
    print("=== 高级计算器演示 ===")
    
    # 基本运算
    print(f"加法: 2 + 3 = {calc.add(2, 3)}")
    print(f"减法: 10 - 4 = {calc.subtract(10, 4)}")
    print(f"乘法: 5 * 6 = {calc.multiply(5, 6)}")
    print(f"除法: 15 / 3 = {calc.divide(15, 3)}")
    print(f"幂运算: 2 ^ 8 = {calc.power(2, 8)}")
    print(f"平方根: sqrt(16) = {calc.square_root(16)}")
    
    # 新功能
    print(f"阶乘: 5! = {calc.factorial(5)}")
    print(f"百分比: 15% of 200 = {calc.percentage(200, 15)}")
    
    # 链式操作
    print(f"链式操作: 上一结果 + 10 = {calc.chain_operation('+', 10)}")
    print(f"链式操作: 上一结果 * 2 = {calc.chain_operation('*', 2)}")
    
    # 显示历史
    print("\n操作历史:")
    for i, record in enumerate(calc.get_operation_history(), 1):
        print(f"  {i}. {record}")
    
    print(f"\n最终结果: {calc.get_previous_result()}")


if __name__ == "__main__":
    demonstrate_calculator() 
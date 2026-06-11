"""
数据验证模块
提供数据验证和清洗功能
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Callable, Tuple
import logging
import re

logger = logging.getLogger(__name__)

class Validator:
    """数据验证器基类"""
    
    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        """
        验证数据
        :param data: 待验证数据
        :return: (是否通过验证, 错误信息)
        """
        raise NotImplementedError

class RangeValidator(Validator):
    """范围验证器"""
    
    def __init__(self, min_val: float = None, max_val: float = None):
        self.min_val = min_val
        self.max_val = max_val
    
    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        if pd.isna(data):
            return True, None
        
        try:
            val = float(data)
            if self.min_val is not None and val < self.min_val:
                return False, f"值 {val} 小于最小值 {self.min_val}"
            if self.max_val is not None and val > self.max_val:
                return False, f"值 {val} 大于最大值 {self.max_val}"
            return True, None
        except (ValueError, TypeError):
            return False, f"无法转换为数值: {data}"

class PatternValidator(Validator):
    """正则表达式验证器"""
    
    def __init__(self, pattern: str, description: str = ""):
        self.pattern = re.compile(pattern)
        self.description = description
    
    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        if pd.isna(data):
            return True, None
        
        if isinstance(data, str):
            if self.pattern.match(data):
                return True, None
            return False, f"格式不正确{', ' + self.description if self.description else ''}: {data}"
        return False, f"不是字符串类型: {type(data).__name__}"

class TypeValidator(Validator):
    """类型验证器"""
    
    def __init__(self, data_type: type):
        self.data_type = data_type
    
    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        if pd.isna(data):
            return True, None
        
        if isinstance(data, self.data_type):
            return True, None
        
        try:
            self.data_type(data)
            return True, None
        except (ValueError, TypeError):
            return False, f"无法转换为 {self.data_type.__name__}: {data}"

class NotNullValidator(Validator):
    """非空验证器"""
    
    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        if pd.isna(data):
            return False, "值不能为空"
        if isinstance(data, str) and data.strip() == "":
            return False, "值不能为空字符串"
        return True, None

class ChoiceValidator(Validator):
    """选项验证器"""
    
    def __init__(self, choices: List[Any], case_sensitive: bool = True):
        self.choices = choices
        self.case_sensitive = case_sensitive
    
    def validate(self, data: Any) -> Tuple[bool, Optional[str]]:
        if pd.isna(data):
            return True, None
        
        if isinstance(data, str) and not self.case_sensitive:
            data = data.lower()
            choices = [c.lower() if isinstance(c, str) else c for c in self.choices]
        else:
            choices = self.choices
        
        if data in choices:
            return True, None
        return False, f"值不在可选范围内: {data}, 可选值: {choices}"

class ValidationRule:
    """验证规则"""
    
    def __init__(self, column: str, validators: List[Validator], required: bool = False):
        self.column = column
        self.validators = validators
        self.required = required

class DataValidator:
    """数据验证器"""
    
    def __init__(self, rules: List[ValidationRule] = None):
        self.rules = rules or []
        self.errors = []
    
    def add_rule(self, rule: ValidationRule):
        """添加验证规则"""
        self.rules.append(rule)
    
    def validate_row(self, row: Dict[str, Any], row_index: int) -> bool:
        """
        验证单行数据
        :param row: 行数据
        :param row_index: 行索引
        :return: 是否通过验证
        """
        row_errors = []
        
        for rule in self.rules:
            value = row.get(rule.column)
            
            if rule.required and pd.isna(value):
                row_errors.append(f"{rule.column}: 必填字段为空")
                continue
            
            for validator in rule.validators:
                is_valid, error_msg = validator.validate(value)
                if not is_valid:
                    row_errors.append(f"{rule.column}: {error_msg}")
        
        if row_errors:
            self.errors.append(f"第{row_index}行: {', '.join(row_errors)}")
            return False
        
        return True
    
    def validate_data(self, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        验证所有数据
        :param data: 数据列表
        :return: (通过验证的数据, 错误列表)
        """
        self.errors = []
        valid_data = []
        
        for i, row in enumerate(data, 1):
            if self.validate_row(row, i):
                valid_data.append(row)
        
        return valid_data, self.errors
    
    def get_errors(self) -> List[str]:
        """获取所有错误"""
        return self.errors

class NBADataValidator(DataValidator):
    """NBA数据专用验证器"""
    
    def __init__(self, strict: bool = False):
        super().__init__()
        self.strict = strict
        self._init_rules()
    
    def _init_rules(self):
        """初始化验证规则"""
        # 球员名称（仅在严格模式下必填）
        if self.strict:
            self.add_rule(ValidationRule(
                column='player_name',
                validators=[NotNullValidator(), PatternValidator(r'^[A-Za-z\s.-]+$', '应为英文姓名')],
                required=True
            ))
        else:
            self.add_rule(ValidationRule(
                column='player_name',
                validators=[PatternValidator(r'^[A-Za-z\s.-]*$', '应为英文姓名')],
                required=False
            ))
        
        # 年龄
        self.add_rule(ValidationRule(
            column='age',
            validators=[RangeValidator(18, 45)],
            required=False
        ))
        
        # 位置
        self.add_rule(ValidationRule(
            column='position',
            validators=[ChoiceValidator(['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'F/C', 'G/F'])],
            required=False
        ))
        
        # 比赛场数
        self.add_rule(ValidationRule(
            column='games',
            validators=[RangeValidator(0, 100)],
            required=False
        ))
        
        # 命中率
        self.add_rule(ValidationRule(
            column='fg_pct',
            validators=[RangeValidator(0, 1)],
            required=False
        ))
        
        # 三分命中率
        self.add_rule(ValidationRule(
            column='three_pct',
            validators=[RangeValidator(0, 1)],
            required=False
        ))
        
        # 罚球命中率
        self.add_rule(ValidationRule(
            column='ft_pct',
            validators=[RangeValidator(0, 1)],
            required=False
        ))
        
        # 得分
        self.add_rule(ValidationRule(
            column='points',
            validators=[RangeValidator(0, 100)],
            required=False
        ))
        
        # 篮板
        self.add_rule(ValidationRule(
            column='rebounds',
            validators=[RangeValidator(0, 50)],
            required=False
        ))
        
        # 助攻
        self.add_rule(ValidationRule(
            column='assists',
            validators=[RangeValidator(0, 30)],
            required=False
        ))
        
        # 抢断
        self.add_rule(ValidationRule(
            column='steals',
            validators=[RangeValidator(0, 10)],
            required=False
        ))
        
        # 盖帽
        self.add_rule(ValidationRule(
            column='blocks',
            validators=[RangeValidator(0, 10)],
            required=False
        ))
        
        # 赛季格式
        self.add_rule(ValidationRule(
            column='season_id',
            validators=[PatternValidator(r'^\d{4}-\d{2}$', '应为格式 YYYY-YY')],
            required=False
        ))

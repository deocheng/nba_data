# 数据处理执行计划

## 计划概述

根据项目规范文档 `PROJECT_SPEC.md`，本计划用于标准化数据处理流程，确保数据从CSV原始文件到PostgreSQL数据库的完整导入流程。

---

## 1. 数据处理流程

### 1.1 标准流程（已在规范中定义）
```
CSV原始数据 → 了解表结构 → 筛选有用数据 → 导出JSON → 导入数据库
```

### 1.2 流程详情

| 步骤 | 任务 | 负责人 | 状态 |
|------|------|--------|------|
| 1 | 查看CSV文件内容和结构 | AutoPick | 待执行 |
| 2 | 检查数据库表结构（如有） | AutoPick | 待执行 |
| 3 | 创建检查脚本确认数据格式 | AutoPick | 待执行 |
| 4 | 筛选有效数据（跳过注释行、空行） | AutoPick | 待执行 |
| 5 | 导出为JSON中间文件 | AutoPick | 待执行 |
| 6 | 创建导入脚本 | AutoPick | 待执行 |
| 7 | 执行数据库导入 | AutoPick | 待执行 |
| 8 | 验证数据完整性 | AutoPick | 待执行 |
| 9 | 更新项目规范文档 | AutoPick | 待执行 |

---

## 2. 当前待处理任务

### 2.1 马刺队赛季数据问题
**问题描述**: 2025-26赛季显示83场比赛，而常规赛季应为82场

**处理步骤**:
1. 检查CSV文件结构和内容
2. 确认是否包含表头行或重复记录
3. 修复数据并重新导入

### 2.2 临时文件管理
**处理步骤**:
1. 保留所有临时脚本文件（`import_*.py`, `check_*.py`, `fix_*.py`）
2. 文件名使用清晰的功能描述
3. 脚本开头添加标准注释模板

---

## 3. 脚本文件规范

### 3.1 脚本分类
| 类型 | 命名规则 | 用途 |
|------|---------|------|
| 检查脚本 | `check_*.py` | 验证数据格式、统计数量、查找问题 |
| 导入脚本 | `import_*.py` | 将CSV/JSON数据导入数据库 |
| 修复脚本 | `fix_*.py` | 修复数据问题（去重、更正错误） |
| 更新脚本 | `update_*.py` | 更新JSON中间文件 |

### 3.2 脚本模板
```python
#!/usr/bin/env python3
"""
脚本功能描述：[简要说明]
创建时间：YYYY-MM-DD
作者：AutoPick
关联文档：PROJECT_SPEC.md
"""

import psycopg2
import os

DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'nba'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433')
}

def main():
    # 主逻辑
    pass

if __name__ == '__main__':
    main()
```

---

## 4. 执行计划

### 4.1 第一阶段：数据检查（立即执行）
- [ ] 创建 `check_season_data.py` - 检查各赛季数据完整性
- [ ] 创建 `check_csv_structure.py` - 分析CSV文件结构
- [ ] 创建 `check_duplicates.py` - 查找重复记录

### 4.2 第二阶段：数据修复（根据检查结果）
- [ ] 创建 `fix_2025_2026spurs.py` - 修复2025-26赛季数据
- [ ] 创建 `update_games_json.py` - 更新比赛数据JSON文件

### 4.3 第三阶段：数据导入
- [ ] 创建 `import_all_csv.py` - 统一导入所有CSV数据
- [ ] 创建 `import_player_career.py` - 导入球员生涯数据

### 4.4 第四阶段：验证与文档更新
- [ ] 创建 `validate_data.py` - 验证导入数据
- [ ] 更新 `PROJECT_SPEC.md` - 添加变更记录

---

## 5. 数据验证规则

### 5.1 比赛数据验证
| 验证项 | 规则 | 期望值 |
|--------|------|--------|
| 常规赛数量 | 每队每赛季 | 82场 |
| 日期格式 | 统一格式 | YYYY-MM-DD |
| 胜负判断 | 结果字段 | W/L 或 比分比较 |
| 数据完整性 | 非空字段 | Date, Opp, Score |

### 5.2 验证SQL查询示例
```sql
-- 检查重复日期
SELECT "Date", COUNT(*) FROM tbl_2025_2026spurs GROUP BY "Date" HAVING COUNT(*) > 1;

-- 检查空值
SELECT COUNT(*) FROM tbl_2025_2026spurs WHERE "Date" IS NULL OR "Date" = '';

-- 统计胜负场次
SELECT "Rslt", COUNT(*) FROM tbl_2025_2026spurs GROUP BY "Rslt";
```

---

## 6. 风险与应对

### 6.1 潜在风险
| 风险 | 描述 | 应对措施 |
|------|------|----------|
| 数据丢失 | 导入过程中数据损坏 | 导入前备份，使用事务 |
| 重复导入 | 多次执行导致数据重复 | 使用 `ON CONFLICT` 处理 |
| 格式错误 | CSV格式不一致 | 统一预处理脚本 |
| 性能问题 | 大量数据导入耗时 | 分批导入，使用COPY命令 |

### 6.2 安全措施
- 导入前自动备份数据库
- 使用事务确保原子性
- 导入后验证数据完整性

---

## 7. 交付物

| 交付物 | 描述 | 状态 |
|--------|------|------|
| `PROJECT_SPEC.md` | 项目规范文档 | ✅ 已完成 |
| `check_*.py` | 数据检查脚本 | 待创建 |
| `fix_*.py` | 数据修复脚本 | 待创建 |
| `import_*.py` | 数据导入脚本 | 待创建 |
| `validate_data.py` | 数据验证脚本 | 待创建 |
| 数据库数据 | 完整的NBA数据 | 待导入 |

---

**计划版本**: v1.0  
**创建时间**: 2026-05-12  
**最后更新**: 2026-05-12
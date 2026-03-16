# Cursor 提示词库

## 🎯 快速提示词

### 提示词 1：完整实现新功能
```
@notes.py @test_notes.py @schemas.py

请完整实现 [功能名称]：

后端（notes.py）：
- 端点：[HTTP方法] [路径]
- 功能：[描述]
- 参数：[列表]
- 返回：[格式]

测试（test_notes.py）：
- 测试正常情况
- 测试边界情况
- 测试错误情况

验证（schemas.py）：
- 添加必要的验证规则

完成后运行 make test 验证。
```

### 提示词 2：添加完整测试
```
@test_notes.py

请为 [功能名称] 添加完整测试：

测试场景：
1. 正常情况：[描述]
2. 边界情况：[描述]
3. 404 错误：[描述]
4. 400 错误：[描述]

使用 pytest，确保所有测试通过。
```

### 提示词 3：优化现有代码
```
@notes.py

请优化以下代码：
1. 检查性能问题（N+1查询、缺少索引）
2. 检查安全问题（SQL注入、XSS）
3. 检查代码重复
4. 添加必要的注释
5. 运行 make lint 和 make format
```

### 提示词 4：生成文档
```
@writeup.md

请记录我刚完成的功能：

功能：[名称]
设计：
- 目标：[描述]
- 输入：[参数]
- 输出：[返回值]

实现：
- 修改的文件：[列表]
- 关键代码：[描述]

测试：
- 测试场景：[列表]
- 测试结果：[通过/失败]

使用的自动化：
- [描述如何使用 Cursor]
```

---

## 📋 具体任务提示词

### 任务 2：笔记搜索（已完成大部分）

#### 2.1 添加前端搜索界面
```
@frontend/index.html @frontend/style.css

请在前端添加搜索功能：

1. 搜索区域（在笔记列表上方）：
   - 搜索输入框（placeholder: "搜索笔记..."）
   - 搜索按钮
   - 清除按钮

2. 结果显示：
   - 显示搜索结果数量："找到 X 条笔记"
   - 高亮搜索关键词

3. 分页控件：
   - 上一页按钮
   - 页码显示："第 X 页 / 共 Y 页"
   - 下一页按钮

4. 排序选择：
   - 下拉菜单：最新、最旧、标题A-Z、标题Z-A

5. JavaScript 功能：
   - 调用 /notes/search/ API
   - 处理响应并更新列表
   - 处理分页点击事件

使用现有的样式风格，保持界面简洁美观。
```

#### 2.2 添加搜索测试
```
@backend/tests/test_notes.py

请添加搜索功能的完整测试：

测试用例：
1. test_search_notes_by_title - 按标题搜索
2. test_search_notes_by_content - 按内容搜索
3. test_search_notes_case_insensitive - 不区分大小写
4. test_search_notes_pagination - 分页功能
5. test_search_notes_sorting - 排序功能
6. test_search_notes_empty_result - 无结果
7. test_search_notes_no_query - 不提供搜索词（返回全部）

每个测试需要：
- 创建测试数据
- 调用 API
- 验证响应格式和内容
- 清理测试数据
```

---

### 任务 3：完整 CRUD 功能

```
@notes.py @test_notes.py @schemas.py

请完整实现笔记的更新和删除功能：

1. 更新端点（notes.py）：
   - PUT /notes/{note_id}
   - 接收 NoteCreate 数据
   - 更新标题和内容
   - 返回更新后的笔记
   - 404 如果笔记不存在

2. 删除端点（notes.py）：
   - DELETE /notes/{note_id}
   - 删除指定笔记
   - 返回 204 No Content
   - 404 如果笔记不存在

3. 数据验证（schemas.py）：
   - title: 1-200 字符
   - content: 至少 1 字符

4. 测试（test_notes.py）：
   - test_update_note_success
   - test_update_note_not_found
   - test_update_note_validation_error
   - test_delete_note_success
   - test_delete_note_not_found

完成后运行 make test 验证。
```

---

### 任务 7：错误处理

```
@main.py @schemas.py @notes.py

请实现统一的错误处理：

1. 全局异常处理器（main.py）：
   - HTTPException → {"ok": false, "error": {...}}
   - ValidationError → {"ok": false, "error": {...}}
   - 其他异常 → {"ok": false, "error": {"code": "INTERNAL_ERROR", ...}}

2. 数据验证（schemas.py）：
   - NoteCreate: title (1-200字符), content (非空)
   - 添加自定义错误消息

3. 更新所有端点（notes.py）：
   - 使用新的错误格式
   - 添加适当的状态码

4. 测试错误情况：
   - test_create_note_empty_title
   - test_create_note_title_too_long
   - test_create_note_empty_content
   - test_get_note_not_found

完成后运行 make test 验证。
```

---

### 任务 8：列表分页

```
@notes.py @action_items.py @test_notes.py

请为所有列表端点添加分页：

1. 更新 GET /notes（notes.py）：
   - 添加参数：page (默认1), page_size (默认10)
   - 返回：{"items": [...], "total": N, "page": 1, "page_size": 10}
   - 添加分页逻辑

2. 更新 GET /action-items（action_items.py）：
   - 同样的分页逻辑

3. 测试（test_notes.py）：
   - test_list_notes_pagination
   - test_list_notes_first_page
   - test_list_notes_last_page
   - test_list_notes_empty_page
   - test_list_notes_invalid_page_size

完成后运行 make test 验证。
```

---

### 任务 10：测试覆盖率

```
@backend/tests/

请提高测试覆盖率到 80% 以上：

1. 检查当前覆盖率：
   - 运行 pytest --cov=backend --cov-report=term-missing
   - 找出未覆盖的代码

2. 添加缺失的测试：
   - 所有端点的成功情况
   - 所有端点的错误情况（400, 404, 500）
   - 边界情况（空数据、大数据）
   - 并发情况（如适用）

3. 测试文件组织：
   - test_notes.py - 笔记相关测试
   - test_action_items.py - 待办事项测试
   - test_extract.py - 提取功能测试

4. 运行并报告：
   - make coverage
   - 确保覆盖率 > 80%
```

---

## 🤖 多智能体工作流提示词

### 使用 Composer 并行处理

```
@notes.py @test_notes.py @frontend/index.html

请同时完成以下三个独立任务：

任务 A（notes.py）：
- 添加 PUT /notes/{id} 端点
- 添加 DELETE /notes/{id} 端点
- 添加错误处理

任务 B（test_notes.py）：
- 为新端点添加测试
- 测试成功和错误情况
- 确保测试通过

任务 C（frontend/index.html）：
- 添加编辑按钮到每个笔记
- 添加删除按钮到每个笔记
- 实现编辑和删除的 JavaScript 逻辑

这三个任务可以并行完成，互不依赖。
```

---

## 📊 文档生成提示词

### 生成 writeup.md

```
@writeup.md

请帮我生成完整的作业报告：

## 我完成的任务：
1. 任务 2：笔记搜索功能
2. 任务 8：列表分页
3. 任务 10：测试覆盖率

## 使用的 Cursor 功能：
1. Cursor Rules（.cursorrules）
2. Cursor Composer（多文件编辑）
3. 自定义提示词库

## 请包含以下内容：
1. 每个任务的设计（目标、输入、输出、步骤）
2. 前后对比（手动 vs 自动化）
3. 使用的自主级别和监督策略
4. 多智能体工作流的实现方式
5. 解决的痛点和效果

使用清晰的 Markdown 格式，包含代码示例。
```

---

## 💡 使用技巧

### 1. 使用 @ 符号引用文件
```
@notes.py 请添加新端点
@test_notes.py 请添加测试
```

### 2. 使用 Composer 处理多文件
- 按 Ctrl + I 打开 Composer
- 添加多个文件
- 给出多任务指令

### 3. 保存常用提示词
- 复制到这个文件
- 需要时直接使用
- 根据需要修改

### 4. 链式提示
```
第一步：@notes.py 实现功能
第二步：@test_notes.py 添加测试
第三步：运行 make test 验证
第四步：@writeup.md 记录结果
```

---

## 🎯 快速开始检查清单

- [ ] 创建 .cursorrules 文件
- [ ] 阅读这个提示词库
- [ ] 选择 2-3 个任务
- [ ] 使用 Composer 实现
- [ ] 运行测试验证
- [ ] 生成 writeup.md
- [ ] 提交作业

---

需要实现哪个任务？直接复制对应的提示词使用！



# 任务列表（可选任务）

## ✅ 你已经完成的任务

### 2) 笔记搜索功能（带分页和排序）✅ 
**难度：中等**

你已经实现了：
- ✅ `GET /notes/search?q=...&page=1&page_size=10&sort=created_desc`
- ✅ 不区分大小写的标题/内容匹配
- ✅ 返回 `items`, `total`, `page`, `page_size`, `total_pages`
- ✅ SQLAlchemy 查询组合（过滤、排序、分页）
- ✅ 添加了 `created_at` 字段

**还需要做的：**
- ⬜ 在前端添加搜索输入框
- ⬜ 显示结果数量
- ⬜ 添加上一页/下一页按钮
- ⬜ 在 `backend/tests/test_notes.py` 添加测试

---

## 📋 其他可选任务

### 1) 将前端迁移到 Vite + React
**难度：复杂**

**要做什么：**
- 在 `week5/frontend/` 创建 Vite + React 应用
- 替换当前的静态文件为构建后的包
- 用 React 实现现有功能（笔记列表、创建、删除、编辑）
- 更新 Makefile

**为什么选这个：**
- 学习现代前端开发
- 体验 React 组件化开发
- 练习前后端分离

---

### 3) 完整的笔记 CRUD 功能
**难度：中等** ⭐ 推荐

**要做什么：**
- 添加 `PUT /notes/{id}` - 更新笔记
- 添加 `DELETE /notes/{id}` - 删除笔记
- 在前端实现乐观更新（先更新 UI，再发请求）
- 添加数据验证（最小长度、最大长度）

**实操步骤：**

1. **添加更新端点**（在 `notes.py`）：
```python
@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteCreate, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = payload.title
    note.content = payload.content
    db.commit()
    db.refresh(note)
    return NoteRead.model_validate(note)
```

2. **添加删除端点**：
```python
@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
```

3. **在前端添加编辑和删除按钮**

---

### 4) 待办事项：过滤和批量完成
**难度：中等** ⭐ 推荐

**要做什么：**
- 添加 `GET /action-items?completed=true|false` - 按完成状态过滤
- 添加 `POST /action-items/bulk-complete` - 批量标记完成
- 在前端添加过滤开关和批量操作 UI

**为什么选这个：**
- 学习查询参数过滤
- 练习事务处理
- 实现批量操作

---

### 5) 标签功能（多对多关系）
**难度：复杂**

**要做什么：**
- 添加 `Tag` 模型和 `note_tags` 关联表
- 实现标签的增删查
- 笔记可以添加/移除标签
- 自动从 `#hashtags` 提取标签

**为什么选这个：**
- 学习数据库多对多关系
- 练习复杂的数据模型设计

---

### 6) 改进提取逻辑
**难度：中等**

**要做什么：**
- 扩展 `extract.py` 解析：
  - `#hashtags` → 标签
  - `- [ ] task text` → 待办事项
- 添加 `POST /notes/{id}/extract` 端点

**示例：**
输入笔记内容：
```
学习 #Python 和 #FastAPI
- [ ] 完成作业
- [ ] 写报告
```

自动提取：
- 标签：Python, FastAPI
- 待办事项：完成作业、写报告

---

### 7) 健壮的错误处理
**难度：简单-中等** ⭐⭐ 强烈推荐

**要做什么：**
- 添加数据验证（最小长度、非空字符串）
- 统一错误响应格式：
```json
{
  "ok": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "笔记未找到"
  }
}
```

**实操步骤：**

1. **更新 schemas.py**：
```python
from pydantic import BaseModel, Field

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
```

2. **添加全局异常处理器**（在 `main.py`）：
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            }
        }
    )
```

---

### 8) 列表端点分页
**难度：简单** ⭐⭐⭐ 最推荐（简单且实用）

**要做什么：**
- 给 `GET /notes` 和 `GET /action-items` 添加分页
- 返回 `items` 和 `total`

**实操步骤：**

修改 `list_notes` 函数：
```python
@router.get("/", response_model=dict)
def list_notes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # 计算总数
    total = db.execute(select(func.count()).select_from(Note)).scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    items = db.execute(
        select(Note).offset(offset).limit(page_size)
    ).scalars().all()
    
    return {
        "items": [NoteRead.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size
    }
```

---

### 9) 查询性能和索引
**难度：简单-中等**

**要做什么：**
- 添加 SQLite 索引（如 `notes.title`）
- 验证查询性能改进

**实操步骤：**

在 `models.py` 中：
```python
class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)  # 添加索引
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)  # 添加索引
```

---

### 10) 测试覆盖率改进
**难度：简单** ⭐⭐⭐ 强烈推荐

**要做什么：**
- 为每个端点添加测试
- 测试 400/404 错误场景
- 测试并发/事务行为

**实操步骤：**

创建 `backend/tests/test_notes.py`：
```python
def test_create_note(client):
    response = client.post("/notes/", json={
        "title": "Test",
        "content": "Content"
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test"

def test_search_notes(client):
    # 先创建笔记
    client.post("/notes/", json={"title": "Python", "content": "Learning"})
    
    # 搜索
    response = client.get("/notes/search/?q=python")
    assert response.status_code == 200
    assert response.json()["total"] >= 1

def test_note_not_found(client):
    response = client.get("/notes/999")
    assert response.status_code == 404
```

---

### 11) 部署到 Vercel
**难度：中等-复杂**

**要做什么：**
- 配置前端部署到 Vercel
- 配置后端 API（Vercel 或其他平台）
- 设置环境变量和 CORS

---

## 🎯 推荐选择组合

### 组合 1：简单快速（适合新手）
- ✅ 任务 2：笔记搜索（已完成大部分）
- ⭐ 任务 8：列表端点分页
- ⭐ 任务 10：测试覆盖率改进

### 组合 2：中等挑战
- ✅ 任务 2：笔记搜索（已完成）
- ⭐ 任务 3：完整 CRUD
- ⭐ 任务 7：错误处理

### 组合 3：高级挑战
- ✅ 任务 2：笔记搜索（已完成）
- 任务 5：标签功能
- 任务 1：迁移到 React

---

## 💡 如何选择任务？

### 考虑因素：
1. **时间**：你有多少时间？
2. **难度**：你的技术水平如何？
3. **兴趣**：你想学什么？
4. **实用性**：哪些功能最有用？

### 建议：
- **如果时间紧**：选任务 8 + 10（简单且快速）
- **如果想学更多**：选任务 3 + 7（实用且全面）
- **如果想挑战**：选任务 5 + 1（复杂但有趣）

---

## 📝 下一步行动

1. **完成任务 2 的剩余部分**：
   - 添加前端搜索界面
   - 添加测试

2. **选择另外 1-2 个任务**

3. **编写 writeup.md**：
   - 记录你的设计
   - 记录前后对比
   - 记录如何使用 Warp 自动化

4. **测试和提交**

---

需要我帮你实现哪个任务？或者有什么不清楚的地方？



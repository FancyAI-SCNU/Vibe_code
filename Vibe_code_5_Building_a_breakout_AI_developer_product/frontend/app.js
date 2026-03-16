async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// 当前选中的标签
let selectedTag = null;

// 加载所有笔记
async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const notes = await fetchJSON('/notes/');
  renderNotes(notes);
  await fetchTags();
}

// 获取并渲染标签云
async function fetchTags() {
  try {
    const tags = await fetchJSON('/tags/');
    const tagCloud = document.getElementById('tag-cloud');
    tagCloud.innerHTML = '';
    
    if (tags.length === 0) {
      tagCloud.innerHTML = '<p class="no-tags">暂无标签</p>';
      return;
    }
    
    for (const tag of tags) {
      const btn = document.createElement('button');
      btn.className = 'tag-btn';
      if (selectedTag === tag.name) {
        btn.classList.add('active');
      }
      btn.innerHTML = `${tag.name} <span class="tag-count">${tag.note_count}</span>`;
      btn.onclick = () => filterNotesByTag(tag.name);
      tagCloud.appendChild(btn);
    }
  } catch (error) {
    console.error('Failed to fetch tags:', error);
  }
}

// 按标签筛选笔记
async function filterNotesByTag(tagName) {
  try {
    // 如果点击的是当前选中的标签，则取消筛选
    if (selectedTag === tagName) {
      selectedTag = null;
      await loadNotes();
      return;
    }
    
    selectedTag = tagName;
    
    // 获取该标签的笔记
    const notes = await fetchJSON(`/tags/${encodeURIComponent(tagName)}/notes`);
    renderNotes(notes, '', tagName);
    
    // 更新标签云的选中状态
    await fetchTags();
  } catch (error) {
    console.error('Failed to filter by tag:', error);
  }
}

// 搜索笔记
async function searchNotes() {
  const searchInput = document.getElementById('search-input');
  const query = searchInput.value.trim();
  const statusDiv = document.getElementById('search-status');
  
  // 如果搜索框为空，加载所有笔记
  if (!query) {
    statusDiv.textContent = '请输入搜索关键词';
    statusDiv.className = 'search-status warning';
    setTimeout(() => statusDiv.textContent = '', 2000);
    return;
  }
  
  try {
    // 显示加载状态
    statusDiv.textContent = '🔍 搜索中...';
    statusDiv.className = 'search-status loading';
    
    // 调用搜索 API
    const url = `/notes/search/?q=${encodeURIComponent(query)}&sort=created_desc`;
    const result = await fetchJSON(url);
    const notes = result.items || [];
    
    // 清除标签筛选
    selectedTag = null;
    await fetchTags();
    
    // 显示搜索结果
    if (notes.length === 0) {
      statusDiv.textContent = `未找到包含 "${query}" 的笔记`;
      statusDiv.className = 'search-status info';
      document.getElementById('notes').innerHTML = '<li class="no-results">没有找到匹配的笔记</li>';
    } else {
      statusDiv.textContent = `找到 ${notes.length} 条结果`;
      statusDiv.className = 'search-status success';
      renderNotes(notes, query);
    }
    
    // 3秒后清除状态提示
    setTimeout(() => statusDiv.textContent = '', 3000);
    
  } catch (error) {
    statusDiv.textContent = `搜索失败: ${error.message}`;
    statusDiv.className = 'search-status error';
    console.error('Search error:', error);
  }
}

// 清除搜索
async function clearSearch() {
  const searchInput = document.getElementById('search-input');
  const statusDiv = document.getElementById('search-status');
  
  searchInput.value = '';
  statusDiv.textContent = '';
  selectedTag = null;
  
  // 重新加载所有笔记
  await loadNotes();
}

// 渲染笔记列表（支持关键词高亮和标签显示）
function renderNotes(notes, highlightQuery = '', filterTag = '') {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  
  if (notes.length === 0) {
    list.innerHTML = '<li class="no-results">没有找到匹配的笔记</li>';
    return;
  }
  
  for (const n of notes) {
    const li = document.createElement('li');
    li.className = 'note-item';
    
    let title = n.title;
    let content = n.content;
    
    // 如果有搜索关键词，高亮显示
    if (highlightQuery) {
      const regex = new RegExp(`(${highlightQuery})`, 'gi');
      title = title.replace(regex, '<mark>$1</mark>');
      content = content.replace(regex, '<mark>$1</mark>');
    }
    
    // 构建笔记内容
    const noteContent = document.createElement('div');
    noteContent.className = 'note-content';
    noteContent.innerHTML = `<strong>${title}</strong>: ${content}`;
    li.appendChild(noteContent);
    
    // 添加标签显示
    if (n.tags && n.tags.length > 0) {
      const tagsContainer = document.createElement('div');
      tagsContainer.className = 'note-tags';
      
      for (const tag of n.tags) {
        const tagSpan = document.createElement('span');
        tagSpan.className = 'tag';
        if (filterTag === tag.name) {
          tagSpan.classList.add('active');
        }
        tagSpan.textContent = `#${tag.name}`;
        tagSpan.onclick = (e) => {
          e.stopPropagation();
          filterNotesByTag(tag.name);
        };
        tagsContainer.appendChild(tagSpan);
      }
      
      li.appendChild(tagsContainer);
    }
    
    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  // 笔记表单提交
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  // 搜索按钮点击事件
  document.getElementById('search-btn').addEventListener('click', searchNotes);
  
  // 清除按钮点击事件
  document.getElementById('clear-btn').addEventListener('click', clearSearch);
  
  // 搜索框回车键事件
  document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      searchNotes();
    }
  });

  // Action Items 表单提交
  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  // 初始加载
  loadNotes();
  loadActions();
});

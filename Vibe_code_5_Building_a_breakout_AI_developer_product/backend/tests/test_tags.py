def test_create_tag(client):
    """测试创建标签"""
    payload = {"name": "Python"}
    r = client.post("/tags", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Python"
    assert data["id"] is not None
    assert data["note_count"] == 0


def test_get_tags(client):
    """测试获取标签列表"""
    # Create some tags
    client.post("/tags", json={"name": "Python"})
    client.post("/tags", json={"name": "AI"})
    
    r = client.get("/tags")
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) >= 2
    assert all("id" in tag and "name" in tag and "note_count" in tag for tag in tags)


def test_delete_tag(client):
    """测试删除标签"""
    # Create a tag
    r = client.post("/tags", json={"name": "ToDelete"})
    tag_id = r.json()["id"]
    
    # Delete the tag
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204
    
    # Verify it's deleted
    r = client.get("/tags")
    tags = r.json()
    assert not any(tag["name"] == "ToDelete" for tag in tags)


def test_add_tag_to_note(client):
    """测试为笔记添加标签"""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    note_id = r.json()["id"]
    
    # Add tag to note
    tag_payload = {"name": "Python"}
    r = client.post(f"/notes/{note_id}/tags", json=tag_payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Python"
    assert data["note_count"] == 1


def test_remove_tag_from_note(client):
    """测试移除笔记的标签"""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    note_id = r.json()["id"]
    
    # Add tag to note
    tag_payload = {"name": "Python"}
    r = client.post(f"/notes/{note_id}/tags", json=tag_payload)
    tag_id = r.json()["id"]
    
    # Remove tag from note
    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 204


def test_tag_not_found(client):
    """测试404错误"""
    # Try to delete non-existent tag
    r = client.delete("/tags/99999")
    assert r.status_code == 404
    
    # Try to remove tag from non-existent note
    r = client.delete("/notes/99999/tags/1")
    assert r.status_code == 404


def test_note_tags_relationship(client):
    """测试多对多关系"""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    note_id = r.json()["id"]
    
    # Add multiple tags to the note
    client.post(f"/notes/{note_id}/tags", json={"name": "Python"})
    client.post(f"/notes/{note_id}/tags", json={"name": "AI"})
    client.post(f"/notes/{note_id}/tags", json={"name": "ML"})
    
    # Verify tags are associated
    r = client.get("/tags")
    tags = r.json()
    python_tag = next((t for t in tags if t["name"] == "Python"), None)
    assert python_tag is not None
    assert python_tag["note_count"] >= 1
    
    # Create another note and add the same tag
    note_payload2 = {"title": "Another Note", "content": "More content"}
    r = client.post("/notes/", json=note_payload2)
    note_id2 = r.json()["id"]
    client.post(f"/notes/{note_id2}/tags", json={"name": "Python"})
    
    # Verify the tag now has 2 notes
    r = client.get("/tags")
    tags = r.json()
    python_tag = next((t for t in tags if t["name"] == "Python"), None)
    assert python_tag["note_count"] >= 2


def test_create_duplicate_tag(client):
    """测试创建重复标签返回现有标签"""
    # Create a tag
    r = client.post("/tags", json={"name": "Duplicate"})
    assert r.status_code == 201
    first_id = r.json()["id"]
    
    # Try to create the same tag again
    r = client.post("/tags", json={"name": "Duplicate"})
    assert r.status_code == 201
    second_id = r.json()["id"]
    
    # Should return the same tag
    assert first_id == second_id


def test_add_duplicate_tag_to_note(client):
    """测试为笔记添加重复标签"""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Test content"}
    r = client.post("/notes/", json=note_payload)
    note_id = r.json()["id"]
    
    # Add tag twice
    client.post(f"/notes/{note_id}/tags", json={"name": "Python"})
    r = client.post(f"/notes/{note_id}/tags", json={"name": "Python"})
    assert r.status_code == 201
    
    # Verify tag count is still 1
    r = client.get("/tags")
    tags = r.json()
    python_tag = next((t for t in tags if t["name"] == "Python"), None)
    assert python_tag["note_count"] == 1



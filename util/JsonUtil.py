import json
import re

def set_json(json_data, path, value):
    if not isinstance(json_data, (dict, list)):
        raise ValueError("Initial data must be a dictionary or list")
    keys = parse_path(path)
    if not keys:  # 如果解析结果为空，说明路径格式有误
        raise ValueError("Path format error or empty key found")
    return _set_recursive(json_data, keys, value)

def parse_path(path):
    path = path.strip('$')
    pattern = r'\[([0-9]+)\]'
    keys = []
    for part in path.split('.'):
        if not part:  # 忽略空键
            continue
        if '[' in part:
            key = part.split('[')[0]
            if key:
                keys.append(key)
            index = int(re.search(pattern, part).group(1))
            keys.append(index)
        else:
            keys.append(part)
    return keys

def _set_recursive(data, keys, value):
    if not keys:
        return value
    current = keys.pop(0)
    if isinstance(current, int):
        if not isinstance(data, list):
            raise TypeError("Expected a list at index, found '{}'".format(type(data).__name__))
        while len(data) <= current:
            data.append(None)
        if data[current] is None or (keys and not isinstance(data[current], (dict, list))):
            data[current] = _create_structure_for_next_key(keys)
        data[current] = _set_recursive(data[current], keys, value)
    else:
        if not isinstance(data, dict):
            raise TypeError("Expected a dict at key '{}', found '{}'".format(current, type(data).__name__))
        if current not in data or (keys and not isinstance(data[current], (dict, list))):
            data[current] = _create_structure_for_next_key(keys)
        data[current] = _set_recursive(data[current], keys, value)
    return data

def _create_structure_for_next_key(keys):
    if keys and isinstance(keys[0], int):
        return []  # 需要数组
    else:
        return {}  # 需要字典

def test_set_json():
    errors = 0

    # 测试用例 1
    json_data = {}
    set_json(json_data, "$.a.b", 5)
    expected = {'a': {'b': 5}}
    if json_data != expected:
        
        errors += 1

    # 测试用例 2
    json_data = {"a": [{}]}
    set_json(json_data, "$.a[0].b", 1)
    expected = {'a': [{'b': 1}]}
    if json_data != expected:
        
        errors += 1

    # 测试用例 3
    json_data = {"a": []}
    set_json(json_data, "$.a[2].b", 3)
    expected = {'a': [None, None, {'b': 3}]}
    if json_data != expected:
        
        errors += 1

    # 测试用例 4
    json_data = {"a": "string"}
    set_json(json_data, "$.a.b", {"x": "y"})
    expected = {'a': {'b': {'x': 'y'}}}
    if json_data != expected:
        
        errors += 1

    # 测试用例 5
    json_data = {}
    set_json(json_data, "$.a.b.c.d.e", 10)
    expected = {'a': {'b': {'c': {'d': {'e': 10}}}}}
    if json_data != expected:
        
        errors += 1

# 运行测试
test_set_json()


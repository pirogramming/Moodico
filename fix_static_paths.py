# 'image': static('images/test.jpg')이렇게 하드 코딩하면 베포나 파일 구조 바뀌면 안좋다고 해서 
# 자동으로 이미지 경로 지정해주는거 해봤습니다. 이파일 실행 하기전에 파일 커밋해두고 해주세요 의도하지 않은게 바뀔수도 있어서요.....

import os
import re

PROJECT_DIR = '.'  # 프로젝트 루트 경로
STATIC_PATTERN = re.compile(r"[\"'](/static/[^\"']+\.(jpg|jpeg|png|gif|css|js))[\"']")

def update_python_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_content = content
    matches = STATIC_PATTERN.findall(content)

    if matches:
        # static import가 없다면 추가
        if 'from django.templatetags.static import static' not in content:
            updated_content = "from django.templatetags.static import static\n" + updated_content

        def replacer(match):
            path = match.group(1).replace('/static/', '')
            return f"static('{path}')"

        updated_content = re.sub(STATIC_PATTERN, lambda m: replacer(m), updated_content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f'✅ Python 파일 수정됨: {file_path}')

def update_template_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_content = content
    matches = STATIC_PATTERN.findall(content)

    if matches:
        # {% load static %} 추가
        if '{% load static %}' not in content:
            updated_content = '{% load static %}\n' + updated_content

        def replacer(match):
            path = match.group(1).replace('/static/', '')
            return f'"{{% static \'{path}\' %}}"'

        updated_content = re.sub(STATIC_PATTERN, lambda m: replacer(m), updated_content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f'🎨 템플릿 파일 수정됨: {file_path}')

def walk_and_fix_static(project_dir):
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith('.py'):
                update_python_file(os.path.join(root, file))
            elif file.endswith('.html'):
                update_template_file(os.path.join(root, file))

if __name__ == '__main__':
    walk_and_fix_static(PROJECT_DIR)

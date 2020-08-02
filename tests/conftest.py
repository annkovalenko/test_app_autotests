import pytest
import requests
import os
from urllib.parse import quote

BACKEND_BASE_URL = 'http://localhost:5000/api/v1/templates'


@pytest.fixture(name="load_templates")
def load_templates(request):
    # Очистим шаблоны перед накатом фикстуры
    resp = requests.get(BACKEND_BASE_URL)
    assert resp.status_code == 200
    existing_templates = resp.json()["templates"]
    for template_id in existing_templates:
        resp = requests.delete(f'{BACKEND_BASE_URL}/{quote(template_id)}')
        assert resp.status_code == 200
    check = requests.get(BACKEND_BASE_URL)
    assert check.status_code == 200
    assert check.json()["templates"] == []
    # Извлекаем список файлов шаблонов для наката из маркера
    mark = request.node.get_closest_marker("load_templates")
    if not mark:
        raise ValueError("Не указан маркер @pytest.mark.load_templates(список шаблонов)")
    templates = mark.args[0] # Берём 1й из переданных параметров в маркер
    for filename in templates:
        short_filename = os.path.basename(filename)
        with open(filename, "rb") as f:
            payload = {
                "file": (short_filename, f)
            }
            resp = requests.put(BACKEND_BASE_URL, files=payload)
            assert resp.status_code == 201
    yield
    response = requests.get(BACKEND_BASE_URL)
    assert response.status_code == 200
    template_ids = response.json()["templates"]
    for template_id in template_ids:
        resp = requests.delete(f'{BACKEND_BASE_URL}/{quote(template_id)}')
        assert resp.status_code == 200


def pytest_runtest_makereport(item, call):
    if "smoke" in item.keywords:
        if call.excinfo is not None:
            pytest.exit('Не проходит smoke-test. Нет смысла выполнять остальные тесты.', 1)
    

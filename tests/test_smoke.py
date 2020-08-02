# TODO: 

# 2. плагин + декоратор для запуска модуля первым!
# 3. Метки на выход при непрохождении тестов.
# "Из-за того что подготовка данных через фикстуры возможна 
# только с использованием методов, которые собственно и необходимо протестировать 
# (замкнутый круг: нет гарантии, что они работают корректно), мы сначала проведём "дым" работоспособности
# методов, используемых в фикстуре. Без этого подготовка данных для тестов 
# нельзя считать стабильной"

import pytest
import requests
from .conftest import BACKEND_BASE_URL
from urllib.parse import quote

@pytest.mark.first # Из pytest-ordering
@pytest.mark.smoke # Собственный маркер для критически важного теста
def test_template_list():
    response = requests.get(BACKEND_BASE_URL)
    assert response.status_code == 200
    template_ids = response.json()["templates"]
    if template_ids:
        for template_id in template_ids:
            resp = requests.delete(f'{BACKEND_BASE_URL}/{quote(template_id)}')
            assert resp.status_code == 200
    
    payload = {"file": (open('etc/data_fixtures/element_boundary_values.yaml', 'rb'))}
    lst = requests.put(BACKEND_BASE_URL, files=payload)
    assert lst.status_code == 201

    response_lst = requests.get(BACKEND_BASE_URL)
    assert response_lst.status_code == 200
    assert response_lst.json() == {"templates": ["element_boundary_values"]} # не уверена, нужна ли проверка месседжа

    del_template = requests.delete(f"{BACKEND_BASE_URL}/element_boundary_values")
    assert del_template.status_code == 200

    empty_lst = requests.get(BACKEND_BASE_URL)
    assert response.status_code == 200
    assert empty_lst.json()["templates"] == []




        


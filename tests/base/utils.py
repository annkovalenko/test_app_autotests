import os
import requests
import yaml
from bs4 import BeautifulSoup


def not_found_message(tmpl_id):
    return {"message": f"No template with tmpl_id={tmpl_id} found!"}


def success_delete(tmpl_id):
    return {"message": f"Template with tmpl_id={tmpl_id} successfully deleted!"}


def success_upload(tmpl_id):
    return {"message": f"Template successfully uploaded. tmpl_id={tmpl_id}"}


def success_install(tmpl_id):
    return {"message": f"Template with tmpl_id={tmpl_id} successfully installed!"}


def get_tmpl_id_from_filename(filename):
    short_filename = os.path.basename(filename)
    dot_pos = short_filename.rfind(".")
    if dot_pos >= 0:
        return short_filename[:dot_pos]
    return short_filename

WEB_PAGE_URL = 'http://localhost:5000'

def check_no_template_installed():
    resp = requests.get(WEB_PAGE_URL)
    assert resp.status_code == 200
    
    soup = BeautifulSoup(resp.text, "html.parser")
    tag = soup.find(string='No template uploaded or your template is empty...')
    assert tag is not None

def check_success_install(tmpl_filename):
    resp = requests.get(WEB_PAGE_URL)
    assert resp.status_code == 200
    
    soup = BeautifulSoup(resp.text, "html.parser")

    with open(tmpl_filename, 'r') as f:
        template = yaml.safe_load(f)
    for element in template:
        tag = soup.find(id=str(element["id"]))
        assert tag is not None
        assert tag.string == str(element["label"])
        if "link" not in element:
            assert "disabled" in tag.attrs["class"]
            assert tag.name != "a"
        else:
            assert "disabled" not in tag.attrs["class"]
            assert tag.name == "a"
            assert "href" in tag.attrs
            assert tag.attrs["href"] == str(element["link"])
            


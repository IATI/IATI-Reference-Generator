import os
import shutil
import json
from bs4 import BeautifulSoup


if os.path.exists("output.zip"):
    os.remove("output.zip")
if os.path.isdir("output"):
    shutil.rmtree("output")


class_dict = dict()


build_dirs = {
    "203": "IATI-Standard-SSOT-version-2.03/docs/en/_build/dirhtml",
    "202": "IATI-Standard-SSOT-version-2.02/docs/en/_build/dirhtml",
    "201": "IATI-Standard-SSOT-version-2.01/docs/en/_build/dirhtml",
    "105": "IATI-Standard-SSOT-version-1.05/docs/en/_build/dirhtml",
    "104": "IATI-Standard-SSOT-version-1.04/docs/en/_build/dirhtml",
    "103": "IATI-Standard-SSOT-version-1.03/103.new",
    "102": "IATI-Standard-SSOT-version-1.02/102.new",
    "101": "IATI-Standard-SSOT-version-1.01/101.new",
    "guidance": "IATI-Guidance/en/_build/dirhtml",
    "developer-documentation": "IATI-Developer-Documentation/_build/dirhtml"
}

ignore_dirs = [
    "404",
    "CONTRIBUTING",
    "genindex",
    "gsearch",
    "license",
    "README",
    "search",
    "sitemap"
]


for parent_slug, root_dir in build_dirs.items():
    class_dict[parent_slug] = dict()
    for dirname, dirs, files in os.walk(root_dir, followlinks=True):
        dir_split = dirname.split(os.path.sep)
        root_len = len(root_dir.split(os.path.sep))
        if len(dir_split) == root_len or dir_split[root_len] not in ignore_dirs:
            if "index.html" in files:
                input_path = os.path.join(dirname, "index.html")
                with open(input_path, 'r') as input_html:
                    soup = BeautifulSoup(input_html.read(), 'html.parser')
                    main = soup.find("div", attrs={"role": "main"})
                    if main is None:
                        main = soup.find("div", attrs={"id": "main"})
                    if main is not None:
                        for tag in main():
                            if tag.name not in class_dict[parent_slug].keys():
                                class_dict[parent_slug][tag.name] = dict()
                            tag_class = tag.get("class", None)
                            if tag_class:
                                if "|".join(tag_class) not in class_dict[parent_slug][tag.name].keys():
                                    class_dict[parent_slug][tag.name]["|".join(tag_class)] = 0
                                class_dict[parent_slug][tag.name]["|".join(tag_class)] += 1
                        pre_spans = main.findAll("span", attrs={'class': 'pre'})
                        for pre_span in pre_spans:
                            pre_span.name = 'pre'
                        for tag in main():
                            for attribute in ["class", "style"]:
                                del tag[attribute]
                        output_dir = os.path.join("output", parent_slug, *dir_split[root_len:])
                        output_path = os.path.join(output_dir, "index.html")
                        if not os.path.isdir(output_dir):
                            os.makedirs(output_dir)
                        with open(output_path, 'w') as output_xml:
                            output_xml.write(str(main))

with open("class_dict.json", "w") as json_file:
    json.dump(class_dict, json_file, indent=4)

shutil.make_archive("output", "zip", "output")

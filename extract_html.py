import os
import shutil
import json
import csv
import re
from six.moves.urllib.parse import urlparse
from bs4 import BeautifulSoup
from spellchecker import SpellChecker


spell = SpellChecker()
spell.word_frequency.load_text_file('./known_words.txt')


def is_relative(url):
    return not bool(urlparse(url).netloc)


def is_local(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc in ["reference.iatistandard.org", "iatistandard.org"]


local_url_map = {
    "101": "en/iati-standard/101/",
    "102": "en/iati-standard/102/",
    "103": "en/iati-standard/103/",
    "104": "en/iati-standard/104/",
    "105": "en/iati-standard/105/",
    "201": "en/iati-standard/201/",
    "202": "en/iati-standard/202/",
    "203": "en/iati-standard/203/",
    "introduction": "en/iati-standard/203/",
    "reference": "en/iati-standard/203/",
    "organisation-identifiers": "en/guidance/publishing-data/registering-and-managing-your-organisation-account/how-to-create-your-iati-organisation-identifier/",
    "activity-standard": "en/iati-standard/203/activity-standard/",
    "organisation-standard": "en/iati-standard/203/organisation-standard/",
    "namespaces-extensions": "en/iati-standard/203/namespaces-extensions/",
    "codelists": "en/iati-standard/203/codelists/",
    "codelists-guides": "en/iati-standard/203/codelists-guides/",
    "schema": "en/iati-standard/203/schema/",
    "rulesets": "en/iati-standard/203/rulesets/",
    "upgrades": "en/iati-standard/upgrades/upgrade-changelogs/",
    "guidance": "en/guidance/standard-guidance/",
    "developer": "en/guidance/developer/",
    "en": "en/",
    "documents": "documents/",
    "org-ref": "en/guidance/publishing-data/registering-and-managing-your-organisation-account/how-to-create-your-iati-organisation-identifier/"
}


old_download_paths = [
    r"^\/downloads.*",
    r".*codelists\/downloads.*",
    r".*schema\/downloads.*"
]
combined_download_regex = "(" + ")|(".join(old_download_paths) + ")"
download_roots = ("/101", "/102", "/103", "/104", "/105", "/201", "/202", "/203")


def rewrite_relative_href(url, parent_href):
    if "index.htm" in url.split("/")[-1]:
        return "/".join(url.split("/")[:-1]) + "/"
    if url.startswith("/"):
        absolute_href = url
    else:
        absolute_href = os.path.abspath(os.path.join(parent_href, url))
    if absolute_href.startswith("/downloads"):
        return "/reference_downloads/archive{}".format(absolute_href)
    if re.search(combined_download_regex, absolute_href):
        if absolute_href.startswith(download_roots):
            return "/reference_downloads{}".format(absolute_href)
        else:
            return "/reference_downloads/203{}".format(absolute_href)
    return url


def rewrite_local_href(url):
    BASE_DOMAIN = "/"
    parsed_url = urlparse(url)
    parsed_path = parsed_url.path
    parsed_path = re.sub("/{2,}", "/", parsed_path)
    if parsed_path:
        if parsed_path.startswith("/reference_downloads"):
            return parsed_path
        if re.search(combined_download_regex, parsed_path):
            if parsed_path.startswith("/downloads"):
                return "/reference_downloads/archive{}".format(parsed_path)
            if not parsed_path.startswith(download_roots):
                return "/reference_downloads/203{}".format(parsed_path)
            return "/reference_downloads{}".format(parsed_path)
        parsed_path_split = parsed_path.split("/")
        root_slug = parsed_path_split[1]
        slug_remainder = ""
        if len(parsed_path_split) > 2:
            slug_remainder = "/".join(parsed_path_split[2:])
        if root_slug in local_url_map.keys():
            if slug_remainder.startswith("upgrades"):  # Special case where we've moved upgrades out of version roots
                root_slug = "upgrades"
                slug_remainder = "/".join(slug_remainder.split("/")[1:])
            return BASE_DOMAIN + local_url_map[root_slug] + slug_remainder
        return url
    else:
        return BASE_DOMAIN


if os.path.exists("output.zip"):
    os.remove("output.zip")
if os.path.isdir("output"):
    shutil.rmtree("output")
if os.path.isdir("downloads"):
    shutil.rmtree("downloads")


with open("class_transformations.json", "r") as json_file:
    class_transformations = json.load(json_file)


class_dict = dict()
image_dict = dict()
href_list = list()
href_csv = []
word_dict = dict()
word_csv = []


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
    "upgrades": "IATI-Upgrades/en/_build/dirhtml",
    "developer": "IATI-Developer-Documentation/_build/dirhtml"
}

download_folders = {
    "203": {
        "IATI-Standard-SSOT-version-2.03/docs/en/_build/dirhtml/codelists/downloads/": "codelists/downloads",
        "IATI-Standard-SSOT-version-2.03/docs/en/_build/dirhtml/schema/downloads/": "schema/downloads"
    },
    "202": {
        "IATI-Standard-SSOT-version-2.02/docs/en/_build/dirhtml/codelists/downloads/": "codelists/downloads",
        "IATI-Standard-SSOT-version-2.02/docs/en/_build/dirhtml/schema/downloads/": "schema/downloads"
    },
    "201": {
        "IATI-Standard-SSOT-version-2.01/docs/en/_build/dirhtml/codelists/downloads/": "codelists/downloads",
        "IATI-Standard-SSOT-version-2.01/docs/en/_build/dirhtml/schema/downloads/": "schema/downloads"
    },
    "105": {
        "IATI-Standard-SSOT-version-1.05/docs/en/_build/dirhtml/codelists/downloads/": "codelists/downloads",
        "IATI-Standard-SSOT-version-1.05/docs/en/_build/dirhtml/schema/downloads/": "schema/downloads"
    },
    "104": {
        "IATI-Standard-SSOT-version-1.04/docs/en/_build/dirhtml/codelists/downloads/": "codelists/downloads",
        "IATI-Standard-SSOT-version-1.04/docs/en/_build/dirhtml/schema/downloads/": "schema/downloads"
    },
    "103": {},
    "102": {},
    "101": {},
    "guidance": {},
    "upgrades": {},
    "developer": {},
    "archive": {
        "archive_downloads/": "downloads"
    }
}
allowed_download_ext = [".csv", ".xml", ".json", ".xsd", ".txt", ".xslt", ".odt", ".doc"]

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


for parent_slug, download_dict in download_folders.items():
    for download_folder, download_suffix in download_dict.items():
        for dirname, dirs, files in os.walk(download_folder, followlinks=True):
            for filename in files:
                if os.path.splitext(filename)[1].lower() in allowed_download_ext:
                    download_output_dir = os.path.join("downloads", parent_slug, download_suffix, dirname[len(download_folder):])
                    if not os.path.isdir(download_output_dir):
                        os.makedirs(download_output_dir)
                    shutil.copy(os.path.join(dirname, filename), os.path.join(download_output_dir, filename))

for parent_slug, root_dir in build_dirs.items():
    class_dict[parent_slug] = dict()
    for dirname, dirs, files in os.walk(root_dir, followlinks=True):
        dir_split = dirname.split(os.path.sep)
        root_len = len(root_dir.split(os.path.sep))
        if len(dir_split) == root_len or dir_split[root_len] not in ignore_dirs:
            if "index.html" in files:
                input_path = os.path.join(dirname, "index.html")
                with open(input_path, 'r') as input_html:
                    soup = BeautifulSoup(input_html.read(), 'lxml')
                    main = soup.find("div", attrs={"role": "main"})
                    meta = soup.findAll("meta", attrs={"name": ["title", "description", "guidance_type", "order", "date"]})
                    if main is None:
                        main = soup.find("div", attrs={"id": "main"})
                    if main is not None:
                        for tag in main():
                            if tag.name == "a":
                                href = tag.get("href", None)
                                if href and href not in href_list and is_local(href):
                                    href_list.append(href)
                                    href_csv.append([href, dirname])
                            if tag.name not in class_dict[parent_slug].keys():
                                class_dict[parent_slug][tag.name] = dict()
                            tag_class = tag.get("class", ["None"])
                            if tag_class:
                                if "|".join(tag_class) not in class_dict[parent_slug][tag.name].keys():
                                    class_dict[parent_slug][tag.name]["|".join(tag_class)] = dirname
                            misspelled = spell.unknown(spell.split_words(tag.get_text(separator=" ", strip=True)))
                            for m_word in misspelled:
                                if dirname not in word_dict.keys():
                                    word_dict[dirname] = list()
                                if m_word not in word_dict[dirname]:
                                    word_dict[dirname].append(m_word)
                                    word_csv.append([m_word, dirname])
                        for tag_to_remove in class_transformations["remove_tags"]:
                            remove_tag = tag_to_remove["tag"]
                            remove_class = tag_to_remove["class"]
                            if len(remove_class) == 0:
                                remove_matches = main.findAll(remove_tag)
                            else:
                                remove_matches = main.findAll(remove_tag, attrs={'class': remove_class})
                            for remove_match in remove_matches:
                                remove_match.decompose()
                        for class_unwrap in class_transformations["unwrap_by_parent"]:
                            parent_tag = class_unwrap["parent"]["tag"]
                            parent_class = class_unwrap["parent"]["class"]
                            child_tag = class_unwrap["child"]["tag"]
                            child_class = class_unwrap["child"]["class"]
                            unwrap_type = class_unwrap["unwrap"]
                            if len(parent_class) == 0:
                                parent_matches = main.findAll(parent_tag)
                            else:
                                parent_matches = main.findAll(parent_tag, attrs={'class': parent_class})
                            for parent_match in parent_matches:
                                if len(child_class) == 0:
                                    child_matches = parent_match.findAll(child_tag)
                                else:
                                    child_matches = parent_match.findAll(child_tag, attrs={'class': child_class})
                                if unwrap_type == "parent" and len(child_matches) > 0:
                                    parent_match.unwrap()
                                else:
                                    for child_match in child_matches:
                                        child_match.unwrap()
                        for class_unwrap in class_transformations["unwrap"]:
                            unwrap_tag = class_unwrap["tag"]
                            unwrap_class = class_unwrap["class"]
                            if len(unwrap_class) == 0:
                                unwrap_matches = main.findAll(unwrap_tag)
                            else:
                                unwrap_matches = main.findAll(unwrap_tag, attrs={'class': unwrap_class})
                            for unwrap_match in unwrap_matches:
                                unwrap_match.unwrap()
                        for class_tbp in class_transformations["transform_by_parent"]:
                            parent_tag = class_tbp["parent"]["tag"]
                            parent_class = class_tbp["parent"]["class"]
                            b_child_tag = class_tbp["before"]["tag"]
                            b_child_class = class_tbp["before"]["class"]
                            a_child_tag = class_tbp["after"]["tag"]
                            a_child_class = class_tbp["after"]["class"]
                            if len(parent_class) == 0:
                                parent_matches = main.findAll(parent_tag)
                            else:
                                parent_matches = main.findAll(parent_tag, attrs={'class': parent_class})
                            for parent_match in parent_matches:
                                if len(b_child_class) == 0:
                                    child_matches = parent_match.findAll(b_child_tag)
                                else:
                                    child_matches = parent_match.findAll(b_child_tag, attrs={'class': b_child_class})
                                for child_match in child_matches:
                                    child_match.name = a_child_tag
                                    child_match["class"] = a_child_class
                                    child_match.transformed = True
                        for class_transform in class_transformations["transform"]:
                            old_tag = class_transform["before"]["tag"]
                            new_tag = class_transform["after"]["tag"]
                            old_class = class_transform["before"]["class"]
                            new_class = class_transform["after"]["class"]
                            if len(old_class) == 0 and len(new_class) == 0:
                                tags_to_transform = main.findAll(old_tag)
                                for tag_to_transform in tags_to_transform:
                                    tag_to_transform.name = new_tag
                            elif len(new_class) == 0:
                                tags_to_transform = main.findAll(old_tag, attrs={'class': old_class})
                                for tag_to_transform in tags_to_transform:
                                    tag_to_transform.name = new_tag
                            else:
                                tags_to_transform = main.findAll(old_tag, attrs={'class': old_class})
                                for tag_to_transform in tags_to_transform:
                                    tag_to_transform.name = new_tag
                                    tag_to_transform["class"] = new_class
                                    tag_to_transform.transformed = True
                        for class_unwrap in class_transformations["unwrap_by_parent_last"]:
                            parent_tag = class_unwrap["parent"]["tag"]
                            parent_class = class_unwrap["parent"]["class"]
                            child_tag = class_unwrap["child"]["tag"]
                            child_class = class_unwrap["child"]["class"]
                            unwrap_type = class_unwrap["unwrap"]
                            if len(parent_class) == 0:
                                parent_matches = main.findAll(parent_tag)
                            else:
                                parent_matches = main.findAll(parent_tag, attrs={'class': parent_class})
                            for parent_match in parent_matches:
                                if len(child_class) == 0:
                                    child_matches = parent_match.findAll(child_tag)
                                else:
                                    child_matches = parent_match.findAll(child_tag, attrs={'class': child_class})
                                if unwrap_type == "parent" and len(child_matches) > 0:
                                    parent_match.unwrap()
                                else:
                                    for child_match in child_matches:
                                        child_match.unwrap()
                        for class_transform in class_transformations["transform_last"]:
                            old_tag = class_transform["before"]["tag"]
                            new_tag = class_transform["after"]["tag"]
                            old_class = class_transform["before"]["class"]
                            new_class = class_transform["after"]["class"]
                            if len(old_class) == 0 and len(new_class) == 0:
                                tags_to_transform = main.findAll(old_tag)
                                for tag_to_transform in tags_to_transform:
                                    tag_to_transform.name = new_tag
                            elif len(new_class) == 0:
                                tags_to_transform = main.findAll(old_tag, attrs={'class': old_class})
                                for tag_to_transform in tags_to_transform:
                                    tag_to_transform.name = new_tag
                            else:
                                tags_to_transform = main.findAll(old_tag, attrs={'class': old_class})
                                for tag_to_transform in tags_to_transform:
                                    tag_to_transform.name = new_tag
                                    tag_to_transform["class"] = new_class
                                    tag_to_transform.transformed = True
                        for tag in main():
                            if tag.name in ["p", "span"]:
                                if len(tag.get_text(strip=True)) == 0 and tag.parent.name != "pre":
                                    tag.decompose()
                                    continue
                            if tag.name in ["a"]:
                                if tag.get_text(strip=True) == "¶":
                                    tag.decompose()
                                    continue
                            # Fix for hardcoded index.html's, images, references to old url
                            if tag.name == "a":
                                href = tag.get("href", None)
                                if href:
                                    amended_href = href
                                    if is_relative(amended_href):
                                        parent_href = "/{}{}".format(parent_slug, dirname[len(root_dir):])
                                        amended_href = rewrite_relative_href(amended_href, parent_href)
                                    elif is_local(amended_href):
                                        amended_href = rewrite_local_href(amended_href)
                                    tag["href"] = amended_href
                            if tag.name == "img":
                                src = tag.get("src", None)
                                src_basename = os.path.basename(src)
                                amended_src = "/media/original_images/{}".format(src_basename)
                                tag["src"] = amended_src
                                parent_href = tag.parent.get("href", None)  # For anchor wrapped img tags
                                if parent_href:
                                    if os.path.basename(parent_href) == src_basename:
                                        tag.parent["href"] = amended_src
                            try:
                                del tag["style"]
                                if not tag.transformed:
                                    del tag["class"]
                            except AttributeError:
                                pass
                        for meta_tag in meta:
                            main.append(meta_tag)
                        output_dir = os.path.join("output", parent_slug, *dir_split[root_len:])
                        output_path = os.path.join(output_dir, "index.html")
                        if not os.path.isdir(output_dir):
                            os.makedirs(output_dir)
                        with open(output_path, 'w') as output_xml:
                            output_xml.write(str(main))


with open("class_dict.json", "w") as json_file:
    json.dump(class_dict, json_file, indent=4)

with open("href_list.csv", "w") as txt_file:
    href_csv.sort(key=lambda x: x[0])
    href_csv.insert(0, ["href", "dirname"])
    csvwriter = csv.writer(txt_file, delimiter=',')
    csvwriter.writerows(href_csv)

with open("unknown_words.csv", "w") as txt_file:
    word_csv.sort(key=lambda x: x[0])
    word_csv.insert(0, ["word", "dirname"])
    csvwriter = csv.writer(txt_file, delimiter=',')
    csvwriter.writerows(word_csv)

shutil.make_archive("output", "zip", "output")
shutil.make_archive("downloads", "zip", "downloads")

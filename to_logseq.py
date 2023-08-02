import sys
import re
import time
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import os

def step1():
    # get all entry id
    os.system("wallabag list --read | cut -c-8 > exports/read_list.txt")
    with open("exports/read_list.txt", "r") as f:
        list_content = f.read().split("\n")
    list_content = [ll for ll in list_content if ll.isdigit()]

    # export the content and annotations
    Path("exports").mkdir(exist_ok=True)

    for entry_id in tqdm(list_content):
        print(entry_id)
        os.system(f"wallabag export {entry_id} -o exports -f MARKDOWN")

        os.system(f"wallabag anno -c list -e {entry_id} > exports/{entry_id}_annots.md")

        os.system(f"wallabag info {entry_id} > exports/{entry_id}_info.md")

def step3():
    # get all entry id
    Path("exports/unreads").mkdir(exist_ok=True)
    os.system("rm exports/unreads/urls.txt")
    os.system("wallabag list --unread | cut -c-8 > exports/unreads/unread_list.txt")
    with open("exports/unreads/unread_list.txt", "r") as f:
        list_content = f.read().split("\n")
    list_content = [ll for ll in list_content if ll.isdigit()]

    # export the info to get the url

    for entry_id in tqdm(list_content):
        print(entry_id)

        os.system(f"wallabag info {entry_id} | grep Url | cut -c6- >> exports/unreads/urls.txt")

def step4():
    urls = Path("exports/unreads/urls.txt").read_text().split("\n")
    with open("exports/unreads/url.csv", "w") as f:
        f.write("URL,status,labels\n")
        for url in tqdm(urls):
            url = url.strip()
            if not url:
                continue
            f.write(f"{url},SUCCEDED,[wallabag_import]\n")

def step2():
    output = "- # Wallabag Imports"

    all_files = [str(p) for p in Path("exports").iterdir() if "_annots.md" not in str(p) and "_info.md" not in str(p)]
    all_files.remove("exports/read_list.txt")
    all_files = sorted(all_files)


    for path in tqdm(all_files):
        content = Path(path).read_text()
        entry_id = re.search(r"exports/(\d*)", path)[0].replace("exports/", "")

        infos = Path(f"exports/{entry_id}_info.md").read_text().split("\n")
        dict_infos = {
                line.split(":", 1)[0]: line.split(":", 1)[1].strip()
                for line in infos
                if ":" in line
                }
        if "Annotations" not in dict_infos:
            dict_infos["Annotations"] = 0
        print(dict_infos["Url"])

        annots = Path(f"exports/{entry_id}_annots.md").read_text().split("\n")
        for i, an in enumerate(annots):
            if not an:
                continue
            try:
                while an[0].isdigit():  # remove annot numbers
                    an = an[1:]
                an = an[2:]  # remove '. '
                an = an.replace(" months ago) [0]", "")
                while an[-1].isdigit():
                    an = an[:-1]
                an = an[:-2]
            except Exception as err:
                print(err)
                print(annots[i])

            an = an.strip()
            if an in content:
                content = content.replace(an, f" =={an}== ")
            else:
                offset = 0
                for offset in range(0, len(an)):
                    for cnt in range(offset, len(an)):
                        if an[offset:cnt] not in content:
                            cnt -= 1
                            break
                    if cnt == list(range(len(an)))[-1]:
                        # it was never found, trying with a bigger offset
                        continue
                    content = content.replace(an[offset:cnt], f" =={an[offset:cnt].strip()}== ")
                    break

            annots[i] = an

        lines = content.split("\n")
        lines = [ll for ll in lines if ll.strip() != ""]
        header = lines[0]
        if header.startswith("# "):
            header = header[2:]

        output += f"\n  - ## TODO {header}"
        output += f"\n    diy_type:: wallabag_import"
        output += f"\n    reading_time:: {dict_infos['Reading time']}"
        output += f"\n    url:: {dict_infos['Url']}"
        output += f"\n    wallabag_title:: {dict_infos['Title']}"
        output += f"\n    wallabag_n_annotations:: {dict_infos['Annotations']}"
        output += f"\n    wallabag_is_read:: {dict_infos['Is read']}"
        output += f"\n    wallabag_is_starred:: {dict_infos['Is starred']}"

        for ll in lines[1:]:
            if not ll.strip():
                continue
            if not ll.strip()[1:].strip():
                continue
            output += f"\n    - {ll}"

        if annots:
            output += "\n    - ### Highlights"
        for an in annots:
            if an.strip():
                output += f"\n        - TODO =={an}=="
                output += f"\n          diy_type:: wallabag_annotation"



    if sys.argv[1:] == []:
        with open("./output.md", "w") as f:
            f.write(output)
    else:
        with open(sys.argv[1:][0], "w") as f:
            f.write(output)


if __name__ == "__main__":
    #step1()
    #step2()
    #step3()
    step4()
    # todo : get url and tags

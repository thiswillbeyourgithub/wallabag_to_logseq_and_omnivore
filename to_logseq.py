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
    os.system("wallabag list --read | cut -c-8 > list.txt")
    with open("list.txt", "r") as f:
        list_content = f.read().split("\n")
    list_content = [ll for ll in list_content if ll.isdigit()]

    # export the content and annotations
    Path("exports").mkdir(exist_ok=True)

    for entry_id in tqdm(list_content):
        print(entry_id)
        os.system(f"wallabag export {entry_id} -o exports -f MARKDOWN")
        time.sleep(1)

        os.system(f"wallabag anno -c list -e {entry_id} > exports/{entry_id}_annots.md")
        time.sleep(1)
    os.system("cp list.txt exports/list.txt")



def step2():
    output = ""

    all_files = [str(p) for p in Path("exports").iterdir() if "annots" not in str(p)]
    all_files.remove("exports/list.txt")
    all_files = sorted(all_files)


    for path in tqdm(all_files):
        content = Path(path).read_text()
        entry_id = re.search(r"exports/(\d*)", path)[0].replace("exports/", "")

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

            if an in content:
                content = content.replace(an, f"=={an}==")
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
                    content = content.replace(an[offset:cnt], f"=={an[offset:cnt]}==")
                    break

            annots[i] = an

        lines = content.split("\n")
        lines = [ll for ll in lines if ll.strip() != ""]
        header = lines[0]

        output += f"\n- TODO {header}"
        output += "\n    diy_type:: wallabag_import"

        for ll in lines[1:]:
            if not ll.strip():
                continue
            if not ll.strip()[1:].strip():
                continue
            output += f"\n    - {ll}"

        for an in annots:
            if an.strip():
                output += f"\n   - TODO =={an}=="
                output += f"\n     diy_type:: wallabag_annotation"



    if sys.argv[1:] == []:
        with open("./output.md", "w") as f:
            f.write(output)
    else:
        with open(sys.argv[1:][0], "w") as f:
            f.write(output)


if __name__ == "__main__":
    #step1()
    step2()
    # todo : get url and tags

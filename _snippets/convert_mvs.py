import codecs
import sys
import json
from tqdm import tqdm

if __name__ == '__main__':
    assert len(sys.argv) == 3

    with codecs.open(sys.argv[1], "r") as fp_in:
        with codecs.open(sys.argv[2], "w", encoding="utf8") as fp_out:
            data = json.load(fp_in)

            for d in tqdm(data):
                d["FIRST_NAME"] = d["FIRST_NAME_R"]
                d["LAST_NAME"] = d["LAST_NAME_R"]
                d["MIDDLE_NAME"] = d["MIDDLE_NAME_R"]
                d["BIRTH_DATE"], _ = d["BIRTH_DATE"].split("T")
                d["LOST_DATE"], _ = d["LOST_DATE"].split("T")

                del d["FIRST_NAME_U"]
                del d["LAST_NAME_U"]
                del d["MIDDLE_NAME_U"]

            json.dump(data, fp_out, ensure_ascii=False, indent=4)

import json
import sys

import requests


def convert(filePointers):
    labels_dict = {"2": "ORG",
                   "3": "MISC",
                   "4": "PERSON"}
    for document in filePointers:
        json_doc = json.load(open(document,"r",encoding='utf-8'))

        converted_doc = dict()
        converted_doc["text"] = json_doc["text"]

        labels = []
        annotations = json_doc["annotations"]

        for annotation in annotations:
            start_offset = annotation["start_offset"]
            end_offset = annotation["end_offset"]
            label = labels_dict[str(annotation["label"])]

            new_labels = list()
            new_labels.append(start_offset)
            new_labels.append(end_offset)
            new_labels.append(label)

            labels.append(new_labels)

        converted_doc["labels"] = labels
        print(json.dumps(converted_doc))
        return json.dumps(converted_doc)


if __name__ == '__main__':
   print(convert(["AnnotatedData/Annotation42.json"]))
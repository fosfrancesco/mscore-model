import music21 as m21
from pathlib import Path
from score_model.m21utils import model_score
from colorama import Fore, init

init(autoreset=True)

datasets = {
    "/Users/lyrodrig/datasets/asap-dataset",
    "/Users/lyrodrig/datasets/qparse-test/gmmt_dataset/corrected_musicxml",
    "/Users/lyrodrig/datasets/qparse-test/gmmt_dataset/musicxml",
    "/Users/lyrodrig/datasets/qparse-test/lamarque_dataset/musicxml",
}

hashtable = {}

for dataset_path in datasets:
    dataset_name = "/".join(dataset_path.split("/")[4:])

    for xml_file in Path(dataset_path).glob("*.xml"):
        score = m21.converter.parse(xml_file)
        try:
            model_score(score)
        except Exception as error:
            if str(error) not in hashtable:
                hashtable[str(error)] = []
            hashtable[str(error)].append(xml_file)

# print summary
print("-------------------------")
print("SUMMARY")
print("-------------------------")

if hashtable == {}:
    print("Congratulations ! There was no error found in this execution.\n")
else:
    for key in hashtable.keys():
        print(
            Fore.CYAN + key + Fore.RED + " : " + str(len(hashtable[key])) + " errors\n"
        )

    print("-------------------------")
    print("ALL ERRORS")
    print("-------------------------")

    # print errors and all the files concerned
    for key in hashtable.keys():
        print(Fore.CYAN + "\n-------------------------")
        print(Fore.CYAN + key + Fore.RED + " : " + str(len(hashtable[key])) + " errors")
        for value in hashtable[key]:
            print("     ", value)


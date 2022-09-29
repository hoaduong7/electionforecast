import csv

def get_result():
    with open('results.csv', 'r') as infile:
        reader = csv.reader(infile)
        filtered = filter(lambda p: "Aldershot" == p[0], reader)
        mydict = {}
        for rows in filtered:
            mydict[rows[2]] = [int(rows[4]), rows[5]]
        print(mydict)

get_result()

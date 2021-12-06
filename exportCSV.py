import csv
from database import client as db
from datetime import datetime

hostname = input('Enter hostname(optional): ')

while True:
    try:
        minScore = float(input('Enter Minimum score (0-1): '))
        if minScore or (minScore < 0 and minScore > 1):
            break
        print('Invalid Minimum Score, Try Again\n')
    except ValueError:
        print('Invalid Minimum Score, Try Again\n')

while True:
    try:
        maxScore = float(input('Enter Maximum score (0-1): '))
        if maxScore or (maxScore < 0 and maxScore > 1):
            break
        print('Invalid Maximum Score, Try Again\n')
    except ValueError:
        print('Invalid Maximum Score, Try Again\n')


pipeline = [
    {
        '$lookup': {
            'from': 'SentenceScores',
            'localField': '_id',
            'foreignField': 'crawledPageId',
            'as': 'SentenceScores'
        }
    }, {
        '$unwind': {
            'path': '$SentenceScores',
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$addFields': {
            'sentence': '$SentenceScores.text',
            'sentenceScore': '$SentenceScores.score'
        }
    }, {
        '$match': {
            '$and': [
                {'sentenceScore': {'$gte': minScore}},
                {'sentenceScore': {'$lte': maxScore}}
            ]
        }
    }, {
        '$project': {
            '_id': 0,
            'metaData': 0,
            'SentenceScores': 0,
            'rawHTML': 0
        }
    }
]

if hostname:
    pipeline.index(0, {
        '$match': {
            'hostname': hostname
        }
    })

print("Retriving....")
time = datetime.now()
file = f'./report/csv-out {time}.csv'
results = db.ExplictDetect.crawledPage.aggregate(pipeline)
print("Retrived")

print("Writing to file....")
results = list(results)
if len(results):
    keys = results[0].keys()
    with open(file, 'w+', newline='') as output_file:
        dw = csv.DictWriter(output_file, keys)
        dw.writeheader()
        dw.writerows(results)
    print(f'CSV file exported at {file}')
else: 
    print("No Data found in given conditions")

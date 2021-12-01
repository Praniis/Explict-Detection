from datetime import datetime
import predictor
import dbConn

print("Program Started on " + datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))

def updateDocument(find, updateData):
    dbConn.ExplictDetectDB.matchedContent.update_one(find, updateData)

while True:
    documents = dbConn.ExplictDetectDB.matchedContent.find({
        "$or": [{
                "isScanned": {"$exists": False}
                }, {
                "isScanned": False
            }]
    }).limit(20)

    nosDocs = documents.count(True)
    if nosDocs == 0:
        break

    explictContentList = list()
    documentsIdList = list()
    for i in documents:
        documentsIdList.append(i['_id'])
        explictContentList.append(i['explictContent'])
    
    for key, value in enumerate(predictor.predict_prob(explictContentList)):
        updateData = {
            "$set": {
                "isScanned": True,
                "explictScale": 0
            }
        }
        updateData['$set']['explictScale'] = value
        updateDocument({
            "_id": documentsIdList[key]
        }, updateData)

print("Program Ended on " + datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))

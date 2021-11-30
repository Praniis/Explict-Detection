import predictor
import dbConn

WordMatch = dbConn.ExplictDetectDB.get_collection("WordMatch")
for x in WordMatch.find():
    text = str(x['explictContent'])
    if(predictor.predict_prob([text])[0] > 0.8):
        print(text, end="\n========\n\n")

"""Pack the modules contained in the db directory."""
import db.dynamodb as ddb
import db.facade as dbf


DynamoDB = ddb.DynamoDB
DBFacade = dbf.DBFacade

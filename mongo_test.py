from module9_interview_ai.db import db
print("Ping:", db.command("ping"))
print("Collections now:", db.list_collection_names())

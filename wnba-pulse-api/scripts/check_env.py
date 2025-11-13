from dotenv import load_dotenv
import os
load_dotenv()
for k in ["REDDIT_CLIENT_ID","REDDIT_CLIENT_SECRET","REDDIT_USER_AGENT"]:
    v = os.getenv(k)
    print(k, "len=", 0 if v is None else len(v), "startswith=", None if not v else v[:3])

# from pydantic  import BaseModel
# from typing import List, Optional
# import json

# class Product(BaseModel):
#     userId: int
#     id: int
#     title: str
#     completed: bool

# with open('example.json') as f:
#     data = json.load(f)
#     items = [Product(**item) for item in data['todos']]

# print(items)



class ValueException(Exception):
    ...

try:
    raise ValueException
except ValueException:
    print("I came here")



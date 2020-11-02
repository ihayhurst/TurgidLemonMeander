# Mode Of Action / Mode of Resistance database API

## Usage
All responses will have the form
Content-Type application/json

Then an array [ {"column_name":value, "column":value... }, {...}]
for a single value or multiple values

### Entity from ID

**Definition**  
>`GET /moa/entity`        - with no arguement will return all ids  
>`GET /moa/entity/<id>`   - returns individual entity  

**Arguements**

- `"id": integer` ENTITY_ID

**Response**

- `200 OK` on success

```json
[  
    {  
        'ENTITY_ID': 222,  
        'LEVEL_ID': 1,  
        'PREF_SYNONYM_ID': 168,  
        'FIRST_SYNONYM': 'protein biosynthesis',  
        'IGNORE': None,  
        'CLASS_ID': 3  
    }  
]  
```
Subsequent responses will be of the same form

### Triple from ID

**Definition**

| Endpoint                           | Expected return                         |
|:-----------------------------------|:----------------------------------------|
| `GET /moa/triple`                  | - returns all triple ids                |
| `GET /moa/triple/<id>`             | - returns triple(s) with given id       |
| `GET /moa/triple/triple/<id>`      | - returns triple(s) with given id       |
| `GET /moa/triple/subject/<id>`     | - returns subject(s) with given id      |
| `GET /moa/triple/predicate/<id>`   | - returns predicate(s) with given id    |
| `GET /moa/triple/object/<id>`      | - returns objects(s) with given id      |

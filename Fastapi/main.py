
import json

from fastapi import FastAPI, HTTPException, Path, Query

# FastAPI app instance: this is the main application object.
# Every route (@app.get, @app.post, etc.) is attached to this app.
app = FastAPI()

# Interview reminder:
# - @app.get("/") defines an HTTP GET endpoint.
# - A route function is called when a client hits that URL.
# - Return value is automatically converted to JSON by FastAPI.
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!, Akshay..."}

# Helper function to read the JSON file.
# This is a small example of how we separate logic from our route functions.
def get_data():
    with open("data.json", "r", encoding="utf-8") as file:
        return json.load(file)


# Interview reminder:
# - /data_read is a simple GET route.
# - It returns all dataset records without filtering.
@app.get("/data_read")
def read_data():
    return get_data()


# Path parameter example:
# item_id is part of the URL and must match a student ID in the JSON data.
@app.get("/data_read/{item_id}")
def read_data_by_id(
    item_id: str = Path(
        ...,
        description="Student ID to fetch from the dataset",
        examples=["1001"],
    )
):
    data = get_data()

    for student_id, student in data.items():
        if student_id == item_id:
            return student

    # Raising HTTPException is a good practice because it gives a proper API error response.
    raise HTTPException(status_code=404, detail=f"Student not found: {item_id}")


# Query parameter example:
# This endpoint filters students by their branch field.
@app.get("/data_filter")
def read_by_branch(
    branch: str = Query(
        None,
        description="Filter students by branch",
        examples=["AI Engineer"],
    )
):
    data = get_data()

    # If branch is not provided, return all students.
    if branch is None:
        return data

    matches = {
        student_id: student_data
        for student_id, student_data in data.items()
        if student_data.get("major") == branch
    }
    return matches


# Allowed values for sorting.
# This is useful to prevent invalid sort inputs.
sort_options = ["major", "gpa"]


# Interview reminder:
# - Query() gives us optional request parameters.
# - We can validate them by checking allowed values before sorting.
@app.get("/data_sort")
def sort_major_gpa(
    sort_by: str = Query("major", description="Sort by 'major' or 'gpa'"),
    order: str = Query("asc", description="Sort order: 'asc' for ascending, 'desc' for descending"),
):
    if sort_by not in sort_options:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid sort option. Please choose from {sort_options}",
        )

    students = []
    data = get_data()

    for student_id, student in data.items():
        student["id_new"] = student_id
        students.append(student)

    reverse_order = order == "desc"
    sorted_data = sorted(students, key=lambda x: x[sort_by], reverse=reverse_order)
    return sorted_data


# Pagination concept:
# We fetch a chunk of records instead of all records at once.
# start = (page - 1) * limit
@app.get("/data_paginate")
def paginate(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(5, ge=1, le=100, description="Number of items per page"),
):
    data = get_data()
    students = []

    for student_id, student in data.items():
        student["id_new"] = student_id
        students.append(student)

    start = (page - 1) * limit
    end = start + limit

    return students[start:end]


# Pydantic concepts will start here in the next examples.
# For interview prep, remember:
# - Pydantic validates input data and converts values automatically.
# - Models help define expected request/response structures.
# - FastAPI uses Pydantic models behind the scenes for validation."


import json
from tkinter.filedialog import test

from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator, ValidationError


##_____  # here we are defining data type and also validating value conditions and also computing a new field based on existing field value
class Student_class(BaseModel):
    id_new: str = Field(..., description="Unique ID of the student", json_schema_extra={"example": "1001"})
    full_name: str = Field(..., min_length=2, max_length=100, description="Name of the student", json_schema_extra={"example": "John Doe"})
    email: EmailStr = Field(..., description="Email of the student", json_schema_extra={"example": "john.doe@example.com"})
    major: str = Field(..., description="Major of the student", json_schema_extra={"example": "Computer Science"})
    gpa: float = Field(..., description="GPA of the student", json_schema_extra={"example": 3.5})

    @field_validator("gpa")
    @classmethod
    def validate_gpa_check(cls, value):
        if not (0.0 <= value <= 10.0):
            raise ValueError("GPA must be a float between 0.0 and 10.0")
        return value

    @computed_field
    @property
    def validate_gpa(self) -> bool:
        if (0.0 <= self.gpa <= 3.0):
            return "Fail"
        elif (3.0 < self.gpa <= 5.0):
            return "Pass"
        if (5.0 < self.gpa <= 10.0):
            return "Excellent"
        return "Invalid GPA"


def get_data():   # Simulate fetching data from a database or an external API
   with open("data.json", "r", encoding="utf-8") as file:
       return json.load(file)

    # "full_name": "Devansh Saxena",
    # "email": "devansh.saxena@example.edu.in",
    # "major": "Mech",
    # "gpa": 3.63

def data_dump_json(data):
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# data = get_data()
# for student_id, student in data.items():
#     try:
#         student_obj = Student_class(**student)
#         # print(f"Student ID: {student_id}, Name: {student_obj.full_name}, Email: {student_obj.email}, Major: {student_obj.major}, GPA: {student_obj.gpa}, GPA Validation: {student_obj.validate_gpa}")
#         print(print(student_obj.model_dump()))
#     except ValidationError as e:
#         print(f"Validation error for student ID {student_id}: {e}")



@app.post("/add_student")
def add_student(student: Student_class):
    data = get_data()

    if student.id_new in data:
        raise HTTPException(status_code=400, detail=f"Student with ID {student.id_new} already exists.")
    
    data[student.id_new] = student.model_dump(exclude={"id_new","validate_gpa"})  # Convert Pydantic model to dictionary
    data_dump_json(data)  # Save updated data back to JSON file
    return {"message": "Student added successfully", "student": student.model_dump()}


class StudentUpdate(BaseModel):
    id_new: str | None = Field(None, description="Unique ID of the student", json_schema_extra={"example": "1001"})
    full_name: str | None = Field(None, min_length=2, max_length=100, description="Name of the student", json_schema_extra={"example": "John Doe"})
    email: EmailStr | None = Field(None, description="Email of the student", json_schema_extra={"example": "john.doe@example.com"})
    major: str | None = Field(None, description="Major of the student", json_schema_extra={"example": "Computer Science"})
    gpa: float | None = Field(None, description="GPA of the student", json_schema_extra={"example": 3.5})

@app.put("/update_student/{student_id}")
def update_student(student_id:str,
                    student_update: StudentUpdate):
    data = get_data()

    # check if the student exists in the data
    if student_id not in data:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found.")

    # STEP - 01  Existing student_data = data[student_id]
    #Create object of Student_class using existing data and then update it with new values from student_update
    student_data = data[student_id]                             
    # student_obj = Student_class(id_new=student_id, **student_data) # Create a Student_class object with existing data
    print(f"Existing student data: {student_data}")

    # STEP - 02 Update only those fields which are provided in the request body (student_update)
    studuent_Update_data = student_update.model_dump()  # Get only the fields that are provided in the request body
    # this get request data in code  dict format

    # STEP - 03 Update the existing student_data with new values from student_update
    for key, value in studuent_Update_data.items():
        if value is not None:  # Only update fields that are provided in the request body
            student_data[key] = value

    # STEP - 04 Now check our orginal Student_class model validation for updated data
    try:
        updated_student = Student_class(id_new=student_id, **student_data)  # Validate updated data
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")

    # STEP - 05 Save the updated student data back to the JSON file

    data[student_id] = updated_student.model_dump(exclude={"id_new", "validate_gpa"})  # Update the data dictionary with the updated student data
    data_dump_json(data)  # Save updated data back to JSON file

    return {"message": "Student updated successfully", "student": updated_student.model_dump()}



@app.delete("/delete_student/{student_id}")
def delete_student(student_id: str = Path(..., description="Student ID to delete from the dataset", examples=["1001"])):
    data = get_data()

    if student_id not in data:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found.")

    del data[student_id]  # Remove the student from the data
    data_dump_json(data)  # Save updated data back to JSON file

    return {"message": "Student deleted successfully", "student_id": student_id}
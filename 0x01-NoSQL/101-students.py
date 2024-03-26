#!/usr/bin/env python3
"""
Python function that returns all students
sorted by average score.
"""


def top_students(mongo_collection):
    """
    Prints all students in a collection
    sorted by average score.
    """

    students = mongo_collection.aggregate([
        {
            "$project": {
                "name": "$name",
                "averageScore": {"$avg": "$topics.score"}
            }
        },
        {"$sort": {"averageScore": -1}}
    ])

    return students

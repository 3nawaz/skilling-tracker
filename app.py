from flask import Flask, request, jsonify

app = Flask(__name__)


# ==========================================
# DEMO COURSE REVIEWS DATABASE
# ==========================================

reviews = [

    {
        "user": 1,
        "course": "Python for Data Science",
        "rating": 5,
        "feedback": "Very useful for data analysis."
    },

    {
        "user": 2,
        "course": "Python for Data Science",
        "rating": 4,
        "feedback": "Good course for beginners."
    },

    {
        "user": 3,
        "course": "Python for Data Science",
        "rating": 5,
        "feedback": "Helped me understand Python."
    },

    {
        "user": 4,
        "course": "Data Analytics with SQL",
        "rating": 5,
        "feedback": "Very useful for database jobs."
    },

    {
        "user": 5,
        "course": "Data Analytics with SQL",
        "rating": 4,
        "feedback": "Good practical examples."
    },

    {
        "user": 6,
        "course": "Full Stack Web Development",
        "rating": 4,
        "feedback": "Good project-based learning."
    },

    {
        "user": 7,
        "course": "Full Stack Web Development",
        "rating": 5,
        "feedback": "Helped me build web projects."
    },

    {
        "user": 8,
        "course": "Machine Learning Fundamentals",
        "rating": 5,
        "feedback": "Excellent introduction to ML."
    },

    {
        "user": 9,
        "course": "Machine Learning Fundamentals",
        "rating": 4,
        "feedback": "Good but mathematics is difficult."
    }

]


# ==========================================
# CALCULATE COURSE AVERAGES
# ==========================================

def calculate_average_ratings():

    course_data = {}


    for review in reviews:

        course = review["course"]

        rating = review["rating"]


        if course not in course_data:

            course_data[course] = {

                "total_rating": 0,

                "number_of_reviews": 0

            }


        course_data[course]["total_rating"] += rating

        course_data[course]["number_of_reviews"] += 1


    results = []


    for course, data in course_data.items():

        average = (
            data["total_rating"]
            /
            data["number_of_reviews"]
        )


        results.append({

            "course": course,

            "average_rating":
                round(average, 2),

            "reviews":
                data["number_of_reviews"]

        })


    return results


# ==========================================
# DASHBOARD API
# ==========================================

@app.route("/api/courses")
def get_courses():

    courses = calculate_average_ratings()

    return jsonify(courses)


# ==========================================
# RECOMMEND COURSES
# ==========================================

@app.route("/api/recommend")
def recommend_courses():

    # Example:
    # User has already completed these courses

    completed_courses = [

        "Python for Data Science",

        "Full Stack Web Development"

    ]


    all_courses = calculate_average_ratings()


    recommendations = []


    for course in all_courses:

        if course["course"] not in completed_courses:

            recommendations.append(course)


    # Highest rated courses first

    recommendations.sort(

        key=lambda x:
        x["average_rating"],

        reverse=True

    )


    return jsonify(recommendations)


# ==========================================
# ADD NEW REVIEW
# ==========================================

@app.route(
    "/api/review",
    methods=["POST"]
)
def add_review():

    data = request.json


    course = data.get("course")

    rating = data.get("rating")

    feedback = data.get(
        "feedback",
        ""
    )


    if not course or not rating:

        return jsonify({

            "error":
                "Course and rating are required"

        }), 400


    if rating < 1 or rating > 5:

        return jsonify({

            "error":
                "Rating must be between 1 and 5"

        }), 400


    new_review = {

        "user":
            len(reviews) + 1,

        "course":
            course,

        "rating":
            rating,

        "feedback":
            feedback

    }


    reviews.append(new_review)


    return jsonify({

        "message":
            "Review added successfully",

        "course":
            course,

        "rating":
            rating

    })


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )

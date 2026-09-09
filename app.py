from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app) # This fixes the browser blocking error!

# ==========================================
# DEMO COURSE REVIEWS DATABASE
# ==========================================
reviews = [
    {"user": 1, "course": "Python for Data Science", "rating": 5, "feedback": "Very useful for data analysis."},
    {"user": 2, "course": "Python for Data Science", "rating": 4, "feedback": "Good course for beginners."},
    {"user": 3, "course": "Python for Data Science", "rating": 5, "feedback": "Helped me understand Python."},
    {"user": 4, "course": "Data Analytics with SQL", "rating": 5, "feedback": "Very useful for database jobs."},
    {"user": 5, "course": "Data Analytics with SQL", "rating": 4, "feedback": "Good practical examples."},
    {"user": 6, "course": "Full Stack Web Development", "rating": 4, "feedback": "Good project-based learning."},
    {"user": 7, "course": "Full Stack Web Development", "rating": 5, "feedback": "Helped me build web projects."},
    {"user": 8, "course": "Machine Learning Fundamentals", "rating": 5, "feedback": "Excellent introduction to ML."},
    {"user": 9, "course": "Machine Learning Fundamentals", "rating": 4, "feedback": "Good but mathematics is difficult."}
]

def calculate_average_ratings():
    course_data = {}
    for review in reviews:
        course = review["course"]
        rating = review["rating"]
        if course not in course_data:
            course_data[course] = {"total_rating": 0, "number_of_reviews": 0}
        course_data[course]["total_rating"] += rating
        course_data[course]["number_of_reviews"] += 1
    
    results = []
    for course, data in course_data.items():
        average = data["total_rating"] / data["number_of_reviews"]
        results.append({
            "course": course,
            "average_rating": round(average, 2),
            "reviews": data["number_of_reviews"]
        })
    return results

# ==========================================
# SERVE THE HTML FRONTEND PAGES
# ==========================================
@app.route("/")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    if os.path.exists(os.path.join(BASE_DIR, path)):
        return send_from_directory(BASE_DIR, path)
    return jsonify({"error": "File not found"}), 404

# ==========================================
# DASHBOARD API ENDPOINTS
# ==========================================
@app.route("/api/courses")
def get_courses():
    return jsonify(calculate_average_ratings())

@app.route("/api/recommend")
def recommend_courses():
    completed_courses = ["Python for Data Science", "Full Stack Web Development"]
    all_courses = calculate_average_ratings()
    recommendations = [c for c in all_courses if c["course"] not in completed_courses]
    recommendations.sort(key=lambda x: x["average_rating"], reverse=True)
    return jsonify(recommendations)

@app.route("/api/review", methods=["POST"])
def add_review():
    data = request.json
    course = data.get("course")
    rating = data.get("rating")
    feedback = data.get("feedback", "")

    if not course or not rating:
        return jsonify({"error": "Course and rating are required"}), 400
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    new_review = {"user": len(reviews) + 1, "course": course, "rating": rating, "feedback": feedback}
    reviews.append(new_review)
    return jsonify({"message": "Review added successfully", "course": course, "rating": rating})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

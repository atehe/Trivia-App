import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()

        if not categories:
            abort(404)

        return (
            jsonify(
                {
                    "success": True,
                    "categories": [category.format() for category in categories],
                }
            ),
            200,
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.all()

        if not questions:
            abort(404)

        category = request.args.get("category")
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        # get questions if they match categrory or no category given
        formatted_questions = [
            question.format()
            for question in questions
            if not category or question.category.lower() == category.lower()
        ]

        return (
            jsonify(
                {
                    "success": True,
                    "questions": formatted_questions[start:end],
                    "total_questions": len(formatted_questions),
                    "current_category": category,
                    "categories": [category.type for category in categories],
                }
            ),
            200,
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if not question:
            abort(404)

        try:
            question.delete()
        except Exception:
            abort(422)

        return jsonify({"success": True, "deleted": question_id}), 200

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        req = request.get_json()

        try:
            current_round_question = req["question"]
            current_round_question_answer = req["answer"]
            current_round_question_difficulty = req["difficulty"]
            current_round_question_category = req["category"]

            question = Question(
                question=current_round_question,
                answer=current_round_question_answer,
                difficulty=current_round_question_difficulty,
                category=current_round_question_category,
            )

            question.insert()
        except:
            abort(422)

        return (
            jsonify(
                {
                    "success": True,
                    "question": question.format(),
                }
            ),
            201,
        )

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search")
    def search_questions():
        search_query = request.arg.get("query")

        search_results = (
            Question.query.filter(Question.question.ilike(f"%{search_query}%"))
            .order_by(Question.id)
            .all()
        )

        if not search_results:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": [result.format() for result in search_results],
                "total_result": len(search_results),
            }
        )

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        category = Category.query.filter(Category.id == category_id).one_or_none()

        if not category:
            abort(404)

        category_type = category.type

        questions = (
            Question.query.filter(Question.category == category_type)
            .order_by(Question.id)
            .all()
        )

        if not questions:
            abort(404)

        formatted_questions = [question.format() for question in questions]

        return (
            jsonify(
                {
                    "success": True,
                    "questions": formatted_questions,
                    "total_questions": len(formatted_questions),
                    "category": category.format(),
                }
            ),
            200,
        )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/play_quiz", methods=["POST"])
    def play_quiz():
        try:
            req = request.get_json()
            quiz_category = req["category"]
            played_questions = req["previous_question"]

            played_question_ids = [question.get("id") for question in played_questions]
            category_type = quiz_category.get("type")

            if category_type:
                questions_to_play = Question.query.filter(
                    Question.id.notin_(
                        (played_question_ids), Question.category == category_type
                    )
                ).all()
            else:
                questions_to_play = Question.query.filter(
                    Question.id.notin_((played_question_ids))
                ).all()

            current_round_question = (
                random.choice(questions_to_play).format()
                if len(questions_to_play) > 0
                else None
            )

            return jsonify({"success": True, "question": current_round_question})
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app

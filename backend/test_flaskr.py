import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represponseents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresponse://{}/{}".format(
            "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        response = self.client().get("/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 10)

    def test_404_beyond_valid_pages(self):
        response = self.client().get("/questions?page=5000")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        test_question = Question(
            question="test question", answer="test answer", difficulty=1, category=1
        )
        test_question.insert()
        question_id = test_question.id

        response = self.client().delete(f"/questions/{question_id}")
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == question.id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(question, None)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], question_id)

    def test_create_question(self):
        test_question = {
            "question": "test question",
            "answer": "test answer",
            "difficulty": 1,
            "category": 1,
        }
        num_questions_before = len(Question.query.all())
        response = self.client().post("/questions", json=test_question)
        data = json.loads(response.data)

        num_questions_after = len(Question.query.all())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(num_questions_before, num_questions_after + 1)

    def test_get_question_by_category(self):

        response = self.client().get("/categories/1/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            data["success"],
        )
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["category"])

    def test_search_questions(self):
        search_question = Question(
            question="test search",
            answer="test answer",
            difficulty=1,
            category=1,
        )
        search_question.insert()

        search_query = {"query": "test search"}
        response = self.client().post("/questions/search", json=search_query)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["questions"])
        self.assertIsNotNone(data["total_result"])

    def test_play_quiz(self):
        new_quiz_round = {
            "previous_questions": [],
            "quiz_category": {"type": "Entertainment", "id": 5},
        }

        res = self.client().post("/play_quiz", json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

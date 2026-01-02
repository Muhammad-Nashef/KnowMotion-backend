from flask import Blueprint, request, jsonify
from models.db import get_db_connection
from psycopg2.extras import RealDictCursor

answers_bp = Blueprint("answers", __name__)

# route to check if an answer is correct
@answers_bp.route("/answers/check", methods=["POST"])
def check_answer():
    data = request.json
    question_id = data["question_id"]
    answer_id = data["answer_id"]

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    #Check if selected answer is correct
    cursor.execute("""
        SELECT is_correct
        FROM answers
        WHERE id = %s AND question_id = %s
    """, (answer_id, question_id))

    selected = cursor.fetchone()

    if not selected:
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid answer"}), 400

    #Always fetch the correct answer id
    cursor.execute("""
        SELECT id
        FROM answers
        WHERE question_id = %s AND is_correct = TRUE
        LIMIT 1
    """, (question_id,))

    correct_answer = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({
        "correct": bool(selected["is_correct"]),
        "correct_answer_id": correct_answer["id"] if correct_answer else None
    })
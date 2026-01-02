from flask import Blueprint, request, jsonify
from models.db import get_db_connection
from utils.decorators import admin_required
from utils.cloudinary_utils import delete_image
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

questions_bp = Blueprint("questions", __name__)

# route to get questions by sub-category id
@questions_bp.route("/questions/by-sub-category/<int:sub_category_id>")
def get_questions_by_sub_category(sub_category_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT id, question_text, img_url
        FROM questions
        WHERE sub_category_id = %s
    """, (sub_category_id,))
    questions = cursor.fetchall()

    for question in questions:
        cursor.execute("""
            SELECT id, answer_text
            FROM answers
            WHERE question_id = %s
        """, (question["id"],))
        question["answers"] = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(questions)



# route to get questions by main category id
@questions_bp.route("/questions/by-main-category/<int:main_category_id>")
def get_questions_by_main_category(main_category_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                q.id,
                q.question_text,
                q.img_url,
                json_agg(
                    json_build_object(
                        'id', a.id,
                        'answer_text', a.answer_text,
                        'is_correct', a.is_correct
                    )
                ) AS answers
            FROM questions q
            JOIN sub_categories sc ON q.sub_category_id = sc.id
            LEFT JOIN answers a ON a.question_id = q.id
            WHERE sc.main_category_id = %s
            GROUP BY q.id
            ORDER BY q.id;
        """
        cursor.execute(query, (main_category_id,))
        questions = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(questions)

    except Exception as e:
        return jsonify({"error": str(e)}), 500 
    


# route to get questions for a specific sub-category
@questions_bp.route("/subcategories/<int:sub_id>/questions")
def get_questions(sub_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT
            q.id,
            q.question_text,
            q.img_url,
            json_agg(
                json_build_object(
                    'id', a.id,
                    'answer_text', a.answer_text,
                    'is_correct', a.is_correct
                )
            ) AS answers
        FROM questions q
        LEFT JOIN answers a ON a.question_id = q.id
        WHERE q.sub_category_id = %s
        GROUP BY q.id
        ORDER BY q.id;
    """, (sub_id,))

    questions = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(questions)



# route to update questions and answers

@questions_bp.route("/questions/update", methods=["POST"])
@admin_required
def update_questions():
    data = request.json
    questions = data["questions"]
    deleted_ids = data["deletedQuestionIds"]

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 🗑 DELETE QUESTIONS
        if deleted_ids:
            # 1️⃣ Get img_urls for deleted questions
            query = sql.SQL("SELECT img_url FROM questions WHERE id IN ({})").format(
                sql.SQL(',').join(sql.Placeholder() * len(deleted_ids))
            )
            cursor.execute(query, deleted_ids)
            img_urls = [row['img_url'] for row in cursor.fetchall() if row['img_url']]

            for url in img_urls:
                filename = url.rsplit('/', 1)[-1].split('.')[0]
                public_id = f"knowmotion/questions_images/{filename}"
                delete_image(public_id)

            # 2️⃣ Delete answers
            query = sql.SQL("DELETE FROM answers WHERE question_id IN ({})").format(
                sql.SQL(',').join(sql.Placeholder() * len(deleted_ids))
            )
            cursor.execute(query, deleted_ids)

            # 3️⃣ Delete questions
            query = sql.SQL("DELETE FROM questions WHERE id IN ({})").format(
                sql.SQL(',').join(sql.Placeholder() * len(deleted_ids))
            )
            cursor.execute(query, deleted_ids)

        # INSERT / UPDATE QUESTIONS
        for q in questions:
            if q.get("id") is None:
                # Insert new question and get ID
                cursor.execute("""
                    INSERT INTO questions (sub_category_id, question_text, img_url)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (q["sub_category_id"], q["question_text"], q.get("img_url")))
                question_id = cursor.fetchone()["id"]
            else:
                question_id = q["id"]
                cursor.execute("""
                    UPDATE questions
                    SET question_text = %s, img_url = %s
                    WHERE id = %s
                """, (q["question_text"], q.get("img_url"), question_id))

            # Insert / update answers
            for a in q.get("answers", []):
                if a.get("id") is None:
                    cursor.execute("""
                        INSERT INTO answers (question_id, answer_text, is_correct)
                        VALUES (%s, %s, %s)
                    """, (question_id, a["answer_text"], a["is_correct"]))
                else:
                    cursor.execute("""
                        UPDATE answers
                        SET answer_text = %s, is_correct = %s
                        WHERE id = %s
                    """, (a["answer_text"], a["is_correct"], a["id"]))

        conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()



@questions_bp.route("/questions/delete-image", methods=["POST"])
@admin_required
def delete_question_image():
    data = request.json
    img_url = data.get("img_url")
    print("data:", data)
    print("Received request to delete image URL:", img_url)
    if not img_url:
        return jsonify({"success": False, "message": "No image URL provided"}), 400

    # Extract filename without extension
    filename = img_url.rsplit('/', 1)[-1].split('.')[0]
    # Include folder path
    public_id = f"knowmotion/questions_images/{filename}"
    print("Deleting image with public_id:", public_id)

    delete_image(public_id)  # delete from Cloudinary

    return jsonify({"success": True})
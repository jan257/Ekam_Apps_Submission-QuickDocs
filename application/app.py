from flask import Flask, render_template, request, redirect,flash, get_flashed_messages, url_for
import mysql.connector
import re
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from nl_query.query_interface import nl_to_sql_and_params

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')

# MySQL Connection Config
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Customer Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    success_message = False
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        process_id = request.form['process_id']

        cursor.execute("INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)",
                       (name, email, phone))
        customer_id = cursor.lastrowid

        cursor.execute("INSERT INTO process_assignments (customer_id, process_id) VALUES (%s, %s)",
                       (customer_id, process_id))
        flash("Customer registered successfully!", "success")

        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/register')

    cursor.execute("SELECT * FROM processes")
    processes = cursor.fetchall()

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    cursor.close()
    conn.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template('register.html', processes=processes, customers=customers,messages=messages)

UPLOAD_FOLDER = 'files/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'docx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Helper to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Document Submission
@app.route('/submit-document', methods=['GET', 'POST'])
def submit_document():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        process_id = request.form['process_id']
        document_type_id = request.form['document_type_id']
        file_url = request.form.get('file_url', '').strip()
        extracted_data = request.form.get('extracted_data', '').strip()
        file_path = None

        # Handle file upload
        if 'doc_file' in request.files:
            file = request.files['doc_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
            elif file and file.filename != '':
                flash("Invalid file type. Allowed: pdf, jpg, jpeg, png, docx", "error")
                return redirect(url_for('submit_document'))

        # If URL provided, store it instead of file path
        if file_url and not file_path:
            file_path = file_url

        cursor.execute("""
            INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, extracted_data)
            VALUES (%s, %s, %s, %s, %s)
        """, (customer_id, process_id, document_type_id, file_url, extracted_data))
                
        # Step 1: Count required documents for this process
        cursor.execute("""
            SELECT COUNT(*) AS required_docs
            FROM process_documents
            WHERE process_id = %s
        """, (process_id,))
        required_docs = cursor.fetchone()['required_docs']

        # Step 2: Count submitted documents for this customer-process
        cursor.execute("""
            SELECT COUNT(DISTINCT document_type_id) AS submitted_docs
            FROM document_submissions
            WHERE customer_id = %s AND process_id = %s
        """, (customer_id, process_id))
        submitted_docs = cursor.fetchone()['submitted_docs']

        # Step 3: Calculate completion percentage
        completion_percentage = int((submitted_docs / required_docs) * 100) if required_docs > 0 else 0

        # Step 4: Determine status
        if completion_percentage == 100:
            status = 'completed'
        elif completion_percentage > 0:
            status = 'in-progress'
        else:
            status = 'pending'

        # Step 5: Update process_assignments
        cursor.execute("""
            UPDATE process_assignments
            SET completion_percentage = %s, status = %s
            WHERE customer_id = %s AND process_id = %s
        """, (completion_percentage, status, customer_id, process_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Document submitted successfully!", "success")
        return redirect('/submit-document')

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    cursor.execute("SELECT * FROM processes")
    processes = cursor.fetchall()

    cursor.execute("SELECT * FROM document_types")
    document_types = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('submit_document.html', customers=customers, processes=processes, document_types=document_types)

# Status Dashboard
@app.route('/dashboard')
def dashboard():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            pa.assignment_id, 
            c.name AS customer_name, 
            p.name AS process_name,
            pa.status, 
            pa.completion_percentage,
            COALESCE(submitted_docs_count.submitted_docs, 0) AS submitted_docs,
            COALESCE(required_docs_count.required_docs, 0) AS required_docs
            FROM process_assignments pa
            JOIN customers c ON pa.customer_id = c.customer_id
            JOIN processes p ON pa.process_id = p.process_id
            LEFT JOIN (
            SELECT customer_id, process_id, COUNT(DISTINCT document_type_id) AS submitted_docs
            FROM document_submissions
            GROUP BY customer_id, process_id
        ) submitted_docs_count 
            ON pa.customer_id = submitted_docs_count.customer_id
            AND pa.process_id = submitted_docs_count.process_id
            LEFT JOIN (
            SELECT process_id, COUNT(document_type_id) AS required_docs
            FROM process_documents
            GROUP BY process_id
        ) required_docs_count
            ON pa.process_id = required_docs_count.process_id
        ORDER BY c.name;
        """


    cursor.execute(query)
    assignments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('dashboard.html', assignments=assignments)


#NL_Query
@app.route('/query', methods=['GET', 'POST'])
def query():
    sql_query = None
    results = None
    message = None
    display_sql = None

    if request.method == 'POST':
        nl_query = request.form['nl_query'].strip()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        sql_query, params, message = nl_to_sql_and_params(nl_query, cursor)

        if sql_query is None:
            # couldn't parse / entity not found
            cursor.close()
            conn.close()
            return render_template('query.html', sql_query=None, results=None, message=message)

        # Safety: disallow non-SELECT (extra protection)
        if re.search(r'\b(drop|delete|update|insert|alter|truncate)\b', sql_query.lower()):
            cursor.close()
            conn.close()
            return render_template('query.html', sql_query=None, results=None, message="Dangerous SQL detected; aborted.")

        # Execute query safely with params (if any)
        try:
            if params:
                cursor.execute(sql_query, params)
            else:
                cursor.execute(sql_query)
            results = cursor.fetchall()
            # cursor.statement sometimes gives final executed query with params substituted
            display_sql = getattr(cursor, 'statement', None) or sql_query
        except Exception as e:
            message = f"SQL execution error: {str(e)}"
            results = None
        finally:
            cursor.close()
            conn.close()

    return render_template('query.html', sql_query=display_sql, results=results, message=message)


if __name__ == '__main__':
    app.run(debug=True)

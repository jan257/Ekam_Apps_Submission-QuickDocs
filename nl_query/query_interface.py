import re
import difflib

# ---------- Helper functions ----------
def fetch_column_list(cursor, table, col):
    cursor.execute(f"SELECT {col} FROM {table}")
    rows = cursor.fetchall()
    # rows from mysql-connector with cursor(dictionary=True) are dicts, else tuples
    if rows and isinstance(rows[0], dict):
        return [r[col] for r in rows]
    return [r[0] for r in rows]

def match_best_entity(query_fragment, candidates):
    """Try to find the best matching candidate (substring first, then fuzzy)."""
    q = query_fragment.strip().lower()
    if not q:
        return None
    # substring match
    for c in candidates:
        if q in c.lower():
            return c
    # fuzzy match with difflib
    matches = difflib.get_close_matches(query_fragment, candidates, n=1, cutoff=0.6)
    if matches:
        return matches[0]
    # token match: any word in query matches any word in candidate
    q_tokens = set(re.findall(r'\w+', q))
    for c in candidates:
        c_tokens = set(re.findall(r'\w+', c.lower()))
        if q_tokens & c_tokens:
            return c
    return None

def nl_to_sql_and_params(nl_query, cursor):
    """Return (sql, params, message). If sql is None, message explains failure."""
    q = nl_query.strip().lower()

    # load known names from DB
    customers = fetch_column_list(cursor, "customers", "name")
    processes = fetch_column_list(cursor, "processes", "name")
    doc_types = fetch_column_list(cursor, "document_types", "name")

    # 1) Show all customers
    if re.search(r'\b(show|list|get)\b.*\bcustomers\b', q):
        sql = "SELECT * FROM customers"
        return sql, None, None

    # 2a) List all pending processes (interpret as processes that have pending assignments)
    if re.search(r'\b(list|show|list all|What are the).*\bpending processes\b', q) or re.search(r'\bpending processes\b', q):
        sql = """
        SELECT p.process_id, p.name AS process_name, COUNT(pa.assignment_id) AS pending_assignments
        FROM processes p
        JOIN process_assignments pa ON p.process_id = pa.process_id
        WHERE pa.status = 'pending'
        GROUP BY p.process_id, p.name
        HAVING pending_assignments > 0
        """
        return sql, None, None
    
    # 2b) In-progress processes
    if re.search(r'\b(list|show|list all|What are the).*\bin-progress processes\b', q) or re.search(r'\bin-progress processes\b', q):
        sql = """
        SELECT p.process_id, p.name AS process_name, COUNT(pa.assignment_id) AS inprogress_assignments
        FROM processes p
        JOIN process_assignments pa ON p.process_id = pa.process_id
        WHERE pa.status = 'in-progress'
        GROUP BY p.process_id, p.name
        HAVING inprogress_assignments > 0
        """
        return sql, None, None

    # 2c) Completed processes
    if re.search(r'\b(list|show|list all|What are the).*\bcompleted processes\b', q) or re.search(r'\bcompleted processes\b', q):
        sql = """
        SELECT p.process_id, p.name AS process_name, COUNT(pa.assignment_id) AS completed_assignments
        FROM processes p
        JOIN process_assignments pa ON p.process_id = pa.process_id
        WHERE pa.status = 'completed'
        GROUP BY p.process_id, p.name
        HAVING completed_assignments > 0
        """
        return sql, None, None

    # 3) How many documents has [customer name] submitted?
    m = re.search(r'how many documents (has|did) (.+?) (submitted|did submit)', q)
    if not m:
        m = re.search(r'how many documents (.+?) submitted', q)  # alt phrasing
    if m:
        # try to extract the customer name fragment
        # group could be like "ramesh sharma" or "has ramesh sharma submitted"
        # We'll attempt to locate a known customer name within the query
        # Strategy: look for any customer name appearing in the query text
        found = None
        for cust in customers:
            if cust.lower() in q:
                found = cust
                break
        # fallback: use the group capture if not found
        if not found:
            candidate_fragment = m.group(2) if len(m.groups()) >= 2 else None
            if candidate_fragment:
                found = match_best_entity(candidate_fragment, customers)
        if not found:
            return None, None, f"Customer not found in query. Try exact name (e.g., 'How many documents has Ramesh Sharma submitted?')"
        sql = """
        SELECT COUNT(*) AS doc_count
        FROM document_submissions ds
        JOIN customers c ON ds.customer_id = c.customer_id
        WHERE c.name = %s
        """
        return sql, (found,), None

    # 4) Which process has the most documents?
    if re.search(r'which process (has|with).*(most|maximum).*documents', q) or re.search(r'process.*most documents', q):
        sql = """
        SELECT p.process_id, p.name AS process_name, COUNT(ds.submission_id) AS total_docs
        FROM processes p
        LEFT JOIN document_submissions ds ON p.process_id = ds.process_id
        GROUP BY p.process_id, p.name
        ORDER BY total_docs DESC
        LIMIT 1
        """
        return sql, None, None

    # 5) Which customers are assigned to [process name]?
    m = re.search(r'which customers are assigned to (?:the )?(.+)', q)
    if m:
        proc_fragment = m.group(1).strip()
        # match to known process
        matched_proc = match_best_entity(proc_fragment, processes)
        if not matched_proc:
            # try a looser approach: check any process name in query text
            for p in processes:
                if p.lower() in q:
                    matched_proc = p
                    break
        if not matched_proc:
            return None, None, f"Process '{proc_fragment}' not recognized. Try exact process name."
        sql = """
        SELECT c.customer_id, c.name AS customer_name, c.email
        FROM customers c
        JOIN process_assignments pa ON c.customer_id = pa.customer_id
        JOIN processes p ON pa.process_id = p.process_id
        WHERE p.name = %s
        """
        return sql, (matched_proc,), None

    # Additional helpful patterns:
    # - "show customers assigned to KYC"
    m = re.search(r'(show|list|get)\b.*customers.*assigned to (.+)', q)
    if m:
        proc_fragment = m.group(2).strip()
        matched_proc = match_best_entity(proc_fragment, processes)
        if matched_proc:
            sql = """
            SELECT c.customer_id, c.name AS customer_name, c.email
            FROM customers c
            JOIN process_assignments pa ON c.customer_id = pa.customer_id
            JOIN processes p ON pa.process_id = p.process_id
            WHERE p.name = %s
            """
            return sql, (matched_proc,), None

    # - "how many documents has [customer]" alternate short pattern
    m = re.search(r'documents (?:has|has )?(.*?) submitted', q)
    if m:
        frag = m.group(1).strip()
        matched = match_best_entity(frag, customers)
        if matched:
            sql = """
            SELECT COUNT(*) AS doc_count
            FROM document_submissions ds
            JOIN customers c ON ds.customer_id = c.customer_id
            WHERE c.name = %s
            """
            return sql, (matched,), None
        
    # Which customers should provide [document type]?
    m = re.search(r'(should provide|needs to submit|have not submitted|have not provided|missing)\s+(.+?)\s+(document|proof|card)?', q)
    if m:
        doc_fragment = m.group(2).strip()
        matched_doc = match_best_entity(doc_fragment, doc_types)
        if not matched_doc:
            return None, None, f"Document type '{doc_fragment}' not recognized. Try exact document name."
        
        sql = """
        SELECT DISTINCT c.customer_id, c.name AS customer_name, c.email
        FROM customers c
        JOIN process_assignments pa ON c.customer_id = pa.customer_id
        JOIN process_documents pd ON pa.process_id = pd.process_id
        JOIN document_types dt ON pd.document_type_id = dt.document_type_id
        WHERE dt.name = %s
        AND c.customer_id NOT IN (
            SELECT customer_id
            FROM document_submissions ds
            JOIN document_types dtt ON ds.document_type_id = dtt.document_type_id
            WHERE dtt.name = %s
        )
        """
        return sql, (matched_doc, matched_doc), None
      

    # If we still haven't matched: return helpful message
    return None, None, "Could not parse query. Try simple phrases like 'Show all customers', 'How many documents has Ramesh Sharma submitted?', 'Which process has the most documents?', or 'Which customers are assigned to Home Loan Application?'."

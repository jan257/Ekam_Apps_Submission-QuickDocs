CREATE DATABASE QuickDocs;
USE QuickDocs;

CREATE TABLE processes (
    process_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE document_types (
    document_type_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    required_fields JSON
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE process_assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    process_id INT NOT NULL,
    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'in-progress', 'completed') DEFAULT 'pending',
    completion_percentage INT DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (process_id) REFERENCES processes(process_id)
);

CREATE TABLE document_submissions (
    submission_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    process_id INT NOT NULL,
    document_type_id INT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_url TEXT,
    extracted_data JSON,
    validation_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (process_id) REFERENCES processes(process_id),
    FOREIGN KEY (document_type_id) REFERENCES document_types(document_type_id)
);

-- Additional Tables 
CREATE TABLE process_documents (
    process_document_id INT AUTO_INCREMENT PRIMARY KEY,
    process_id INT NOT NULL,
    document_type_id INT NOT NULL,
    FOREIGN KEY (process_id) REFERENCES processes(process_id) ON DELETE CASCADE,
    FOREIGN KEY (document_type_id) REFERENCES document_types(document_type_id) ON DELETE CASCADE
);


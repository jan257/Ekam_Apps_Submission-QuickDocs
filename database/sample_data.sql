INSERT INTO processes (name, description) VALUES
('Home Loan Application', 'Process for home loan verification'),
('KYC Verification', 'Know Your Customer verification process');


INSERT INTO document_types (name, description, required_fields) VALUES
('PAN Card', 'Permanent Account Number card', '["PAN Number", "Name"]'),
('Salary Slip', 'Monthly salary statement', '["Employer Name", "Salary Amount", "Month"]'),
('Bank Statement', 'Monthly bank account statement', '["Account Number", "Transaction List"]'),
('Aadhaar Card', 'Unique Identification Card', '["Aadhaar Number", "Name", "DOB"]'),
('Passport', 'Travel document', '["Passport Number", "Name", "Nationality"]');


INSERT INTO customers (name, email, phone) VALUES
('Ramesh Sharma', 'ramesh@gmail.com', '9876543210'),
('Priya Iyer', 'priya@gmail.com', '9876501234'),
('Amit Verma', 'amit@gmail.com', '9876541234'),
('Neha Gupta', 'neha@gmail.com', '9876512345'),
('Arjun Singh', 'arjun@gmail.com', '9876523456');


INSERT INTO process_assignments (customer_id, process_id, status, completion_percentage) VALUES
(1, 1, 'in-progress', 33),
(2, 1, 'pending', 0),
(3, 2, 'completed', 100),
(4, 2, 'in-progress', 50),
(5, 1, 'pending', 0);


INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, extracted_data, validation_status) VALUES
(1, 1, 2, 'http://example.com/salaryslip_ramesh.pdf', '{"Employer Name":"Infosys","Salary Amount":"50000","Month":"July"}', 'approved'),
(3, 2, 1, 'http://example.com/pancard_amit.pdf', '{"PAN Number":"ABCDE1234F","Name":"Amit Verma"}', 'approved'),
(4, 2, 4, 'http://example.com/aadhaar_neha.pdf', '{"Aadhaar Number":"123412341234","Name":"Neha Gupta","DOB":"1995-06-10"}', 'pending');


INSERT INTO process_documents (process_id, document_type_id) VALUES
(2, 1), -- KYC requires PAN
(2, 4), -- KYC requires Aadhaar
(1, 1), -- Loan Application requires PAN
(1, 2), -- Loan Application requires Salary Slip
(1, 3); -- Loan Application requires Bank Statement


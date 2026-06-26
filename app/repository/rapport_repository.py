# I want to be able to store the generated data from generated reports in a database for future reference. This will allow me to keep track of all the reports that have been generated, along with their associated data and metadata. By storing this information in a structured format, I can easily query and analyze the data later on, which will be useful for auditing purposes and for generating insights from the report data.

#   """
#             CREATE TABLE IF NOT EXISTS reports (
#                 id TEXT PRIMARY KEY,              -- report_number
#                 created_at TEXT NOT NULL,
#                 excel_path TEXT NOT NULL,
#                 template_path TEXT NOT NULL,
#                 row_number INTEGER NOT NULL,
#                 data_json TEXT NOT NULL
#             )
#             """
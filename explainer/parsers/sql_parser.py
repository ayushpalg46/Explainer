import re
from typing import List, Dict, Optional
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class SqlParser(BaseParser):
    """
    Parses SQL files (.sql) line-by-line, extracting table definitions,
    columns, constraints, indexes, queries, and relations with
    word-by-word breakdowns, 4-year-old beginner analogies, and cross-file links.
    """

    SQL_KEYWORDS = {
        "CREATE": "SQL command to create a brand new database object (like a table, index, or view).",
        "TABLE": "Specifies that the object being created is a structured relational table.",
        "PRIMARY": "Part of PRIMARY KEY, marking a column as the unique identifier for every record.",
        "KEY": "Designates an index or relational constraint rule on a table.",
        "FOREIGN": "Part of FOREIGN KEY, establishing a parent-child relationship to another table.",
        "REFERENCES": "Specifies which outside table and column this foreign key points to.",
        "NOT": "Logical negation, commonly used with NULL to forbid empty values.",
        "NULL": "Represents missing, unknown, or empty data in a database slot.",
        "UNIQUE": "Constraint rule requiring all values in this column to be completely distinct.",
        "AUTO_INCREMENT": "Automatically increases the number by 1 for every newly inserted row.",
        "DEFAULT": "Sets the default fallback value used when no data is supplied.",
        "SELECT": "Query command used to retrieve records and columns from one or more tables.",
        "FROM": "Specifies which table(s) to fetch records from.",
        "WHERE": "Filters records so only rows meeting this condition are returned or modified.",
        "JOIN": "Combines rows from two or more tables based on a related column between them.",
        "INSERT": "Command used to add new rows of data into a table.",
        "INTO": "Specifies the target table for an INSERT statement.",
        "VALUES": "Specifies the actual data items being inserted into columns.",
        "UPDATE": "Command used to modify existing records in a table.",
        "SET": "Specifies the new values to assign to columns during an UPDATE.",
        "DELETE": "Command used to remove records from a table.",
        "INDEX": "A fast search structure (like an index at the back of a book) speeding up queries.",
        "ORDER": "Part of ORDER BY, used to sort results in ascending or descending order.",
        "BY": "Specifies the columns to group or sort by.",
        "GROUP": "Part of GROUP BY, used to aggregate rows sharing identical values.",
    }

    SQL_TYPES = {
        "INT": "Integer data type storing whole numbers (like 1, 2, 42).",
        "INTEGER": "Integer data type storing whole numbers.",
        "BIGINT": "Large integer type storing very big numbers (up to 9 quintillion).",
        "VARCHAR": "Variable-length text string storing letters, words, or sentences.",
        "TEXT": "Long text data type storing large paragraphs or documents.",
        "BOOLEAN": "True or False flag value.",
        "TIMESTAMP": "Date and time record tracking when an event occurred.",
        "DATETIME": "Date and time storage.",
        "FLOAT": "Floating-point number storing decimal values.",
        "DOUBLE": "High-precision floating-point number.",
        "DECIMAL": "Exact fixed-point decimal number, ideal for money and currency.",
        "JSON": "Structured JSON document data stored directly inside a database column.",
    }

    def __init__(self):
        super().__init__(language="SQL Database Script")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        analysis.beginner_story = (
            "Think of a SQL file like a blueprint for a giant, super-organized filing cabinet! "
            "It builds labeled drawers (called tables), creates labeled folders with strict rules "
            "(like names and ages), and sets up fast index tabs so your computer can find any piece of information "
            "in less than a blink of an eye!"
        )

        tables_created = []
        foreign_keys = []
        queries_found = []
        in_create_table = False

        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("--") or clean.startswith("/*"):
                continue

            upper = clean.upper()

            # 1. CREATE TABLE
            if "CREATE TABLE" in upper:
                in_create_table = True
                m_tbl = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?([a-zA-Z0-9_]+)["`]?', clean, re.IGNORECASE)
                tbl_name = m_tbl.group(1) if m_tbl else "table"
                tables_created.append(tbl_name)

                words_dict = {
                    "CREATE TABLE": "Command instructing the database engine to build a new structured data table.",
                    tbl_name: f"The unique name of this database table: '{tbl_name}'."
                }

                analysis.elements.append(ElementExplanation(
                    name=f"Table: {tbl_name}",
                    kind="table",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"SQL table creation definition `{tbl_name}`.",
                    how_it_is_used=f"Builds a new database relation named `{tbl_name}` at line {idx}.",
                    where_it_is_used=f"Table definition at line {idx}.",
                    why_it_works="The SQL DDL engine allocates schema catalog metadata and disk pages for this table.",
                    best_practices_and_pitfalls="Always define a PRIMARY KEY to optimize B-Tree indexing and replication.",
                    simple_analogy=f"Think of table '{tbl_name}' like building a brand new toy drawer with a name tag '{tbl_name}' on it!",
                    what_happens_on_screen="Prepares structured storage in the database to store rows of data.",
                    what_if_removed=f"The database will not have a `{tbl_name}` table, and any backend code querying `{tbl_name}` will crash with 'Table does not exist'.",
                    words_breakdown=words_dict,
                    interconnection_note=f"Stores data queried by backend models in `server.py`, `models.py`, or application routes."
                ))
                if clean.endswith(");") or clean.endswith(")"):
                    in_create_table = False
                continue

            # Check if closing table
            if in_create_table and (clean.endswith(");") or clean.endswith(")") or clean == ");"):
                in_create_table = False
                if clean in (");", ")"):
                    continue

            # 2. FOREIGN KEY / REFERENCES
            if "FOREIGN KEY" in upper or "REFERENCES" in upper:
                m_fk = re.search(r'REFERENCES\s+["`]?([a-zA-Z0-9_]+)["`]?\s*\(([^)]+)\)', clean, re.IGNORECASE)
                target_table = m_fk.group(1) if m_fk else "parent_table"
                target_col = m_fk.group(2) if m_fk else "id"
                foreign_keys.append(target_table)
                analysis.raw_imports.append(target_table)

                words_dict = {
                    "FOREIGN KEY": "Relational constraint ensuring this value matches an existing record in the parent table.",
                    "REFERENCES": f"Specifies the target parent table '{target_table}' and column '({target_col})'."
                }

                analysis.elements.append(ElementExplanation(
                    name=f"Relation: -> {target_table}({target_col})",
                    kind="relation",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Relational foreign key constraint linking to `{target_table}({target_col})`.",
                    how_it_is_used=f"Enforces referential integrity at line {idx}.",
                    where_it_is_used=f"Foreign key definition at line {idx}.",
                    why_it_works="The database engine checks the parent index before allowing inserts or deletes.",
                    best_practices_and_pitfalls="Add an index on foreign key columns to speed up JOIN operations.",
                    simple_analogy=f"Like tethering a baby toy with a little string to the mother toy '{target_table}' so it never gets lost!",
                    what_happens_on_screen="Guarantees valid relationships so orphaned or corrupted records cannot exist in the database.",
                    what_if_removed=f"The database allows dangling records pointing to nonexistent `{target_table}` rows.",
                    words_breakdown=words_dict,
                    interconnection_note=f"Establishes a relational dependency link to table `{target_table}`."
                ))
                continue

            # 3. Queries and Query Clauses (SELECT, FROM, JOIN, WHERE, INSERT, UPDATE, DELETE)
            if any(upper.startswith(q) for q in ["SELECT", "FROM", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "INSERT", "UPDATE", "DELETE", "CREATE INDEX"]):
                q_verb = upper.split()[0]
                words_dict = {q_verb: self.SQL_KEYWORDS.get(q_verb, f"SQL operation `{q_verb}`.")}
                for kw in ["SELECT", "FROM", "JOIN", "WHERE", "GROUP", "ORDER", "ON", "AND", "OR"]:
                    if f" {kw} " in f" {upper} ":
                        words_dict[kw] = self.SQL_KEYWORDS.get(kw, f"SQL clause keyword `{kw}`.")

                queries_found.append(q_verb)

                analysis.elements.append(ElementExplanation(
                    name=f"Query: {clean[:40]}",
                    kind="query",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"SQL Query / DML statement clause: `{clean}`.",
                    how_it_is_used=f"Specifies database query operation at line {idx}.",
                    where_it_is_used=f"Query at line {idx}.",
                    why_it_works="Parsed by query optimizer into an execution plan scanning indexes and disk blocks.",
                    best_practices_and_pitfalls="Use parameterized queries / prepared statements to prevent SQL injection.",
                    simple_analogy=f"Think of this query like asking the filing assistant robot: 'Please fetch or organize the cards for me!'",
                    what_happens_on_screen="Fetches, filters, or modifies data displayed in the application.",
                    what_if_removed="This query clause will be omitted, causing incorrect data results or query syntax errors.",
                    words_breakdown=words_dict,
                    interconnection_note="Executed by backend API routes or database migration pipelines."
                ))
                continue

            # 4. Column Definition inside CREATE TABLE (e.g. id INT PRIMARY KEY, email VARCHAR(255) NOT NULL)
            if in_create_table and not upper.startswith(("PRIMARY", "KEY", "CONSTRAINT", "FOREIGN")):
                m_col = re.match(r'^\s*["`]?([a-zA-Z0-9_]+)["`]?\s+([A-Za-z0-9_()]+)(.*)$', clean)
                if m_col:
                    col_name = m_col.group(1)
                    col_type = m_col.group(2)
                    col_rest = m_col.group(3).strip()

                    words_dict = {
                        col_name: f"Column identifier name: '{col_name}'.",
                        col_type: self.SQL_TYPES.get(col_type.split("(")[0].upper(), f"Data type `{col_type}`.")
                    }

                    for kw in ["PRIMARY KEY", "AUTO_INCREMENT", "NOT NULL", "UNIQUE", "DEFAULT"]:
                        if kw in col_rest.upper():
                            words_dict[kw] = self.SQL_KEYWORDS.get(kw.split()[0], f"Constraint rule: `{kw}`.")

                    analysis.elements.append(ElementExplanation(
                        name=f"Column: {col_name} {col_type}",
                        kind="column",
                        line_number=idx,
                        snippet=clean,
                        what_it_is=f"Table column `{col_name}` storing type `{col_type}` with constraints `{col_rest}`.",
                        how_it_is_used=f"Defines attribute field `{col_name}` at line {idx}.",
                        where_it_is_used=f"Column schema at line {idx}.",
                        why_it_works="Maps to a fixed or dynamic offset in the database storage record format.",
                        best_practices_and_pitfalls="Use NOT NULL wherever possible to avoid three-valued boolean logic in SQL queries.",
                        simple_analogy=f"Think of column '{col_name}' like a designated slot inside the drawer reserved for '{col_name}'!",
                        what_happens_on_screen=f"Holds the `{col_name}` value displayed on user screens or API JSON outputs.",
                        what_if_removed=f"The table loses the `{col_name}` field, breaking code that queries it.",
                        words_breakdown=words_dict,
                        interconnection_note=f"Mapped to entity models and serializer schemas in backend application code."
                    ))
                    continue

        detected_concepts = []
        if tables_created:
            detected_concepts.append(f"Database Relational Schema ({len(tables_created)} tables: {', '.join(tables_created[:4])})")
        if foreign_keys:
            detected_concepts.append(f"Referential Foreign Key Integrity ({len(foreign_keys)} constraints)")
        if queries_found:
            detected_concepts.append(f"SQL Operations ({', '.join(list(set(queries_found))[:3])})")

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = ["Relational SQL Database Engine (PostgreSQL / MySQL / SQLite)"]
        analysis.role_in_codebase = "Database Schema Definition, Migration, or Query Script"
        analysis.summary = (
            f"SQL database script containing {len(lines)} lines. "
            f"Defines {len(tables_created)} relational table(s): {', '.join(tables_created) if tables_created else 'queries only'}. "
            f"{f'Enforces {len(foreign_keys)} referential constraint(s). ' if foreign_keys else ''}"
            f"Interacts with backend models and application data stores."
        )
        return analysis

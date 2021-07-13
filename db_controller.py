import logging
import os
import psycopg2 as pg
import psycopg2.extras
import psycopg2.sql

class DatabaseController():

    def __init__(self):
        self.init_conn()

    def init_conn(self):
        self.db_conn = pg.connect(os.environ['DATABASE_URL'], sslmode='require')
        logging.info(f'connected to db: {self.db_conn.dsn}')

    def close_conn(self):
        self.db_conn.close()
        logging.info('db connection closed')

    def bulk_insert(self, table, items):
        if not all(type(item) == type(items[0]) for item in items):
            self.close_conn()
            raise TypeError('all items must be of same type for bulk_insert')

        items_to_insert = self.get_filtered_items_to_insert(items, table)

        if items_to_insert:
            logging.info(f'bulk insert of {len(items_to_insert)} items to {table}...')

            colnames = self.get_colnames(items_to_insert, table)
            template = self.get_template(colnames)
            query = self.get_query(table, colnames)
            cur = self.db_conn.cursor()

            try:
                pg.extras.execute_values(cur, query, items_to_insert, template)
                self.db_conn.commit()
            except (pg.DatabaseError) as error:
                logging.error(error)
                self.db_conn.rollback()

            cur.close()
        else:
            logging.info(f'no items to insert for table {table}')

    def get_colnames(self, items_to_insert, table):
        cur = self.db_conn.cursor()
        query = pg.sql.SQL(f'SELECT * FROM {table} LIMIT 0')
        cur.execute(query)
        cur.close()
        colnames = [col.name for col in cur.description]
        return list(filter(lambda colname: colname in items_to_insert[0].keys(), colnames))

    def get_template(self, colnames):
        colnames_formatted = [f'%({colname})s' for colname in colnames]
        return f"({', '.join(colnames_formatted)})"

    def get_query(self, table, colnames):
        colnames_str = ', '.join(colnames)
        return pg.sql.SQL(f'INSERT INTO {table} ({colnames_str}) VALUES %s')

    def get_filtered_items_to_insert(self, items, table):
        pkey_columns = self.get_pkey_columns(table)
        pkey_columns_str = self.get_pkey_columns_str(pkey_columns)

        cur = self.db_conn.cursor()
        query = pg.sql.SQL(f'SELECT {pkey_columns_str} FROM {table}')
        cur.execute(query)

        existing_records = self.get_existing_records(cur.fetchall(), pkey_columns)
        cur.close()

        return self.get_item_dicts_not_in_existing_records(items, existing_records, pkey_columns)

    def get_existing_records(self, entries, pkey_columns):
        existing_records = []
        for entry in entries:
            record = {}
            for index, col in enumerate(entry):
                record[pkey_columns[index]] = entry[index]
            existing_records.append(record)
        return existing_records

    def get_item_dicts_not_in_existing_records(self, items, existing_records, pkey_columns):
        items_to_insert = []
        for item in items:
            item_dict = vars(item)
            item_dict_pkey_columns = {}
            for column in pkey_columns:
                item_dict_pkey_columns[column] = item_dict[column]
            if item_dict_pkey_columns not in existing_records:
                items_to_insert.append(item_dict)
        return items_to_insert

    def get_pkey_columns(self, table):
        cur = self.db_conn.cursor()
        query_string = f"""SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a
                ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{table}'::regclass
                AND i.indisprimary"""
        query = pg.sql.SQL(query_string)
        cur.execute(query)
        pkey_columns = [entry[0] for entry in cur.fetchall()]
        cur.close()
        return pkey_columns

    def get_pkey_columns_str(self, pkey_columns):
        if len(pkey_columns) > 1:
            return ', '.join(pkey_columns)
        else:
            return pkey_columns[0]

    def delete_table(self, table):
        cur = self.db_conn.cursor()
        query = pg.sql.SQL(f'DELETE FROM {table}')
        cur.execute(query)
        logging.info(f'wiped table: {table}')
        self.db_conn.commit()
        cur.close()

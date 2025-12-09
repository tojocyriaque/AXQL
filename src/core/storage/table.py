import struct
from config import ROOT_DIR
from core.exceptions import (
    TableAttributeExistsException,
    TableAttributeNotFoundException,
)
from core.entities.table import TableAttribute
import re
import operator


def match_constraint(value, attr: TableAttribute):
    if isinstance(value, (int, float)):
        return attr.min_size <= value <= attr.max_size
    elif isinstance(value, str):
        return attr.min_size <= len(value) <= attr.max_size
    else:
        raise Exception("Support for this data type is not implemented")


def eval_math_cond(value, cond_str):
    OPS = {
        "==": operator.eq,
        "!=": operator.ne,
        "<=": operator.le,
        ">=": operator.ge,
        ">": operator.gt,
        "<": operator.lt,
    }

    for op_sym, op_func in OPS.items():
        if cond_str.startswith(op_sym):
            rhs = float(cond_str[len(op_sym) :])
            return op_func(value, rhs)
    raise ValueError("Unsupported condition")


# verify if the value match the conditions
def verify_conditions(value, conditions: list[str | int], all_match=False):
    if isinstance(value, (int, float)):
        # Math conditions
        for cond in conditions:
            math_eval = (
                (value == cond)
                if isinstance(cond, (float, int))
                else eval_math_cond(value, cond)
            )
            if math_eval and not all_match:
                return True  # one condition in the OR is verified

            elif not math_eval and all_match:
                return False  # one condition in the AND is not verified

    elif isinstance(value, str):
        meta = ".^$*+?{}[]|()"
        # Regex matching
        for cond in [c for c in conditions if isinstance(c, str)]:
            # matching the pattern now
            if any(c in meta for c in cond):  # regular expression
                regex_match = re.match(cond, value) is not None
            else:  # not a regular expression
                # fullmatch required
                regex_match = cond == value

            if regex_match and not all_match:
                return True  # one condition in the OR is verified
            elif not regex_match and all_match:
                return False  # one condition in the AND is not verified

    # If loop is finished:
    # OR mode → none matched → False
    # AND mode → none failed → True
    return all_match


"""
Handing tables
"""


class Table:
    def __init__(self, dbname: str, tablename: str):
        self.tablename = tablename
        self.attributes: dict[str, TableAttribute] = {}
        self.dbname = dbname
        self.file = None
        self.filepath = f"{ROOT_DIR}/{self.dbname}/{self.tablename}.tbl"

    # CLI things
    def describe(self):
        """
        Prints a nicely formatted description of the table's schema.
        """
        RESET = "\033[0m"
        BOLD = "\033[1m"
        YELLOW = "\033[33m"
        GREEN = "\033[32m"

        # Helper function to strip ANSI escape sequences.
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

        def strip_ansi(text):
            return ansi_escape.sub("", text)

        # Define the header labels
        headers = ["Column", "Type", "Min Size", "Max Size", "Default", "Constraint"]
        headers = [f"{BOLD}{YELLOW}{header}{RESET}" for header in headers]
        # Build rows from each attribute
        rows = []
        for attr_name, attr in self.attributes.items():
            rows.append(
                [
                    f"{GREEN}{attr_name}{RESET}",
                    attr.dtype,
                    str(attr.min_size),
                    str(attr.max_size),
                    str(attr.default) if attr.default is not None else "",
                    str(attr.constraint) if attr.constraint is not None else "",
                ]
            )

        # Compute column widths based on header and row values
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(strip_ansi(header))
            for row in rows:
                cell_len = len(strip_ansi(row[i]))
                if cell_len > max_width:
                    max_width = cell_len
            col_widths.append(max_width)

        # Build border lines using Unicode box-drawing characters
        top_line = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        sep_line = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bottom_line = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

        # Print a header for the table description
        print(f"\nTable: {self.tablename}\n")
        print(top_line)

        # Print header row
        header_cells = []
        for i, cell in enumerate(headers):
            visible = strip_ansi(cell)
            pad = col_widths[i] - len(visible)
            header_cells.append(cell + " " * pad)
        header_row = "│ " + " │ ".join(header_cells) + " │"
        print(header_row)
        print(sep_line)

        # Print each row
        for row in rows:
            row_cells = []
            for i, cell in enumerate(row):
                visible = strip_ansi(cell)
                pad = col_widths[i] - len(visible)
                row_cells.append(cell + " " * pad)
            row_line = "│ " + " │ ".join(row_cells) + " │"
            print(row_line)

        print(bottom_line)

    def print_records(self, records):
        """
        Prints a nicely formatted grid of the selected records,
        similar style to describe().
        """
        if not records:
            print("No records found.")
            return

        RESET = "\033[0m"
        BOLD = "\033[1m"
        CYAN = "\033[36m"
        YELLOW = "\033[33m"
        MAGENTA = "\033[35m"
        GREEN = "\033[32m"

        # Helper to strip ANSI codes for width calculations
        ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        strip_ansi = lambda text: ansi_escape.sub("", text)

        # Extract column names from first record
        headers = list(records[0].keys())
        headers_color = [f"{BOLD}{YELLOW}{h}{RESET}" for h in headers]

        # Build rows as strings
        rows = []
        for rec in records:
            row = []
            for val in rec.values():
                if val is None:
                    row.append(f"{MAGENTA} {RESET}")
                elif isinstance(val, (int, float)):
                    row.append(f"{CYAN}{val}{RESET}")
                else:
                    row.append(f"{GREEN}{val}{RESET}")
            rows.append(row)

        # Compute column widths
        col_widths = []
        for i, header in enumerate(headers_color):
            max_w = len(strip_ansi(header))
            for row in rows:
                w = len(strip_ansi(row[i]))
                if w > max_w:
                    max_w = w
            col_widths.append(max_w)

        # Build borders
        top_line = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        sep_line = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bottom_line = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

        print()
        print(top_line)

        # Header row
        header_cells = []
        for i, cell in enumerate(headers_color):
            visible = strip_ansi(cell)
            pad = col_widths[i] - len(visible)
            header_cells.append(cell + " " * pad)
        print("│ " + " │ ".join(header_cells) + " │")
        print(sep_line)

        # Data rows
        for row in rows:
            row_cells = []
            for i, cell in enumerate(row):
                visible = strip_ansi(cell)
                pad = col_widths[i] - len(visible)
                row_cells.append(cell + " " * pad)
            print("│ " + " │ ".join(row_cells) + " │")

        print(bottom_line)
        print(f"{len(records)} record(s).")

    def create(self, attributes):
        self.file = open(
            self.filepath, "a"
        )  # create the table file if it does not exist
        self.setup(attributes)

    def setup_attributes(self, attributes: dict[str, dict]):
        for attr_name, attr in attributes.items():
            self.attributes[attr_name] = TableAttribute(
                name=attr_name,
                dtype=attr["dtype"],
                max_size=attr["max_size"],
                min_size=attr["min_size"],
                default=attr["default"],
                constraint=attr["constraint"],
            )

    def setup(self, attributes: list):
        for attr in attributes:
            print("setup attr:", attr)
            attr_name, dtype, max, min, default, constraint = attr
            self.attributes[attr_name] = TableAttribute(
                name=attr_name,
                dtype=dtype,
                max_size=max,
                min_size=min,
                default=default,
                constraint=constraint,
            )

        self.file = open(self.filepath, "r")  # read the file

    def add_attributes(self, *attributes):
        new_attrs = []
        for attr in attributes:
            attr_name, dtype, max, min, default, constraint = attr
            # print(
            #     f"attr:{attr_name}, dtype:{dtype}, max:{max}, min:{min}, default:{default}, constraint:{constraint}"
            # )
            if attr_name in self.attributes.keys():
                raise TableAttributeExistsException("Attribute exists !!")

            if max < min:
                raise Exception("min should always be less than max")

            if type(default).__name__ != dtype:
                print(type(default).__name__, dtype)
                raise Exception("The default value has invalid data type")

            if not isinstance(constraint, str):
                raise Exception("Invalid constraint")

            tbl_attr = TableAttribute(*attr)
            if tbl_attr.default is None:
                raise Exception("Adding new attributes need default values in AXQL")

            new_attrs.append(tbl_attr)

        old_records = self.select(pr=False) if self.attributes != {} else []
        for new_attr in new_attrs:
            self.attributes[new_attr.name] = new_attr

        print("new:", list(map(lambda e: e.name, new_attrs)))
        migrated_records = []
        for record in old_records:
            new_record = dict(record)
            for new_attr in new_attrs:
                new_record[new_attr.name] = new_attr.default

            migrated_records.append(new_record)

        print("Writing migrations")
        with open(self.filepath, "wb") as tbf:
            for record in migrated_records:
                for attr_name, attr_obj in self.attributes.items():
                    value = record[attr_name]

                    if attr_obj.dtype == "int":
                        tbf.write(struct.pack("<B I", 1, value))

                    elif attr_obj.dtype == "float":
                        tbf.write(struct.pack("<B f", 2, value))

                    elif attr_obj.dtype == "str":
                        encoded = value.encode("utf-8")
                        tbf.write(
                            struct.pack(
                                f"<B I {len(encoded)}s", 3, len(encoded), encoded
                            )
                        )

        print(
            f"Added {len(new_attrs)} attribute(s) and migrated {len(old_records)} record(s)."
        )

    def remove_attribute(self, attr_name: str):
        if attr_name not in self.attributes.keys():
            raise TableAttributeNotFoundException(f"No attribute {attr_name} !!")

        records = self.select(pr=False)
        self.attributes.pop(attr_name)

        print("Writing migrations")
        with open(self.filepath, "wb") as tbf:
            for record in records:
                for attr_name, attr_obj in self.attributes.items():
                    value = record[attr_name]

                    if attr_obj.dtype == "int":
                        tbf.write(struct.pack("<B I", 1, value))

                    elif attr_obj.dtype == "float":
                        tbf.write(struct.pack("<B f", 2, value))

                    elif attr_obj.dtype == "str":
                        encoded = value.encode("utf-8")
                        tbf.write(
                            struct.pack(
                                f"<B I {len(encoded)}s", 3, len(encoded), encoded
                            )
                        )

        print(f"Removed attribute {attr_name} and migrated {len(records)} record(s).")

    def modify_attribute(self, attr_name: str, new_attr: tuple):
        if attr_name not in self.attributes.keys():
            raise TableAttributeNotFoundException(f"No attribute {attr_name} !!")

        new_name, dtype, max, min, default, constraint = new_attr
        if max < min:
            raise Exception("min should always be less than max")

        if type(default).__name__ != dtype:
            print(type(default).__name__, dtype)
            raise Exception("The default value has invalid data type")

        if not isinstance(constraint, str):
            raise Exception("Invalid constraint")

        # same attribute
        if new_name == attr_name:
            self.attributes[attr_name] = TableAttribute(*new_attr)
        # different name (replace the attribute)
        else:
            self.remove_attribute(attr_name)
            self.add_attributes(new_attr)

    def description(self):
        return {name: attr.properties() for name, attr in self.attributes.items()}

    # Record handling
    def insert_values(self, **kwargs):
        """
        Writing record following the structure of the table in order
        """
        record_bytes = b""
        for attr in self.attributes.keys():
            if attr not in kwargs:
                default_value = self.attributes[attr].default
                if default_value is not None:
                    kwargs[attr] = default_value
                else:
                    raise Exception(f"Missing attribute {attr} !!")

            if attr not in self.attributes.keys():
                raise Exception(f"Table {self.tablename} has no attribute {attr} !!")

            dtype = self.attributes[attr].dtype
            value = kwargs[attr]

            # the value does not follow the constraint
            if not match_constraint(value, self.attributes[attr]):
                raise Exception("Constraints unmatched")

            packed = bytes()

            match dtype:
                case "int":
                    packed = struct.pack("<B I", 1, value)  # Type 1 = int

                case "float":
                    packed = struct.pack("<B f", 2, value)  # Type 2 = float

                case "str":
                    value = value.encode("utf-8")
                    packed = struct.pack(
                        f"<B I {len(value)}s ", 3, len(value), value
                    )  # Type 3 = str

                case _:
                    pass

            record_bytes += packed

        with open(self.filepath, "ab") as tablefile:
            tablefile.write(record_bytes)

    def match_attribute_conditions(self, attr, value, all_match=False, **where):
        # Handling the where clause
        if attr in where.keys():  # if the attribute is conditionned
            conditions = where[attr]
            condition_verified = True
            if isinstance(conditions, (tuple, list)):  # AND(tuple) , OR(list)
                condition_verified = verify_conditions(
                    value,
                    list(conditions),
                    all_match=isinstance(conditions, tuple),
                )

            elif isinstance(conditions, str):
                if isinstance(value, str):  # regex matching
                    condition_verified = (
                        re.fullmatch(pattern=conditions, string=value) is not None
                    )
                elif isinstance(value, (float, int)):  # numerical condition
                    condition_verified = eval_math_cond(value, conditions)

            else:  # numerical value (for now) check if equal
                condition_verified = value == conditions

            if condition_verified and not all_match:  # for OR conditions
                return True

            elif not condition_verified and all_match:  # for AND conditions
                return False

        # Same logic as the verify_conditions function
        return all_match

    # Reading records
    def select(
        self, pr=True, all_match=True, **where
    ):  # all_match is used for checking if it's an OR or an AND expression and pr if we should print
        records = []
        if self.attributes == {}:
            self.print_records(records)
            print("Table still unstructured")
            return records
        elif any(attr not in self.attributes.keys() for attr in where.keys()):
            raise Exception("Unexpected attribute")

        with open(self.filepath, "rb") as tablefile:
            while True:
                record = {}
                match_conditions = []
                for attr in self.attributes.keys():
                    dtype_code_bytes = tablefile.read(1)
                    value = ""

                    if not dtype_code_bytes:  # end of file
                        records_count = len(records)
                        if pr:
                            self.print_records(records)
                            print(
                                "Found",
                                records_count,
                                "records" if records_count != 1 else "record",
                            )
                        return records

                    # Get the value using struct
                    dtype_code = struct.unpack("<B", dtype_code_bytes)[0]
                    match dtype_code:
                        case 1:  # int
                            data = tablefile.read(4)  # int size is 4
                            value = struct.unpack("<I", data)[0]

                        case 2:  # float
                            data = tablefile.read(4)  # float size is 4
                            value = struct.unpack("<f", data)[0]

                        case 3:  # str
                            strlen_bytes = tablefile.read(4)
                            strlen = struct.unpack("<I", strlen_bytes)[0]

                            data = tablefile.read(strlen)
                            value = struct.unpack(f"<{strlen}s", data)[0].decode(
                                "utf-8"
                            )

                        case _:
                            pass

                    record[attr] = value

                    # Handling the where clause
                    attr_match = self.match_attribute_conditions(
                        attr, value, all_match, **where
                    )
                    match_conditions.append(attr_match)

                if all_match and all(match_conditions):
                    records.append(record)
                elif any(match_conditions) and not all_match:
                    records.append(record)

    def delete(
        self, all_match=True, **where
    ):  # all_match is used for checking OR or AND (true = AND, false = OR)
        all_records = self.select(pr=False)
        remaining = []
        for record in all_records:
            matches = [
                self.match_attribute_conditions(attr, record[attr], all_match, **where)
                for attr in self.attributes.keys()
            ]

            if all_match:
                should_delete = all(matches)
            else:
                should_delete = any(matches)

            if not should_delete:
                remaining.append(record)

        with open(self.filepath, "wb") as tbf:
            for record in remaining:
                for attr in self.attributes.keys():
                    value = record[attr]
                    dtype = self.attributes[attr].dtype

                    if dtype == "int":
                        tbf.write(struct.pack("<B I", 1, value))

                    elif dtype == "float":
                        tbf.write(struct.pack("<B f", 2, value))

                    elif dtype == "str":
                        b = value.encode("utf-8")
                        tbf.write(struct.pack(f"<B I {len(b)}s", 3, len(b), b))

        d_count = len(all_records) - len(remaining)
        print(d_count, "records" if d_count != 1 else "record", "deleted")

    def update(self, where: dict, data: dict, all_match=True):
        all_records = self.select(pr=False)
        updated = []
        for record in all_records:
            matches = [
                self.match_attribute_conditions(attr, record[attr], all_match, **where)
                for attr in self.attributes.keys()
            ]

            if all_match:
                should_update = all(matches)
            else:
                should_update = any(matches)

            if should_update:
                updated.append(record)

        with open(self.filepath, "wb") as tbf:
            for record in all_records:
                for attr in self.attributes.keys():
                    value = record[attr]
                    if (record in updated) and (
                        attr in data.keys()
                    ):  # update new values
                        value = data[attr]

                    dtype = self.attributes[attr].dtype

                    if dtype == "int":
                        tbf.write(struct.pack("<B I", 1, value))

                    elif dtype == "float":
                        tbf.write(struct.pack("<B f", 2, value))

                    elif dtype == "str":
                        b = value.encode("utf-8")
                        tbf.write(struct.pack(f"<B I {len(b)}s", 3, len(b), b))

        up_count = len(updated)
        print(up_count, "records" if up_count != 1 else "record", "affected")

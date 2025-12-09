class TableAttribute:
    def __init__(
        self, name: str, dtype: str, max_size, min_size, default, constraint: str
    ):
        self.name = name
        self.dtype = dtype
        self.max_size = max_size
        self.min_size = min_size
        self.default = default
        self.constraint = constraint

    def properties(self):
        return {
            "dtype": self.dtype,
            "min_size": self.min_size,
            "max_size": self.max_size,
            "default": self.default,
            "constraint": self.constraint,
        }


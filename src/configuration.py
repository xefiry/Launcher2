import subprocess
import time
import tomllib


class Config:
    def __init__(self, file_path: str) -> None:
        """Create configuration from toml file

        Args:
            file_path (str): The .toml file to use

        ToDo:
            manage errors due to missing keys
        """

        with open(file_path, "rb") as file:
            data = tomllib.load(file)

        self.file_path: str = file_path
        self.search_description: bool = data["Config"]["search_description"]
        self.max_results: int = data["Config"]["max_results"]
        self.rules: list[Rule] = []

        for d in data["Rules"]:
            self.rules.append(Rule.from_dict(d))

    def __repr__(self) -> str:
        result: str = ""

        for r in self.rules:
            result += str(r) + "\n"

        return result

    def as_toml(self) -> str:
        result = f"""[Config]
  search_description = {str(self.search_description).lower()}
  max_results = {self.max_results}
"""
        for r in self.rules:
            result += r.as_toml()

        return result

    def write(self) -> None:
        with open(self.file_path, "w") as f:
            f.write(self.as_toml())


class Rule:
    def __init__(
        self, match: str, description: str, args: list[str], last_use: str = ""
    ) -> None:
        self.match: str = match
        self.description: str = description
        self.args: list[str] = args
        self.last_use: str = last_use

    @staticmethod
    def from_dict(d: dict[str, str | list[str]]) -> "Rule":
        match: str = str(d["match"])
        description: str = str(d["description"])
        args: list[str] = list[str](d["args"])
        try:
            last_use: str = str(d["last_use"])
        except KeyError:
            last_use: str = ""

        return Rule(match, description, args, last_use)

    def __repr__(self) -> str:
        return f"Rule('{self.match}' - '{self.description}' - {self.args})"

    def as_toml(self) -> str:
        result = f"""
[[Rules]]
  match = "{self.match}"
  description = "{self.description}"
  args = {self.args}
"""
        if self.last_use != "":
            result += f"""  last_use = {self.last_use}
"""
        return result

    def __eq__(self, value: object) -> bool:
        print("__eq__called")
        if type(value) is Rule:
            return (
                self.match == value.match
                and self.description == value.description
                and self.args == value.args
            )
        else:
            return False

    def check(self, input: str) -> "Rule | None":
        if input.lower() in self.match.lower():
            return self
        else:
            return None

    def execute(self) -> None:
        self.last_use = time.strftime("%Y-%m-%dT%H:%M:%S")
        subprocess.Popen(self.args)

import logging

from autogpt.core.ability.base import Ability
from autogpt.core.ability.schema import (
    AbilityArguments,
    AbilityRequirements,
    AbilityResult,
)
from autogpt.core.workspace import Workspace


class ReadFile(Ability):

    def __init__(
        self,
        logger: logging.Logger,
        workspace: Workspace,
    ):
        self._logger = logger
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read and parse all text from a file."

    @property
    def limitations(self) -> str:
        return ""

    @property
    def arguments(self) -> list[str]:
        return [AbilityArguments.FILENAME]

    @property
    def requirements(self) -> AbilityRequirements:
        return AbilityRequirements(
            packages=["unstructured"],
            workspace=True,
        )

    def _check_preconditions(self, filename: str) -> AbilityResult | None:
        message = ""
        try:
            import unstructured
        except ImportError:
            message = "Package charset_normalizer is not installed."

        try:
            file_path = self._workspace.get_path(filename)
            if not file_path.exists():
                message = f"File {filename} does not exist."
            if not file_path.is_file():
                message = f"{filename} is not a file."
        except ValueError as e:
            message = str(e)

        if message:
            return AbilityResult(
                success=False,
                message=message,
                data=None,
            )

    def __call__(self, filename: str) -> AbilityResult:
        if result := self._check_preconditions(filename):
            return result

        from unstructured.partition.auto import partition

        file_path = self._workspace.get_path(filename)
        try:
            elements = partition(str(file_path))
            # TODO: Lots of other potentially useful information is available
            #   in the partitioned file. Consider returning more of it.
            data = "\n\n".join([element.text for element in elements])
            success = True
            message = f"File {file_path} read successfully."
        except IOError as e:
            data = None
            success = False
            message = str(e)

        return AbilityResult(
            success=success,
            message=message,
            data=data,
        )

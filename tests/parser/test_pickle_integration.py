"""
:Description: Integration tests for the RecipeParserConvert class
"""

from __future__ import annotations

import pickle
from collections.abc import Callable

import pytest

from conda_recipe_manager.parser.recipe_parser import RecipeParser
from conda_recipe_manager.parser.recipe_parser_convert import RecipeParserConvert
from conda_recipe_manager.parser.recipe_reader_deps import RecipeReaderDeps
from conda_recipe_manager.parser.selector_parser import SelectorParser
from conda_recipe_manager.parser.types import SchemaVersion
from conda_recipe_manager.types import SentinelType
from tests.file_loading import load_file


def test_pickle_integration_sentinel_type() -> None:
    """
    Verifies that the `SentinelType` is pickle-able. All `SentinelType` instances act as a second `None`-type.
    """
    assert pickle.loads(pickle.dumps(SentinelType())) == SentinelType()  # type: ignore[misc]


@pytest.mark.parametrize(
    "file,constructor",
    [
        ("types-toml.yaml", RecipeParser),
        ("cctools-ld64.yaml", RecipeParser),
        ("v1_format/v1_types-toml.yaml", RecipeParser),
        ("v1_format/v1_cctools-ld64.yaml", RecipeParser),
        ("types-toml.yaml", RecipeParserConvert),
        ("cctools-ld64.yaml", RecipeParserConvert),
        ("v1_format/v1_types-toml.yaml", RecipeParserConvert),
        ("v1_format/v1_cctools-ld64.yaml", RecipeParserConvert),
        ("types-toml.yaml", RecipeReaderDeps),
        ("cctools-ld64.yaml", RecipeReaderDeps),
        ("v1_format/v1_types-toml.yaml", RecipeReaderDeps),
        ("v1_format/v1_cctools-ld64.yaml", RecipeReaderDeps),
    ],
)
def test_pickle_integration_recipe_parsers(file: str, constructor: Callable[[str], RecipeParser]) -> None:
    """
    Verifies that recipe parsers can be round-tripped with `pickle`'s serialization system. This ensures RecipeParser
    classes can be used with standard libraries that utilize `pickle`, like `multiprocessing`.

    Prior to this test, `RecipeParser` classes could not be reliably pickled due to the original implementation of the
    `SentinelType`. This caused some data corruption issues when `RecipeParser` instances were being generated by
    the thread pool tooling available in `multiprocessing`.

    More details about this problem can be found in this PR:
      https://github.com/conda/conda-recipe-manager/pull/105
    """
    file_text = load_file(file)
    parser = constructor(file_text)
    assert pickle.loads(pickle.dumps(parser)).render() == parser.render()  # type: ignore[misc]


@pytest.mark.parametrize(
    "selector,schema",
    [
        # TODO: Add V1 when V1 selectors are supported
        ("[osx]", SchemaVersion.V0),
        ("[osx and win-32]", SchemaVersion.V0),
    ],
)
def test_pickle_integration_selector_parser(selector: str, schema: SchemaVersion) -> None:
    """
    This test ensures that the SelectorParser class is `pickle`-able.
    """
    parser = SelectorParser(selector, schema)
    assert str(pickle.loads(pickle.dumps(parser))) == str(parser)  # type: ignore[misc]

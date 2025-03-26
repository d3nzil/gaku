"""Tests for paging functionality."""

import logging
from typing import Generator

import gaku
import pytest
import gaku.api_types

from .test_data import IMPORT_LIST
from .utils import TestSetup


class TestBasics(TestSetup):
    """Tests for paging functionality."""

    card_imports: gaku.api_types.GeneratedImports

    @pytest.fixture(autouse=True)
    def _50_setup_teardown(self) -> Generator:
        with open(IMPORT_LIST, "r", encoding="utf-8") as src:
            import_data = src.readlines()

        self.card_imports = self.manager.generate_vocab_import(import_data)
        yield

    def test_paging_order(self) -> None:
        """Verifies that the basic ordering without source works."""
        manager = self.manager

        manager.import_cards(self.card_imports, sources=[])

        filter = gaku.api_types.CardFilter(num_cards=10)
        cards_no_index = manager.db.get_cards_any_state(filter)
        filter.start_index = 1
        cards_index = manager.db.get_cards_any_state(filter)

        assert cards_no_index[1:] == cards_index[:-1]

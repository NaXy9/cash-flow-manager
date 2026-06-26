import pytest
from django.core.exceptions import ValidationError

from apps.transactions.services import validate_cascade_chain


@pytest.mark.django_db
class TestValidateCascadeChain:

    # --- Happy paths ---------------------------------------------------

    def test_valid_chain_passes(self, expense_type, category, subcategory):
        """Correct chain: expense_type → category → subcategory — no exception."""
        validate_cascade_chain(expense_type, category, subcategory)

    def test_valid_chain_income(
        self, db, income_type, other_category, other_subcategory
    ):
        """Income chain also passes when correctly linked."""
        validate_cascade_chain(income_type, other_category, other_subcategory)

    # --- Error: category doesn't match type ----------------------------

    def test_category_wrong_type_raises(
        self, expense_type, other_category, subcategory
    ):
        with pytest.raises(ValidationError) as exc_info:
            validate_cascade_chain(expense_type, other_category, subcategory)
        assert "category" in exc_info.value.message_dict

    # --- Error: subcategory doesn't match category ---------------------

    def test_subcategory_wrong_category_raises(
        self, expense_type, category, other_subcategory
    ):
        with pytest.raises(ValidationError) as exc_info:
            validate_cascade_chain(expense_type, category, other_subcategory)
        assert "subcategory" in exc_info.value.message_dict

    # --- Rule 1 failure short-circuits rule 2 check -------------------

    def test_category_error_prevents_subcategory_check(
        self, expense_type, other_category, other_subcategory
    ):
        with pytest.raises(ValidationError) as exc_info:
            validate_cascade_chain(expense_type, other_category, other_subcategory)
        errors = exc_info.value.message_dict
        assert "category" in errors
        assert "subcategory" not in errors

    # --- None values are skipped (partial validation) -----------------

    def test_none_type_skips_validation(self, category, subcategory):
        """If transaction_type is None, no exception is raised."""
        validate_cascade_chain(None, category, subcategory)

    def test_none_category_skips_validation(self, expense_type, subcategory):
        """If category is None, cascade rule 1 and 2 are both skipped."""
        validate_cascade_chain(expense_type, None, subcategory)

    def test_none_subcategory_skips_rule2(self, expense_type, category):
        """If subcategory is None, rule 2 is skipped."""
        validate_cascade_chain(expense_type, category, None)

    # --- Error message content ----------------------------------------

    def test_error_message_names_the_type(
        self, expense_type, other_category, subcategory
    ):
        with pytest.raises(ValidationError) as exc_info:
            validate_cascade_chain(expense_type, other_category, subcategory)
        msg = exc_info.value.message_dict["category"][0]
        assert expense_type.name in msg
        assert other_category.name in msg

"""Smoke tests - basic sanity checks that imports work."""


def test_python_works():
    """The simplest possible test."""
    assert 1 + 1 == 2


def test_can_import_pandas():
    """Verify pandas is installed."""
    import pandas as pd
    assert pd.__version__


def test_can_import_streamlit():
    """Verify streamlit is installed."""
    import streamlit as st
    assert st.__version__

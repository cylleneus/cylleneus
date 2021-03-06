#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cylleneus` package."""


import unittest
from click.testing import CliRunner




class TestCylleneus(unittest.TestCase):
    """Tests for `cylleneus` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_command_line_interface(self):
        """Test the CLI."""

        from cylleneus import cli

        runner = CliRunner()
        result = runner.invoke(cli.main)

        assert result.exit_code == 0
        assert "Corpus management commands for Cylleneus." in result.output
        help_result = runner.invoke(cli.main, ["--help"])
        assert help_result.exit_code == 0
        assert "--help  Show this message and exit." in help_result.output

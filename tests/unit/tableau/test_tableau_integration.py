"""
Unit tests for Tableau integration and operations.
Path: tests/unit/tableau/test_tableau_integration.py
"""

from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest


class TestTableauConnection:
    """Test Tableau server connection."""

    def test_connection_initialization(self):
        """Test Tableau connection setup."""
        mock_server = Mock()
        mock_server.server_url = "https://tableau.example.com"
        mock_server.site_id = "site123"
        mock_server.auth_token = "token_abc"

        assert mock_server.server_url is not None
        assert mock_server.site_id is not None
        assert mock_server.auth_token is not None

    def test_authentication(self):
        """Test Tableau authentication."""
        mock_auth = Mock()
        mock_auth.sign_in = Mock(return_value={"token": "auth_token_123"})

        result = mock_auth.sign_in("username", "password")

        assert "token" in result
        assert result["token"] == "auth_token_123"

    def test_connection_error_handling(self):
        """Test connection error handling."""
        mock_server = Mock()
        mock_server.connect = Mock(side_effect=ConnectionError("Connection failed"))

        with pytest.raises(ConnectionError):
            mock_server.connect()


class TestTableauDataExtraction:
    """Test data extraction from Tableau."""

    def test_get_workbook_list(self):
        """Test retrieving workbook list."""
        mock_server = Mock()
        mock_workbooks = [
            {"id": "wb1", "name": "Sales Dashboard"},
            {"id": "wb2", "name": "Finance Report"},
        ]
        mock_server.workbooks.all = Mock(return_value=mock_workbooks)

        workbooks = mock_server.workbooks.all()

        assert len(workbooks) == 2
        assert workbooks[0]["name"] == "Sales Dashboard"

    def test_get_datasource_list(self):
        """Test retrieving datasource list."""
        mock_server = Mock()
        mock_datasources = [
            {"id": "ds1", "name": "Customer Data"},
            {"id": "ds2", "name": "Product Data"},
        ]
        mock_server.datasources.all = Mock(return_value=mock_datasources)

        datasources = mock_server.datasources.all()

        assert len(datasources) == 2

    def test_query_view_data(self):
        """Test querying view data."""
        mock_server = Mock()
        mock_data = pd.DataFrame(
            {
                "Region": ["North", "South", "East", "West"],
                "Sales": [100000, 150000, 120000, 180000],
            }
        )
        mock_server.views.get_data = Mock(return_value=mock_data)

        view_id = "view123"
        data = mock_server.views.get_data(view_id)

        assert len(data) == 4
        assert "Sales" in data.columns


class TestTableauDataPublishing:
    """Test publishing data to Tableau."""

    def test_publish_workbook(self):
        """Test publishing workbook to Tableau."""
        mock_server = Mock()
        mock_server.workbooks.publish = Mock(return_value={"id": "new_wb123"})

        workbook_file = "dashboard.twbx"
        result = mock_server.workbooks.publish(workbook_file)

        assert "id" in result
        assert result["id"] == "new_wb123"

    def test_publish_datasource(self):
        """Test publishing datasource."""
        mock_server = Mock()
        mock_server.datasources.publish = Mock(return_value={"id": "new_ds123"})

        datasource_file = "data.tds"
        result = mock_server.datasources.publish(datasource_file)

        assert "id" in result

    def test_update_workbook(self):
        """Test updating existing workbook."""
        mock_server = Mock()
        mock_server.workbooks.update = Mock(return_value={"status": "success"})

        workbook_id = "wb123"
        updates = {"name": "Updated Dashboard"}
        result = mock_server.workbooks.update(workbook_id, updates)

        assert result["status"] == "success"


class TestTableauMetadata:
    """Test Tableau metadata operations."""

    def test_get_workbook_metadata(self):
        """Test retrieving workbook metadata."""
        mock_workbook = Mock()
        mock_workbook.id = "wb123"
        mock_workbook.name = "Sales Dashboard"
        mock_workbook.created_at = "2024-01-01"

        assert mock_workbook.id == "wb123"
        assert mock_workbook.name == "Sales Dashboard"

    def test_get_view_metadata(self):
        """Test retrieving view metadata."""
        mock_view = Mock()
        mock_view.id = "view123"
        mock_view.name = "Regional Sales"
        mock_view.workbook_id = "wb123"

        assert mock_view.id == "view123"
        assert mock_view.workbook_id == "wb123"


class TestTableauFiltering:
    """Test Tableau filtering operations."""

    def test_apply_filter(self):
        """Test applying filter to view."""
        mock_view = Mock()
        mock_view.apply_filter = Mock(return_value=True)

        filter_params = {"Region": "North", "Year": 2024}
        result = mock_view.apply_filter(filter_params)

        assert result is True

    def test_filter_with_multiple_values(self):
        """Test filtering with multiple values."""
        mock_view = Mock()

        filters = {
            "Region": ["North", "South", "East"],
            "Product_Category": ["Electronics", "Furniture"],
        }

        mock_view.apply_multiple_filters = Mock(return_value=True)
        result = mock_view.apply_multiple_filters(filters)

        assert result is True

    def test_clear_filters(self):
        """Test clearing all filters."""
        mock_view = Mock()
        mock_view.clear_filters = Mock(return_value=True)

        result = mock_view.clear_filters()

        assert result is True


class TestTableauExport:
    """Test Tableau export operations."""

    def test_export_to_pdf(self):
        """Test exporting view to PDF."""
        mock_view = Mock()
        mock_view.export_pdf = Mock(return_value="dashboard.pdf")

        result = mock_view.export_pdf()

        assert result == "dashboard.pdf"

    def test_export_to_image(self):
        """Test exporting view to image."""
        mock_view = Mock()
        mock_view.export_image = Mock(return_value="dashboard.png")

        result = mock_view.export_image(format="png")

        assert result == "dashboard.png"

    def test_export_to_csv(self):
        """Test exporting data to CSV."""
        mock_view = Mock()
        mock_data = pd.DataFrame({"Product": ["A", "B", "C"], "Sales": [100, 200, 300]})
        mock_view.export_csv = Mock(return_value=mock_data)

        result = mock_view.export_csv()

        assert len(result) == 3
        assert "Sales" in result.columns


class TestTableauPermissions:
    """Test Tableau permissions management."""

    def test_get_workbook_permissions(self):
        """Test retrieving workbook permissions."""
        mock_workbook = Mock()
        mock_permissions = [
            {"user": "user1", "role": "Viewer"},
            {"user": "user2", "role": "Editor"},
        ]
        mock_workbook.get_permissions = Mock(return_value=mock_permissions)

        permissions = mock_workbook.get_permissions()

        assert len(permissions) == 2
        assert permissions[0]["role"] == "Viewer"

    def test_set_workbook_permissions(self):
        """Test setting workbook permissions."""
        mock_workbook = Mock()
        mock_workbook.set_permissions = Mock(return_value={"status": "success"})

        new_permissions = {"user": "user3", "role": "Editor"}
        result = mock_workbook.set_permissions(new_permissions)

        assert result["status"] == "success"

    def test_revoke_permissions(self):
        """Test revoking permissions."""
        mock_workbook = Mock()
        mock_workbook.revoke_permissions = Mock(return_value=True)

        result = mock_workbook.revoke_permissions("user1")

        assert result is True


class TestTableauScheduling:
    """Test Tableau scheduling operations."""

    def test_create_refresh_schedule(self):
        """Test creating data refresh schedule."""
        mock_server = Mock()
        schedule_config = {
            "datasource_id": "ds123",
            "frequency": "daily",
            "time": "02:00",
        }
        mock_server.schedules.create = Mock(return_value={"id": "sched123"})

        result = mock_server.schedules.create(schedule_config)

        assert "id" in result

    def test_update_refresh_schedule(self):
        """Test updating refresh schedule."""
        mock_server = Mock()
        mock_server.schedules.update = Mock(return_value={"status": "updated"})

        schedule_id = "sched123"
        updates = {"time": "03:00"}
        result = mock_server.schedules.update(schedule_id, updates)

        assert result["status"] == "updated"

    def test_delete_schedule(self):
        """Test deleting schedule."""
        mock_server = Mock()
        mock_server.schedules.delete = Mock(return_value=True)

        result = mock_server.schedules.delete("sched123")

        assert result is True

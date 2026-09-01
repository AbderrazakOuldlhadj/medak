"""
Google Sheets MCP Server
Provides tools to list, read, create, update, and append data in Google Sheets via Model Context Protocol (MCP).
"""

import sys
import os
import glob
import json
from typing import Any, List, Dict, Optional

# Include user site-packages for mcp module
sys.path.append(r'C:\Users\msipc\AppData\Roaming\Python\Python310\site-packages')
sys.stdout.reconfigure(encoding='utf-8')

from mcp.server.mcpserver import MCPServer
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Initialize MCPServer instance
mcp = MCPServer("google-sheets")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email'
]

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_drive_service():
    token_file = os.path.join(ROOT_DIR, 'token.json')
    if not os.path.exists(token_file):
        token_file = 'token.json'
    if not os.path.exists(token_file):
        raise FileNotFoundError("token.json not found. Please authorize Google access first.")
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    return build('drive', 'v3', credentials=creds)

def get_sheets_service():
    token_file = os.path.join(ROOT_DIR, 'token.json')
    if not os.path.exists(token_file):
        token_file = 'token.json'
    if not os.path.exists(token_file):
        raise FileNotFoundError("token.json not found. Please authorize Google access first.")
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    return build('sheets', 'v4', credentials=creds)

@mcp.tool()
def list_sheets(order_by: str = "modifiedTime desc", max_results: int = 50) -> str:
    """
    List all Google Sheets spreadsheets in your Google Drive.
    
    Args:
        order_by: Sorting field. Default is 'modifiedTime desc' (newest / last edited first).
                  Other options: 'name', 'modifiedTime', 'createdTime desc'.
        max_results: Maximum number of files to return (default: 50).
    """
    try:
        service = get_drive_service()
        query = "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
        results = service.files().list(
            q=query,
            pageSize=max_results,
            orderBy=order_by,
            fields="nextPageToken, files(id, name, modifiedTime, webViewLink, createdTime)"
        ).execute()
        files = results.get('files', [])
        
        output = []
        output.append(f"Found {len(files)} Google Sheets (Sorted by: {order_by}):\n")
        output.append("| # | Sheet Name | Last Modified | Spreadsheet ID | Link |")
        output.append("|---|---|---|---|---|")
        for i, file in enumerate(files, start=1):
            name = file.get('name', 'Untitled').replace('|', '-')
            mod = file.get('modifiedTime', '').replace('T', ' ').replace('Z', '')
            fid = file.get('id')
            link = file.get('webViewLink')
            output.append(f"| {i} | **{name}** | `{mod}` | `{fid}` | [Open]({link}) |")
            
        return "\n".join(output)
    except Exception as e:
        return f"Error listing sheets: {str(e)}"

@mcp.tool()
def create_spreadsheet(title: str) -> str:
    """
    Create a new empty Google Spreadsheet with the given title.
    
    Args:
        title: Title of the new spreadsheet.
    """
    try:
        service = get_sheets_service()
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        res = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
        sp_id = res.get('spreadsheetId')
        url = res.get('spreadsheetUrl')
        return f"Successfully created spreadsheet '{title}'!\nID: `{sp_id}`\nURL: {url}"
    except Exception as e:
        return f"Error creating spreadsheet: {str(e)}"

@mcp.tool()
def read_spreadsheet_values(spreadsheet_id: str, range_name: str = "Sheet1!A1:Z100") -> str:
    """
    Read cell values from a Google Spreadsheet range.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_name: The A1 notation range to read (e.g. 'Sheet1!A1:D50' or 'Sheet1').
    """
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        rows = result.get('values', [])
        if not rows:
            return f"No data found in range '{range_name}' of spreadsheet {spreadsheet_id}."
        
        output = [f"Data from range '{range_name}' ({len(rows)} rows):\n"]
        for row in rows:
            output.append(json.dumps(row, ensure_ascii=False))
        return "\n".join(output)
    except Exception as e:
        return f"Error reading spreadsheet values: {str(e)}"

@mcp.tool()
def append_spreadsheet_rows(spreadsheet_id: str, range_name: str, rows: List[List[Any]]) -> str:
    """
    Append rows of data to a spreadsheet starting after the existing content.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_name: Target sheet/range name (e.g., 'Sheet1' or 'Sheet1!A1').
        rows: List of row arrays, where each array contains cell values.
    """
    try:
        service = get_sheets_service()
        body = {'values': rows}
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        updated = result.get('updates', {}).get('updatedRows', 0)
        return f"Successfully appended {updated} rows to spreadsheet {spreadsheet_id}."
    except Exception as e:
        return f"Error appending rows: {str(e)}"

@mcp.tool()
def update_spreadsheet_range(spreadsheet_id: str, range_name: str, rows: List[List[Any]]) -> str:
    """
    Update cell values in a specific range of a spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_name: Specific A1 range to update (e.g. 'Sheet1!A1:C5').
        rows: List of row arrays with cell values to write.
    """
    try:
        service = get_sheets_service()
        body = {'values': rows}
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        updated_cells = result.get('updatedCells', 0)
        return f"Successfully updated {updated_cells} cells in range '{range_name}'."
    except Exception as e:
        return f"Error updating spreadsheet: {str(e)}"

if __name__ == '__main__':
    mcp.run()

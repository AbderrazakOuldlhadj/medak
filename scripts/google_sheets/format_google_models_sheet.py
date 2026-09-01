import sys
import os

sys.path.append(r'C:\Users\msipc\AppData\Roaming\Python\Python310\site-packages')
sys.path.append(os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')

import google_sheets_mcp as mcp_mod

SPREADSHEET_ID = "1oI09pLLMrCaoJokOB_gvIQQP7pObCE3_M7_LiyWf8rc"

def format_sheet():
    service = mcp_mod.get_sheets_service()
    
    requests = [
        # Format Title (Row 1)
        {
            "repeatCell": {
                "range": {
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 9
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "fontSize": 14,
                            "bold": True,
                            "foregroundColor": {"red": 0.1, "green": 0.25, "blue": 0.55}
                        }
                    }
                },
                "fields": "userEnteredFormat(textFormat)"
            }
        },
        # Format Table Header (Row 4, index 3)
        {
            "repeatCell": {
                "range": {
                    "startRowIndex": 3,
                    "endRowIndex": 4,
                    "startColumnIndex": 0,
                    "endColumnIndex": 9
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.1, "green": 0.45, "blue": 0.91},
                        "textFormat": {
                            "fontSize": 11,
                            "bold": True,
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        },
        # Align Intelligence Score & Prices to Center
        {
            "repeatCell": {
                "range": {
                    "startRowIndex": 4,
                    "endRowIndex": 14,
                    "startColumnIndex": 2,
                    "endColumnIndex": 8
                },
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment)"
            }
        },
        # Auto-resize columns A to I
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 9
                }
            }
        }
    ]
    
    body = {'requests': requests}
    res = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print("Formatting applied successfully!")

if __name__ == '__main__':
    format_sheet()

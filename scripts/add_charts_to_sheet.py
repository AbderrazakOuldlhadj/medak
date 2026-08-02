import sys
import os

sys.path.append(r'C:\Users\msipc\AppData\Roaming\Python\Python310\site-packages')
sys.path.append(os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')

import google_sheets_mcp as mcp_mod

SPREADSHEET_ID = "1oI09pLLMrCaoJokOB_gvIQQP7pObCE3_M7_LiyWf8rc"

def add_horizontal_bar_chart():
    service = mcp_mod.get_sheets_service()
    
    requests = [
        # Chart 2: Horizontal Bar Chart of Intelligence Ratings
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Google AI Models - Intelligence Ranking (Horizontal Bar Chart)",
                        "basicChart": {
                            "chartType": "BAR",
                            "legendPosition": "NO_LEGEND",
                            "axis": [
                                {
                                    "position": "BOTTOM_AXIS",
                                    "title": "Intelligence Rating (1-10)"
                                },
                                {
                                    "position": "LEFT_AXIS",
                                    "title": "Model Name"
                                }
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": 0,
                                                    "startRowIndex": 3,
                                                    "endRowIndex": 14,
                                                    "startColumnIndex": 0,
                                                    "endColumnIndex": 1
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": 0,
                                                    "startRowIndex": 3,
                                                    "endRowIndex": 14,
                                                    "startColumnIndex": 2,
                                                    "endColumnIndex": 3
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "BOTTOM_AXIS"
                                }
                            ],
                            "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": 0,
                                "rowIndex": 39,
                                "columnIndex": 0
                            },
                            "widthPixels": 750,
                            "heightPixels": 450
                        }
                    }
                }
            }
        }
    ]
    
    body = {'requests': requests}
    res = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    print("Horizontal Bar Chart added successfully!")

if __name__ == '__main__':
    add_horizontal_bar_chart()

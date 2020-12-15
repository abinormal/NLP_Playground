# Create the head plus quick css
head = '''
<html>
    <head>
        <style>
            html, body {
                padding: 10;
                margin: 10;
            }

            body {
                font-family: BlinkMacSystemFont, -apple-system, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", "Helvetica", "Arial", sans-serif;
            }

            h1 {
                text-align: center;
            }

            th {
                position: sticky;
                top: 0;
                background: #6c7ae0;
                text-align: left;
                font-weight: normal;
                font-size: 1.1rem;
                color: white;
                padding: 15px 10px;
                min-width: 150px;
            }

            th:last-child {
                border: 0;
            }

            td {
                padding: 10px;
                vertical-align: top;
            }

            tr:nth-child(even) td {
                background: #f8f6ff;
            }

        </style>
    </head>
    <body id="top">
        <h1>The most frequent interesting words</h1>
'''
middle = '''        
        <table>
            <thead>
                <tr>
                    <th>Word (frequency)</th>
                    <th>Documents</th>
                    <th>Sentences</th>
                </tr>
            </thead>
            <tbody>
'''
# Create the tail
tail = '''  </tbody>
        </table>
    </body>
</html> '''

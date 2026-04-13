

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Live Camera Stream</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            text-align: center;
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            border: 2px solid #667eea;
        }
        .status {
            margin-top: 15px;
            font-size: 14px;
            color: #666;
        }
        .status.active {
            color: #4CAF50;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📹 Live Camera Stream</h1>
        <img src="/video_feed" alt="Live Stream" width="640" height="480">
        <div class="status active">✓ Stream Active</div>
    </div>
</body>
</html>
'''
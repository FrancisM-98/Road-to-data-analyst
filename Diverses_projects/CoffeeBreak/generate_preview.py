import base64
import os

def get_b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

img_empty = get_b64('assets/mug_empty.png')
img_full = get_b64('assets/mug_full.png')

html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Coffee Mug Animation Preview</title>
<style>
  body {{
    font-family: 'Segoe UI', sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 0;
  }}
  .card {{
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    text-align: center;
    max-width: 400px;
  }}
  h2 {{
    color: #333;
    margin-bottom: 0.5rem;
  }}
  p {{
    color: #666;
    margin-bottom: 1.5rem;
  }}
  .mug-container {{
    position: relative;
    width: 200px;
    height: 200px;
    margin: 0 auto;
  }}
  .mug-base {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    z-index: 1;
  }}
  .fill-container {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 75%;
    overflow: hidden;
    z-index: 2;
    transition: height 0.3s ease-out;
  }}
  .mug-full {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 200px;
    object-fit: contain;
  }}
  .controls {{
    margin-top: 1.5rem;
  }}
  .controls label {{
    font-weight: bold;
    color: #333;
  }}
  input[type=range] {{
    width: 100%;
    margin: 10px 0;
    -webkit-appearance: none;
    height: 8px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 4px;
    outline: none;
  }}
  input[type=range]::-webkit-slider-thumb {{
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  }}
  .fill-text {{
    font-size: 24px;
    font-weight: bold;
    color: #764ba2;
    margin-top: 1rem;
  }}
</style>
</head>
<body>
  <div class="card">
    <h2>☕ Coffee Mug Animation</h2>
    <p>Interactive preview for portfolio</p>
    
    <div class="mug-container">
      <img src="data:image/png;base64,{img_empty}" class="mug-base">
      <div class="fill-container" id="filler">
        <img src="data:image/png;base64,{img_full}" class="mug-full">
      </div>
    </div>
    
    <div class="fill-text"><span id="val">50</span>%</div>
    
    <div class="controls">
      <label>Fill Level</label>
      <input type="range" min="0" max="100" value="50" oninput="updateFill(this.value)">
    </div>
  </div>

  <script>
    function updateFill(val) {{
      const minHeight = 60;
      const maxHeight = 90;
      const visualHeight = minHeight + ((val / 100) * (maxHeight - minHeight));
      document.getElementById('filler').style.height = visualHeight + '%';
      document.getElementById('val').textContent = val;
    }}
  </script>
</body>
</html>'''

with open('preview_mug.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Created preview_mug.html')
